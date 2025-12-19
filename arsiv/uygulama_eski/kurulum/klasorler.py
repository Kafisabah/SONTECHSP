# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kurulum.klasorler
# Description: Klasör yönetimi işlemleri
# Changelog:
# - Klasör oluşturma ve kontrol fonksiyonları eklendi

"""
Klasör yönetimi modülü

Bu modül, kurulum sırasında gerekli klasörlerin oluşturulması ve
kontrolü için fonksiyonlar içerir.
"""

import logging
from pathlib import Path
from typing import List

from .sabitler import GEREKLI_KLASORLER
from . import KlasorHatasi, logger


def klasorleri_olustur(proje_koku: Path) -> None:
    """
    Gerekli klasörleri oluştur
    
    Args:
        proje_koku: Proje kök dizini
        
    Raises:
        KlasorHatasi: Klasör oluşturma işlemi başarısızsa
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        logger.info(f"Klasörler oluşturuluyor: {proje_koku}")
        
        # Her gerekli klasörü oluştur
        for klasor_adi in GEREKLI_KLASORLER:
            klasor_yolu = proje_koku / klasor_adi
            
            try:
                # Klasör zaten varsa geç
                if klasor_yolu.exists():
                    if klasor_yolu.is_dir():
                        logger.debug(f"Klasör zaten mevcut: {klasor_yolu}")
                        continue
                    else:
                        raise KlasorHatasi(
                            f"'{klasor_yolu}' yolu bir dosya olarak mevcut, "
                            f"klasör oluşturulamıyor"
                        )
                
                # Klasörü oluştur (parents=True ile üst klasörleri de oluştur)
                klasor_yolu.mkdir(parents=True, exist_ok=True)
                logger.info(f"Klasör oluşturuldu: {klasor_yolu}")
                
            except PermissionError as e:
                raise KlasorHatasi(
                    f"'{klasor_yolu}' klasörü oluşturulamadı: İzin hatası - {e}"
                )
            except OSError as e:
                raise KlasorHatasi(
                    f"'{klasor_yolu}' klasörü oluşturulamadı: Sistem hatası - {e}"
                )
        
        logger.info("Tüm gerekli klasörler başarıyla oluşturuldu")
        
    except Exception as e:
        if isinstance(e, KlasorHatasi):
            raise
        raise KlasorHatasi(f"Klasör oluşturma işlemi başarısız: {e}")


def klasor_var_mi(proje_koku: Path) -> bool:
    """
    Tüm gerekli klasörlerin var olup olmadığını kontrol et
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        bool: Tüm klasörler mevcutsa True, değilse False
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        # Proje kök dizini yoksa False döndür
        if not proje_koku.exists():
            return False
        
        # Her gerekli klasörü kontrol et
        for klasor_adi in GEREKLI_KLASORLER:
            klasor_yolu = proje_koku / klasor_adi
            
            # Klasör yoksa veya dizin değilse False döndür
            if not klasor_yolu.exists() or not klasor_yolu.is_dir():
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Klasör kontrol hatası: {e}")
        return False


def eksik_klasorleri_listele(proje_koku: Path) -> List[str]:
    """
    Eksik klasörlerin listesini döndür
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        List[str]: Eksik klasörlerin listesi
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        eksik_klasorler = []
        
        # Her gerekli klasörü kontrol et
        for klasor_adi in GEREKLI_KLASORLER:
            klasor_yolu = proje_koku / klasor_adi
            
            # Klasör yoksa veya dizin değilse listeye ekle
            if not klasor_yolu.exists() or not klasor_yolu.is_dir():
                eksik_klasorler.append(klasor_adi)
        
        return eksik_klasorler
        
    except Exception as e:
        logger.error(f"Eksik klasör listesi oluşturma hatası: {e}")
        return list(GEREKLI_KLASORLER)  # Hata durumunda tüm klasörleri eksik say


def klasor_yolunu_dogrula(proje_koku: Path, klasor_adi: str) -> Path:
    """
    Klasör yolunu doğrula ve Path nesnesi döndür
    
    Args:
        proje_koku: Proje kök dizini
        klasor_adi: Klasör adı
        
    Returns:
        Path: Doğrulanmış klasör yolu
        
    Raises:
        KlasorHatasi: Geçersiz yol durumunda
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        # Klasör yolunu oluştur
        klasor_yolu = proje_koku / klasor_adi
        
        # Yolun geçerliliğini kontrol et
        try:
            # resolve() ile mutlak yolu al ve geçerliliği test et
            mutlak_yol = klasor_yolu.resolve()
            return mutlak_yol
        except (OSError, ValueError) as e:
            raise KlasorHatasi(f"Geçersiz klasör yolu: {klasor_yolu} - {e}")
        
    except Exception as e:
        if isinstance(e, KlasorHatasi):
            raise
        raise KlasorHatasi(f"Klasör yolu doğrulama hatası: {e}")