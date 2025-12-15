# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ana
# Description: SONTECHSP ana uygulama giriş noktası (bootstrap sadece)
# Changelog:
# - İlk oluşturma
# - Kod kalitesi: 120 satır limitine uygun hale getirildi

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
from PyQt6.QtWidgets import QApplication

# SONTECHSP çekirdek modülleri
from sontechsp.uygulama.cekirdek.kayit import log_sistemi, logger_al
from sontechsp.uygulama.cekirdek.hatalar import (
    SONTECHSPHatasi, 
    EntegrasyonHatasi
)

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


def hata_yonet(hata: Exception, logger) -> None:
    """
    Hata yönetimi ve loglama
    
    Args:
        hata: Oluşan hata
        logger: Logger instance'ı
    """
    if isinstance(hata, SONTECHSPHatasi):
        _sontechsp_hatasi_isle(hata, logger)
    elif isinstance(hata, EntegrasyonHatasi):
        _entegrasyon_hatasi_isle(hata, logger)
    else:
        _genel_hata_isle(hata, logger)


def _sontechsp_hatasi_isle(hata: SONTECHSPHatasi, logger) -> None:
    """SONTECHSP hatası işler"""
    if logger:
        logger.error(f"SONTECHSP hatası: {hata}")
    print(f"SONTECHSP Hatası: {hata}")
    sys.exit(1)


def _entegrasyon_hatasi_isle(hata: EntegrasyonHatasi, logger) -> None:
    """Entegrasyon hatası işler"""
    if logger:
        logger.error(f"Entegrasyon hatası: {hata}")
    print(f"Entegrasyon Hatası: {hata}")
    sys.exit(1)


def _genel_hata_isle(hata: Exception, logger) -> None:
    """Genel hata işler"""
    if logger:
        logger.critical(f"Beklenmeyen hata: {hata}")
        logger.critical(f"Hata detayı: {traceback.format_exc()}")
    
    print(f"Kritik Hata: {hata}")
    print("Detaylı hata bilgisi için log dosyasını kontrol edin.")
    sys.exit(1)


def main():
    """Ana uygulama başlatma fonksiyonu (bootstrap)"""
    logger = None
    
    try:
        # Log sistemi kurulumu
        log_sistemi.kur()
        logger = logger_al("ana")
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