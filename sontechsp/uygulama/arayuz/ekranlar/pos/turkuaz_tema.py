# Version: 0.3.0
# Last Update: 2024-12-19
# Module: turkuaz_tema
# Description: POS ekranları için turkuaz renk teması ve QSS stilleri - Tamamlanmış stil sistemi
# Changelog:
# - İlk oluşturma
# - Kapsamlı QSS stilleri eklendi, büyük butonlar, artırılmış satır yüksekliği, QFrame kartlar
# - Tema uygulama iyileştirmeleri, widget stil sınıfları, animasyon efektleri

"""
Turkuaz Tema - POS ekranları için renk teması ve stil tanımları
Gereksinimler 9.1, 9.2, 9.3, 9.4, 9.5 için kapsamlı stil sistemi
"""

from dataclasses import dataclass
from typing import Dict, Optional

from PyQt6.QtWidgets import QApplication


@dataclass
class TurkuazTema:
    """Turkuaz renk teması sabitleri"""

    # Ana renkler
    ana_renk: str = "#20B2AA"  # Turkuaz
    ikincil_renk: str = "#708090"  # Slate Gray
    arka_plan: str = "#F8F8FF"  # Ghost White
    vurgu_renk: str = "#48D1CC"  # Medium Turquoise
    hata_renk: str = "#FF6347"  # Tomato
    basari_renk: str = "#32CD32"  # Lime Green

    # Ek renkler
    koyu_turkuaz: str = "#008B8B"  # Dark Cyan
    acik_gri: str = "#F5F5F5"  # White Smoke
    orta_gri: str = "#D3D3D3"  # Light Gray
    koyu_gri: str = "#696969"  # Dim Gray
    beyaz: str = "#FFFFFF"  # White
    siyah: str = "#000000"  # Black

    @classmethod
    def qss_stilleri(cls) -> str:
        """Kapsamlı QSS stil tanımlarını döndürür"""
        return f"""
        /* ===== ANA POS EKRANI ===== */
        POSSatisEkrani {{
            background-color: {cls.arka_plan};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }}

        /* ===== ÜST BAR ===== */
        UstBar {{
            background-color: {cls.ana_renk};
            border-bottom: 3px solid {cls.vurgu_renk};
            padding: 12px;
            min-height: 70px;
        }}

        UstBar QLineEdit {{
            background-color: {cls.beyaz};
            border: 2px solid {cls.orta_gri};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            min-height: 35px;
        }}

        UstBar QLineEdit:focus {{
            border-color: {cls.vurgu_renk};
            background-color: {cls.acik_gri};
        }}

        UstBar QComboBox {{
            background-color: {cls.beyaz};
            border: 2px solid {cls.orta_gri};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            min-height: 35px;
            min-width: 200px;
        }}

        UstBar QComboBox:hover {{
            border-color: {cls.vurgu_renk};
        }}

        UstBar QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        UstBar QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.koyu_gri};
        }}

        UstBar QLabel {{
            color: {cls.beyaz};
            font-size: 14px;
            font-weight: bold;
        }}

        UstBar QPushButton {{
            background-color: {cls.beyaz};
            color: {cls.ana_renk};
            border: 2px solid {cls.ana_renk};
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: bold;
            min-height: 40px;
            min-width: 120px;
        }}

        UstBar QPushButton:hover {{
            background-color: {cls.vurgu_renk};
            color: {cls.beyaz};
        }}

        UstBar QPushButton:pressed {{
            background-color: {cls.koyu_turkuaz};
        }}

        /* ===== SEPET TABLOSU ===== */
        QTableView {{
            background-color: {cls.beyaz};
            border: 2px solid {cls.orta_gri};
            border-radius: 10px;
            gridline-color: {cls.acik_gri};
            selection-background-color: {cls.vurgu_renk};
            font-size: 13px;
        }}

        QTableView::item {{
            padding: 12px 8px;
            min-height: 45px;
            border-bottom: 1px solid {cls.acik_gri};
        }}

        QTableView::item:selected {{
            background-color: {cls.vurgu_renk};
            color: {cls.beyaz};
            font-weight: bold;
        }}

        QTableView::item:hover {{
            background-color: {cls.acik_gri};
        }}

        QHeaderView::section {{
            background-color: {cls.ana_renk};
            color: {cls.beyaz};
            padding: 12px 8px;
            border: none;
            font-size: 14px;
            font-weight: bold;
            min-height: 40px;
        }}

        QHeaderView::section:first {{
            border-top-left-radius: 8px;
        }}

        QHeaderView::section:last {{
            border-top-right-radius: 8px;
        }}

        /* ===== ÖDEME PANELİ ===== */
        OdemePaneli {{
            background-color: {cls.beyaz};
            border: 2px solid {cls.orta_gri};
            border-radius: 10px;
            padding: 15px;
        }}

        /* Genel Toplam Göstergesi - Gereksinim 9.5 */
        QLabel#genel-toplam {{
            font-size: 28px;
            font-weight: bold;
            color: {cls.ana_renk};
            background-color: {cls.acik_gri};
            border: 3px solid {cls.ana_renk};
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            min-height: 60px;
        }}

        /* Ara toplam, indirim, KDV göstergeleri */
        QLabel.ara-toplam {{
            font-size: 16px;
            font-weight: bold;
            color: {cls.koyu_gri};
            padding: 8px;
        }}

        /* Ödeme Butonları - Gereksinim 9.2 */
        QPushButton.odeme-buton {{
            background-color: {cls.ana_renk};
            color: {cls.beyaz};
            border: none;
            border-radius: 10px;
            padding: 18px 20px;
            font-size: 16px;
            font-weight: bold;
            min-height: 55px;
            min-width: 140px;
            margin: 4px;
        }}

        QPushButton.odeme-buton:hover {{
            background-color: {cls.vurgu_renk};
            transform: scale(1.02);
        }}

        QPushButton.odeme-buton:pressed {{
            background-color: {cls.koyu_turkuaz};
        }}

        QPushButton.odeme-buton:disabled {{
            background-color: {cls.orta_gri};
            color: {cls.koyu_gri};
        }}

        /* Nakit ödeme alanı */
        QWidget.nakit-alan {{
            background-color: {cls.acik_gri};
            border: 2px solid {cls.ana_renk};
            border-radius: 8px;
            padding: 10px;
        }}

        /* ===== HIZLI İŞLEM ŞERİDİ ===== */
        HizliIslemSeridi {{
            background-color: {cls.ikincil_renk};
            border-top: 3px solid {cls.ana_renk};
            padding: 12px;
            min-height: 70px;
        }}

        /* Hızlı İşlem Butonları - Gereksinim 9.2 */
        QPushButton.hizli-islem {{
            background-color: {cls.ikincil_renk};
            color: {cls.beyaz};
            border: 2px solid {cls.ana_renk};
            border-radius: 8px;
            padding: 12px 18px;
            font-size: 13px;
            font-weight: bold;
            min-width: 120px;
            min-height: 45px;
            margin: 2px;
        }}

        QPushButton.hizli-islem:hover {{
            background-color: {cls.ana_renk};
            border-color: {cls.vurgu_renk};
        }}

        QPushButton.hizli-islem:pressed {{
            background-color: {cls.koyu_turkuaz};
        }}

        /* ===== HIZLI ÜRÜNLER SEKMESİ ===== */
        HizliUrunlerSekmesi {{
            background-color: {cls.beyaz};
        }}

        /* Hızlı ürün butonları */
        QPushButton.hizli-urun {{
            background-color: {cls.acik_gri};
            color: {cls.koyu_gri};
            border: 2px solid {cls.orta_gri};
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
            font-weight: bold;
            min-height: 60px;
            min-width: 80px;
        }}

        QPushButton.hizli-urun:hover {{
            background-color: {cls.vurgu_renk};
            color: {cls.beyaz};
            border-color: {cls.ana_renk};
        }}

        QPushButton.hizli-urun:pressed {{
            background-color: {cls.ana_renk};
        }}

        /* ===== QFRAME KARTLAR - Gereksinim 9.4 ===== */
        QFrame.kart {{
            background-color: {cls.beyaz};
            border: 2px solid {cls.orta_gri};
            border-radius: 12px;
            padding: 15px;
            margin: 8px;
        }}

        QFrame.kart:hover {{
            border-color: {cls.vurgu_renk};
            box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
        }}

        /* ===== TAB WİDGET ===== */
        QTabWidget::pane {{
            border: 2px solid {cls.orta_gri};
            border-radius: 8px;
            background-color: {cls.beyaz};
        }}

        QTabBar::tab {{
            background-color: {cls.acik_gri};
            color: {cls.koyu_gri};
            border: 2px solid {cls.orta_gri};
            border-bottom: none;
            border-radius: 8px 8px 0px 0px;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: bold;
            min-width: 120px;
        }}

        QTabBar::tab:selected {{
            background-color: {cls.ana_renk};
            color: {cls.beyaz};
            border-color: {cls.ana_renk};
        }}

        QTabBar::tab:hover {{
            background-color: {cls.vurgu_renk};
            color: {cls.beyaz};
        }}

        /* ===== DIALOG'LAR ===== */
        QDialog {{
            background-color: {cls.arka_plan};
            border: 3px solid {cls.ana_renk};
            border-radius: 12px;
        }}

        QDialog QLabel {{
            font-size: 14px;
            color: {cls.koyu_gri};
        }}

        QDialog QPushButton {{
            background-color: {cls.ana_renk};
            color: {cls.beyaz};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            min-height: 40px;
            min-width: 100px;
        }}

        QDialog QPushButton:hover {{
            background-color: {cls.vurgu_renk};
        }}

        QDialog QPushButton:pressed {{
            background-color: {cls.koyu_turkuaz};
        }}

        /* İptal butonu */
        QPushButton.iptal-buton {{
            background-color: {cls.hata_renk};
        }}

        QPushButton.iptal-buton:hover {{
            background-color: #FF4500;
        }}

        /* ===== GENEL BUTONLAR - Gereksinim 9.2 ===== */
        QPushButton {{
            background-color: {cls.ana_renk};
            color: {cls.beyaz};
            border: none;
            border-radius: 8px;
            padding: 12px 18px;
            font-size: 14px;
            font-weight: bold;
            min-height: 40px;
            min-width: 100px;
        }}

        QPushButton:hover {{
            background-color: {cls.vurgu_renk};
        }}

        QPushButton:pressed {{
            background-color: {cls.koyu_turkuaz};
        }}

        QPushButton:disabled {{
            background-color: {cls.orta_gri};
            color: {cls.koyu_gri};
        }}
        
        /* ===== WIDGET SPACING VE MARGIN - Gereksinim 9.4 ===== */
        QWidget {{
            margin: 2px;
        }}
        
        QVBoxLayout {{
            spacing: 8px;
        }}
        
        QHBoxLayout {{
            spacing: 8px;
        }}

        /* ===== SEPET ALT BUTONLARI ===== */
        QPushButton.sepet-alt-buton {{
            background-color: {cls.ikincil_renk};
            color: {cls.beyaz};
            border: 2px solid {cls.ana_renk};
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: bold;
            min-height: 35px;
            min-width: 90px;
        }}

        QPushButton.sepet-alt-buton:hover {{
            background-color: {cls.ana_renk};
            border-color: {cls.vurgu_renk};
        }}

        /* ===== SCROLLBAR ===== */
        QScrollBar:vertical {{
            background-color: {cls.acik_gri};
            width: 16px;
            border-radius: 8px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.ana_renk};
            border-radius: 8px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.vurgu_renk};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        /* ===== SPLITTER ===== */
        QSplitter::handle {{
            background-color: {cls.orta_gri};
            width: 4px;
        }}

        QSplitter::handle:hover {{
            background-color: {cls.ana_renk};
        }}

        /* ===== MESAJ KUTULARI ===== */
        QMessageBox {{
            background-color: {cls.arka_plan};
            color: {cls.koyu_gri};
        }}

        QMessageBox QPushButton {{
            min-width: 80px;
            min-height: 30px;
        }}
        """

    @classmethod
    def temayı_uygula(cls, uygulama: QApplication):
        """Uygulamaya tema stillerini uygular"""
        uygulama.setStyleSheet(cls.qss_stilleri())

    @classmethod
    def widget_temayı_uygula(cls, widget):
        """Tek bir widget'a tema uygular"""
        widget.setStyleSheet(cls.qss_stilleri())

    @classmethod
    def buton_temayı_uygula(cls, buton, buton_turu: str = ""):
        """Butona tema ve stil sınıfı uygular"""
        if buton_turu:
            stil_sinifi = cls.buton_stil_sinifi_al(buton_turu)
            if stil_sinifi:
                buton.setProperty("class", stil_sinifi)
        if buton.style():
            buton.style().unpolish(buton)
            buton.style().polish(buton)

    @classmethod
    def buton_stil_sinifi_al(cls, buton_turu: str) -> str:
        """Buton türüne göre stil sınıfı döndürür"""
        stil_sinifi_map = {
            "odeme": "odeme-buton",
            "hizli_islem": "hizli-islem",
            "hizli_urun": "hizli-urun",
            "iptal": "iptal-buton",
        }
        return stil_sinifi_map.get(buton_turu, "")

    @classmethod
    def label_stil_sinifi_al(cls, label_turu: str) -> str:
        """Label türüne göre stil sınıfı döndürür"""
        stil_sinifi_map = {"genel_toplam": "genel-toplam", "ara_toplam": "ara-toplam"}
        return stil_sinifi_map.get(label_turu, "")

    @classmethod
    def widget_stil_sinifi_al(cls, widget_turu: str) -> str:
        """Widget türüne göre stil sınıfı döndürür"""
        stil_sinifi_map = {"kart": "kart", "nakit_alan": "nakit-alan"}
        return stil_sinifi_map.get(widget_turu, "")

    @classmethod
    def tema_renklerini_al(cls) -> Dict[str, str]:
        """Tema renklerini dict olarak döndürür"""
        return {
            "ana_renk": cls.ana_renk,
            "ikincil_renk": cls.ikincil_renk,
            "arka_plan": cls.arka_plan,
            "vurgu_renk": cls.vurgu_renk,
            "hata_renk": cls.hata_renk,
            "basari_renk": cls.basari_renk,
            "koyu_turkuaz": cls.koyu_turkuaz,
            "acik_gri": cls.acik_gri,
            "orta_gri": cls.orta_gri,
            "koyu_gri": cls.koyu_gri,
            "beyaz": cls.beyaz,
            "siyah": cls.siyah,
        }

    @classmethod
    def tema_dogrulama(cls) -> bool:
        """Tema renklerinin geçerliliğini kontrol eder"""
        renkler = cls.tema_renklerini_al()
        for renk_adi, renk_kodu in renkler.items():
            if not renk_kodu.startswith("#") or len(renk_kodu) != 7:
                return False
        return True
