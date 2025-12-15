# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.baglanti_yardimci
# Description: SONTECHSP veritabanı bağlantı yardımcı fonksiyonları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Veritabanı Bağlantı Yardımcı Fonksiyonları

Bu modül veritabanı bağlantı yönetimi için yardımcı fonksiyonları içerir.
Engine oluşturma ve yapılandırma işlemleri burada yapılır.
"""

import logging
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.pool import StaticPool

from ..cekirdek.ayarlar import ayar_al
from ..cekirdek.hatalar import VeritabaniHatasi

logger = logging.getLogger(__name__)


def postgresql_engine_olustur() -> Engine:
    """PostgreSQL engine oluştur"""
    try:
        # PostgreSQL bağlantı URL'i oluştur
        host = ayar_al('veritabani.postgresql.host', 'localhost')
        port = ayar_al('veritabani.postgresql.port', 5432)
        database = ayar_al('veritabani.postgresql.database', 'sontechsp')
        username = ayar_al('veritabani.postgresql.username', 'postgres')
        password = ayar_al('veritabani.postgresql.password', '')
        
        url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        
        # Engine oluştur
        engine = create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=ayar_al('debug', False)
        )
        
        # Connection event listeners
        @event.listens_for(engine, "connect")
        def set_postgresql_pragma(dbapi_connection, connection_record):
            """PostgreSQL bağlantı ayarları"""
            pass
        
        logger.info(f"PostgreSQL engine oluşturuldu: {host}:{port}/{database}")
        return engine
        
    except Exception as e:
        logger.error(f"PostgreSQL engine oluşturma hatası: {e}")
        raise VeritabaniHatasi(f"PostgreSQL bağlantısı kurulamadı: {e}")


def sqlite_engine_olustur(dosya_yolu: str = "sontechsp_offline.db") -> Engine:
    """SQLite engine oluştur (offline POS için)"""
    try:
        url = f"sqlite:///{dosya_yolu}"
        
        # SQLite engine oluştur
        engine = create_engine(
            url,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 30
            },
            echo=ayar_al('debug', False)
        )
        
        # SQLite pragma ayarları
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """SQLite performans ve güvenlik ayarları"""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
        
        logger.info(f"SQLite engine oluşturuldu: {dosya_yolu}")
        return engine
        
    except Exception as e:
        logger.error(f"SQLite engine oluşturma hatası: {e}")
        raise VeritabaniHatasi(f"SQLite bağlantısı kurulamadı: {e}")


def baglanti_test_et_yardimci(engine: Engine, veritabani_tipi: str) -> bool:
    """Veritabanı bağlantısını test et"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
            logger.info(f"{veritabani_tipi} bağlantı testi başarılı")
            return True
    except Exception as e:
        logger.error(f"{veritabani_tipi} bağlantı testi başarısız: {e}")
        return False