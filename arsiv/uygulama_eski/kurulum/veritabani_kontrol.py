# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kurulum.veritabani_kontrol
# Description: Veritabanı bağlantı kontrolü ve migration yönetimi
# Changelog:
# - Veritabanı bağlantı testi ve Alembic migration fonksiyonları eklendi

"""
Veritabanı kontrol modülü

Bu modül, kurulum sırasında veritabanı bağlantısının test edilmesi ve
Alembic migration'larının çalıştırılması için fonksiyonlar içerir.
"""

import logging
from pathlib import Path
from typing import Optional
import sys
import os

from .sabitler import ALEMBIC_CONFIG_YOLU, ALEMBIC_CONFIG_DOSYASI
from . import DogrulamaHatasi, MigrationHatasi, logger

# SQLAlchemy ve Alembic import'ları
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("SQLAlchemy bulunamadı, veritabanı işlemleri devre dışı")

try:
    from alembic.config import Config
    from alembic import command
    from alembic.script import ScriptDirectory
    from alembic.runtime.environment import EnvironmentContext
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False
    logger.warning("Alembic bulunamadı, migration işlemleri devre dışı")


def baglanti_test_et(veritabani_url: str) -> None:
    """
    Veritabanı bağlantısını test et
    
    Args:
        veritabani_url: Veritabanı bağlantı URL'i
        
    Raises:
        DogrulamaHatasi: Bağlantı başarısızsa
    """
    if not SQLALCHEMY_AVAILABLE:
        raise DogrulamaHatasi(
            "SQLAlchemy bulunamadı. Lütfen 'pip install sqlalchemy' çalıştırın."
        )
    
    try:
        # URL'in geçerliliğini kontrol et
        if not veritabani_url or not isinstance(veritabani_url, str):
            raise DogrulamaHatasi("Geçersiz veritabanı URL'i")
        
        if len(veritabani_url.strip()) < 10:
            raise DogrulamaHatasi("Veritabanı URL'i çok kısa")
        
        # PostgreSQL URL formatını kontrol et
        if not veritabani_url.startswith(('postgresql://', 'postgres://')):
            raise DogrulamaHatasi(
                "Sadece PostgreSQL veritabanları desteklenir. "
                "URL 'postgresql://' ile başlamalı."
            )
        
        logger.info(f"Veritabanı bağlantısı test ediliyor...")
        
        # Engine oluştur
        engine = create_engine(veritabani_url, echo=False)
        
        # Basit bir sorgu ile bağlantıyı test et
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            test_result = result.scalar()
            
            if test_result != 1:
                raise DogrulamaHatasi("Veritabanı bağlantı testi başarısız")
        
        logger.info("Veritabanı bağlantısı başarıyla test edildi")
        
    except SQLAlchemyError as e:
        error_msg = str(e)
        if "could not connect" in error_msg.lower():
            raise DogrulamaHatasi(
                f"Veritabanına bağlanılamadı. Sunucu çalışıyor mu? Hata: {error_msg}"
            )
        elif "authentication failed" in error_msg.lower():
            raise DogrulamaHatasi(
                f"Veritabanı kimlik doğrulama hatası. Kullanıcı adı/şifre doğru mu? Hata: {error_msg}"
            )
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            raise DogrulamaHatasi(
                f"Belirtilen veritabanı mevcut değil. Hata: {error_msg}"
            )
        else:
            raise DogrulamaHatasi(f"Veritabanı bağlantı hatası: {error_msg}")
    
    except Exception as e:
        if isinstance(e, DogrulamaHatasi):
            raise
        raise DogrulamaHatasi(f"Beklenmeyen veritabanı hatası: {e}")


