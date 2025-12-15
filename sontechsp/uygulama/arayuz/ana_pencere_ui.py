# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ana_pencere_ui
# Description: SONTECHSP ana pencere UI bileşenleri
# Changelog:
# - İlk oluşturma
# - ana_pencere.py'den ayrıldı (kod kalitesi için)

"""
SONTECHSP Ana Pencere UI Bileşenleri

Ana pencere için UI oluşturma ve yönetim fonksiyonları.
Ana pencere sınıfından ayrılmış UI mantığı.

Sorumluluklar:
- UI bileşenlerini oluşturma
- Menü ve toolbar kurulumu
- Stil ve layout yönetimi
- Widget oluşturma yardımcıları
"""

from typing import List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
    QStackedWidget, QLabel, QStatusBar, QMenuBar, 
    QToolBar, QSplitter, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction


def ana_ui_kur(pencere) -> None:
    """
    Ana UI bileşenlerini kurar
    
    Args:
        pencere: Ana pencere instance'ı
    """
    pencere.setWindowTitle("SONTECHSP - POS + ERP + CRM")
    pencere.setGeometry(100, 100, 1400, 900)
    pencere.setMinimumSize(1000, 600)
    
    # Ana widget ve splitter
    ana_widget = QWidget()
    pencere.setCentralWidget(ana_widget)
    ana_layout = QHBoxLayout(ana_widget)
    ana_layout.setContentsMargins(5, 5, 5, 5)
    
    # Splitter (yeniden boyutlandırılabilir)
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Sol panel (menü)
    sol_panel = sol_panel_olustur(pencere)
    splitter.addWidget(sol_panel)
    
    # İçerik alanı
    pencere.icerik_alani = QStackedWidget()
    varsayilan_ekran_ekle(pencere)
    splitter.addWidget(pencere.icerik_alani)
    
    # Splitter oranları (20% sol, 80% sağ)
    splitter.setSizes([280, 1120])
    splitter.setCollapsible(0, False)  # Sol panel kapatılamaz
    
    ana_layout.addWidget(splitter)


def sol_panel_olustur(pencere) -> QWidget:
    """
    Sol panel (menü) oluşturur
    
    Args:
        pencere: Ana pencere instance'ı
        
    Returns:
        QWidget: Sol panel widget'ı
    """
    sol_widget = QWidget()
    sol_layout = QVBoxLayout(sol_widget)
    sol_layout.setContentsMargins(5, 5, 5, 5)
    
    # Başlık
    baslik_label = QLabel("MODÜLLER")
    baslik_label.setStyleSheet("""
        QLabel {
            font-weight: bold;
            font-size: 12px;
            color: #2c3e50;
            padding: 5px;
            background-color: #ecf0f1;
            border-radius: 3px;
        }
    """)
    sol_layout.addWidget(baslik_label)
    
    # Modül menüsü
    pencere.modul_menusu = QListWidget()
    pencere.modul_menusu.setMaximumWidth(270)
    pencere.modul_menusu.setMinimumWidth(250)
    
    # Modül listesi (tasarım belgesinden)
    moduller = modul_listesi_al()
    
    for modul_kodu, modul_adi in moduller:
        pencere.modul_menusu.addItem(modul_adi)
        # Modül kodunu item'a data olarak ekle
        item = pencere.modul_menusu.item(pencere.modul_menusu.count() - 1)
        item.setData(Qt.ItemDataRole.UserRole, modul_kodu)
    
    # Menü stili uygula
    menu_stili_uygula(pencere.modul_menusu)
    
    sol_layout.addWidget(pencere.modul_menusu)
    
    return sol_widget


def modul_listesi_al() -> List[Tuple[str, str]]:
    """
    Modül listesini döndürür
    
    Returns:
        List[Tuple[str, str]]: (modul_kodu, modul_adi) listesi
    """
    return [
        ("stok", "Stok Yönetimi"),
        ("pos", "POS Satış"),
        ("crm", "CRM"),
        ("satis_belgeleri", "Satış Belgeleri"),
        ("eticaret", "E-Ticaret"),
        ("ebelge", "E-Belge"),
        ("kargo", "Kargo"),
        ("raporlar", "Raporlar")
    ]


def menu_stili_uygula(menu_widget: QListWidget) -> None:
    """
    Menü widget'ına stil uygular
    
    Args:
        menu_widget: Stil uygulanacak menü widget'ı
    """
    menu_widget.setStyleSheet("""
        QListWidget {
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            background-color: white;
            selection-background-color: #3498db;
            selection-color: white;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }
        QListWidget::item:hover {
            background-color: #f8f9fa;
        }
    """)


