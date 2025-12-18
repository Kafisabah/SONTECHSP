# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.repositories.offline_kuyruk_repository
# Description: Offline kuyruk repository implementasyonu
# Changelog:
# - İlk oluşturma

"""
Offline Kuyruk Repository Implementasyonu

Bu modül offline kuyruk veri erişim işlemlerini yönetir.
SQLite kuyruk operasyonları ve kuyruk durumu yönetimi sağlar.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc

from sontechsp.uygulama.veritabani.baglanti import sqlite_session
from sontechsp.uygulama.moduller.pos.arayuzler import (
    IOfflineKuyrukRepository, IslemTuru, KuyrukDurum
)
from sontechsp.uygulama.moduller.pos.database.models.offline_kuyruk import (
    OfflineKuyruk, offline_kuyruk_validasyon,
    satis_kuyruk_verisi_olustur, iade_kuyruk_verisi_olustur, stok_dusumu_kuyruk_verisi_olustur
)
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class OfflineKuyrukRepository(IOfflineKuyrukRepository):
    """
    Offline kuyruk repository implementasyonu
    
    SQLite tabanlı kuyruk operasyonlarını yönetir.
    Network kesintilerinde işlem kuyruğu yönetimi sağlar.
    """
    
    def __init__(self):
        """Repository'yi başlatır"""
        pass
    
    def kuyruga_ekle(self, islem_turu: IslemTuru, veri: Dict[str, Any], 
                    terminal_id: int = None, kasiyer_id: int = None, 
                    oncelik: int = 1, notlar: Optional[str] = None) -> int:
        """
        Kuyruğa yeni işlem ekler
        
        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            oncelik: İşlem önceliği (1=yüksek, 5=düşük)
            notlar: İşlem notları (opsiyonel)
            
        Returns:
            Oluşturulan kuyruk ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if terminal_id <= 0:
            raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
        
        if kasiyer_id <= 0:
            raise DogrulamaHatasi("Kasiyer ID pozitif olmalıdır")
        
        if not veri:
            raise DogrulamaHatasi("İşlem verisi boş olamaz")
        
        if oncelik < 1 or oncelik > 5:
            raise DogrulamaHatasi("Öncelik 1-5 arasında olmalıdır")
        
        with sqlite_session() as session:
            try:
                # Yeni kuyruk kaydı oluştur
                yeni_kuyruk = OfflineKuyruk(
                    islem_turu=islem_turu,
                    durum=KuyrukDurum.BEKLEMEDE,
                    veri=veri,
                    terminal_id=terminal_id,
                    kasiyer_id=kasiyer_id,
                    islem_tarihi=datetime.now(),
                    deneme_sayisi=0,
                    max_deneme_sayisi=3,
                    oncelik=oncelik,
                    notlar=notlar
                )
                
                # Validasyon
                hatalar = offline_kuyruk_validasyon(yeni_kuyruk)
                if hatalar:
                    raise DogrulamaHatasi(f"Kuyruk validasyon hataları: {', '.join(hatalar)}")
                
                session.add(yeni_kuyruk)
                session.commit()
                
                return yeni_kuyruk.id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk ekleme hatası: {str(e)}")
    
    def kuyruk_ekle(self, islem_turu: IslemTuru, veri: Dict[str, Any], 
                   terminal_id: int, kasiyer_id: int, 
                   oncelik: int = 1, notlar: Optional[str] = None) -> int:
        """
        Kuyruğa yeni işlem ekler (alternatif metod adı)
        
        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            oncelik: İşlem önceliği (1=yüksek, 5=düşük)
            notlar: İşlem notları (opsiyonel)
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        return self.kuyruga_ekle(islem_turu, veri, terminal_id, kasiyer_id, oncelik, notlar)
    
    def kuyruk_getir(self, kuyruk_id: int) -> Optional[Dict[str, Any]]:
        """
        Kuyruk kaydını getirir
        
        Args:
            kuyruk_id: Kuyruk kimliği
            
        Returns:
            Kuyruk bilgileri dict formatında veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz kuyruk ID
            VeritabaniHatasi: Veritabanı hatası
        """
        if kuyruk_id <= 0:
            raise DogrulamaHatasi("Kuyruk ID pozitif olmalıdır")
        
        with sqlite_session() as session:
            try:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                
                if not kuyruk:
                    return None
                
                return self._kuyruk_dict_donustur(kuyruk)
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Kuyruk getirme hatası: {str(e)}")
    
    def bekleyen_kuyruk_listesi(self, terminal_id: Optional[int] = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """
        Bekleyen kuyruk kayıtlarını getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            limit: Maksimum kayıt sayısı
            
        Returns:
            Bekleyen kuyruk listesi
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if limit <= 0 or limit > 1000:
            raise DogrulamaHatasi("Limit 1-1000 arasında olmalıdır")
        
        with sqlite_session() as session:
            try:
                query = session.query(OfflineKuyruk).filter(
                    OfflineKuyruk.durum == KuyrukDurum.BEKLEMEDE
                )
                
                if terminal_id:
                    query = query.filter(OfflineKuyruk.terminal_id == terminal_id)
                
                # Öncelik ve tarihe göre sırala
                query = query.order_by(
                    asc(OfflineKuyruk.oncelik),
                    asc(OfflineKuyruk.islem_tarihi)
                ).limit(limit)
                
                kuyruklar = query.all()
                
                return [self._kuyruk_dict_donustur(kuyruk) for kuyruk in kuyruklar]
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Bekleyen kuyruk listesi hatası: {str(e)}")
    
    def kuyruk_durum_guncelle(self, kuyruk_id: int, yeni_durum: KuyrukDurum,
                            hata_mesaji: Optional[str] = None) -> bool:
        """
        Kuyruk durumunu günceller
        
        Args:
            kuyruk_id: Kuyruk kimliği
            yeni_durum: Yeni durum
            hata_mesaji: Hata mesajı (hata durumu için)
            
        Returns:
            Güncelleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Kuyruk bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if kuyruk_id <= 0:
            raise DogrulamaHatasi("Kuyruk ID pozitif olmalıdır")
        
        with sqlite_session() as session:
            try:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                if not kuyruk:
                    raise SontechHatasi(f"Kuyruk bulunamadı: {kuyruk_id}")
                
                # Duruma göre güncelleme
                if yeni_durum == KuyrukDurum.ISLENIYOR:
                    kuyruk.isleme_basla()
                elif yeni_durum == KuyrukDurum.TAMAMLANDI:
                    kuyruk.tamamla()
                elif yeni_durum == KuyrukDurum.HATA:
                    kuyruk.hata_durumuna_getir(hata_mesaji or "Bilinmeyen hata")
                elif yeni_durum == KuyrukDurum.BEKLEMEDE:
                    kuyruk.beklemede_durumuna_getir()
                
                # Validasyon
                hatalar = offline_kuyruk_validasyon(kuyruk)
                if hatalar:
                    raise DogrulamaHatasi(f"Kuyruk validasyon hataları: {', '.join(hatalar)}")
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk durum güncelleme hatası: {str(e)}")
    
    def kuyruk_deneme_artir(self, kuyruk_id: int, hata_mesaji: str) -> bool:
        """
        Kuyruk deneme sayısını artırır
        
        Args:
            kuyruk_id: Kuyruk kimliği
            hata_mesaji: Hata mesajı
            
        Returns:
            Artırma başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Kuyruk bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if kuyruk_id <= 0:
            raise DogrulamaHatasi("Kuyruk ID pozitif olmalıdır")
        
        if not hata_mesaji or not hata_mesaji.strip():
            raise DogrulamaHatasi("Hata mesajı boş olamaz")
        
        with sqlite_session() as session:
            try:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                if not kuyruk:
                    raise SontechHatasi(f"Kuyruk bulunamadı: {kuyruk_id}")
                
                kuyruk.deneme_artir()
                
                # Maksimum deneme sayısı aşıldı mı kontrol et
                if kuyruk.max_deneme_asildi_mi():
                    kuyruk.hata_durumuna_getir(f"Maksimum deneme sayısı aşıldı: {hata_mesaji}")
                else:
                    kuyruk.hata_durumuna_getir(hata_mesaji)
                    kuyruk.beklemede_durumuna_getir()  # Tekrar deneme için
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk deneme artırma hatası: {str(e)}")
    
    def hata_durumundaki_kuyruklar(self, terminal_id: Optional[int] = None,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """
        Hata durumundaki kuyruk kayıtlarını getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            limit: Maksimum kayıt sayısı
            
        Returns:
            Hata durumundaki kuyruk listesi
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if limit <= 0 or limit > 1000:
            raise DogrulamaHatasi("Limit 1-1000 arasında olmalıdır")
        
        with sqlite_session() as session:
            try:
                query = session.query(OfflineKuyruk).filter(
                    OfflineKuyruk.durum == KuyrukDurum.HATA
                )
                
                if terminal_id:
                    query = query.filter(OfflineKuyruk.terminal_id == terminal_id)
                
                # Son deneme tarihine göre sırala
                query = query.order_by(desc(OfflineKuyruk.son_deneme_tarihi)).limit(limit)
                
                kuyruklar = query.all()
                
                return [self._kuyruk_dict_donustur(kuyruk) for kuyruk in kuyruklar]
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Hata durumundaki kuyruklar hatası: {str(e)}")
    
    def kuyruk_temizle(self, gun_sayisi: int = 30) -> int:
        """
        Tamamlanan eski kuyruk kayıtlarını temizler
        
        Args:
            gun_sayisi: Kaç gün önceki kayıtlar temizlenecek
            
        Returns:
            Temizlenen kayıt sayısı
            
        Raises:
            DogrulamaHatasi: Geçersiz gün sayısı
            VeritabaniHatasi: Veritabanı hatası
        """
        if gun_sayisi <= 0:
            raise DogrulamaHatasi("Gün sayısı pozitif olmalıdır")
        
        with sqlite_session() as session:
            try:
                # Belirtilen gün sayısından eski tarihi hesapla
                eski_tarih = datetime.now() - timedelta(days=gun_sayisi)
                
                # Tamamlanan eski kayıtları sil
                silinen_sayisi = session.query(OfflineKuyruk).filter(
                    and_(
                        OfflineKuyruk.durum == KuyrukDurum.TAMAMLANDI,
                        OfflineKuyruk.tamamlanma_tarihi < eski_tarih
                    )
                ).delete()
                
                session.commit()
                return silinen_sayisi
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk temizleme hatası: {str(e)}")
    
    def kuyruk_istatistikleri(self, terminal_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Kuyruk istatistiklerini getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            
        Returns:
            Kuyruk istatistikleri
            
        Raises:
            VeritabaniHatasi: Veritabanı hatası
        """
        with sqlite_session() as session:
            try:
                query = session.query(OfflineKuyruk)
                
                if terminal_id:
                    query = query.filter(OfflineKuyruk.terminal_id == terminal_id)
                
                tum_kuyruklar = query.all()
                
                # Durum bazında sayılar
                durum_sayilari = {}
                for durum in KuyrukDurum:
                    durum_sayilari[durum.value] = 0
                
                # İşlem türü bazında sayılar
                islem_turu_sayilari = {}
                for turu in IslemTuru:
                    islem_turu_sayilari[turu.value] = 0
                
                # Sayıları hesapla
                for kuyruk in tum_kuyruklar:
                    durum_sayilari[kuyruk.durum.value] += 1
                    islem_turu_sayilari[kuyruk.islem_turu.value] += 1
                
                # Ortalama bekleme süresi (bekleyen kayıtlar için)
                bekleyen_kuyruklar = [k for k in tum_kuyruklar if k.durum == KuyrukDurum.BEKLEMEDE]
                ortalama_bekleme_suresi = 0
                if bekleyen_kuyruklar:
                    toplam_bekleme = sum(
                        (datetime.now() - kuyruk.islem_tarihi).total_seconds()
                        for kuyruk in bekleyen_kuyruklar
                    )
                    ortalama_bekleme_suresi = toplam_bekleme / len(bekleyen_kuyruklar)
                
                return {
                    'toplam_kayit': len(tum_kuyruklar),
                    'durum_sayilari': durum_sayilari,
                    'islem_turu_sayilari': islem_turu_sayilari,
                    'ortalama_bekleme_suresi_saniye': int(ortalama_bekleme_suresi),
                    'terminal_id': terminal_id,
                    'rapor_tarihi': datetime.now().isoformat()
                }
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Kuyruk istatistikleri hatası: {str(e)}")
    
    def satis_kuyruk_ekle(self, satis_data: Dict[str, Any], terminal_id: int, 
                         kasiyer_id: int) -> int:
        """
        Satış işlemi için kuyruk ekler
        
        Args:
            satis_data: Satış verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        veri = satis_kuyruk_verisi_olustur(satis_data)
        return self.kuyruk_ekle(IslemTuru.SATIS, veri, terminal_id, kasiyer_id, oncelik=1)
    
    def iade_kuyruk_ekle(self, iade_data: Dict[str, Any], terminal_id: int, 
                        kasiyer_id: int) -> int:
        """
        İade işlemi için kuyruk ekler
        
        Args:
            iade_data: İade verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        veri = iade_kuyruk_verisi_olustur(iade_data)
        return self.kuyruk_ekle(IslemTuru.IADE, veri, terminal_id, kasiyer_id, oncelik=2)
    
    def stok_dusumu_kuyruk_ekle(self, stok_data: Dict[str, Any], terminal_id: int, 
                               kasiyer_id: int) -> int:
        """
        Stok düşümü işlemi için kuyruk ekler
        
        Args:
            stok_data: Stok düşümü verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        veri = stok_dusumu_kuyruk_verisi_olustur(stok_data)
        return self.kuyruk_ekle(IslemTuru.STOK_DUSUMU, veri, terminal_id, kasiyer_id, oncelik=3)
    
    def _kuyruk_dict_donustur(self, kuyruk: OfflineKuyruk) -> Dict[str, Any]:
        """
        OfflineKuyruk nesnesini dict formatına çevirir (private method)
        
        Args:
            kuyruk: OfflineKuyruk nesnesi
            
        Returns:
            Dict formatında kuyruk bilgileri
        """
        return {
            'id': kuyruk.id,
            'islem_turu': kuyruk.islem_turu.value,
            'durum': kuyruk.durum.value,
            'veri': kuyruk.veri,
            'terminal_id': kuyruk.terminal_id,
            'kasiyer_id': kuyruk.kasiyer_id,
            'islem_tarihi': kuyruk.islem_tarihi.isoformat(),
            'son_deneme_tarihi': kuyruk.son_deneme_tarihi.isoformat() if kuyruk.son_deneme_tarihi else None,
            'tamamlanma_tarihi': kuyruk.tamamlanma_tarihi.isoformat() if kuyruk.tamamlanma_tarihi else None,
            'deneme_sayisi': kuyruk.deneme_sayisi,
            'max_deneme_sayisi': kuyruk.max_deneme_sayisi,
            'hata_mesaji': kuyruk.hata_mesaji,
            'oncelik': kuyruk.oncelik,
            'notlar': kuyruk.notlar,
            'olusturma_tarihi': kuyruk.olusturma_tarihi.isoformat() if kuyruk.olusturma_tarihi else None,
            'guncelleme_tarihi': kuyruk.guncelleme_tarihi.isoformat() if kuyruk.guncelleme_tarihi else None,
            # Hesaplanan alanlar
            'beklemede_mi': kuyruk.beklemede_mi(),
            'isleniyor_mu': kuyruk.isleniyor_mu(),
            'tamamlandi_mi': kuyruk.tamamlandi_mi(),
            'hata_durumunda_mi': kuyruk.hata_durumunda_mi(),
            'tekrar_denenebilir_mi': kuyruk.tekrar_denenebilir_mi(),
            'max_deneme_asildi_mi': kuyruk.max_deneme_asildi_mi(),
            'gecikme_suresi_saniye': kuyruk.gecikme_suresi_hesapla()
        }
    
    def bekleyen_islemler(self) -> List[Dict[str, Any]]:
        """
        Bekleyen işlemleri getirir
        
        Returns:
            Bekleyen işlem listesi
            
        Raises:
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                kuyruklar = session.query(OfflineKuyruk).filter(
                    OfflineKuyruk.durum == KuyrukDurum.BEKLEMEDE
                ).order_by(OfflineKuyruk.oncelik, OfflineKuyruk.islem_tarihi).all()
                
                return [self._kuyruk_dict_donustur(kuyruk) for kuyruk in kuyruklar]
                
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Bekleyen işlemler getirme hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"Bekleyen işlemler getirme işlemi başarısız: {str(e)}")
    
    def islem_tamamla(self, kuyruk_id: int) -> bool:
        """
        İşlemi tamamlandı olarak işaretler
        
        Args:
            kuyruk_id: Kuyruk kimliği
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            DogrulamaHatasi: Geçersiz kuyruk kimliği
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                
                if not kuyruk:
                    raise DogrulamaHatasi(f"Kuyruk kaydı bulunamadı: {kuyruk_id}")
                
                kuyruk.durum = KuyrukDurum.TAMAMLANDI
                kuyruk.guncelleme_tarihi = datetime.now()
                
                session.commit()
                return True
                
        except DogrulamaHatasi:
            raise
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"İşlem tamamlama hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"İşlem tamamlama işlemi başarısız: {str(e)}")
    
    def islem_hata(self, kuyruk_id: int, hata_mesaji: str) -> bool:
        """
        İşlemi hatalı olarak işaretler
        
        Args:
            kuyruk_id: Kuyruk kimliği
            hata_mesaji: Hata mesajı
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            DogrulamaHatasi: Geçersiz kuyruk kimliği
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                
                if not kuyruk:
                    raise DogrulamaHatasi(f"Kuyruk kaydı bulunamadı: {kuyruk_id}")
                
                kuyruk.durum = KuyrukDurum.HATA
                kuyruk.hata_mesaji = hata_mesaji
                kuyruk.deneme_sayisi += 1
                kuyruk.guncelleme_tarihi = datetime.now()
                
                session.commit()
                return True
                
        except DogrulamaHatasi:
            raise
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"İşlem hata işaretleme hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"İşlem hata işaretleme işlemi başarısız: {str(e)}")
    
    def kuyruk_temizle(self, gun_sayisi: int = 7) -> bool:
        """
        Eski kuyruk kayıtlarını temizler
        
        Args:
            gun_sayisi: Kaç gün önceki kayıtları temizleyeceği
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                temizlik_tarihi = datetime.now() - timedelta(days=gun_sayisi)
                
                # Tamamlanmış ve hatalı kayıtları temizle
                silinen_sayisi = session.query(OfflineKuyruk).filter(
                    and_(
                        OfflineKuyruk.guncelleme_tarihi < temizlik_tarihi,
                        or_(
                            OfflineKuyruk.durum == KuyrukDurum.TAMAMLANDI,
                            OfflineKuyruk.durum == KuyrukDurum.HATA
                        )
                    )
                ).delete()
                
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Kuyruk temizleme hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"Kuyruk temizleme işlemi başarısız: {str(e)}")
    
    def bekleyen_kuyruk_listesi(self) -> List[Dict[str, Any]]:
        """
        Bekleyen kuyruk listesini getirir
        
        Returns:
            Bekleyen kuyruk listesi
        """
        return self.bekleyen_islemler()