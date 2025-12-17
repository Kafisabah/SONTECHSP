# Version: 0.1.0
# Last Update: 2024-12-17
# Module: raporlar.disari_aktarim
# Description: Raporlama modülü dışa aktarım işlemleri
# Changelog:
# - İlk oluşturma
# - CSV dışa aktarım eklendi
# - PDF dışa aktarım placeholder eklendi
# - Dosya yolu yardımcıları eklendi

"""
SONTECHSP Raporlar Dışa Aktarım Katmanı

Bu modül raporlama sisteminin dışa aktarım işlemlerini içerir:
- CSV formatında dışa aktarım
- PDF formatında dışa aktarım (MVP placeholder)
- Dosya yolu oluşturma yardımcıları
- Hata yönetimi

Desteklenen formatlar: CSV, PDF (placeholder)
"""

import csv
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .dto import DisariAktarDTO, DisariAktarFormat
from .sabitler import RaporSabitleri, HataMesajlari, LogMesajlari

logger = logging.getLogger(__name__)


class DosyaIslemHatasi(Exception):
    """Dosya işlem hatası sınıfı"""
    pass


def benzersiz_dosya_adi_olustur(rapor_turu: str, format: DisariAktarFormat, ozel_ad: Optional[str] = None) -> str:
    """
    Benzersiz dosya adı oluşturur
    
    Args:
        rapor_turu: Rapor türü
        format: Dosya formatı
        ozel_ad: Opsiyonel özel dosya adı
        
    Returns:
        str: Benzersiz dosya adı
    """
    zaman_damgasi = datetime.now().strftime(RaporSabitleri.ZAMAN_DAMGASI_FORMAT)
    
    if ozel_ad:
        temel_ad = f"{ozel_ad}_{zaman_damgasi}"
    else:
        temel_ad = f"{rapor_turu}_{zaman_damgasi}"
    
    uzanti = RaporSabitleri.CSV_UZANTI if format == DisariAktarFormat.CSV else RaporSabitleri.PDF_UZANTI
    
    return f"{temel_ad}{uzanti}"


def klasor_olustur(klasor_yolu: str) -> None:
    """
    Klasör oluşturur (yoksa)
    
    Args:
        klasor_yolu: Oluşturulacak klasör yolu
        
    Raises:
        DosyaIslemHatasi: Klasör oluşturma hatası
    """
    try:
        Path(klasor_yolu).mkdir(parents=True, exist_ok=True)
        logger.info(f"Klasör hazırlandı: {klasor_yolu}")
    except Exception as e:
        hata_mesaji = HataMesajlari.KLASOR_OLUSTURMA_HATASI.format(str(e))
        logger.error(hata_mesaji)
        raise DosyaIslemHatasi(hata_mesaji)


