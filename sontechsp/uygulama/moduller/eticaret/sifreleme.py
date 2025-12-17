# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.sifreleme
# Description: Hassas kimlik bilgileri için şifreleme yardımcıları
# Changelog:
# - İlk oluşturma
# - Fernet tabanlı şifreleme eklendi

"""
E-ticaret kimlik bilgileri için şifreleme yardımcıları.
Hassas verilerin güvenli saklanması için kullanılır.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .hatalar import EntegrasyonHatasi

logger = logging.getLogger(__name__)


class KimlikSifreleme:
    """
    Kimlik bilgileri için şifreleme sınıfı.
    
    Fernet (AES 128) tabanlı simetrik şifreleme kullanır.
    Şifreleme anahtarı environment variable'dan alınır.
    """
    
    def __init__(self, anahtar: Optional[str] = None):
        """
        Şifreleme sınıfını başlatır
        
        Args:
            anahtar: Şifreleme anahtarı (None ise env'den alır)
        """
        if anahtar:
            self._anahtar = anahtar.encode()
        else:
            # Environment variable'dan anahtar al
            env_anahtar = os.getenv('ETICARET_SIFRELEME_ANAHTARI')
            if not env_anahtar:
                # Geliştirme ortamı için varsayılan anahtar
                logger.warning("Şifreleme anahtarı bulunamadı, varsayılan anahtar kullanılıyor")
                env_anahtar = "sontechsp-eticaret-default-key-2024"
            
            self._anahtar = env_anahtar.encode()
        
        # Anahtar türetme
        self._fernet = self._anahtar_turet()
    
    def _anahtar_turet(self) -> Fernet:
        """Güvenli anahtar türetme"""
        try:
            # Salt oluştur (sabit salt - production'da değiştirilmeli)
            salt = b'sontechsp_salt_2024'
            
            # PBKDF2 ile anahtar türet
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(self._anahtar))
            return Fernet(key)
            
        except Exception as e:
            logger.error(f"Anahtar türetme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Şifreleme anahtarı oluşturulamadı",
                detay=str(e)
            )
    
    def sifrele(self, veri: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kimlik bilgilerini şifreler
        
        Args:
            veri: Şifrelenecek kimlik bilgileri
            
        Returns:
            Şifrelenmiş veri (encrypted flag ile)
            
        Raises:
            EntegrasyonHatasi: Şifreleme hatası durumunda
        """
        try:
            if not veri:
                return veri
            
            # JSON string'e çevir
            json_str = json.dumps(veri, ensure_ascii=False, sort_keys=True)
            json_bytes = json_str.encode('utf-8')
            
            # Şifrele
            sifreli_bytes = self._fernet.encrypt(json_bytes)
            sifreli_str = base64.urlsafe_b64encode(sifreli_bytes).decode('ascii')
            
            # Şifrelenmiş veri formatı
            sonuc = {
                'encrypted': True,
                'data': sifreli_str,
                'algorithm': 'fernet-aes128'
            }
            
            logger.debug("Kimlik bilgileri şifrelendi")
            return sonuc
            
        except Exception as e:
            logger.error(f"Şifreleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Kimlik bilgileri şifrelenemedi",
                detay=str(e)
            )
    
    def sifreyi_coz(self, sifreli_veri: Dict[str, Any]) -> Dict[str, Any]:
        """
        Şifrelenmiş kimlik bilgilerini çözer
        
        Args:
            sifreli_veri: Şifrelenmiş veri
            
        Returns:
            Çözülmüş kimlik bilgileri
            
        Raises:
            EntegrasyonHatasi: Şifre çözme hatası durumunda
        """
        try:
            if not sifreli_veri:
                return sifreli_veri
            
            # Şifrelenmiş veri kontrolü
            if not isinstance(sifreli_veri, dict) or not sifreli_veri.get('encrypted'):
                # Şifrelenmemiş veri - olduğu gibi döndür
                logger.warning("Şifrelenmemiş kimlik bilgisi tespit edildi")
                return sifreli_veri
            
            # Şifrelenmiş veriyi çöz
            sifreli_str = sifreli_veri.get('data')
            if not sifreli_str:
                raise ValueError("Şifrelenmiş veri bulunamadı")
            
            sifreli_bytes = base64.urlsafe_b64decode(sifreli_str.encode('ascii'))
            json_bytes = self._fernet.decrypt(sifreli_bytes)
            json_str = json_bytes.decode('utf-8')
            
            # JSON'dan dict'e çevir
            sonuc = json.loads(json_str)
            
            logger.debug("Kimlik bilgileri şifresi çözüldü")
            return sonuc
            
        except Exception as e:
            logger.error(f"Şifre çözme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Kimlik bilgileri şifresi çözülemedi",
                detay=str(e)
            )
    
    def sifreli_mi(self, veri: Dict[str, Any]) -> bool:
        """
        Verinin şifrelenmiş olup olmadığını kontrol eder
        
        Args:
            veri: Kontrol edilecek veri
            
        Returns:
            Şifrelenmiş ise True
        """
        if not isinstance(veri, dict):
            return False
        
        return veri.get('encrypted', False) is True
    
    @staticmethod
    def anahtar_olustur() -> str:
        """
        Yeni şifreleme anahtarı oluşturur
        
        Returns:
            Base64 encoded anahtar
        """
        anahtar = Fernet.generate_key()
        return base64.urlsafe_b64encode(anahtar).decode('ascii')


# Global şifreleme instance'ı
_sifreleme_instance: Optional[KimlikSifreleme] = None


def sifreleme_al() -> KimlikSifreleme:
    """
    Global şifreleme instance'ını döndürür (singleton pattern)
    
    Returns:
        KimlikSifreleme instance'ı
    """
    global _sifreleme_instance
    
    if _sifreleme_instance is None:
        _sifreleme_instance = KimlikSifreleme()
    
    return _sifreleme_instance


def kimlik_sifrele(kimlik_bilgileri: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kimlik bilgilerini şifreler (kolaylık fonksiyonu)
    
    Args:
        kimlik_bilgileri: Şifrelenecek kimlik bilgileri
        
    Returns:
        Şifrelenmiş kimlik bilgileri
    """
    sifreleme = sifreleme_al()
    return sifreleme.sifrele(kimlik_bilgileri)


def kimlik_sifreyi_coz(sifreli_kimlik: Dict[str, Any]) -> Dict[str, Any]:
    """
    Şifrelenmiş kimlik bilgilerini çözer (kolaylık fonksiyonu)
    
    Args:
        sifreli_kimlik: Şifrelenmiş kimlik bilgileri
        
    Returns:
        Çözülmüş kimlik bilgileri
    """
    sifreleme = sifreleme_al()
    return sifreleme.sifreyi_coz(sifreli_kimlik)