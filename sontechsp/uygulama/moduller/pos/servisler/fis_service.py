# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.servisler.fis_service
# Description: Fiş service implementasyonu
# Changelog:
# - İlk oluşturma

"""
Fiş Service Implementasyonu

Bu modül fiş formatlaması ve yazdırma işlemlerini yönetir.
Satış fişi ve iade fişi oluşturma, formatlaması ve yazdırma hazırlığı sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from sontechsp.uygulama.moduller.pos.arayuzler import (
    IFisService, ISatisRepository, IIadeRepository
)
from sontechsp.uygulama.moduller.pos.hatalar import YazdirmaHatasi
from sontechsp.uygulama.moduller.pos.monitoring import islem_izle, get_pos_monitoring
from sontechsp.uygulama.cekirdek.hatalar import (
    DogrulamaHatasi, SontechHatasi, VeritabaniHatasi
)
from sontechsp.uygulama.cekirdek.kayit import kayit_sistemi_al

logger = kayit_sistemi_al()


class FisService(IFisService):
    """
    Fiş service implementasyonu
    
    Fiş formatlaması ve yazdırma işlemlerinin iş kurallarını yönetir.
    Repository katmanını kullanarak veri işlemlerini gerçekleştirir.
    """
    
    def __init__(self, satis_repository: ISatisRepository, iade_repository: IIadeRepository):
        """
        Service'i başlatır
        
        Args:
            satis_repository: Satış repository instance'ı
            iade_repository: İade repository instance'ı
        """
        self.satis_repository = satis_repository
        self.iade_repository = iade_repository
        logger.info("FisService başlatıldı")
    
    @islem_izle("fis_satis_olusturma")
    def satis_fisi_olustur(self, satis_id: int, magaza_bilgileri: Optional[Dict[str, Any]] = None) -> str:
        """
        Satış fişi oluşturur ve formatlar
        
        Args:
            satis_id: Satış kimliği
            magaza_bilgileri: Mağaza bilgileri (opsiyonel)
            
        Returns:
            Formatlanmış fiş içeriği
            
        Raises:
            DogrulamaHatasi: Geçersiz satış ID
            SontechHatasi: Satış bulunamadı
            YazdirmaHatasi: Fiş oluşturma hatası
        """
        try:
            if satis_id <= 0:
                raise DogrulamaHatasi("Satış ID pozitif olmalıdır")
            
            logger.info(f"Satış fişi oluşturuluyor - Satış ID: {satis_id}")
            
            # Satış bilgilerini getir
            satis_bilgisi = self.satis_repository.satis_getir(satis_id)
            if not satis_bilgisi:
                raise SontechHatasi(f"Satış bulunamadı: {satis_id}")
            
            # Fiş içeriğini formatla
            fis_icerik = self._satis_fisi_formatla(satis_bilgisi, magaza_bilgileri)
            
            logger.info(f"Satış fişi başarıyla oluşturuldu - Satış ID: {satis_id}")
            return fis_icerik
            
        except (DogrulamaHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"Satış fişi oluşturma hatası: {str(e)}")
            raise YazdirmaHatasi(f"Satış fişi oluşturma işlemi başarısız: {str(e)}")
    
    @islem_izle("fis_iade_olusturma")
    def iade_fisi_olustur(self, iade_id: int, magaza_bilgileri: Optional[Dict[str, Any]] = None) -> str:
        """
        İade fişi oluşturur ve formatlar
        
        Args:
            iade_id: İade kimliği
            magaza_bilgileri: Mağaza bilgileri (opsiyonel)
            
        Returns:
            Formatlanmış iade fişi içeriği
            
        Raises:
            DogrulamaHatasi: Geçersiz iade ID
            SontechHatasi: İade bulunamadı
            YazdirmaHatasi: Fiş oluşturma hatası
        """
        try:
            if iade_id <= 0:
                raise DogrulamaHatasi("İade ID pozitif olmalıdır")
            
            logger.info(f"İade fişi oluşturuluyor - İade ID: {iade_id}")
            
            # İade bilgilerini getir
            iade_bilgisi = self.iade_repository.iade_getir(iade_id)
            if not iade_bilgisi:
                raise SontechHatasi(f"İade bulunamadı: {iade_id}")
            
            # Fiş içeriğini formatla
            fis_icerik = self._iade_fisi_formatla(iade_bilgisi, magaza_bilgileri)
            
            logger.info(f"İade fişi başarıyla oluşturuldu - İade ID: {iade_id}")
            return fis_icerik
            
        except (DogrulamaHatasi, SontechHatasi):
            raise
        except Exception as e:
            logger.error(f"İade fişi oluşturma hatası: {str(e)}")
            raise YazdirmaHatasi(f"İade fişi oluşturma işlemi başarısız: {str(e)}")
    
    @islem_izle("fis_yazdirma")
    def fis_yazdir(self, fis_icerik: str, yazici_adi: Optional[str] = None) -> bool:
        """
        Fiş yazdırır
        
        Args:
            fis_icerik: Yazdırılacak fiş içeriği
            yazici_adi: Yazıcı adı (opsiyonel, varsayılan yazıcı kullanılır)
            
        Returns:
            Yazdırma başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz fiş içeriği
            YazdirmaHatasi: Yazdırma hatası
        """
        try:
            if not fis_icerik or not fis_icerik.strip():
                raise DogrulamaHatasi("Fiş içeriği boş olamaz")
            
            logger.info(f"Fiş yazdırılıyor - Yazıcı: {yazici_adi or 'Varsayılan'}")
            
            # Yazdırma işlemi simülasyonu
            # Gerçek implementasyonda Windows Print API veya yazıcı driver'ı kullanılır
            yazdirma_basarili = self._yazici_gonder(fis_icerik, yazici_adi)
            
            if yazdirma_basarili:
                logger.info("Fiş başarıyla yazdırıldı")
            else:
                logger.warning("Fiş yazdırma işlemi başarısız")
            
            return yazdirma_basarili
            
        except DogrulamaHatasi:
            raise
        except Exception as e:
            logger.error(f"Fiş yazdırma hatası: {str(e)}")
            raise YazdirmaHatasi(f"Fiş yazdırma işlemi başarısız: {str(e)}", yazici_adi)
    
    def fis_onizleme(self, fis_icerik: str) -> Dict[str, Any]:
        """
        Fiş önizlemesi oluşturur
        
        Args:
            fis_icerik: Fiş içeriği
            
        Returns:
            Önizleme bilgileri
            
        Raises:
            DogrulamaHatasi: Geçersiz fiş içeriği
        """
        try:
            if not fis_icerik or not fis_icerik.strip():
                raise DogrulamaHatasi("Fiş içeriği boş olamaz")
            
            # Fiş içeriğini analiz et
            satirlar = fis_icerik.split('\n')
            karakter_sayisi = len(fis_icerik)
            satir_sayisi = len(satirlar)
            
            # En uzun satırı bul
            en_uzun_satir = max(len(satir) for satir in satirlar) if satirlar else 0
            
            onizleme = {
                'fis_icerik': fis_icerik,
                'satir_sayisi': satir_sayisi,
                'karakter_sayisi': karakter_sayisi,
                'en_uzun_satir': en_uzun_satir,
                'tahmini_kagit_boyu': satir_sayisi * 0.5,  # cm cinsinden
                'olusturma_tarihi': datetime.now().isoformat(),
                'yazdirma_hazir': True
            }
            
            logger.debug(f"Fiş önizlemesi oluşturuldu - Satır: {satir_sayisi}, Karakter: {karakter_sayisi}")
            return onizleme
            
        except DogrulamaHatasi:
            raise
        except Exception as e:
            logger.error(f"Fiş önizleme hatası: {str(e)}")
            raise YazdirmaHatasi(f"Fiş önizleme işlemi başarısız: {str(e)}")
    
    def _satis_fisi_formatla(self, satis_bilgisi: Dict[str, Any], 
                           magaza_bilgileri: Optional[Dict[str, Any]] = None) -> str:
        """
        Satış fişini formatlar (private method)
        
        Args:
            satis_bilgisi: Satış bilgileri
            magaza_bilgileri: Mağaza bilgileri
            
        Returns:
            Formatlanmış fiş içeriği
        """
        fis_satirlari = []
        
        # Başlık
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("         SATIŞ FİŞİ")
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("")
        
        # Mağaza bilgileri
        if magaza_bilgileri:
            fis_satirlari.append(f"Mağaza: {magaza_bilgileri.get('adi', 'SONTECHSP')}")
            if magaza_bilgileri.get('adres'):
                fis_satirlari.append(f"Adres: {magaza_bilgileri['adres']}")
            if magaza_bilgileri.get('telefon'):
                fis_satirlari.append(f"Tel: {magaza_bilgileri['telefon']}")
            fis_satirlari.append("")
        
        # Fiş bilgileri
        fis_satirlari.append(f"Fiş No: {satis_bilgisi.get('fis_no', 'N/A')}")
        
        # Tarih formatlaması
        satis_tarihi = satis_bilgisi.get('satis_tarihi', datetime.now())
        if isinstance(satis_tarihi, datetime):
            tarih_str = satis_tarihi.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tarih_str = str(satis_tarihi)[:19] if satis_tarihi else 'N/A'
        
        fis_satirlari.append(f"Tarih: {tarih_str}")
        fis_satirlari.append(f"Terminal: {satis_bilgisi.get('terminal_id', 'N/A')}")
        fis_satirlari.append(f"Kasiyer: {satis_bilgisi.get('kasiyer_id', 'N/A')}")
        fis_satirlari.append("")
        fis_satirlari.append("-" * 40)
        
        # Ürün listesi başlığı
        fis_satirlari.append("ÜRÜN                 ADET  B.FİYAT  TOPLAM")
        fis_satirlari.append("-" * 40)
        
        # Ürün satırları
        satirlar = satis_bilgisi.get('satirlar', [])
        for satir in satirlar:
            urun_adi = satir.get('urun_adi', 'Bilinmeyen Ürün')[:15]
            adet = satir.get('adet', 0)
            birim_fiyat = satir.get('birim_fiyat', 0.0)
            toplam = satir.get('toplam_tutar', 0.0)
            
            # Satırı formatla (sabit genişlik)
            satir_str = f"{urun_adi:<15} {adet:>4} {birim_fiyat:>8.2f} {toplam:>8.2f}"
            fis_satirlari.append(satir_str)
        
        fis_satirlari.append("-" * 40)
        
        # Toplam bilgileri
        toplam_tutar = Decimal(str(satis_bilgisi.get('toplam_tutar', 0.0)))
        indirim_tutari = Decimal(str(satis_bilgisi.get('indirim_tutari', 0.0)))
        net_tutar = toplam_tutar - indirim_tutari
        
        fis_satirlari.append(f"Ara Toplam:              {toplam_tutar:>10.2f} TL")
        if indirim_tutari > 0:
            fis_satirlari.append(f"İndirim:                 {indirim_tutari:>10.2f} TL")
        fis_satirlari.append(f"NET TOPLAM:              {net_tutar:>10.2f} TL")
        fis_satirlari.append("")
        
        # Ödeme bilgileri
        odemeler = satis_bilgisi.get('odemeler', [])
        if odemeler:
            fis_satirlari.append("ÖDEME BİLGİLERİ:")
            for odeme in odemeler:
                odeme_turu = odeme.get('odeme_turu', 'Bilinmeyen').upper()
                tutar = odeme.get('tutar', 0.0)
                fis_satirlari.append(f"{odeme_turu}:                   {tutar:>10.2f} TL")
            fis_satirlari.append("")
        
        # Alt bilgi
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("    Alışverişiniz için teşekkürler!")
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("")
        fis_satirlari.append(f"Yazdırma: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
        return '\n'.join(fis_satirlari)
    
    def _iade_fisi_formatla(self, iade_bilgisi: Dict[str, Any], 
                          magaza_bilgileri: Optional[Dict[str, Any]] = None) -> str:
        """
        İade fişini formatlar (private method)
        
        Args:
            iade_bilgisi: İade bilgileri
            magaza_bilgileri: Mağaza bilgileri
            
        Returns:
            Formatlanmış iade fişi içeriği
        """
        fis_satirlari = []
        
        # Başlık
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("         İADE FİŞİ")
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("")
        
        # Mağaza bilgileri
        if magaza_bilgileri:
            fis_satirlari.append(f"Mağaza: {magaza_bilgileri.get('adi', 'SONTECHSP')}")
            if magaza_bilgileri.get('adres'):
                fis_satirlari.append(f"Adres: {magaza_bilgileri['adres']}")
            if magaza_bilgileri.get('telefon'):
                fis_satirlari.append(f"Tel: {magaza_bilgileri['telefon']}")
            fis_satirlari.append("")
        
        # İade bilgileri
        fis_satirlari.append(f"İade No: {iade_bilgisi.get('fis_no', 'N/A')}")
        fis_satirlari.append(f"Tarih: {iade_bilgisi.get('iade_tarihi', datetime.now().isoformat())[:19]}")
        fis_satirlari.append(f"Terminal: {iade_bilgisi.get('terminal_id', 'N/A')}")
        fis_satirlari.append(f"Kasiyer: {iade_bilgisi.get('kasiyer_id', 'N/A')}")
        fis_satirlari.append(f"Orijinal Satış: {iade_bilgisi.get('orijinal_satis_id', 'N/A')}")
        fis_satirlari.append(f"İade Nedeni: {iade_bilgisi.get('neden', 'Belirtilmemiş')}")
        fis_satirlari.append("")
        fis_satirlari.append("-" * 40)
        
        # Ürün listesi başlığı
        fis_satirlari.append("ÜRÜN                 ADET  B.FİYAT  TOPLAM")
        fis_satirlari.append("-" * 40)
        
        # İade satırları
        satirlar = iade_bilgisi.get('satirlar', [])
        for satir in satirlar:
            urun_adi = satir.get('urun_adi', 'Bilinmeyen Ürün')[:15]
            adet = satir.get('adet', 0)
            birim_fiyat = satir.get('birim_fiyat', 0.0)
            toplam = satir.get('toplam_tutar', 0.0)
            
            # Satırı formatla (sabit genişlik)
            satir_str = f"{urun_adi:<15} {adet:>4} {birim_fiyat:>8.2f} {toplam:>8.2f}"
            fis_satirlari.append(satir_str)
        
        fis_satirlari.append("-" * 40)
        
        # Toplam bilgileri
        toplam_tutar = iade_bilgisi.get('toplam_tutar', 0.0)
        fis_satirlari.append(f"İADE TOPLAMI:            {toplam_tutar:>10.2f} TL")
        fis_satirlari.append("")
        
        # Alt bilgi
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("         İADE TAMAMLANDI")
        fis_satirlari.append("=" * 40)
        fis_satirlari.append("")
        fis_satirlari.append(f"Yazdırma: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
        return '\n'.join(fis_satirlari)
    
    def _yazici_gonder(self, fis_icerik: str, yazici_adi: Optional[str] = None) -> bool:
        """
        Fiş içeriğini yazıcıya gönderir (private method)
        
        Args:
            fis_icerik: Yazdırılacak içerik
            yazici_adi: Yazıcı adı
            
        Returns:
            Yazdırma başarılı mı
        """
        try:
            # Gerçek implementasyonda Windows Print API kullanılır
            # Şimdilik simülasyon yapıyoruz
            
            logger.debug(f"Yazıcıya gönderiliyor - Yazıcı: {yazici_adi or 'Varsayılan'}")
            logger.debug(f"İçerik uzunluğu: {len(fis_icerik)} karakter")
            
            # Yazdırma simülasyonu
            # Gerçek kodda burada şunlar yapılır:
            # 1. Yazıcı durumu kontrol edilir
            # 2. Print job oluşturulur
            # 3. İçerik yazıcıya gönderilir
            # 4. Yazdırma durumu takip edilir
            
            # Simülasyon için her zaman başarılı döndürüyoruz
            return True
            
        except Exception as e:
            logger.error(f"Yazıcı gönderme hatası: {str(e)}")
            return False
    
    def yazici_durumu_kontrol(self, yazici_adi: Optional[str] = None) -> Dict[str, Any]:
        """
        Yazıcı durumunu kontrol eder
        
        Args:
            yazici_adi: Yazıcı adı (opsiyonel)
            
        Returns:
            Yazıcı durum bilgileri
        """
        try:
            # Gerçek implementasyonda Windows Print API kullanılır
            # Şimdilik simülasyon yapıyoruz
            
            durum = {
                'yazici_adi': yazici_adi or 'Varsayılan Yazıcı',
                'durum': 'hazir',  # hazir, mesgul, hata, kagit_yok, offline
                'kagit_durumu': 'dolu',
                'toner_durumu': 'dolu',
                'son_kontrol': datetime.now().isoformat(),
                'yazdirma_hazir': True,
                'hata_mesaji': None
            }
            
            logger.debug(f"Yazıcı durumu kontrol edildi: {durum['yazici_adi']}")
            return durum
            
        except Exception as e:
            logger.error(f"Yazıcı durum kontrol hatası: {str(e)}")
            return {
                'yazici_adi': yazici_adi or 'Bilinmeyen',
                'durum': 'hata',
                'yazdirma_hazir': False,
                'hata_mesaji': str(e)
            }
    
    def fis_kaydet(self, fis_icerik: str, dosya_adi: Optional[str] = None) -> str:
        """
        Fiş içeriğini dosyaya kaydeder
        
        Args:
            fis_icerik: Kaydedilecek fiş içeriği
            dosya_adi: Dosya adı (opsiyonel, otomatik oluşturulur)
            
        Returns:
            Kaydedilen dosya yolu
            
        Raises:
            DogrulamaHatasi: Geçersiz fiş içeriği
            YazdirmaHatasi: Dosya kaydetme hatası
        """
        try:
            if not fis_icerik or not fis_icerik.strip():
                raise DogrulamaHatasi("Fiş içeriği boş olamaz")
            
            # Dosya adı oluştur
            if not dosya_adi:
                zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = f"fis_{zaman_damgasi}.txt"
            
            # Dosya yolu
            dosya_yolu = f"logs/fisler/{dosya_adi}"
            
            # Klasör oluştur (eğer yoksa)
            import os
            os.makedirs(os.path.dirname(dosya_yolu), exist_ok=True)
            
            # Dosyaya yaz
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(fis_icerik)
            
            logger.info(f"Fiş dosyaya kaydedildi: {dosya_yolu}")
            return dosya_yolu
            
        except DogrulamaHatasi:
            raise
        except Exception as e:
            logger.error(f"Fiş kaydetme hatası: {str(e)}")
            raise YazdirmaHatasi(f"Fiş kaydetme işlemi başarısız: {str(e)}")