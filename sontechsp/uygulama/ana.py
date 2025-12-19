# Version: 0.1.0
# Last Update: 2024-12-18
# Module: ana
# Description: SONTECHSP ana uygulama giriş noktası (bootstrap sadece)
# Changelog:
# - İlk oluşturma
# - Kod kalitesi: 120 satır limitine uygun hale getirildi
# - Type hinting iyileştirmeleri

"""
SONTECHSP Ana Uygulama Bootstrap

Sadece bootstrap işlevi gören ana giriş noktası.
İş kuralı içermez, sadece uygulamayı başlatır.

Sorumluluklar:
- PyQt6 uygulama başlatma
- Log sistemi kurulumu
- Merkezi hata yönetimi
- Ana pencere başlatma
"""

import sys
import traceback
from typing import Optional

from PyQt6.QtWidgets import QApplication

# SONTECHSP çekirdek modülleri
from sontechsp.uygulama.cekirdek.kayit import kayit_sistemi_al, kayit_al
from sontechsp.uygulama.cekirdek.hatalar import SontechHatasi, EntegrasyonHatasi

# Ana pencere modülü
from sontechsp.uygulama.arayuz.ana_pencere import AnaPencere


def uygulama_kur() -> QApplication:
    """
    PyQt6 uygulamasını kurar

    Returns:
        QApplication: Yapılandırılmış uygulama
    """
    app = QApplication(sys.argv)
    app.setApplicationName("SONTECHSP")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("SONTECHSP")
    app.setOrganizationDomain("sontechsp.com")

    return app


def ana_pencere_olustur() -> AnaPencere:
    """
    Ana pencereyi oluşturur

    Returns:
        AnaPencere: Ana pencere instance'ı
    """
    ana_pencere = AnaPencere()
    ana_pencere.show()

    return ana_pencere


def hata_yonet(hata: Exception, logger: Optional[object]) -> None:
    """
    Hata yönetimi ve loglama

    Args:
        hata: Oluşan hata
        logger: Logger instance'ı (None olabilir)
    """
    if isinstance(hata, SontechHatasi):
        _sontechsp_hatasi_isle(hata, logger)
    elif isinstance(hata, EntegrasyonHatasi):
        _entegrasyon_hatasi_isle(hata, logger)
    else:
        _genel_hata_isle(hata, logger)


def _sontechsp_hatasi_isle(hata: SontechHatasi, logger: Optional[object]) -> None:
    """SONTECHSP hatası işler"""
    if logger:
        logger.error(f"SONTECHSP hatası: {hata}")
    print(f"SONTECHSP Hatası: {hata}")
    sys.exit(1)


def _entegrasyon_hatasi_isle(hata: EntegrasyonHatasi, logger: Optional[object]) -> None:
    """Entegrasyon hatası işler"""
    if logger:
        logger.error(f"Entegrasyon hatası: {hata}")
    print(f"Entegrasyon Hatası: {hata}")
    sys.exit(1)


def _genel_hata_isle(hata: Exception, logger: Optional[object]) -> None:
    """Genel hata işler"""
    if logger:
        logger.critical(f"Beklenmeyen hata: {hata}")
        logger.critical(f"Hata detayı: {traceback.format_exc()}")

    print(f"Kritik Hata: {hata}")
    print("Detaylı hata bilgisi için log dosyasını kontrol edin.")
    sys.exit(1)


def uygulama_baslat():
    """Ana uygulama başlatma fonksiyonu (alias)"""
    main()


def merkezi_hata_yakalayici(exc_type, exc_value, exc_traceback):
    """
    Merkezi hata yakalayıcı fonksiyon

    Args:
        exc_type: Exception tipi
        exc_value: Exception değeri
        exc_traceback: Exception traceback
    """
    logger = kayit_al("hata_yakalayici")
    logger.critical(f"Yakalanmamış hata: {exc_type.__name__}: {exc_value}")
    logger.critical(f"Traceback: {''.join(traceback.format_tb(exc_traceback))}")


def main():
    """Ana uygulama başlatma fonksiyonu (bootstrap)"""
    logger = None

    try:
        # Log sistemi kurulumu
        kayit_sistemi = kayit_sistemi_al()
        logger = kayit_al("ana")
        logger.info("SONTECHSP uygulaması başlatılıyor...")

        # PyQt6 uygulama oluştur
        app = uygulama_kur()
        logger.info("PyQt6 uygulama oluşturuldu")

        # Ana pencere oluştur ve göster
        ana_pencere = ana_pencere_olustur()
        logger.info("Ana pencere gösterildi")

        # Uygulama döngüsünü başlat
        logger.info("Uygulama döngüsü başlatılıyor")
        sys.exit(app.exec())

    except Exception as e:
        hata_yonet(e, logger)


if __name__ == "__main__":
    main()