def alembic_config_yolunu_bul(proje_koku: Path) -> Path:
    """
    Alembic config dosyasının yolunu bul
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        Path: Alembic config dosyasının yolu
        
    Raises:
        MigrationHatasi: Config dosyası bulunamazsa
    """
    # Proje kök dizinini Path nesnesine çevir
    if isinstance(proje_koku, str):
        proje_koku = Path(proje_koku)
    
    # Önce belirtilen yolda ara
    config_yolu = proje_koku / ALEMBIC_CONFIG_YOLU / ALEMBIC_CONFIG_DOSYASI
    if config_yolu.exists():
        return config_yolu
    
    # Proje kök dizininde ara
    config_yolu = proje_koku / ALEMBIC_CONFIG_DOSYASI
    if config_yolu.exists():
        return config_yolu
    
    # Mevcut dizinde ara
    config_yolu = Path(ALEMBIC_CONFIG_DOSYASI)
    if config_yolu.exists():
        return config_yolu
    
    raise MigrationHatasi(
        f"Alembic config dosyası bulunamadı. Aranan yerler: "
        f"{proje_koku / ALEMBIC_CONFIG_YOLU / ALEMBIC_CONFIG_DOSYASI}, "
        f"{proje_koku / ALEMBIC_CONFIG_DOSYASI}, "
        f"{ALEMBIC_CONFIG_DOSYASI}"
    )


def gocleri_calistir(proje_koku: Path) -> None:
    """
    Alembic migration'larını çalıştır (upgrade head)
    
    Args:
        proje_koku: Proje kök dizini
        
    Raises:
        MigrationHatasi: Migration işlemi başarısızsa
    """
    if not ALEMBIC_AVAILABLE:
        raise MigrationHatasi(
            "Alembic bulunamadı. Lütfen 'pip install alembic' çalıştırın."
        )
    
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        logger.info("Alembic migration'ları çalıştırılıyor...")
        
        # Alembic config dosyasını bul
        config_dosya_yolu = alembic_config_yolunu_bul(proje_koku)
        
        # Alembic Config nesnesi oluştur
        alembic_cfg = Config(str(config_dosya_yolu))
        
        # Migration dizininin varlığını kontrol et
        script_location = alembic_cfg.get_main_option("script_location")
        if script_location:
            script_dir = Path(script_location)
            if not script_dir.is_absolute():
                script_dir = config_dosya_yolu.parent / script_dir
            
            if not script_dir.exists():
                raise MigrationHatasi(
                    f"Migration dizini bulunamadı: {script_dir}"
                )
        
        # Migration'ları çalıştır (upgrade head)
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Alembic migration'ları başarıyla tamamlandı")
        
    except Exception as e:
        if isinstance(e, MigrationHatasi):
            raise
        
        error_msg = str(e)
        if "No such file or directory" in error_msg:
            raise MigrationHatasi(
                f"Migration dosyaları bulunamadı: {error_msg}"
            )
        elif "Target database is not up to date" in error_msg:
            raise MigrationHatasi(
                f"Veritabanı güncel değil, migration gerekli: {error_msg}"
            )
        elif "Can't locate revision identified by" in error_msg:
            raise MigrationHatasi(
                f"Migration revision bulunamadı: {error_msg}"
            )
        else:
            raise MigrationHatasi(f"Migration hatası: {error_msg}")


def migration_durumunu_kontrol_et(proje_koku: Path) -> dict:
    """
    Migration durumunu kontrol et
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        dict: Migration durum bilgileri
        
    Raises:
        MigrationHatasi: Kontrol işlemi başarısızsa
    """
    if not ALEMBIC_AVAILABLE:
        raise MigrationHatasi("Alembic bulunamadı")
    
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        # Alembic config dosyasını bul
        config_dosya_yolu = alembic_config_yolunu_bul(proje_koku)
        
        # Alembic Config nesnesi oluştur
        alembic_cfg = Config(str(config_dosya_yolu))
        
        # Script directory oluştur
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Mevcut head revision'ı al
        head_revision = script.get_current_head()
        
        durum = {
            "config_dosyasi": str(config_dosya_yolu),
            "script_location": script.dir,
            "head_revision": head_revision,
            "migration_mevcut": head_revision is not None
        }
        
        return durum
        
    except Exception as e:
        if isinstance(e, MigrationHatasi):
            raise
        raise MigrationHatasi(f"Migration durum kontrolü hatası: {e}")


def veritabani_baglantisini_dogrula(veritabani_url: str) -> bool:
    """
    Veritabanı bağlantısını doğrula (hata fırlatmadan)
    
    Args:
        veritabani_url: Veritabanı bağlantı URL'i
        
    Returns:
        bool: Bağlantı başarılıysa True, değilse False
    """
    try:
        baglanti_test_et(veritabani_url)
        return True
    except DogrulamaHatasi:
        return False
    except Exception:
        return False