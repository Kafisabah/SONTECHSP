# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.baglanti
# Description: SONTECHSP SQLAlchemy session yönetimi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Veritabanı Bağlantı Yönetimi

Bu modül SQLAlchemy session yönetimini sağlar.
Hem PostgreSQL (ana) hem SQLite (offline POS) desteği içerir.
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, Session

from ..cekirdek.hatalar import VeritabaniHatasi
from .taban import Taban
from .baglanti_yardimci import postgresql_engine_olustur, sqlite_engine_olustur, baglanti_test_et_yardimci

logger = logging.getLogger(__name__)


class VeriTabaniBaglanti:
    """SONTECHSP veritabanı bağlantı yöneticisi"""
    
    _instance: Optional['VeriTabaniBaglanti'] = None
    _postgresql_engine: Optional[Engine] = None
    _sqlite_engine: Optional[Engine] = None
    _postgresql_session_factory: Optional[sessionmaker] = None
    _sqlite_session_factory: Optional[sessionmaker] = None
    
    def __new__(cls) -> 'VeriTabaniBaglanti':
        """Singleton pattern uygulaması"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Bağlantı yöneticisi başlatma"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("Veritabanı bağlantı yöneticisi başlatıldı")
    
    def postgresql_engine_al(self) -> Engine:
        """PostgreSQL engine al"""
        if self._postgresql_engine is None:
            self._postgresql_engine = postgresql_engine_olustur()
        return self._postgresql_engine
    
    def sqlite_engine_al(self, dosya_yolu: str = "sontechsp_offline.db") -> Engine:
        """SQLite engine al"""
        if self._sqlite_engine is None:
            self._sqlite_engine = sqlite_engine_olustur(dosya_yolu)
        return self._sqlite_engine
    
    def postgresql_session_factory_olustur(self) -> sessionmaker:
        """PostgreSQL session factory oluştur"""
        if self._postgresql_session_factory is None:
            engine = self.postgresql_engine_al()
            self._postgresql_session_factory = sessionmaker(
                bind=engine,
                autoflush=False,
                autocommit=False
            )
            logger.info("PostgreSQL session factory oluşturuldu")
        return self._postgresql_session_factory
    
    def sqlite_session_factory_olustur(self) -> sessionmaker:
        """SQLite session factory oluştur"""
        if self._sqlite_session_factory is None:
            engine = self.sqlite_engine_al()
            self._sqlite_session_factory = sessionmaker(
                bind=engine,
                autoflush=False,
                autocommit=False
            )
            logger.info("SQLite session factory oluşturuldu")
        return self._sqlite_session_factory
    
    @contextmanager
    def postgresql_session(self) -> Generator[Session, None, None]:
        """PostgreSQL session context manager"""
        session_factory = self.postgresql_session_factory_olustur()
        session = session_factory()
        
        try:
            yield session
            session.commit()
            logger.debug("PostgreSQL session commit edildi")
        except Exception as e:
            session.rollback()
            logger.error(f"PostgreSQL session rollback: {e}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def sqlite_session(self) -> Generator[Session, None, None]:
        """SQLite session context manager"""
        session_factory = self.sqlite_session_factory_olustur()
        session = session_factory()
        
        try:
            yield session
            session.commit()
            logger.debug("SQLite session commit edildi")
        except Exception as e:
            session.rollback()
            logger.error(f"SQLite session rollback: {e}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def readonly_session(self) -> Generator[Session, None, None]:
        """Salt okunur PostgreSQL session context manager"""
        session_factory = self.postgresql_session_factory_olustur()
        session = session_factory()
        
        try:
            # Salt okunur modda autocommit kapalı, rollback yapılacak
            yield session
            # Salt okunur session'da commit yapılmaz
            session.rollback()
            logger.debug("Salt okunur session kapatıldı")
        except Exception as e:
            session.rollback()
            logger.error(f"Salt okunur session hatası: {e}")
            raise
        finally:
            session.close()
    
    def baglanti_test_et(self, veritabani_tipi: str = "postgresql") -> bool:
        """Veritabanı bağlantısını test et"""
        if veritabani_tipi == "postgresql":
            engine = self.postgresql_engine_al()
            return baglanti_test_et_yardimci(engine, "PostgreSQL")
        elif veritabani_tipi == "sqlite":
            engine = self.sqlite_engine_al()
            return baglanti_test_et_yardimci(engine, "SQLite")
        else:
            raise ValueError(f"Geçersiz veritabanı tipi: {veritabani_tipi}")
    
    def tablolari_olustur(self, veritabani_tipi: str = "postgresql"):
        """Tüm tabloları oluştur"""
        try:
            if veritabani_tipi == "postgresql":
                engine = self.postgresql_engine_al()
            elif veritabani_tipi == "sqlite":
                engine = self.sqlite_engine_al()
            else:
                raise ValueError(f"Geçersiz veritabanı tipi: {veritabani_tipi}")
            
            Taban.metadata.create_all(engine)
            logger.info(f"{veritabani_tipi} tabloları oluşturuldu")
            
        except Exception as e:
            logger.error(f"{veritabani_tipi} tablo oluşturma hatası: {e}")
            raise VeritabaniHatasi(f"Tablolar oluşturulamadı: {e}")


# Global bağlantı yöneticisi instance
veritabani_baglanti = VeriTabaniBaglanti()

# Kısayol fonksiyonlar
def postgresql_session():
    """PostgreSQL session kısayolu"""
    return veritabani_baglanti.postgresql_session()

def sqlite_session():
    """SQLite session kısayolu"""
    return veritabani_baglanti.sqlite_session()

def get_readonly_session():
    """Salt okunur session kısayolu"""
    return veritabani_baglanti.readonly_session()

def baglanti_test_et(veritabani_tipi: str = "postgresql") -> bool:
    """Bağlantı testi kısayolu"""
    return veritabani_baglanti.baglanti_test_et(veritabani_tipi)

def tablolari_olustur(veritabani_tipi: str = "postgresql"):
    """Tablo oluşturma kısayolu"""
    return veritabani_baglanti.tablolari_olustur(veritabani_tipi)