def csv_disari_aktar(veri: List[Dict[str, Any]], dosya_yolu: str, baslik: Optional[str] = None) -> str:
    """
    Veriyi CSV formatında dışa aktarır
    
    Args:
        veri: Dışa aktarılacak veri listesi
        dosya_yolu: Hedef dosya yolu
        baslik: Opsiyonel başlık
        
    Returns:
        str: Oluşturulan dosyanın tam yolu
        
    Raises:
        DosyaIslemHatasi: CSV oluşturma hatası
    """
    try:
        logger.info(LogMesajlari.DISARI_AKTARIM_BASLATILDI.format("CSV", dosya_yolu))
        
        if not veri:
            # Boş veri için boş CSV oluştur
            with open(dosya_yolu, 'w', newline='', encoding='utf-8') as dosya:
                if baslik:
                    dosya.write(f"# {baslik}\n")
                dosya.write("# Veri bulunamadı\n")
            return dosya_yolu
        
        # CSV başlıklarını ilk kayıttan al
        basliklar = list(veri[0].keys())
        
        with open(dosya_yolu, 'w', newline='', encoding='utf-8') as dosya:
            # Opsiyonel başlık ekle
            if baslik:
                dosya.write(f"# {baslik}\n")
                dosya.write(f"# Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                dosya.write(f"# Toplam Kayıt: {len(veri)}\n")
                dosya.write("\n")
            
            # CSV yazıcı oluştur
            yazici = csv.DictWriter(dosya, fieldnames=basliklar)
            yazici.writeheader()
            
            # Veriyi yaz
            for satir in veri:
                # Decimal ve diğer özel türleri string'e çevir
                temizlenmis_satir = {}
                for anahtar, deger in satir.items():
                    if deger is None:
                        temizlenmis_satir[anahtar] = ""
                    else:
                        temizlenmis_satir[anahtar] = str(deger)
                yazici.writerow(temizlenmis_satir)
        
        logger.info(LogMesajlari.DISARI_AKTARIM_TAMAMLANDI.format(dosya_yolu))
        return dosya_yolu
        
    except Exception as e:
        hata_mesaji = HataMesajlari.DOSYA_YAZMA_HATASI.format(str(e))
        logger.error(hata_mesaji)
        raise DosyaIslemHatasi(hata_mesaji)


def pdf_disari_aktar(veri: List[Dict[str, Any]], dosya_yolu: str, baslik: Optional[str] = None) -> str:
    """
    Veriyi PDF formatında dışa aktarır (MVP placeholder)
    
    Args:
        veri: Dışa aktarılacak veri listesi
        dosya_yolu: Hedef dosya yolu
        baslik: Opsiyonel başlık
        
    Returns:
        str: Oluşturulan dosyanın tam yolu
        
    Note:
        Bu fonksiyon MVP'de placeholder olarak çalışır
    """
    logger.warning(LogMesajlari.MVP_PLACEHOLDER_UYARISI.format("pdf_disari_aktar"))
    
    try:
        # MVP için basit metin dosyası oluştur
        with open(dosya_yolu, 'w', encoding='utf-8') as dosya:
            dosya.write("PDF PLACEHOLDER - MVP\n")
            dosya.write("=" * 50 + "\n\n")
            
            if baslik:
                dosya.write(f"Başlık: {baslik}\n")
            
            dosya.write(f"Oluşturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            dosya.write(f"Toplam Kayıt: {len(veri)}\n\n")
            
            if veri:
                dosya.write("VERİ:\n")
                dosya.write("-" * 30 + "\n")
                for i, satir in enumerate(veri[:10], 1):  # İlk 10 kayıt
                    dosya.write(f"{i}. {satir}\n")
                
                if len(veri) > 10:
                    dosya.write(f"... ve {len(veri) - 10} kayıt daha\n")
            else:
                dosya.write("Veri bulunamadı.\n")
        
        logger.info(LogMesajlari.DISARI_AKTARIM_TAMAMLANDI.format(dosya_yolu))
        return dosya_yolu
        
    except Exception as e:
        hata_mesaji = HataMesajlari.DOSYA_YAZMA_HATASI.format(str(e))
        logger.error(hata_mesaji)
        raise DosyaIslemHatasi(hata_mesaji)


def disari_aktar(rapor_turu: str, veri: List[Dict[str, Any]], disari_aktar_dto: DisariAktarDTO) -> str:
    """
    Ana dışa aktarım fonksiyonu
    
    Args:
        rapor_turu: Rapor türü
        veri: Dışa aktarılacak veri
        disari_aktar_dto: Dışa aktarım parametreleri
        
    Returns:
        str: Oluşturulan dosyanın tam yolu
        
    Raises:
        DosyaIslemHatasi: Dışa aktarım hatası
    """
    try:
        # Klasör yolu belirle
        if disari_aktar_dto.klasor_yolu:
            klasor_yolu = disari_aktar_dto.klasor_yolu
        else:
            klasor_yolu = RaporSabitleri.VARSAYILAN_KLASOR
        
        # Klasörü oluştur
        klasor_olustur(klasor_yolu)
        
        # Dosya adı belirle
        if disari_aktar_dto.dosya_adi:
            dosya_adi = disari_aktar_dto.dosya_adi
        else:
            dosya_adi = benzersiz_dosya_adi_olustur(rapor_turu, disari_aktar_dto.format)
        
        # Tam dosya yolu
        tam_dosya_yolu = os.path.join(klasor_yolu, dosya_adi)
        
        # Formata göre dışa aktar
        if disari_aktar_dto.format == DisariAktarFormat.CSV:
            return csv_disari_aktar(veri, tam_dosya_yolu, disari_aktar_dto.baslik)
        elif disari_aktar_dto.format == DisariAktarFormat.PDF:
            return pdf_disari_aktar(veri, tam_dosya_yolu, disari_aktar_dto.baslik)
        else:
            raise DosyaIslemHatasi(f"Desteklenmeyen format: {disari_aktar_dto.format}")
            
    except Exception as e:
        if isinstance(e, DosyaIslemHatasi):
            raise
        else:
            hata_mesaji = HataMesajlari.DOSYA_OLUSTURMA_HATASI.format(str(e))
            logger.error(hata_mesaji)
            raise DosyaIslemHatasi(hata_mesaji)