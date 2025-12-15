# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.gocler.env
# Description: SONTECHSP Alembic environment yapılandırması
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Alembic Environment Yapılandırması

Bu dosya Alembic migration ortamını yapılandırır.
Hem PostgreSQL hem SQLite desteği sağlar.
"""

import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# SONTECHSP modüllerini import edebilmek için path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# SONTECHSP modüllerini import et
from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.veritabani.modeller import *  # Tüm modelleri import et

# Alembic Config nesnesi
config = context.config

# Logging yapılandırması
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata nesnesi (tüm tablolar için)
target_metadata = Taban.metadata

# Logger
logger = logging.getLogger('alembic.env')


def get_url():
    """
    Veritabanı URL'ini environment variable'dan veya config'den al
    """
    # Environment variable'dan al (öncelik)
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    
    # Config dosyasından al
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """
    Offline migration modunda çalıştır
    
    Bu mod veritabanına bağlanmadan SQL scriptleri oluşturur.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online migration modunda çalıştır
    
    Bu mod veritabanına bağlanarak migration'ları uygular.
    """
    # Veritabanı URL'ini config'e set et
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    # Engine oluştur
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
            # Türkçe ASCII tablo isimlendirmesi için
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()


# Migration modunu belirle ve çalıştır
if context.is_offline_mode():
    logger.info("Offline migration modu")
    run_migrations_offline()
else:
    logger.info("Online migration modu")
    run_migrations_online()