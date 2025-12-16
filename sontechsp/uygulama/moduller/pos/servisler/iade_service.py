# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.servisler.iade_service
# Description: İade service implementasyonu
# Changelog:
# - İlk oluşturma

"""
İade Service Implementasyonu

Bu modül iade işlemlerinin iş kurallarını yönetir.
İade işlemi başlatma, doğrulama, tutarı hesaplama ve stok girişi işlemlerini sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from sontechsp.uygulama.moduller.pos.arayuzler import (
    IIadeService, IIadeRepository, IStokService, SatisDurum
)
from sontechsp.uygulama.moduller.pos.hatalar import IadeHatasi
from sontechsp.uygulama.cekirdek.hatalar import (
    DogrulamaHatasi, SontechHatasi, VeritabaniHatasi
)
from sontechsp.uygulama.cekirdek.kayit import kayit_sistemi_al

logger = kayit_sistemi_al()


class IadeService(IIadeService):
    """
    İade service implementasyonu
    
    İade işlemlerinin iş kurallarını yönetir.
    Repository katmanını kullanarak veri işlemlerini gerçekleştirir.
    """
    
    def __init__(self, iade_repository: IIadeRepository, stok_service: IStokService):
        """
        Service'i başlatır
        
        Args:
            iade_repository: İade repository instance'ı
            stok_service: Stok service instance'ı
        """
        self.iade_repository = iade_repository
        self.stok_service = stok_service
        logger.info("IadeService başlatıldı")
    
    def iade_baslat(self, satis_id: int, terminal_id: int, kasiyer_id: int, 
                   neden: str, musteri_id: Optional[int] = None) -> int:
        """
        İade işlemi başlatır ve orijinal satış kaydını doğrular
        
        Args:
            satis_id: Orijinal satış kimliği
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            neden: İade nedeni
            musteri_id: Müşteri kimliği (opsiyonel)
            
        Returns:
            Oluşturulan iade ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            IadeHatasi: İade işlemi hataları
            SontechHatasi: Orijinal satış bulunamadı veya iade edilemez
        """
        try:
            # Parametre validasyonu
            if satis_id <= 0:
                raise DogrulamaHatasi("Satış ID pozitif olmalıdır")
            
            if terminal_id <= 0:
                raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
            
            if kasiyer_id <= 0:
                raise DogrulamaHatasi("Kasiyer ID pozitif olmalıdır")
            
            if not neden or not neden.strip():
                raise DogrulamaHatasi("İade nedeni boş olamaz")
            
            if musteri_id and musteri_id <= 0:
                raise DogrulamaHatasi("Müşteri ID pozitif olmalıdır")
            
            logger.info(f"İade başlatılıyor - Satış ID: {satis_id}, Neden: {neden}")
            
            # Orijinal satış doğrulama
            satis_bilgisi = self.iade_repository.orijinal_satis_dogrula(satis_id)
            
            if not satis_bilgisi['iade_edilebilir']:
                if satis_bilgisi['durum'] != SatisDurum.TAMAMLANDI.value:
                    raise IadeHatasi("Sadece tamamlanan satışlar iade edilebilir")
                elif satis_bilgisi['kalan_iade_tutari'] <= 0:
                    raise IadeHatasi("Bu satış için iade edilebilir tutar kalmamış")
                else:
                    raise IadeHatasi("Bu satış iade edilemez")
            
            # İade kaydı oluştur
            iade_id = self.iade_repository.iade_olustur(
                orijinal_satis_id=satis_id,
                terminal_id=terminal_id,
                kasiyer_id=kasiyer_id,
                neden=neden.strip(),
                musteri_id=musteri_id
            )
            
            logger.info(f"İade başarıyla oluşturuldu - İade ID: {iade_id}")
            return iade_id
            
        except (DogrulamaHatasi, IadeHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"İade başlatma hatası: {str(e)}")
            raise IadeHatasi(f"İade başlatma işlemi başarısız: {str(e)}")
    
    def iade_kalemi_ekle(self, iade_id: int, urun_id: int, barkod: str, 
                        urun_adi: str, adet: int, birim_fiyat: Decimal,
                        orijinal_sepet_satiri_id: Optional[int] = None,
                        iade_nedeni: Optional[str] = None) -> int:
        """
        İadeye kalem ekler ve iade tutarını hesaplar
        
        Args:
            iade_id: İade kimliği
            urun_id: Ürün kimliği
            barkod: Ürün barkodu
            urun_adi: Ürün adı
            adet: İade edilen adet
            birim_fiyat: Birim fiyat
            orijinal_sepet_satiri_id: Orijinal sepet satırı kimliği (opsiyonel)
            iade_nedeni: Bu kalem için özel iade nedeni (opsiyonel)
            
        Returns:
            Oluşturulan iade satırı ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            IadeHatasi: İade işlemi hataları
            SontechHatasi: İade bulunamadı
        """
        try:
            # Parametre validasyonu
            if iade_id <= 0:
                raise DogrulamaHatasi("İade ID pozitif olmalıdır")
            
            if urun_id <= 0:
                raise DogrulamaHatasi("Ürün ID pozitif olmalıdır")
            
            if not barkod or not barkod.strip():
                raise DogrulamaHatasi("Barkod boş olamaz")
            
            if not urun_adi or not urun_adi.strip():
                raise DogrulamaHatasi("Ürün adı boş olamaz")
            
            if adet <= 0:
                raise DogrulamaHatasi("Adet pozitif olmalıdır")
            
            if birim_fiyat < 0:
                raise DogrulamaHatasi("Birim fiyat negatif olamaz")
            
            logger.info(f"İade kalemi ekleniyor - İade ID: {iade_id}, Ürün: {urun_adi}, Adet: {adet}")
            
            # İade var mı kontrol et
            iade_bilgisi = self.iade_repository.iade_getir(iade_id)
            if not iade_bilgisi:
                raise SontechHatasi(f"İade bulunamadı: {iade_id}")
            
            # Ürün bilgisi kontrol et (stok service'den)
            urun_bilgisi = self.stok_service.urun_bilgisi_getir(barkod)
            if not urun_bilgisi:
                raise IadeHatasi(f"Ürün bulunamadı: {barkod}")
            
            # İade satırı ekle
            satir_id = self.iade_repository.iade_satiri_ekle(
                iade_id=iade_id,
                urun_id=urun_id,
                barkod=barkod.strip(),
                urun_adi=urun_adi.strip(),
                adet=adet,
                birim_fiyat=birim_fiyat,
                orijinal_sepet_satiri_id=orijinal_sepet_satiri_id,
                iade_nedeni=iade_nedeni
            )
            
            logger.info(f"İade kalemi başarıyla eklendi - Satır ID: {satir_id}")
            return satir_id
            
        except (DogrulamaHatasi, IadeHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"İade kalemi ekleme hatası: {str(e)}")
            raise IadeHatasi(f"İade kalemi ekleme işlemi başarısız: {str(e)}")
    
    def iade_tutari_hesapla(self, iade_id: int) -> Dict[str, Any]:
        """
        İade tutarını hesaplar ve detayları döner
        
        Args:
            iade_id: İade kimliği
            
        Returns:
            İade tutarı hesaplama detayları
            
        Raises:
            DogrulamaHatasi: Geçersiz iade ID
            SontechHatasi: İade bulunamadı
            IadeHatasi: İade tutarı hesaplama hatası
        """
        try:
            if iade_id <= 0:
                raise DogrulamaHatasi("İade ID pozitif olmalıdır")
            
            logger.info(f"İade tutarı hesaplanıyor - İade ID: {iade_id}")
            
            # İade bilgilerini getir
            iade_bilgisi = self.iade_repository.iade_getir(iade_id)
            if not iade_bilgisi:
                raise SontechHatasi(f"İade bulunamadı: {iade_id}")
            
            # Tutarları hesapla
            toplam_tutar = Decimal('0.00')
            toplam_adet = 0
            satir_sayisi = len(iade_bilgisi['satirlar'])
            
            for satir in iade_bilgisi['satirlar']:
                satir_tutari = Decimal(str(satir['toplam_tutar']))
                toplam_tutar += satir_tutari
                toplam_adet += satir['adet']
            
            # Orijinal satış bilgilerini getir
            orijinal_satis = self.iade_repository.orijinal_satis_dogrula(
                iade_bilgisi['orijinal_satis_id']
            )
            
            hesaplama_detaylari = {
                'iade_id': iade_id,
                'toplam_tutar': float(toplam_tutar),
                'toplam_adet': toplam_adet,
                'satir_sayisi': satir_sayisi,
                'orijinal_satis_tutari': orijinal_satis['net_tutar'],
                'kalan_iade_tutari': orijinal_satis['kalan_iade_tutari'],
                'iade_orani': float(toplam_tutar / Decimal(str(orijinal_satis['net_tutar'])) * 100) if orijinal_satis['net_tutar'] > 0 else 0,
                'iade_edilebilir': toplam_tutar <= Decimal(str(orijinal_satis['kalan_iade_tutari'])),
                'hesaplama_tarihi': datetime.now().isoformat()
            }
            
            logger.info(f"İade tutarı hesaplandı - Toplam: {toplam_tutar}")
            return hesaplama_detaylari
            
        except (DogrulamaHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"İade tutarı hesaplama hatası: {str(e)}")
            raise IadeHatasi(f"İade tutarı hesaplama işlemi başarısız: {str(e)}")
    
    def iade_tamamla(self, iade_id: int, fis_no: Optional[str] = None) -> bool:
        """
        İadeyi tamamlar ve stok girişi yapar
        
        Args:
            iade_id: İade kimliği
            fis_no: Fiş numarası (opsiyonel, otomatik oluşturulur)
            
        Returns:
            İade tamamlama başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz iade ID
            SontechHatasi: İade bulunamadı
            IadeHatasi: İade tamamlama hatası
        """
        try:
            if iade_id <= 0:
                raise DogrulamaHatasi("İade ID pozitif olmalıdır")
            
            logger.info(f"İade tamamlanıyor - İade ID: {iade_id}")
            
            # İade bilgilerini getir
            iade_bilgisi = self.iade_repository.iade_getir(iade_id)
            if not iade_bilgisi:
                raise SontechHatasi(f"İade bulunamadı: {iade_id}")
            
            # İade satırları var mı kontrol et
            if not iade_bilgisi['satirlar']:
                raise IadeHatasi("İade satırları olmadan iade tamamlanamaz")
            
            # İade tutarını kontrol et
            tutari_hesaplama = self.iade_tutari_hesapla(iade_id)
            if not tutari_hesaplama['iade_edilebilir']:
                raise IadeHatasi("İade tutarı orijinal satış tutarını aşıyor")
            
            # Fiş numarası oluştur (eğer verilmemişse)
            if not fis_no:
                fis_no = self._fis_numarasi_olustur(iade_id)
            
            # Stok girişi yap (her satır için)
            for satir in iade_bilgisi['satirlar']:
                try:
                    stok_basarili = self.stok_service.stok_artir(
                        urun_id=satir['urun_id'],
                        adet=satir['adet']
                    )
                    
                    if not stok_basarili:
                        logger.warning(f"Stok girişi başarısız - Ürün ID: {satir['urun_id']}, Adet: {satir['adet']}")
                        # Stok girişi başarısız olsa bile iade tamamlanabilir
                        # Çünkü fiziksel ürün iade edilmiş olabilir
                    
                except Exception as stok_hatasi:
                    logger.error(f"Stok girişi hatası - Ürün ID: {satir['urun_id']}: {str(stok_hatasi)}")
                    # Stok hatası iade işlemini durdurmaz
            
            # Fiş numarasını güncelle
            self.iade_repository.iade_fis_no_guncelle(iade_id, fis_no)
            
            logger.info(f"İade başarıyla tamamlandı - İade ID: {iade_id}, Fiş No: {fis_no}")
            return True
            
        except (DogrulamaHatasi, SontechHatasi, IadeHatasi):
            raise
        except Exception as e:
            logger.error(f"İade tamamlama hatası: {str(e)}")
            raise IadeHatasi(f"İade tamamlama işlemi başarısız: {str(e)}")
    
    def iade_bilgisi_getir(self, iade_id: int) -> Dict[str, Any]:
        """
        İade bilgilerini detaylı olarak getirir
        
        Args:
            iade_id: İade kimliği
            
        Returns:
            Detaylı iade bilgileri
            
        Raises:
            DogrulamaHatasi: Geçersiz iade ID
            SontechHatasi: İade bulunamadı
        """
        try:
            if iade_id <= 0:
                raise DogrulamaHatasi("İade ID pozitif olmalıdır")
            
            # İade bilgilerini getir
            iade_bilgisi = self.iade_repository.iade_getir(iade_id)
            if not iade_bilgisi:
                raise SontechHatasi(f"İade bulunamadı: {iade_id}")
            
            # Tutarı hesapla
            tutari_hesaplama = self.iade_tutari_hesapla(iade_id)
            
            # Orijinal satış bilgilerini ekle
            orijinal_satis = self.iade_repository.orijinal_satis_dogrula(
                iade_bilgisi['orijinal_satis_id']
            )
            
            # Detaylı bilgileri birleştir
            detayli_bilgi = {
                **iade_bilgisi,
                'tutari_hesaplama': tutari_hesaplama,
                'orijinal_satis': orijinal_satis,
                'durum': 'tamamlandi' if iade_bilgisi['fis_no'] else 'devam_ediyor'
            }
            
            return detayli_bilgi
            
        except (DogrulamaHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"İade bilgisi getirme hatası: {str(e)}")
            raise IadeHatasi(f"İade bilgisi getirme işlemi başarısız: {str(e)}")
    
    def iade_satiri_guncelle(self, satir_id: int, yeni_adet: int) -> bool:
        """
        İade satırını günceller
        
        Args:
            satir_id: Satır kimliği
            yeni_adet: Yeni adet
            
        Returns:
            Güncelleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Satır bulunamadı
            IadeHatasi: Güncelleme hatası
        """
        try:
            if satir_id <= 0:
                raise DogrulamaHatasi("Satır ID pozitif olmalıdır")
            
            if yeni_adet <= 0:
                raise DogrulamaHatasi("Adet pozitif olmalıdır")
            
            logger.info(f"İade satırı güncelleniyor - Satır ID: {satir_id}, Yeni Adet: {yeni_adet}")
            
            # Repository'den güncelle
            basarili = self.iade_repository.iade_satiri_guncelle(satir_id, yeni_adet)
            
            if basarili:
                logger.info(f"İade satırı başarıyla güncellendi - Satır ID: {satir_id}")
            
            return basarili
            
        except (DogrulamaHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"İade satırı güncelleme hatası: {str(e)}")
            raise IadeHatasi(f"İade satırı güncelleme işlemi başarısız: {str(e)}")
    
    def iade_satiri_sil(self, satir_id: int) -> bool:
        """
        İade satırını siler
        
        Args:
            satir_id: Satır kimliği
            
        Returns:
            Silme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz satır ID
            SontechHatasi: Satır bulunamadı
            IadeHatasi: Silme hatası
        """
        try:
            if satir_id <= 0:
                raise DogrulamaHatasi("Satır ID pozitif olmalıdır")
            
            logger.info(f"İade satırı siliniyor - Satır ID: {satir_id}")
            
            # Repository'den sil
            basarili = self.iade_repository.iade_satiri_sil(satir_id)
            
            if basarili:
                logger.info(f"İade satırı başarıyla silindi - Satır ID: {satir_id}")
            
            return basarili
            
        except (DogrulamaHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"İade satırı silme hatası: {str(e)}")
            raise IadeHatasi(f"İade satırı silme işlemi başarısız: {str(e)}")
    
    def _fis_numarasi_olustur(self, iade_id: int) -> str:
        """
        İade fiş numarası oluşturur (private method)
        
        Args:
            iade_id: İade kimliği
            
        Returns:
            Oluşturulan fiş numarası
        """
        # Format: IADE-YYYYMMDD-HHMMSS-IADEID
        simdi = datetime.now()
        tarih_str = simdi.strftime("%Y%m%d")
        saat_str = simdi.strftime("%H%M%S")
        
        fis_no = f"IADE-{tarih_str}-{saat_str}-{iade_id:06d}"
        
        logger.debug(f"İade fiş numarası oluşturuldu: {fis_no}")
        return fis_no