def varsayilan_ekran_ekle(pencere) -> None:
    """
    Varsayılan hoş geldin ekranını ekler
    
    Args:
        pencere: Ana pencere instance'ı
    """
    hosgeldin_widget = QWidget()
    hosgeldin_layout = QVBoxLayout(hosgeldin_widget)
    hosgeldin_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    # Ana başlık
    baslik_label = QLabel("SONTECHSP")
    baslik_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    baslik_label.setStyleSheet("""
        QLabel {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
    """)
    hosgeldin_layout.addWidget(baslik_label)
    
    # Alt başlık
    altbaslik_label = QLabel("POS + ERP + CRM Sistemi")
    altbaslik_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    altbaslik_label.setStyleSheet("""
        QLabel {
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
    """)
    hosgeldin_layout.addWidget(altbaslik_label)
    
    # Bilgi metni
    bilgi_label = QLabel("Başlamak için sol menüden bir modül seçin")
    bilgi_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    bilgi_label.setStyleSheet("""
        QLabel {
            font-size: 14px;
            color: #95a5a6;
        }
    """)
    hosgeldin_layout.addWidget(bilgi_label)
    
    pencere.icerik_alani.addWidget(hosgeldin_widget)


def menu_kur(pencere) -> None:
    """
    Ana menü çubuğunu kurar
    
    Args:
        pencere: Ana pencere instance'ı
    """
    menubar = pencere.menuBar()
    
    # Dosya menüsü
    dosya_menu = menubar.addMenu("&Dosya")
    
    cikis_action = QAction("Çı&kış", pencere)
    cikis_action.setShortcut("Ctrl+Q")
    cikis_action.triggered.connect(pencere.close)
    dosya_menu.addAction(cikis_action)
    
    # Görünüm menüsü
    gorunum_menu = menubar.addMenu("&Görünüm")
    
    # Yardım menüsü
    yardim_menu = menubar.addMenu("&Yardım")
    
    hakkinda_action = QAction("&Hakkında", pencere)
    hakkinda_action.triggered.connect(lambda: hakkinda_goster(pencere))
    yardim_menu.addAction(hakkinda_action)


def toolbar_kur(pencere) -> None:
    """
    Araç çubuğunu kurar
    
    Args:
        pencere: Ana pencere instance'ı
    """
    toolbar = pencere.addToolBar("Ana Araç Çubuğu")
    toolbar.setMovable(False)
    
    # Geri action (ileride kullanılacak)
    geri_action = QAction("Geri", pencere)
    geri_action.setEnabled(False)
    toolbar.addAction(geri_action)
    
    toolbar.addSeparator()
    
    # Yenile action
    yenile_action = QAction("Yenile", pencere)
    yenile_action.setShortcut("F5")
    yenile_action.triggered.connect(lambda: ekrani_yenile(pencere))
    toolbar.addAction(yenile_action)


def statusbar_kur(pencere) -> None:
    """
    Durum çubuğunu kurar
    
    Args:
        pencere: Ana pencere instance'ı
    """
    pencere.statusbar = pencere.statusBar()
    
    # Varsayılan mesaj
    pencere.statusbar.showMessage("Hazır")
    
    # Oturum bilgisi (sağ taraf)
    pencere.oturum_label = QLabel("Oturum: Yok")
    pencere.statusbar.addPermanentWidget(pencere.oturum_label)


def placeholder_ekran_olustur(modul_adi: str) -> QWidget:
    """
    Geçici modül ekranı oluşturur
    
    Args:
        modul_adi: Modül adı
        
    Returns:
        QWidget: Placeholder ekran widget'ı
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    baslik = QLabel(f"{modul_adi} Modülü")
    baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
    baslik.setStyleSheet("""
        QLabel {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        }
    """)
    layout.addWidget(baslik)
    
    bilgi = QLabel("Bu modül henüz geliştirilme aşamasındadır.")
    bilgi.setAlignment(Qt.AlignmentFlag.AlignCenter)
    bilgi.setStyleSheet("""
        QLabel {
            font-size: 14px;
            color: #7f8c8d;
        }
    """)
    layout.addWidget(bilgi)
    
    return widget


def ekrani_yenile(pencere) -> None:
    """
    Aktif ekranı yeniler
    
    Args:
        pencere: Ana pencere instance'ı
    """
    aktif_widget = pencere.icerik_alani.currentWidget()
    if hasattr(aktif_widget, 'yenile'):
        aktif_widget.yenile()
    
    pencere.statusbar.showMessage("Ekran yenilendi", 2000)
    pencere.logger.debug("Ekran yenilendi")


def hakkinda_goster(pencere) -> None:
    """
    Hakkında dialog'unu gösterir
    
    Args:
        pencere: Ana pencere instance'ı
    """
    QMessageBox.about(pencere, "SONTECHSP Hakkında", 
                     "SONTECHSP v0.1.0\n\n"
                     "POS + ERP + CRM Sistemi\n"
                     "Python + PyQt6 + PostgreSQL")