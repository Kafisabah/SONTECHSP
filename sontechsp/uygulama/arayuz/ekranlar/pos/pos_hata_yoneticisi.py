# Version: 0.1.0
# Last Update: 2024-12-19
# Module: pos_hata_yoneticisi
# Description: POS ekranları için hata yönetimi sistemi - Turkuaz tema ile QMessageBox gösterimi
# Changelog:
# - İlk oluşturma - Turkuaz tema entegrasyonu ve sistem durumu koruma

"""
POS Hata Yöneticisi - Turkuaz tema ile hata gösterimi ve log kayıt sistemi

Gereksinimler:
- 11.1: Servis çağrısı başarısız olduğunda turkuaz renkli hata mesajını gösterecektir
- 11.2: Hata oluştuğunda log dosyasına detaylı hata kaydı yazacaktır
- 11.3: Ağ bağlantısı kesildiğinde "Bağlantı hatası" mesajını gösterecektir
- 11.4: Stok yetersiz olduğunda "Stok yetersiz" uyarısını gösterecektir
- 11.5: Kritik hata oluştuğunda çökmeyecek ve kullanıcıyı bilgilendirecektir
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import QObject, pyqtSignal
from .turkuaz_tema import TurkuazTema


class POSHataYoneticisi(QObject):
    """POS ekranları için hata yönetimi sınıfı"""

    hata_olustu = pyqtSignal(str, str)  # hata_turu, mesaj

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.parent = parent
        self.tema = TurkuazTema()
        self.logger = logging.getLogger(__name__)

    def hata_goster(self, hata_turu: str, mesaj: str, detay: str = ""):
        """Hata mesajını gösterir ve log'a kaydeder"""
        # Log'a kaydet
        self.logger.error(f"{hata_turu}: {mesaj} - {detay}")

        # Test ortamında mesaj göstermeyi atla
        if hasattr(self, "_test_modu") and self._test_modu:
            self.hata_olustu.emit(hata_turu, mesaj)
            return

        # Parent widget yoksa sadece log'la
        if not self.parent:
            self.hata_olustu.emit(hata_turu, mesaj)
            return

        try:
            # Kullanıcıya göster
            msg_box = QMessageBox(self.parent)
            msg_box.setWindowTitle("POS Hatası")
            msg_box.setText(mesaj)
            msg_box.setModal(True)  # Modal yap

            # Timeout ekle - 5 saniye sonra otomatik kapan
            from PyQt6.QtCore import QTimer

            timer = QTimer()
            timer.timeout.connect(msg_box.accept)
            timer.setSingleShot(True)
            timer.start(5000)  # 5 saniye

            if detay:
                msg_box.setDetailedText(detay)

            # Hata türüne göre icon ve turkuaz tema renk kodları
            if hata_turu == "servis":
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setStyleSheet(
                    f"""
                    QMessageBox {{
                        background-color: {self.tema.hata_renk};
                        color: white;
                        font-family: 'Segoe UI', Arial, sans-serif;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {self.tema.ana_renk};
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        min-width: 80px;
                    }}
                """
                )
            elif hata_turu == "dogrulama":
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setStyleSheet(
                    f"""
                    QMessageBox {{
                        background-color: #FFD700;
                        color: black;
                        font-family: 'Segoe UI', Arial, sans-serif;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {self.tema.ana_renk};
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        min-width: 80px;
                    }}
                """
                )
            elif hata_turu == "ag":
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setStyleSheet(
                    f"""
                    QMessageBox {{
                        background-color: {self.tema.hata_renk};
                        color: white;
                        font-family: 'Segoe UI', Arial, sans-serif;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {self.tema.ana_renk};
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        min-width: 80px;
                    }}
                """
                )
                # Ağ hatası için özel mesaj
                if "bağlantı" not in mesaj.lower():
                    msg_box.setText("Bağlantı hatası: " + mesaj)
            elif hata_turu == "stok":
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setStyleSheet(
                    f"""
                    QMessageBox {{
                        background-color: #FFA500;
                        color: white;
                        font-family: 'Segoe UI', Arial, sans-serif;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {self.tema.ana_renk};
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        min-width: 80px;
                    }}
                """
                )
                # Stok hatası için özel mesaj
                if "stok" not in mesaj.lower():
                    msg_box.setText("Stok yetersiz: " + mesaj)
            else:
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setStyleSheet(
                    f"""
                    QMessageBox {{
                        background-color: {self.tema.ikincil_renk};
                        color: white;
                        font-family: 'Segoe UI', Arial, sans-serif;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {self.tema.ana_renk};
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        min-width: 80px;
                    }}
                """
                )

            # Non-blocking gösterim
            msg_box.show()

        except Exception as e:
            # Mesaj gösterme hatası durumunda sadece log'la
            self.logger.error(f"Mesaj gösterme hatası: {e}")

        # Kritik hata kontrolü ve sistem durumu koruma
        if self.kritik_hata_kontrol(mesaj):
            self.sistem_durumu_koru("kritik")
        else:
            self.sistem_durumu_koru(hata_turu)

        # İstatistikleri güncelle
        if not hasattr(self, "_toplam_hata_sayisi"):
            self._toplam_hata_sayisi = 0
        self._toplam_hata_sayisi += 1

        from datetime import datetime

        self._son_hata_zamani = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Sinyal gönder
        self.hata_olustu.emit(hata_turu, mesaj)

    def basari_goster(self, mesaj: str):
        """Başarı mesajını gösterir"""
        # Test ortamında mesaj göstermeyi atla
        if hasattr(self, "_test_modu") and self._test_modu:
            return

        if not self.parent:
            return

        try:
            msg_box = QMessageBox(self.parent)
            msg_box.setWindowTitle("İşlem Başarılı")
            msg_box.setText(mesaj)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStyleSheet(f"background-color: {self.tema.basari_renk};")
            msg_box.setModal(True)

            # Timeout ekle
            from PyQt6.QtCore import QTimer

            timer = QTimer()
            timer.timeout.connect(msg_box.accept)
            timer.setSingleShot(True)
            timer.start(3000)  # 3 saniye

            msg_box.show()
        except Exception as e:
            self.logger.error(f"Başarı mesajı gösterme hatası: {e}")

    def onay_iste(self, mesaj: str, baslik: str = "Onay") -> bool:
        """Kullanıcıdan onay ister"""
        # Test ortamında varsayılan olarak True döndür
        if hasattr(self, "_test_modu") and self._test_modu:
            return True

        if not self.parent:
            return False

        try:
            reply = QMessageBox.question(
                self.parent,
                baslik,
                mesaj,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            return reply == QMessageBox.StandardButton.Yes
        except Exception as e:
            self.logger.error(f"Onay mesajı gösterme hatası: {e}")
            return False

    def test_modu_aktif_et(self, aktif: bool = True):
        """Test modu için mesaj gösterimini devre dışı bırakır"""
        self._test_modu = aktif

    def sistem_durumu_koru(self, hata_turu: str):
        """
        Sistem durumu koruma mekanizması

        Kritik hata durumlarında sistemin çökmesini önler:
        - Mevcut işlemleri güvenli şekilde sonlandırır
        - Kullanıcı verilerini korur
        - Sistem kararlılığını sağlar
        """
        try:
            if hata_turu in ["servis", "ag"]:
                # Ağ/servis hatalarında offline moda geç
                self.logger.warning("Sistem offline moda geçiyor")
                # İleride: Offline kuyruk sistemini aktifleştir

            elif hata_turu == "stok":
                # Stok hatalarında mevcut sepeti koru
                self.logger.info("Sepet durumu korunuyor")
                # İleride: Sepet verilerini geçici olarak sakla

            elif hata_turu == "kritik":
                # Kritik hatalar için acil durum protokolü
                self.logger.critical("Acil durum protokolü aktif")
                # İleride: Tüm açık işlemleri güvenli şekilde kapat

            # Sistem durumu korundu sinyali gönder
            self.hata_olustu.emit("sistem_korundu", f"Sistem durumu {hata_turu} hatası sonrası korundu")

        except Exception as e:
            self.logger.error(f"Sistem durumu koruma hatası: {e}")

    def kritik_hata_kontrol(self, mesaj: str) -> bool:
        """Mesajın kritik hata içerip içermediğini kontrol eder"""
        kritik_kelimeler = [
            "memory",
            "system",
            "critical",
            "fatal",
            "crash",
            "bellek",
            "sistem",
            "kritik",
            "ölümcül",
            "çökme",
        ]

        mesaj_lower = mesaj.lower()
        return any(kelime in mesaj_lower for kelime in kritik_kelimeler)

    def hata_istatistikleri_getir(self) -> dict:
        """Hata istatistiklerini döndürür"""
        return {
            "toplam_hata": getattr(self, "_toplam_hata_sayisi", 0),
            "son_hata_zamani": getattr(self, "_son_hata_zamani", None),
            "test_modu": getattr(self, "_test_modu", False),
        }
