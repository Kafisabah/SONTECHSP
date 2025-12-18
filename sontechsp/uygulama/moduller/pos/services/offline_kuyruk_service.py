# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.services.offline_kuyruk_service
# Description: Offline kuyruk service implementasyonu
# Changelog:
# - İlk oluşturma

"""
Offline Kuyruk Service Implementasyonu

Bu modül offline kuyruk yönetimi iş kurallarını içerir.
Network durumu kontrolü, kuyruk yönetimi ve senkronizasyon işlemlerini sağlar.
"""

import socket
import time
import requests
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from threading import Lock

from sontechsp.uygulama.moduller.pos.arayuzler import (
    IOfflineKuyrukService, IOfflineKuyrukRepository, IslemTuru, KuyrukDurum
)
from sontechsp.uygulama.cekirdek.hatalar import (
    SontechHatasi, DogrulamaHatasi, NetworkHatasi
)
from sontechsp.uygulama.cekirdek.kayit import kayit_al


class OfflineKuyrukService(IOfflineKuyrukService):
    """
    Offline kuyruk service implementasyonu
    
    Network kesintilerinde işlem kuyruğu yönetimi sağlar.
    Kuyruk senkronizasyonu ve hata yönetimi işlemlerini yürütür.
    """
    
    def __init__(self, kuyruk_repository: IOfflineKuyrukRepository):
        """
        Service'i başlatır
        
        Args:
            kuyruk_repository: Offline kuyruk repository
        """
        self._kuyruk_repo = kuyruk_repository
        self._logger = kayit_al(__name__)
        self._senkron_lock = Lock()
        self._son_network_kontrol = None
        self._network_durum_cache_suresi = 30  # saniye
        self._network_timeout = 5  # saniye
        self._senkron_batch_boyutu = 10
        self._max_senkron_suresi = 300  # 5 dakika
    
    def network_durumu_kontrol(self) -> bool:
        """
        Network durumunu kontrol eder
        
        Cache mekanizması ile sık kontrol edilmesini önler.
        
        Returns:
            Network bağlantısı var mı
        """
        try:
            # Cache kontrolü
            simdi = datetime.now()
            if (self._son_network_kontrol and 
                (simdi - self._son_network_kontrol).total_seconds() < self._network_durum_cache_suresi):
                return self._cached_network_durumu
            
            # DNS çözümleme testi
            socket.setdefaulttimeout(self._network_timeout)
            socket.gethostbyname('google.com')
            
            # HTTP bağlantı testi
            response = requests.get(
                'https://httpbin.org/status/200',
                timeout=self._network_timeout
            )
            
            network_durumu = response.status_code == 200
            
            # Cache güncelle
            self._son_network_kontrol = simdi
            self._cached_network_durumu = network_durumu
            
            if network_durumu:
                self._logger.debug("Network bağlantısı aktif")
            else:
                self._logger.warning("Network bağlantısı yok - HTTP test başarısız")
            
            return network_durumu
            
        except (socket.gaierror, socket.timeout, requests.RequestException) as e:
            self._logger.warning(f"Network bağlantısı yok: {str(e)}")
            
            # Cache güncelle
            self._son_network_kontrol = simdi
            self._cached_network_durumu = False
            
            return False
        except Exception as e:
            self._logger.error(f"Network durumu kontrol hatası: {str(e)}")
            return False
    
    def islem_kuyruga_ekle(self, islem_turu: IslemTuru, veri: Dict[str, Any],
                          terminal_id: int, kasiyer_id: int, 
                          oncelik: int = 1, notlar: Optional[str] = None) -> bool:
        """
        İşlemi kuyruğa ekler
        
        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            oncelik: İşlem önceliği (1=yüksek, 5=düşük)
            notlar: İşlem notları
            
        Returns:
            Ekleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Kuyruk ekleme hatası
        """
        try:
            # Parametreleri doğrula
            if not isinstance(veri, dict) or not veri:
                raise DogrulamaHatasi("İşlem verisi geçerli bir dict olmalıdır")
            
            if terminal_id <= 0:
                raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
            
            if kasiyer_id <= 0:
                raise DogrulamaHatasi("Kasiyer ID pozitif olmalıdır")
            
            if oncelik < 1 or oncelik > 5:
                raise DogrulamaHatasi("Öncelik 1-5 arasında olmalıdır")
            
            # Network durumu kontrol et
            network_aktif = self.network_durumu_kontrol()
            
            if network_aktif:
                # Network varsa direkt işlemi göndermeyi dene
                try:
                    basarili = self._islem_direkt_gonder(islem_turu, veri, terminal_id, kasiyer_id)
                    if basarili:
                        self._logger.info(f"İşlem direkt gönderildi: {islem_turu.value}")
                        return True
                except Exception as e:
                    self._logger.warning(f"Direkt gönderim başarısız, kuyruğa ekleniyor: {str(e)}")
            
            # Kuyruğa ekle
            kuyruk_id = self._kuyruk_repo.kuyruk_ekle(
                islem_turu=islem_turu,
                veri=veri,
                terminal_id=terminal_id,
                kasiyer_id=kasiyer_id,
                oncelik=oncelik,
                notlar=notlar
            )
            
            self._logger.info(f"İşlem kuyruğa eklendi: ID={kuyruk_id}, Tür={islem_turu.value}")
            
            # Network varsa hemen senkronizasyon dene
            if network_aktif:
                try:
                    self.kuyruk_senkronize_et()
                except Exception as e:
                    self._logger.warning(f"Otomatik senkronizasyon başarısız: {str(e)}")
            
            return True
            
        except (DogrulamaHatasi, SontechHatasi):
            raise
        except Exception as e:
            self._logger.error(f"Kuyruk ekleme hatası: {str(e)}")
            raise SontechHatasi(f"İşlem kuyruğa eklenemedi: {str(e)}")
    
    def kuyruk_senkronize_et(self) -> int:
        """
        Kuyruğu senkronize eder (Ana koordinasyon fonksiyonu)
        
        Bekleyen işlemleri sırayla gönderir ve durumlarını günceller.
        Thread-safe implementasyon.
        
        Returns:
            İşlenen kayıt sayısı
            
        Raises:
            NetworkHatasi: Network bağlantısı yok
            SontechHatasi: Senkronizasyon hatası
        """
        with self._senkron_lock:
            try:
                # 1. Ön kontroller
                self._senkron_on_kontrol()
                
                # 2. Senkronizasyon döngüsü
                islenen_sayisi = self._senkron_dongusu_calistir()
                
                self._logger.info(f"Kuyruk senkronizasyonu tamamlandı: {islenen_sayisi} işlem")
                return islenen_sayisi
                
            except NetworkHatasi:
                raise
            except Exception as e:
                self._logger.error(f"Kuyruk senkronizasyon hatası: {str(e)}")
                raise SontechHatasi(f"Kuyruk senkronize edilemedi: {str(e)}")
    
    def _senkron_on_kontrol(self) -> None:
        """
        Senkronizasyon öncesi kontrolleri yapar
        
        Raises:
            NetworkHatasi: Network bağlantısı yok
        """
        # Network durumu kontrol et
        if not self.network_durumu_kontrol():
            raise NetworkHatasi("Network bağlantısı yok, senkronizasyon yapılamaz")
        
        self._logger.info("Kuyruk senkronizasyonu başlatıldı")
    
    def _senkron_dongusu_calistir(self) -> int:
        """
        Ana senkronizasyon döngüsünü çalıştırır
        
        Returns:
            int: İşlenen kayıt sayısı
        """
        islenen_sayisi = 0
        basla_zamani = datetime.now()
        
        while True:
            # Zaman aşımı kontrolü
            if self._zaman_asimi_kontrol(basla_zamani):
                break
            
            # Bekleyen işlemleri getir
            bekleyen_islemler = self._kuyruk_repo.bekleyen_kuyruk_listesi(
                limit=self._senkron_batch_boyutu
            )
            
            if not bekleyen_islemler:
                break
            
            # İşlemleri sırayla gönder
            batch_islenen = self._batch_islemlerini_gonder(bekleyen_islemler)
            islenen_sayisi += batch_islenen
            
            # Network bağlantısı kesildi mi kontrol et
            if not self.network_durumu_kontrol():
                self._logger.warning("Network bağlantısı kesildi, senkronizasyon durduruluyor")
                break
            
            # Kısa bekleme
            time.sleep(0.1)
        
        return islenen_sayisi
    
    def _zaman_asimi_kontrol(self, basla_zamani: datetime) -> bool:
        """
        Zaman aşımı kontrolü yapar
        
        Args:
            basla_zamani: Başlangıç zamanı
            
        Returns:
            bool: Zaman aşımı var mı
        """
        gecen_sure = (datetime.now() - basla_zamani).total_seconds()
        if gecen_sure > self._max_senkron_suresi:
            self._logger.warning(f"Senkronizasyon zaman aşımı: {gecen_sure} saniye")
            return True
        return False
    
    def _batch_islemlerini_gonder(self, bekleyen_islemler: List[Dict]) -> int:
        """
        Batch işlemlerini gönderir
        
        Args:
            bekleyen_islemler: Bekleyen işlem listesi
            
        Returns:
            int: Bu batch'te işlenen kayıt sayısı
        """
        batch_islenen = 0
        
        for islem in bekleyen_islemler:
            try:
                # Network durumu tekrar kontrol et
                if not self.network_durumu_kontrol():
                    break
                
                # Tek işlemi gönder
                if self._tek_islemi_gonder(islem):
                    batch_islenen += 1
                
            except Exception as e:
                self._islem_hata_yonet(islem, e)
        
        return batch_islenen
    
    def _tek_islemi_gonder(self, islem: Dict) -> bool:
        """
        Tek işlemi gönderir
        
        Args:
            islem: İşlem bilgisi
            
        Returns:
            bool: İşlem başarılı mı
        """
        # İşlemi işleniyor durumuna getir
        self._kuyruk_repo.kuyruk_durum_guncelle(
            islem['id'], 
            KuyrukDurum.ISLENIYOR
        )
        
        # İşlemi gönder
        basarili = self._kuyruk_islemini_gonder(islem)
        
        if basarili:
            # Başarılı - tamamlandı olarak işaretle
            self._kuyruk_repo.kuyruk_durum_guncelle(
                islem['id'], 
                KuyrukDurum.TAMAMLANDI
            )
            self._logger.debug(f"Kuyruk işlemi tamamlandı: ID={islem['id']}")
            return True
        else:
            # Başarısız - deneme sayısını artır
            self._kuyruk_repo.kuyruk_deneme_artir(
                islem['id'], 
                "Senkronizasyon sırasında işlem başarısız"
            )
            self._logger.warning(f"Kuyruk işlemi başarısız: ID={islem['id']}")
            return False
    
    def _islem_hata_yonet(self, islem: Dict, hata: Exception) -> None:
        """
        İşlem hatası yönetimi
        
        Args:
            islem: İşlem bilgisi
            hata: Oluşan hata
        """
        try:
            self._kuyruk_repo.kuyruk_deneme_artir(
                islem['id'], 
                f"Senkronizasyon hatası: {str(hata)}"
            )
        except Exception:
            pass
        
        self._logger.error(f"Kuyruk işlemi hatası: ID={islem['id']}, Hata: {str(hata)}")
    
    def offline_durum_bildir(self, terminal_id: int, kasiyer_id: int, 
                           islem_turu: IslemTuru) -> None:
        """
        Kullanıcıya offline durum bildirimi yapar
        
        Args:
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            islem_turu: İşlem türü
        """
        try:
            mesaj = f"Offline Mod: {islem_turu.value.title()} işlemi kuyruğa eklendi"
            
            # Log kaydı
            self._logger.info(f"Offline durum bildirimi - Terminal: {terminal_id}, "
                            f"Kasiyer: {kasiyer_id}, İşlem: {islem_turu.value}")
            
            # Burada UI bildirimi yapılabilir (signal/slot mekanizması ile)
            # Şimdilik sadece log kaydı yapıyoruz
            
        except Exception as e:
            self._logger.error(f"Offline durum bildirimi hatası: {str(e)}")
    
    def kuyruk_istatistikleri_getir(self, terminal_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Kuyruk istatistiklerini getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            
        Returns:
            Kuyruk istatistikleri
        """
        try:
            istatistikler = self._kuyruk_repo.kuyruk_istatistikleri(terminal_id)
            
            # Network durumu ekle
            istatistikler['network_durumu'] = self.network_durumu_kontrol()
            
            return istatistikler
            
        except Exception as e:
            self._logger.error(f"Kuyruk istatistikleri hatası: {str(e)}")
            return {
                'toplam_kayit': 0,
                'durum_sayilari': {},
                'islem_turu_sayilari': {},
                'network_durumu': False,
                'hata': str(e)
            }
    
    def hata_durumundaki_islemler(self, terminal_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Hata durumundaki işlemleri getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            
        Returns:
            Hata durumundaki işlem listesi
        """
        try:
            return self._kuyruk_repo.hata_durumundaki_kuyruklar(terminal_id)
        except Exception as e:
            self._logger.error(f"Hata durumundaki işlemler getirme hatası: {str(e)}")
            return []
    
    def kuyruk_temizle(self, gun_sayisi: int = 30) -> int:
        """
        Eski tamamlanan kuyruk kayıtlarını temizler
        
        Args:
            gun_sayisi: Kaç gün önceki kayıtlar temizlenecek
            
        Returns:
            Temizlenen kayıt sayısı
        """
        try:
            if gun_sayisi <= 0:
                raise DogrulamaHatasi("Gün sayısı pozitif olmalıdır")
            
            temizlenen_sayisi = self._kuyruk_repo.kuyruk_temizle(gun_sayisi)
            
            self._logger.info(f"Kuyruk temizlendi: {temizlenen_sayisi} kayıt, "
                            f"{gun_sayisi} gün öncesi")
            
            return temizlenen_sayisi
            
        except Exception as e:
            self._logger.error(f"Kuyruk temizleme hatası: {str(e)}")
            return 0
    
    def _islem_direkt_gonder(self, islem_turu: IslemTuru, veri: Dict[str, Any],
                           terminal_id: int, kasiyer_id: int) -> bool:
        """
        İşlemi direkt ana sisteme gönderir (private method)
        
        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Gönderim başarılı mı
        """
        try:
            # Burada ana sistem API'sine HTTP çağrısı yapılacak
            # Şimdilik mock implementasyon
            
            self._logger.debug(f"Direkt gönderim deneniyor: {islem_turu.value}")
            
            # Simüle edilmiş API çağrısı
            time.sleep(0.1)  # Network gecikmesi simülasyonu
            
            # %90 başarı oranı simülasyonu
            import random
            return random.random() > 0.1
            
        except Exception as e:
            self._logger.warning(f"Direkt gönderim hatası: {str(e)}")
            return False
    
    def _kuyruk_islemini_gonder(self, islem: Dict[str, Any]) -> bool:
        """
        Kuyruk işlemini ana sisteme gönderir (private method)
        
        Args:
            islem: Kuyruk işlemi
            
        Returns:
            Gönderim başarılı mı
        """
        try:
            islem_turu = IslemTuru(islem['islem_turu'])
            veri = islem['veri']
            
            self._logger.debug(f"Kuyruk işlemi gönderiliyor: ID={islem['id']}, "
                             f"Tür={islem_turu.value}")
            
            # İşlem türüne göre farklı endpoint'lere gönderim
            if islem_turu == IslemTuru.SATIS:
                return self._satis_islemini_gonder(veri)
            elif islem_turu == IslemTuru.IADE:
                return self._iade_islemini_gonder(veri)
            elif islem_turu == IslemTuru.STOK_DUSUMU:
                return self._stok_dusumu_islemini_gonder(veri)
            else:
                self._logger.error(f"Bilinmeyen işlem türü: {islem_turu}")
                return False
                
        except Exception as e:
            self._logger.error(f"Kuyruk işlemi gönderim hatası: {str(e)}")
            return False
    
    def _satis_islemini_gonder(self, veri: Dict[str, Any]) -> bool:
        """
        Satış işlemini ana sisteme gönderir (private method)
        
        Args:
            veri: Satış verisi
            
        Returns:
            Gönderim başarılı mı
        """
        try:
            # Burada satış API endpoint'ine POST çağrısı yapılacak
            # Şimdilik mock implementasyon
            
            self._logger.debug(f"Satış işlemi gönderiliyor: Fiş No={veri.get('fis_no')}")
            
            # Simüle edilmiş API çağrısı
            time.sleep(0.2)
            
            # %85 başarı oranı
            import random
            return random.random() > 0.15
            
        except Exception as e:
            self._logger.error(f"Satış işlemi gönderim hatası: {str(e)}")
            return False
    
    def _iade_islemini_gonder(self, veri: Dict[str, Any]) -> bool:
        """
        İade işlemini ana sisteme gönderir (private method)
        
        Args:
            veri: İade verisi
            
        Returns:
            Gönderim başarılı mı
        """
        try:
            # Burada iade API endpoint'ine POST çağrısı yapılacak
            # Şimdilik mock implementasyon
            
            self._logger.debug(f"İade işlemi gönderiliyor: İade ID={veri.get('iade_id')}")
            
            # Simüle edilmiş API çağrısı
            time.sleep(0.15)
            
            # %80 başarı oranı
            import random
            return random.random() > 0.2
            
        except Exception as e:
            self._logger.error(f"İade işlemi gönderim hatası: {str(e)}")
            return False
    
    def _stok_dusumu_islemini_gonder(self, veri: Dict[str, Any]) -> bool:
        """
        Stok düşümü işlemini ana sisteme gönderir (private method)
        
        Args:
            veri: Stok düşümü verisi
            
        Returns:
            Gönderim başarılı mı
        """
        try:
            # Burada stok API endpoint'ine POST çağrısı yapılacak
            # Şimdilik mock implementasyon
            
            self._logger.debug(f"Stok düşümü işlemi gönderiliyor: "
                             f"Ürün ID={veri.get('urun_id')}, Adet={veri.get('adet')}")
            
            # Simüle edilmiş API çağrısı
            time.sleep(0.1)
            
            # %90 başarı oranı
            import random
            return random.random() > 0.1
            
        except Exception as e:
            self._logger.error(f"Stok düşümü işlemi gönderim hatası: {str(e)}")
            return False