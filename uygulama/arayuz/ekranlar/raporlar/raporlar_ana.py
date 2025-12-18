# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.raporlar.raporlar_ana
# Description: Ana raporlar ekranı - refactor edilmiş
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QFrame, QHeaderView, QSplitter,
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..temel_ekran import TemelEkran
from ...servis_fabrikasi import ServisFabrikasi
from .rapor_filtreleri import RaporFiltreleriUI, RaporFiltreleriIslemleri
from .rapor_olusturma import RaporOlusturmaUI, RaporOlusturmaIslemleri
from .rapor_export import RaporExportIslemleri
from .rapor_yardimcilar import RaporYardimciUI, RaporYardimciIslemleri


class Raporlar(TemelEkran):
    """Raporlar ekranı - refactor edilmiş"""
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        # Temel özellikler
        self.rapor_tablo = None
        self.durum_label = None
        self.progress_bar = None
        self.rapor_verileri = []
        self.aktif_rapor_tipi = None
        
        super().__init__(servis_fabrikasi, parent)
        
        # Bileşenleri başlat
        self._bileşenleri_baslat()
    
    def _bileşenleri_baslat(self):
        """UI ve işlem bileşenlerini başlat"""
        # UI bileşenleri
        self.filtreleri_ui = RaporFiltreleriUI(self)
        self.olusturma_ui = RaporOlusturmaUI(self)
        self.yardimci_ui = RaporYardimciUI(self)
        
        # İşlem sınıfları
        self.filtreleri_islemleri = RaporFiltreleriIslemleri(self)
        self.olusturma_islemleri = RaporOlusturmaIslemleri(self)
        self.export_islemleri = RaporExportIslemleri(self)
        self.yardimci_islemleri = RaporYardimciIslemleri(self)
    
    def ekrani_hazirla(self):
        """Raporlar ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("Raporlar")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)
        
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Rapor parametreleri
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Rapor sonuçları
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([350, 650])
        
        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True
    
    def sol_panel_olustur(self):
        """Sol panel - rapor parametreleri"""
        panel = QFrame()
        panel.setFixedWidth(350)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        # Scroll area oluştur
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Rapor türü seçimi grubu
        rapor_turu_grup = self.filtreleri_ui.rapor_turu_grubu_olustur()
        layout.addWidget(rapor_turu_grup)
        
        # Tarih aralığı grubu
        tarih_grup = self.filtreleri_ui.tarih_araligi_grubu_olustur()
        layout.addWidget(tarih_grup)
        
        # Filtreler grubu
        filtreler_grup = self.filtreleri_ui.filtreler_grubu_olustur()
        layout.addWidget(filtreler_grup)
        
        # Rapor oluşturma grubu
        olusturma_grup = self.olusturma_ui.rapor_olusturma_grubu_olustur()
        layout.addWidget(olusturma_grup)
        
        # Durum bilgisi grubu
        durum_grup = self.yardimci_ui.durum_bilgisi_grubu_olustur()
        layout.addWidget(durum_grup)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.addWidget(scroll)
        
        return panel
    
    def sag_panel_olustur(self):
        """Sağ panel - rapor sonuçları"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Üst bilgi çubuğu
        ust_bilgi = self.yardimci_ui.ust_bilgi_cubugun_olustur()
        layout.addWidget(ust_bilgi)
        
        # Rapor tablosu
        self.rapor_tablo = QTableWidget()
        self.rapor_tablo.setColumnCount(6)
        self.rapor_tablo.setHorizontalHeaderLabels([
            "Tarih", "Açıklama", "Miktar", "Tutar", "Kategori", "Durum"
        ])
        
        # Tablo ayarları
        header = self.rapor_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.rapor_tablo.setAlternatingRowColors(True)
        self.rapor_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rapor_tablo.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        layout.addWidget(self.rapor_tablo)
        
        # Alt özet bilgileri
        alt_ozet = self.yardimci_ui.alt_ozet_olustur()
        layout.addWidget(alt_ozet)
        
        return panel
    
    # Delegated methods - işlem sınıflarına yönlendirme
    def rapor_turu_degisti(self):
        """Rapor türü değiştiğinde"""
        self.filtreleri_islemleri.rapor_turu_degisti()
    
    def hizli_tarih_sec(self, tur: str):
        """Hızlı tarih seçimi"""
        self.filtreleri_islemleri.hizli_tarih_sec(tur)
    
    def rapor_olustur(self):
        """Rapor oluşturma işlemi"""
        self.olusturma_islemleri.rapor_olustur()
    
    def rapor_verilerini_yukle(self):
        """Rapor verilerini yükle"""
        self.olusturma_islemleri.rapor_verilerini_yukle()
    
    def disa_aktar(self, format_turu: str):
        """Dışa aktarma işlemi"""
        self.export_islemleri.disa_aktar(format_turu)
    
    def yazdir(self):
        """Yazdırma işlemi"""
        self.export_islemleri.yazdir()
    
    def rapor_tablosunu_guncelle(self):
        """Rapor tablosunu güncelle"""
        self.yardimci_islemleri.rapor_tablosunu_guncelle()
    
    def islem_baslat(self, mesaj: str):
        """İşlem başlatma"""
        self.yardimci_islemleri.islem_baslat(mesaj)
    
    def islem_bitir(self):
        """İşlem bitirme"""
        self.yardimci_islemleri.islem_bitir()
    
    def verileri_yukle(self):
        """Ekran açıldığında"""
        # İlk rapor türünü seç
        if hasattr(self, 'rapor_turu_combo') and self.rapor_turu_combo.count() > 0:
            self.rapor_turu_combo.setCurrentIndex(0)
            self.rapor_turu_degisti()
    
    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass