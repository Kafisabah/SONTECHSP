# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.gocler
# Description: SONTECHSP Alembic migration dosyaları paketi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Alembic Migration Dosyaları

Bu paket Alembic tarafından oluşturulan migration dosyalarını içerir.
Veritabanı şema değişiklikleri bu klasörde yönetilir.

Migration organizasyonu:
- versions/: Alembic migration dosyaları
- env.py: Alembic environment yapılandırması
- script.py.mako: Migration şablonu
- alembic.ini: Alembic yapılandırma dosyası (proje kökünde)

Kullanım:
- Migration oluşturma: alembic revision --autogenerate -m "açıklama"
- Migration uygulama: alembic upgrade head
- Migration geri alma: alembic downgrade -1
"""