# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kurulum.ayar_olusturucu
# Description: Ayar dosyası yönetimi
# Changelog:
# - Ayar dosyası oluşturma ve okuma fonksiyonları eklendi

"""
Ayar dosyası yönetimi modülü

Bu modül, kurulum sırasında yapılandırma dosyasının oluşturulması,
okunması ve yönetimi için fonksiyonlar içerir.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from .sabitler import (
    CONFIG_DOSYA_ADI,
    VARSAYILAN_ORTAM,
    VARSAYILAN_LOG_SEVIYESI,
    VARSAYILAN_VERITABANI_URL
)
from . import AyarHatasi, logger


def varsayilan_ayarlar() -> Dict[str, Any]:
    """
    Varsayılan ayarları döndür
    
    Returns:
        Dict[str, Any]: Varsayılan ayar sözlüğü
    """
    return {
        "veritabani_url": VARSAYILAN_VERITABANI_URL,
        "ortam": VARSAYILAN_ORTAM,
        "log_seviyesi": VARSAYILAN_LOG_SEVIYESI
    }


def ayar_dosyasi_var_mi(proje_koku: Path) -> bool:
    """
    Ayar dosyasının var olup olmadığını kontrol et
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        bool: Ayar dosyası mevcutsa True, değilse False
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        ayar_dosya_yolu = proje_koku / CONFIG_DOSYA_ADI
        return ayar_dosya_yolu.exists() and ayar_dosya_yolu.is_file()
        
    except Exception as e:
        logger.error(f"Ayar dosyası kontrol hatası: {e}")
        return False


def ayar_dosyasi_olustur(proje_koku: Path, ayarlar: Dict[str, Any]) -> None:
    """
    Ayar dosyasını oluştur
    
    Args:
        proje_koku: Proje kök dizini
        ayarlar: Ayar sözlüğü
        
    Raises:
        AyarHatasi: Ayar dosyası oluşturma işlemi başarısızsa
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        ayar_dosya_yolu = proje_koku / CONFIG_DOSYA_ADI
        
        # Ayar dosyası zaten varsa üzerine yazma
        if ayar_dosya_yolu.exists():
            logger.info(f"Ayar dosyası zaten mevcut: {ayar_dosya_yolu}")
            return
        
        # Gerekli alanları kontrol et
        gerekli_alanlar = ["veritabani_url", "ortam", "log_seviyesi"]
        for alan in gerekli_alanlar:
            if alan not in ayarlar:
                raise AyarHatasi(f"Gerekli ayar alanı eksik: {alan}")
        
        # Proje kök dizinini oluştur (yoksa)
        proje_koku.mkdir(parents=True, exist_ok=True)
        
        # JSON dosyasını yaz
        with open(ayar_dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(ayarlar, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Ayar dosyası oluşturuldu: {ayar_dosya_yolu}")
        
    except (TypeError, ValueError) as e:
        raise AyarHatasi(f"JSON kodlama hatası: {e}")
    except PermissionError as e:
        raise AyarHatasi(f"Ayar dosyası yazma izni hatası: {e}")
    except OSError as e:
        raise AyarHatasi(f"Ayar dosyası oluşturma sistem hatası: {e}")
    except Exception as e:
        if isinstance(e, AyarHatasi):
            raise
        raise AyarHatasi(f"Ayar dosyası oluşturma hatası: {e}")


def ayarlari_yukle(proje_koku: Path) -> Dict[str, Any]:
    """
    Ayar dosyasını yükle
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        Dict[str, Any]: Ayar sözlüğü
        
    Raises:
        AyarHatasi: Ayar dosyası okuma işlemi başarısızsa
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        ayar_dosya_yolu = proje_koku / CONFIG_DOSYA_ADI
        
        # Ayar dosyası yoksa hata
        if not ayar_dosya_yolu.exists():
            raise AyarHatasi(f"Ayar dosyası bulunamadı: {ayar_dosya_yolu}")
        
        # JSON dosyasını oku
        with open(ayar_dosya_yolu, 'r', encoding='utf-8') as f:
            ayarlar = json.load(f)
        
        # Gerekli alanları kontrol et
        gerekli_alanlar = ["veritabani_url", "ortam", "log_seviyesi"]
        for alan in gerekli_alanlar:
            if alan not in ayarlar:
                raise AyarHatasi(f"Ayar dosyasında gerekli alan eksik: {alan}")
        
        logger.debug(f"Ayar dosyası yüklendi: {ayar_dosya_yolu}")
        return ayarlar
        
    except json.JSONDecodeError as e:
        raise AyarHatasi(f"Ayar dosyası JSON parse hatası: {e}")
    except PermissionError as e:
        raise AyarHatasi(f"Ayar dosyası okuma izni hatası: {e}")
    except OSError as e:
        raise AyarHatasi(f"Ayar dosyası okuma sistem hatası: {e}")
    except Exception as e:
        if isinstance(e, AyarHatasi):
            raise
        raise AyarHatasi(f"Ayar dosyası yükleme hatası: {e}")


def ayar_dosyasini_dogrula(ayarlar: Dict[str, Any]) -> bool:
    """
    Ayar dosyası içeriğini doğrula
    
    Args:
        ayarlar: Ayar sözlüğü
        
    Returns:
        bool: Ayarlar geçerliyse True, değilse False
    """
    try:
        # Gerekli alanları kontrol et
        gerekli_alanlar = ["veritabani_url", "ortam", "log_seviyesi"]
        for alan in gerekli_alanlar:
            if alan not in ayarlar:
                return False
            
            # Boş değer kontrolü
            if not ayarlar[alan] or str(ayarlar[alan]).strip() == "":
                return False
        
        # Ortam değeri kontrolü
        gecerli_ortamlar = ["dev", "test", "prod"]
        if ayarlar["ortam"] not in gecerli_ortamlar:
            return False
        
        # Log seviyesi kontrolü
        gecerli_log_seviyeleri = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if ayarlar["log_seviyesi"] not in gecerli_log_seviyeleri:
            return False
        
        # Veritabanı URL temel kontrolü
        veritabani_url = ayarlar["veritabani_url"]
        if not isinstance(veritabani_url, str) or len(veritabani_url) < 10:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Ayar doğrulama hatası: {e}")
        return False


def ayar_dosyasini_guncelle(proje_koku: Path, yeni_ayarlar: Dict[str, Any]) -> None:
    """
    Mevcut ayar dosyasını güncelle
    
    Args:
        proje_koku: Proje kök dizini
        yeni_ayarlar: Yeni ayar değerleri
        
    Raises:
        AyarHatasi: Güncelleme işlemi başarısızsa
    """
    try:
        # Mevcut ayarları yükle
        mevcut_ayarlar = ayarlari_yukle(proje_koku)
        
        # Yeni ayarları birleştir
        mevcut_ayarlar.update(yeni_ayarlar)
        
        # Doğrula
        if not ayar_dosyasini_dogrula(mevcut_ayarlar):
            raise AyarHatasi("Güncellenmiş ayarlar geçersiz")
        
        # Dosyayı yeniden yaz
        ayar_dosya_yolu = proje_koku / CONFIG_DOSYA_ADI
        with open(ayar_dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(mevcut_ayarlar, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Ayar dosyası güncellendi: {ayar_dosya_yolu}")
        
    except Exception as e:
        if isinstance(e, AyarHatasi):
            raise
        raise AyarHatasi(f"Ayar dosyası güncelleme hatası: {e}")