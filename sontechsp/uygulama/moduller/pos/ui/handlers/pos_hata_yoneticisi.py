# Version: 0.1.0
# Last Update: 2024-12-19
# Module: pos_hata_yoneticisi
# Description: POS hata yönetimi sistemi - QMessageBox gösterimi ve log entegrasyonu
# Changelog:
# - İlk oluşturma - POS hata yönetimi sistemi

"""
POS Hata Yönetimi Sistemi

POS ekranlarında oluşan hataları yönetir:
- QMessageBox ile kullanıcı bilgilendirmesi
- Log kayıt sistemi entegrasyonu
- Sistem durumu koruma mekanizması
- Hata seviye yönetimi
"""

from typing import Any, Callable, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QWidget

from sontechsp.uygulama.cekirdek.hatalar import (
    BarkodHatasi,
    HataSeviyesi,
    IadeHatasi,
    NetworkHatasi,
    OdemeHatasi,
    POSHatasi,
    SontechHatasi,
    StokHatasi,
    YazdirmaHatasi,
    get_hata_yoneticisi,
)
from sontechsp.uygulama.cekirdek.kayit import kayit_al


class POSHataYoneticisi(QObject):
    """
    POS Hata Yönetimi Sistemi

    Sorumluluklar:
    - Hata yakalama ve işleme
    - QMessageBox ile kullanıcı bilgilendirmesi
    - Log kayıt sistemi entegrasyonu
    - Sistem durumu koruma
    """

    # Sinyaller
    hata_islendi = pyqtSignal(str, str)  # hata_tipi, mesaj
    kritik_hata = pyqtSignal(str)  # kritik hata mesajı
    sistem_durumu_korundu = pyqtSignal()  # sistem durumu korundu

    def __init__(self, parent_widget: Optional[QWidget] = None):
        super().__init__()

        self.parent_widget = parent_widget
        self.logger = kayit_al("pos_hata_yoneticisi")
        self.hata_yoneticisi = get_hata_yoneticisi()

        # Hata işleme ayarları
        self.otomatik_mesaj_goster = True
        self.log_kayit_aktif = True
        self.sistem_durumu_koruma_aktif = True

        # Hata seviye mesaj tipleri
        self.seviye_mesaj_tipleri = {
            HataSeviyesi.DUSUK: QMessageBox.Icon.Information,
            HataSeviyesi.ORTA: QMessageBox.Icon.Warning,
            HataSeviyesi.YUKSEK: QMessageBox.Icon.Critical,
            HataSeviyesi.KRITIK: QMessageBox.Icon.Critical,
        }

        # Sistem durumu koruma fonksiyonları
        self.durum_koruma_fonksiyonlari: Dict[str, Callable] = {}

        self.logger.info("POS hata yöneticisi başlatıldı")

    def hata_yakala(
        self, hata: Exception, kaynak: str = "POS", ek_bilgi: Optional[Dict[str, Any]] = None, mesaj_goster: bool = True
    ) -> None:
        """
        Hatayı yakalar ve işler

        Args:
            hata: Yakalanan hata
            kaynak: Hata kaynağı
            ek_bilgi: Ek bilgi sözlüğü
            mesaj_goster: Kullanıcıya mesaj gösterilsin mi
        """
        try:
            # Hata tipini belirle
            hata_tipi = hata.__class__.__name__
            hata_mesaji = str(hata)

            # Log kaydet
            if self.log_kayit_aktif:
                self._hatayi_logla(hata, kaynak, ek_bilgi)

            # Hata yöneticisine kaydet
            self.hata_yoneticisi.hata_isle(hata, ek_bilgi)

            # Kullanıcı mesajı göster
            if mesaj_goster and self.otomatik_mesaj_goster:
                self._kullanici_mesaji_goster(hata, kaynak)

            # Sistem durumunu koru
            if self.sistem_durumu_koruma_aktif:
                self._sistem_durumu_koru(hata, kaynak)

            # Sinyal gönder
            self.hata_islendi.emit(hata_tipi, hata_mesaji)

            # Kritik hata kontrolü
            if self._kritik_hata_mi(hata):
                self.kritik_hata.emit(hata_mesaji)
                self.logger.critical(f"Kritik POS hatası: {hata_mesaji}")

            self.logger.debug(f"Hata işlendi: {hata_tipi} - {kaynak}")

        except Exception as e:
            # Hata işleme sırasında hata oluştu
            self.logger.error(f"Hata işleme sırasında hata: {e}")
            self._acil_durum_mesaji(str(e))

    def _hatayi_logla(self, hata: Exception, kaynak: str, ek_bilgi: Optional[Dict[str, Any]]) -> None:
        """Hatayı log sistemine kaydeder"""
        hata_detayi = {
            "hata_tipi": hata.__class__.__name__,
            "kaynak": kaynak,
            "mesaj": str(hata),
            "ek_bilgi": ek_bilgi or {},
        }

        # SontechHatasi ise seviyesine göre logla
        if isinstance(hata, SontechHatasi):
            if hata.seviye == HataSeviyesi.DUSUK:
                self.logger.warning(f"POS Hatası [{kaynak}]: {hata}", extra=hata_detayi)
            elif hata.seviye == HataSeviyesi.ORTA:
                self.logger.error(f"POS Hatası [{kaynak}]: {hata}", extra=hata_detayi)
            elif hata.seviye == HataSeviyesi.YUKSEK:
                self.logger.error(f"POS Yüksek Hata [{kaynak}]: {hata}", extra=hata_detayi)
            elif hata.seviye == HataSeviyesi.KRITIK:
                self.logger.critical(f"POS Kritik Hata [{kaynak}]: {hata}", extra=hata_detayi)
        else:
            # Genel hata
            self.logger.error(f"POS Genel Hata [{kaynak}]: {hata}", extra=hata_detayi)

    def _kullanici_mesaji_goster(self, hata: Exception, kaynak: str) -> None:
        """Kullanıcıya hata mesajı gösterir"""
        if not self.parent_widget:
            return

        # Mesaj kutusu oluştur
        msg_box = QMessageBox(self.parent_widget)

        # Hata tipine göre mesaj ayarla
        if isinstance(hata, SontechHatasi):
            msg_box.setIcon(self.seviye_mesaj_tipleri.get(hata.seviye, QMessageBox.Icon.Warning))
            baslik = self._hata_baslik_olustur(hata, kaynak)
            mesaj = self._kullanici_dostu_mesaj_olustur(hata)
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            baslik = f"POS Hatası - {kaynak}"
            mesaj = f"Beklenmeyen bir hata oluştu:\n{str(hata)}"

        msg_box.setWindowTitle(baslik)
        msg_box.setText(mesaj)

        # Detay bilgisi ekle
        if isinstance(hata, SontechHatasi) and hata.ek_bilgi:
            detay = self._detay_mesaji_olustur(hata.ek_bilgi)
            msg_box.setDetailedText(detay)

        # Butonları ayarla
        self._mesaj_butonlari_ayarla(msg_box, hata)

        # Mesajı göster
        msg_box.exec()

    def _hata_baslik_olustur(self, hata: SontechHatasi, kaynak: str) -> str:
        """Hata başlığı oluşturur"""
        seviye_metni = {
            HataSeviyesi.DUSUK: "Bilgi",
            HataSeviyesi.ORTA: "Uyarı",
            HataSeviyesi.YUKSEK: "Hata",
            HataSeviyesi.KRITIK: "Kritik Hata",
        }

        return f"POS {seviye_metni.get(hata.seviye, 'Hata')} - {kaynak}"

    def _kullanici_dostu_mesaj_olustur(self, hata: SontechHatasi) -> str:
        """Kullanıcı dostu hata mesajı oluşturur"""
        # Özel hata tiplerini kullanıcı dostu mesajlara çevir
        if isinstance(hata, BarkodHatasi):
            return f"Barkod okuma hatası:\n{hata.mesaj}\n\nLütfen barkodu tekrar okutun."

        elif isinstance(hata, StokHatasi):
            return f"Stok hatası:\n{hata.mesaj}\n\nStok durumunu kontrol edin."

        elif isinstance(hata, OdemeHatasi):
            return f"Ödeme hatası:\n{hata.mesaj}\n\nÖdeme işlemini tekrar deneyin."

        elif isinstance(hata, IadeHatasi):
            return f"İade hatası:\n{hata.mesaj}\n\nİade işlemini kontrol edin."

        elif isinstance(hata, NetworkHatasi):
            return f"Bağlantı hatası:\n{hata.mesaj}\n\nAğ bağlantınızı kontrol edin."

        elif isinstance(hata, YazdirmaHatasi):
            return f"Yazdırma hatası:\n{hata.mesaj}\n\nYazıcı durumunu kontrol edin."

        else:
            return hata.mesaj

    def _detay_mesaji_olustur(self, ek_bilgi: Dict[str, Any]) -> str:
        """Detay mesajı oluşturur"""
        detaylar = []
        for anahtar, deger in ek_bilgi.items():
            detaylar.append(f"{anahtar}: {deger}")

        return "\n".join(detaylar)

    def _mesaj_butonlari_ayarla(self, msg_box: QMessageBox, hata: Exception) -> None:
        """Mesaj kutusu butonlarını ayarlar"""
        if isinstance(hata, SontechHatasi):
            if hata.seviye == HataSeviyesi.KRITIK:
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Help)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            else:
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        else:
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Retry)

    def _sistem_durumu_koru(self, hata: Exception, kaynak: str) -> None:
        """Sistem durumunu korur"""
        try:
            # Kaynak bazlı durum koruma
            if kaynak in self.durum_koruma_fonksiyonlari:
                koruma_fonksiyonu = self.durum_koruma_fonksiyonlari[kaynak]
                koruma_fonksiyonu(hata)

            # Genel durum koruma
            self._genel_durum_koruma(hata, kaynak)

            self.sistem_durumu_korundu.emit()
            self.logger.debug(f"Sistem durumu korundu: {kaynak}")

        except Exception as e:
            self.logger.error(f"Sistem durumu koruma hatası: {e}")

    def _genel_durum_koruma(self, hata: Exception, kaynak: str) -> None:
        """Genel sistem durumu koruma işlemleri"""
        # Kritik hatalar için özel işlemler
        if self._kritik_hata_mi(hata):
            self.logger.critical("Kritik hata nedeniyle sistem durumu korunuyor")
            # İleride: Mevcut işlemleri kaydet, güvenli duruma geç

        # Ağ hatası için offline moda geçiş
        if isinstance(hata, NetworkHatasi):
            self.logger.warning("Ağ hatası nedeniyle offline moda geçiliyor")
            # İleride: Offline kuyruk sistemini aktifleştir

    def _kritik_hata_mi(self, hata: Exception) -> bool:
        """Hatanın kritik olup olmadığını kontrol eder"""
        if isinstance(hata, SontechHatasi):
            return hata.seviye == HataSeviyesi.KRITIK

        # Belirli hata tiplerini kritik olarak değerlendir
        kritik_tipler = (MemoryError, SystemError, OSError)
        return isinstance(hata, kritik_tipler)

    def _acil_durum_mesaji(self, mesaj: str) -> None:
        """Acil durum mesajı gösterir"""
        if self.parent_widget:
            QMessageBox.critical(
                self.parent_widget, "Sistem Hatası", f"Kritik sistem hatası:\n{mesaj}\n\nUygulama yeniden başlatılmalı."
            )

    def durum_koruma_fonksiyonu_ekle(self, kaynak: str, fonksiyon: Callable) -> None:
        """Kaynak bazlı durum koruma fonksiyonu ekler"""
        self.durum_koruma_fonksiyonlari[kaynak] = fonksiyon
        self.logger.debug(f"Durum koruma fonksiyonu eklendi: {kaynak}")

    def ayarlari_guncelle(self, **ayarlar) -> None:
        """Hata yöneticisi ayarlarını günceller"""
        if "otomatik_mesaj_goster" in ayarlar:
            self.otomatik_mesaj_goster = ayarlar["otomatik_mesaj_goster"]

        if "log_kayit_aktif" in ayarlar:
            self.log_kayit_aktif = ayarlar["log_kayit_aktif"]

        if "sistem_durumu_koruma_aktif" in ayarlar:
            self.sistem_durumu_koruma_aktif = ayarlar["sistem_durumu_koruma_aktif"]

        self.logger.debug("Hata yöneticisi ayarları güncellendi")

    def hata_istatistikleri(self) -> Dict[str, Any]:
        """Hata istatistiklerini döndürür"""
        return self.hata_yoneticisi.hata_istatistikleri()

    def son_hatalari_getir(self, sayi: int = 10) -> list:
        """Son hataları getirir"""
        return self.hata_yoneticisi.son_hatalari_getir(sayi)

    def hata_sayaclarini_sifirla(self) -> None:
        """Hata sayaçlarını sıfırlar"""
        self.hata_yoneticisi.hata_sayaclarini_sifirla()
        self.logger.info("POS hata sayaçları sıfırlandı")

    def test_hata_goster(self, hata_tipi: str = "test") -> None:
        """Test amaçlı hata gösterir"""
        if hata_tipi == "barkod":
            test_hata = BarkodHatasi("Test barkod hatası", "123456789")
        elif hata_tipi == "stok":
            test_hata = StokHatasi("Test stok hatası", urun_id=1, mevcut_stok=0, talep_edilen=5)
        elif hata_tipi == "odeme":
            test_hata = OdemeHatasi("Test ödeme hatası", odeme_turu="nakit", tutar=100.0)
        elif hata_tipi == "network":
            test_hata = NetworkHatasi("Test ağ hatası", endpoint="localhost:8000")
        else:
            test_hata = POSHatasi("Test POS hatası", islem_tipi="test")

        self.hata_yakala(test_hata, "Test")
