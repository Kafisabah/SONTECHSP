# Version: 0.1.0
# Last Update: 2025-12-19
# Module: ana_pencere
# Description: SONTECHSP PyQt6 ana pencere sınıfı (sadece mantık)
# Changelog:
# - İlk oluşturma
# - Kod kalitesi: UI bileşenleri ayrı dosyaya taşındı
# - Modül ekranı ekleme metodu tamamlandı
# - Aktif modül kodu alma metodu eklendi
# - POS menü seçimi metodu eklendi (test desteği)
# - closeEvent metodu eklendi (kaynak temizleme)
# - POSYeniEkranWrapper başlatma sırası düzeltildi

"""
SONTECHSP Ana Pencere Sınıfı

PyQt6 tabanlı ana pencere mantığı.
UI bileşenleri ayrı dosyada tutulur.

Sorumluluklar:
- Ana pencere mantığı
- Modül navigasyonu
- Oturum yönetimi
- Ekran geçişleri
"""

from typing import Dict, Optional, Any
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from sontechsp.uygulama.cekirdek.kayit import kayit_al
from sontechsp.uygulama.cekirdek.oturum import oturum_baglamini_al
from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran
from sontechsp.uygulama.arayuz.ana_pencere_ui import (
    ana_ui_kur,
    menu_kur,
    toolbar_kur,
    statusbar_kur,
    placeholder_ekran_olustur,
)


class AnaPencere(QMainWindow):
    """
    SONTECHSP ana pencere sınıfı

    Sol menü + içerik alanı yapısını sağlar.
    Modül ekranları arasında navigasyon yapar.
    """

    # Sinyaller
    modul_secildi = pyqtSignal(str)  # Modül seçildiğinde
    oturum_degisti = pyqtSignal(dict)  # Oturum değiştiğinde

    def __init__(self):
        super().__init__()
        self.logger = kayit_al("ana_pencere")
        self.oturum_baglami = oturum_baglamini_al()

        # Modül ekranları saklayıcı
        self._modul_ekranlari: Dict[str, TabanEkran] = {}

        # UI kurulumu (UI dosyasından)
        ana_ui_kur(self)
        menu_kur(self)
        toolbar_kur(self)
        statusbar_kur(self)
        self._sinyalleri_bagla()

        # Oturum durumu timer'ı
        self._oturum_timer = QTimer()
        self._oturum_timer.timeout.connect(self._oturum_durumunu_kontrol_et)
        self._oturum_timer.start(5000)  # 5 saniyede bir kontrol

        self.logger.info("Ana pencere oluşturuldu")

    def _sinyalleri_bagla(self):
        """Sinyal-slot bağlantılarını kurar"""
        self.modul_menusu.currentRowChanged.connect(self._modul_secildi)
        self.oturum_degisti.connect(self._oturum_bilgisini_guncelle)

    def _modul_secildi(self, index: int):
        """Modül seçildiğinde çağrılır"""
        if index >= 0:
            item = self.modul_menusu.item(index)
            modul_kodu = item.data(Qt.ItemDataRole.UserRole)
            modul_adi = item.text()

            self.logger.info(f"Modül seçildi: {modul_adi} ({modul_kodu})")

            # Modül ekranını yükle
            self._modul_ekranini_yukle(modul_kodu, modul_adi)

            # Sinyal gönder
            self.modul_secildi.emit(modul_kodu)

    def _modul_ekranini_yukle(self, modul_kodu: str, modul_adi: str):
        """Modül ekranını yükler"""
        # Önce cache'de var mı kontrol et
        if modul_kodu in self._modul_ekranlari:
            ekran = self._modul_ekranlari[modul_kodu]
            self.icerik_alani.setCurrentWidget(ekran)
            self.statusbar.showMessage(f"{modul_adi} modülü")
            return

        # Modül koduna göre gerçek ekran oluştur
        ekran = self._gercek_modul_ekrani_olustur(modul_kodu, modul_adi)

        # Cache'e ekle
        self._modul_ekranlari[modul_kodu] = ekran

        # İçerik alanına ekle
        self.icerik_alani.addWidget(ekran)
        self.icerik_alani.setCurrentWidget(ekran)

        self.statusbar.showMessage(f"{modul_adi} modülü")
        self.logger.debug(f"Modül ekranı yüklendi: {modul_kodu}")

    def _gercek_modul_ekrani_olustur(self, modul_kodu: str, modul_adi: str) -> TabanEkran:
        """
        Modül koduna göre gerçek ekran oluşturur

        Args:
            modul_kodu: Modül kodu
            modul_adi: Modül adı

        Returns:
            TabanEkran: Oluşturulan ekran widget'ı
        """
        try:
            if modul_kodu == "pos":
                # POS modülü için yeni tasarım ekranını oluştur
                self.logger.info("POS yeni ekran tasarımı yükleniyor...")

                try:
                    from sontechsp.uygulama.arayuz.ekranlar.pos.pos_satis_ekrani import POSSatisEkrani
                    from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran

                    # Yeni POS ekranını TabanEkran wrapper'ı ile sar
                    class POSYeniEkranWrapper(TabanEkran):
                        def __init__(self):
                            # Önce POS ekranını oluştur
                            self.pos_ekrani = POSSatisEkrani()
                            # Sonra TabanEkran'ı başlat
                            super().__init__("POS Satış - Yeni Tasarım")

                        def _icerik_olustur(self):
                            """İçerik oluşturur"""
                            self.icerik_layout.addWidget(self.pos_ekrani)

                        def yenile(self):
                            """Ekranı yeniler"""
                            if hasattr(self.pos_ekrani, "yenile"):
                                self.pos_ekrani.yenile()

                        def temizle(self):
                            """Ekranı temizler"""
                            if hasattr(self.pos_ekrani, "temizle"):
                                self.pos_ekrani.temizle()

                    self.logger.info("POS yeni ekran tasarımı başarıyla yüklendi")
                    return POSYeniEkranWrapper()

                except ImportError as yeni_ekran_hatasi:
                    self.logger.warning(f"POS yeni ekran yüklenemedi: {yeni_ekran_hatasi}")
                    self.logger.info("Arşivlenmiş eski POS ekranına geçiliyor...")

                    # Arşivlenmiş eski POS ekranını dene
                    try:
                        from arsiv.pos_eski_ui.pos_ana_ekran import POSAnaEkran

                        self.logger.info("Arşivlenmiş POS ekranı yüklendi")
                        return POSAnaEkran()
                    except ImportError as arsiv_hatasi:
                        self.logger.error(f"Arşivlenmiş POS ekranı da yüklenemedi: {arsiv_hatasi}")
                        # Son çare olarak placeholder döndür
                        return placeholder_ekran_olustur("POS Satış")

            else:
                # Diğer modüller için placeholder
                return placeholder_ekran_olustur(modul_adi)

        except ImportError as e:
            self.logger.warning(f"Modül ekranı yüklenemedi ({modul_kodu}): {e}")
            # Hata durumunda placeholder döndür
            return placeholder_ekran_olustur(modul_adi)
        except Exception as e:
            self.logger.error(f"Modül ekranı oluşturulurken hata ({modul_kodu}): {e}")
            # Hata durumunda placeholder döndür
            return placeholder_ekran_olustur(modul_adi)

    def _oturum_durumunu_kontrol_et(self):
        """Oturum durumunu kontrol eder"""
        if self.oturum_baglami and self.oturum_baglami.aktif_mi():
            oturum_bilgisi = {
                "kullanici_id": self.oturum_baglami.kullanici_id,
                "magaza_id": self.oturum_baglami.magaza_id,
                "terminal_id": self.oturum_baglami.terminal_id,
            }
            self.oturum_degisti.emit(oturum_bilgisi)

    def _oturum_bilgisini_guncelle(self, oturum_bilgisi: Dict[str, Any]):
        """Oturum bilgisini günceller"""
        if oturum_bilgisi.get("kullanici_id"):
            kullanici_text = f"Kullanıcı: {oturum_bilgisi['kullanici_id']}"
            if oturum_bilgisi.get("magaza_id"):
                kullanici_text += f" | Mağaza: {oturum_bilgisi['magaza_id']}"
            if oturum_bilgisi.get("terminal_id"):
                kullanici_text += f" | Terminal: {oturum_bilgisi['terminal_id']}"

            self.oturum_label.setText(kullanici_text)
        else:
            self.oturum_label.setText("Oturum: Yok")

    def modul_ekrani_ekle(self, modul_kodu: str, ekran: TabanEkran):
        """
        Modül ekranı ekler

        Args:
            modul_kodu: Modül kodu
            ekran: Ekran widget'ı
        """
        self._modul_ekranlari[modul_kodu] = ekran
        self.icerik_alani.addWidget(ekran)
        self.logger.debug(f"Modül ekranı eklendi: {modul_kodu}")

    def aktif_modul_kodunu_al(self) -> Optional[str]:
        """
        Aktif modül kodunu döndürür

        Returns:
            Optional[str]: Aktif modül kodu
        """
        secili_index = self.modul_menusu.currentRow()
        if secili_index >= 0:
            item = self.modul_menusu.item(secili_index)
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def pos_menusunu_sec(self) -> bool:
        """
        POS menüsünü seçer (test için)

        Returns:
            bool: Seçim başarılı ise True
        """
        for i in range(self.modul_menusu.count()):
            item = self.modul_menusu.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == "pos":
                self.modul_menusu.setCurrentRow(i)
                return True
        return False

    def closeEvent(self, event):
        """Pencere kapatılırken çağrılır"""
        self.logger.info("Ana pencere kapatılıyor")

        # POS ekranı varsa sepet verilerini kaydet
        self._pos_sepet_verilerini_kaydet()

        # Timer'ı durdur
        self._oturum_timer.stop()

        # Tüm modül ekranlarını temizle
        self._modul_ekranlarini_temizle()

        event.accept()

    def _pos_sepet_verilerini_kaydet(self):
        """POS ekranı sepet verilerini güvenli şekilde saklar"""
        try:
            # Aktif POS ekranını bul
            pos_ekrani = None
            for modul_kodu, ekran in self._modul_ekranlari.items():
                if modul_kodu == "pos":
                    pos_ekrani = ekran
                    break

            if pos_ekrani:
                # Yeni POS ekranı ise
                if hasattr(pos_ekrani, "pos_ekrani"):
                    yeni_pos = pos_ekrani.pos_ekrani
                    if hasattr(yeni_pos, "sepet_modeli") and yeni_pos.sepet_modeli.rowCount() > 0:
                        self.logger.info("POS sepet verileri kaydediliyor...")
                        # Sepet verilerini geçici dosyaya kaydet
                        import json
                        import os
                        from datetime import datetime

                        sepet_verileri = []
                        for i in range(yeni_pos.sepet_modeli.rowCount()):
                            oge = yeni_pos.sepet_modeli.sepet_ogeleri[i]
                            sepet_verileri.append(
                                {
                                    "barkod": oge.barkod,
                                    "urun_adi": oge.urun_adi,
                                    "adet": oge.adet,
                                    "birim_fiyat": str(oge.birim_fiyat),
                                    "toplam_fiyat": str(oge.toplam_fiyat),
                                    "indirim_orani": oge.indirim_orani,
                                }
                            )

                        # Geçici klasör oluştur
                        temp_dir = os.path.join(os.getcwd(), "temp")
                        os.makedirs(temp_dir, exist_ok=True)

                        # Sepet dosyasını kaydet
                        sepet_dosyasi = os.path.join(temp_dir, "pos_sepet_backup.json")
                        with open(sepet_dosyasi, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "sepet_verileri": sepet_verileri,
                                    "kayit_zamani": datetime.now().isoformat(),
                                    "musteri": getattr(yeni_pos, "mevcut_musteri", None),
                                },
                                f,
                                ensure_ascii=False,
                                indent=2,
                            )

                        self.logger.info(f"POS sepet verileri kaydedildi: {len(sepet_verileri)} ürün")

                # Eski POS ekranı ise
                elif hasattr(pos_ekrani, "temizle"):
                    pos_ekrani.temizle()

        except Exception as e:
            self.logger.error(f"POS sepet verilerini kaydetme hatası: {e}")

    def _modul_ekranlarini_temizle(self):
        """Tüm modül ekranlarını temizler"""
        try:
            for modul_kodu, ekran in self._modul_ekranlari.items():
                if hasattr(ekran, "temizle"):
                    try:
                        ekran.temizle()
                        self.logger.debug(f"Modül ekranı temizlendi: {modul_kodu}")
                    except Exception as e:
                        self.logger.error(f"Modül ekranı temizleme hatası ({modul_kodu}): {e}")

            self._modul_ekranlari.clear()

        except Exception as e:
            self.logger.error(f"Modül ekranları temizleme hatası: {e}")

    def pos_yeni_ekran_yukle(self) -> bool:
        """
        POS yeni ekranını manuel olarak yükler

        Returns:
            bool: Yükleme başarılı ise True
        """
        try:
            # Mevcut POS ekranını kaldır
            if "pos" in self._modul_ekranlari:
                eski_ekran = self._modul_ekranlari["pos"]
                self.icerik_alani.removeWidget(eski_ekran)
                if hasattr(eski_ekran, "temizle"):
                    eski_ekran.temizle()
                eski_ekran.deleteLater()
                del self._modul_ekranlari["pos"]

            # Yeni POS ekranını yükle
            yeni_ekran = self._gercek_modul_ekrani_olustur("pos", "POS Satış")
            self._modul_ekranlari["pos"] = yeni_ekran
            self.icerik_alani.addWidget(yeni_ekran)

            # POS menüsü seçili ise yeni ekranı göster
            if self.aktif_modul_kodunu_al() == "pos":
                self.icerik_alani.setCurrentWidget(yeni_ekran)

            self.logger.info("POS yeni ekran manuel yükleme başarılı")
            return True

        except Exception as e:
            self.logger.error(f"POS yeni ekran manuel yükleme hatası: {e}")
            return False
