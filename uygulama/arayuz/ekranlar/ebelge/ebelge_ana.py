# Version: 0.1.1
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge.ebelge_ana
# Description: E-belge ana ekran koordinatörü
# Changelog:
# - İlk sürüm oluşturuldu
# - Kod tekrarı düzeltildi, kullanılmayan importlar temizlendi

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame, QSplitter, QTabWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..temel_ekran import TemelEkran
from ...servis_fabrikasi import ServisFabrikasi

from .ebelge_filtreleri import EbelgeFiltreleri
from .ebelge_islemleri import EbelgeIslemleri
from .ebelge_durum import EbelgeDurum
from .ebelge_tablolar import EbelgeTablolar
from .ebelge_yardimcilar import EbelgeYardimcilar
from .ebelge_veri_yoneticisi import EbelgeVeriYoneticisi


class Ebelge(TemelEkran):
    """E-belge yönetimi ana ekranı"""
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.bekleyen_tablo = None
        self.gonderilen_tablo = None
        self.hatali_tablo = None
        self.bekleyen_verileri = []
        self.gonderilen_verileri = []
        self.hatali_verileri = []
        self.tab_widget = None
        self.bekleyen_durum_label = None
        self.gonderilen_durum_label = None
        self.hatali_durum_label = None
        
        # Alt modüller
        self.filtreleri = None
        self.islemleri = None
        self.durum = None
        self.tablolar = None
        self.yardimcilar = None
        
        super().__init__(servis_fabrikasi, parent)
    
    def ekrani_hazirla(self):
        """E-belge ekranını hazırla"""
        # Alt modülleri başlat
        self.filtreleri = EbelgeFiltreleri(self)
        self.islemleri = EbelgeIslemleri(self)
        self.durum = EbelgeDurum(self)
        self.tablolar = EbelgeTablolar(self)
        self.yardimcilar = EbelgeYardimcilar(self)
        
        # Ana başlık
        baslik = QLabel("E-belge Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)
        
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Filtreler ve işlemler
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Sekmeli belge listeleri
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([300, 700])
        
        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True
    
    def sol_panel_olustur(self):
        """Sol panel - filtreler ve işlemler"""
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(panel)
        
        # Filtre grubu
        filtre_grup = self.filtreleri.filtre_grubu_olustur()
        layout.addWidget(filtre_grup)
        
        # İşlemler grubu
        islemler_grup = self.islemleri.islemler_grubu_olustur()
        layout.addWidget(islemler_grup)
        
        # Durum bilgisi grubu
        durum_grup = self.durum.durum_bilgisi_grubu_olustur()
        layout.addWidget(durum_grup)
        
        layout.addStretch()
        
        return panel
    
    def sag_panel_olustur(self):
        """Sağ panel - sekmeli belge listeleri"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Bekleyen belgeler sekmesi
        bekleyen_tab = self.tablolar.bekleyen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(bekleyen_tab, "Bekleyen Belgeler")
        
        # Gönderilen belgeler sekmesi
        gonderilen_tab = self.tablolar.gonderilen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(gonderilen_tab, "Gönderilen Belgeler")
        
        # Hatalı belgeler sekmesi
        hatali_tab = self.tablolar.hatali_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(hatali_tab, "Hatalı Belgeler")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    # Delegasyon fonksiyonları - yardımcı modüle yönlendir
    def filtre_uygula(self):
        """Filtre uygula"""
        self.yardimcilar.filtre_uygula()
    
    def belge_gonder(self):
        """Belge gönderme işlemi"""
        self.yardimcilar.belge_gonder()
    
    def durum_sorgula(self):
        """Durum sorgulama işlemi"""
        self.yardimcilar.durum_sorgula()
    
    def tekrar_dene(self):
        """Tekrar deneme işlemi"""
        self.yardimcilar.tekrar_dene()
    
    def toplu_gonder(self):
        """Toplu gönderme işlemi"""
        self.yardimcilar.toplu_gonder()
    
    def xml_goruntule(self):
        """XML görüntüleme"""
        self.yardimcilar.xml_goruntule()
    
    def secilenleri_gonder(self):
        """Seçilen belgeleri gönder"""
        self.yardimcilar.secilenleri_gonder()
    
    def pdf_indir(self):
        """PDF indirme"""
        self.yardimcilar.pdf_indir()
    
    def hatalari_duzelt(self):
        """Hataları düzeltme"""
        self.yardimcilar.hatalari_duzelt()
    
    # Delegasyon fonksiyonları - tablo modülüne yönlendir
    def bekleyen_listesi_yenile(self):
        """Bekleyen belgeler listesini yenile"""
        self.tablolar.bekleyen_listesi_yenile()
    
    def gonderilen_listesi_yenile(self):
        """Gönderilen belgeler listesini yenile"""
        self.tablolar.gonderilen_listesi_yenile()
    
    def hatali_listesi_yenile(self):
        """Hatalı belgeler listesini yenile"""
        self.tablolar.hatali_listesi_yenile()
    
    def bekleyen_tablosunu_guncelle(self):
        """Bekleyen belgeler tablosunu güncelle"""
        self.tablolar.bekleyen_tablosunu_guncelle()
    
    def gonderilen_tablosunu_guncelle(self):
        """Gönderilen belgeler tablosunu güncelle"""
        self.tablolar.gonderilen_tablosunu_guncelle()
    
    def hatali_tablosunu_guncelle(self):
        """Hatalı belgeler tablosunu güncelle"""
        self.tablolar.hatali_tablosunu_guncelle()
    
    def verileri_yukle(self):
        """Ekran açıldığında"""
        # Tüm listeleri yükle
        self.bekleyen_listesi_yenile()
        self.gonderilen_listesi_yenile()
        self.hatali_listesi_yenile()
    
    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass