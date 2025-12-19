# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kurulum.admin_olusturucu
# Description: Admin kullanıcı oluşturma ve yönetimi
# Changelog:
# - Admin kullanıcı oluşturma ve idempotentlik fonksiyonları eklendi
# - Syntax hatası düzeltildi (çift pwd_context tanımı)
# - Gereksiz globals() kullanımı kaldırıldı

"""
Admin kullanıcı oluşturucu modülü

Bu modül, kurulum sırasında varsayılan admin kullanıcısının oluşturulması
ve yönetimi için fonksiyonlar içerir.
"""

import logging
from typing import Optional
from datetime import datetime

from . import KullaniciHatasi, logger

# Şifre hashleme için passlib import'ları
try:
    from passlib.context import CryptContext
    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False
    logger.warning("passlib bulunamadı, şifre hashleme devre dışı")

# SQLAlchemy ve model import'ları
try:
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("SQLAlchemy bulunamadı, veritabanı işlemleri devre dışı")

try:
    from sontechsp.uygulama.veritabani.modeller.kullanici_yetki import Kullanici
    from sontechsp.uygulama.veritabani.depolar.kullanici_depo import KullaniciDepo
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    logger.warning("Kullanıcı modelleri bulunamadı")

# Bcrypt context oluştur
if PASSLIB_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def sifre_hash_olustur(sifre: str) -> str:
    """
    Şifreyi bcrypt ile hashle
    
    Args:
        sifre: Hashlenecek şifre
        
    Returns:
        str: Hashlenmiş şifre
        
    Raises:
        KullaniciHatasi: Hashleme başarısızsa
    """
    if not PASSLIB_AVAILABLE:
        raise KullaniciHatasi(
            "passlib bulunamadı. Lütfen 'pip install passlib[bcrypt]' çalıştırın."
        )
    
    try:
        if not sifre or not isinstance(sifre, str):
            raise KullaniciHatasi("Geçersiz şifre")
        
        if len(sifre.strip()) < 3:
            raise KullaniciHatasi("Şifre çok kısa (minimum 3 karakter)")
        
        # Bcrypt ile hashle
        hashed = pwd_context.hash(sifre)
        
        if not hashed or len(hashed) < 10:
            raise KullaniciHatasi("Şifre hashleme başarısız")
        
        return hashed
        
    except Exception as e:
        if isinstance(e, KullaniciHatasi):
            raise
        raise KullaniciHatasi(f"Şifre hashleme hatası: {e}")


def sifre_dogrula(sifre: str, hash_sifre: str) -> bool:
    """
    Şifreyi hash ile doğrula
    
    Args:
        sifre: Doğrulanacak şifre
        hash_sifre: Hash şifre
        
    Returns:
        bool: Şifre doğruysa True
    """
    if not PASSLIB_AVAILABLE:
        return False
    
    try:
        return pwd_context.verify(sifre, hash_sifre)
    except Exception:
        return False


def admin_varsa_gec(session: Session) -> bool:
    """
    Admin kullanıcısının var olup olmadığını kontrol et
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        bool: Admin kullanıcısı varsa True
        
    Raises:
        KullaniciHatasi: Kontrol işlemi başarısızsa
    """
    if not SQLALCHEMY_AVAILABLE or not MODELS_AVAILABLE:
        raise KullaniciHatasi(
            "SQLAlchemy veya kullanıcı modelleri bulunamadı"
        )
    
    try:
        kullanici_depo = KullaniciDepo()
        
        # Admin kullanıcısını ara
        admin_kullanici = kullanici_depo.kullanici_adi_ile_getir(
            session, "admin"
        )
        
        if admin_kullanici:
            logger.info("Admin kullanıcısı zaten mevcut")
            return True
        
        logger.info("Admin kullanıcısı bulunamadı")
        return False
        
    except SQLAlchemyError as e:
        logger.error(f"Admin kontrol veritabanı hatası: {e}")
        raise KullaniciHatasi(f"Admin kontrol veritabanı hatası: {e}")
    
    except Exception as e:
        logger.error(f"Admin kontrol hatası: {e}")
        raise KullaniciHatasi(f"Admin kontrol hatası: {e}")


def admin_olustur(session: Session, kullanici_adi: str = "admin", 
                  sifre: str = "admin123") -> None:
    """
    Admin kullanıcısını oluştur
    
    Args:
        session: SQLAlchemy session
        kullanici_adi: Admin kullanıcı adı (varsayılan: "admin")
        sifre: Admin şifresi (varsayılan: "admin123")
        
    Raises:
        KullaniciHatasi: Kullanıcı oluşturma başarısızsa
    """
    if not SQLALCHEMY_AVAILABLE or not MODELS_AVAILABLE:
        raise KullaniciHatasi(
            "SQLAlchemy veya kullanıcı modelleri bulunamadı"
        )
    
    try:
        # Önce admin var mı kontrol et (idempotentlik)
        if admin_varsa_gec(session):
            logger.info("Admin kullanıcısı zaten mevcut, yeni oluşturulmadı")
            return
        
        logger.info(f"Admin kullanıcısı oluşturuluyor: {kullanici_adi}")
        
        # Şifreyi hashle
        sifre_hash = sifre_hash_olustur(sifre)
        
        # Admin kullanıcısını oluştur
        admin_kullanici = Kullanici(
            kullanici_adi=kullanici_adi,
            email="admin@sontechsp.com",
            sifre_hash=sifre_hash,
            ad="Sistem",
            soyad="Yöneticisi",
            aktif=True,
            sifre_degisim_tarihi=datetime.utcnow()
        )
        
        # Veritabanına kaydet
        session.add(admin_kullanici)
        session.commit()
        
        logger.info(f"Admin kullanıcısı başarıyla oluşturuldu: {kullanici_adi}")
        
    except SQLAlchemyError as e:
        session.rollback()
        error_msg = f"Admin oluşturma veritabanı hatası: {e}"
        logger.error(error_msg)
        raise KullaniciHatasi(error_msg)
    
    except Exception as e:
        session.rollback()
        if isinstance(e, KullaniciHatasi):
            logger.error(f"Admin oluşturma hatası: {e}")
            raise
        
        error_msg = f"Admin oluşturma beklenmeyen hatası: {e}"
        logger.error(error_msg)
        raise KullaniciHatasi(error_msg)


def admin_bilgilerini_guncelle(session: Session, kullanici_adi: str = "admin",
                               yeni_sifre: Optional[str] = None,
                               yeni_email: Optional[str] = None) -> None:
    """
    Mevcut admin kullanıcısının bilgilerini güncelle
    
    Args:
        session: SQLAlchemy session
        kullanici_adi: Admin kullanıcı adı
        yeni_sifre: Yeni şifre (opsiyonel)
        yeni_email: Yeni email (opsiyonel)
        
    Raises:
        KullaniciHatasi: Güncelleme başarısızsa
    """
    if not SQLALCHEMY_AVAILABLE or not MODELS_AVAILABLE:
        raise KullaniciHatasi(
            "SQLAlchemy veya kullanıcı modelleri bulunamadı"
        )
    
    try:
        kullanici_depo = KullaniciDepo()
        
        # Admin kullanıcısını bul
        admin_kullanici = kullanici_depo.kullanici_adi_ile_getir(
            session, kullanici_adi
        )
        
        if not admin_kullanici:
            raise KullaniciHatasi(f"Admin kullanıcısı bulunamadı: {kullanici_adi}")
        
        # Güncelleme yapılacak mı kontrol et
        guncelleme_yapildi = False
        
        # Şifre güncelleme
        if yeni_sifre:
            yeni_sifre_hash = sifre_hash_olustur(yeni_sifre)
            admin_kullanici.sifre_hash = yeni_sifre_hash
            admin_kullanici.sifre_degisim_tarihi = datetime.utcnow()
            guncelleme_yapildi = True
            logger.info(f"Admin şifresi güncellendi: {kullanici_adi}")
        
        # Email güncelleme
        if yeni_email:
            admin_kullanici.email = yeni_email
            guncelleme_yapildi = True
            logger.info(f"Admin email güncellendi: {kullanici_adi}")
        
        # Değişiklik varsa kaydet
        if guncelleme_yapildi:
            session.commit()
            logger.info(f"Admin bilgileri başarıyla güncellendi: {kullanici_adi}")
        else:
            logger.info("Güncelleme için yeni bilgi verilmedi")
        
    except SQLAlchemyError as e:
        session.rollback()
        error_msg = f"Admin güncelleme veritabanı hatası: {e}"
        logger.error(error_msg)
        raise KullaniciHatasi(error_msg)
    
    except Exception as e:
        session.rollback()
        if isinstance(e, KullaniciHatasi):
            logger.error(f"Admin güncelleme hatası: {e}")
            raise
        
        error_msg = f"Admin güncelleme beklenmeyen hatası: {e}"
        logger.error(error_msg)
        raise KullaniciHatasi(error_msg)