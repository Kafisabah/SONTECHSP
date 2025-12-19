# Version: 0.1.2
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge.ebelge_ana
# Description: E-belge ana ekran koordinatörü - optimize edilmiş
# Changelog:
# - İlk sürüm oluşturuldu
# - Kod tekrarı düzeltildi, kullanılmayan importlar temizlendi
# - Veri yönetimi fonksiyonları veri yöneticisine taşındı

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QSplitter, QTabWidget, QVBoxLayout

from ...servis_fabrikasi import ServisFabrikasi
from ..temel_ekran import TemelEkran
from .ebelge_durum import EbelgeDurum
from .ebelge_filtreleri import EbelgeFiltreleri
from .ebelge_islemleri import EbelgeIslemleri
from .ebelge_tablolar import EbelgeTablolar
from .ebelge_veri_yoneticisi import EbelgeVeriYoneticisi
from .ebelge_yardimcilar import EbelgeYardimcilar


class Ebelge(TemelEkran):
    """E-belge yönetimi ana ekranı - koordinatör sınıfı"""
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        # Tablo widget'ları
        self.bekleyen_tablo: Optional[object] = None
        self.gonderilen_tablo: Optional[object] = None
        self.hatali_tablo: Optional[object] = None
        
        # Veri listeleri
        self.bekleyen_verileri: list = []
        self.gonderilen_verileri: list = []
        self.hatali_verileri: list = []
        
        # UI bileşenleri
        self.tab_widget: Optional[QTabWidget] = None
        self.bekleyen_durum_label: Optional[QLabel] = None
        self.gonderilen_durum_label: Optional[QLabel] = None
        self.hatali_durum_label: Optional[QLabel] = None
        
        # Alt modüller
        self.filtreleri: Optional[EbelgeFiltreleri] = None
        self.islemleri: Optional[EbelgeIslemleri] = None
        self.durum: Optional[EbelgeDurum] = None
        self.tablolar: Optional[EbelgeTablolar] = None
        self.yardimcilar: Optional[EbelgeYardimcilar] = None
        self.veri_yoneticisi: Optional[EbelgeVeriYoneticisi] = None
        
        super().__init__(servis_fabrikasi, parent)
    
    def ekrani_hazirla(self):
        """E-belge ekranını hazırla - ana koordinasyon"""
        # Alt modülleri başlat
        self._alt_modulleri_baslat()
        
        # UI bileşenlerini oluştur
        self._ui_bilesenleri_olustur()
        
        self.ekran_hazir = True
    
    def _alt_modulleri_baslat(self):
        """Alt modülleri başlat"""
        self.filtreleri = EbelgeFiltreleri(self)
        self.islemleri = EbelgeIslemleri(self)
        self.durum = EbelgeDurum(self)
        self.tablolar = EbelgeTablolar(self)
        self.yardimcilar = EbelgeYardimcilar(self)
        self.veri_yoneticisi = EbelgeVeriYoneticisi(self)
    
    def _ui_bilesenleri_olustur(self):
        """UI bileşenlerini oluştur"""
        # Ana başlık
        baslik = self._ana_baslik_olustur()
        self.ana_layout.addWidget(baslik)
        
        # Ana splitter
        splitter = self._ana_splitter_olustur()
        self.ana_layout.addWidget(splitter)
    
    def _ana_baslik_olustur(self) -> QLabel:
        """Ana başlık oluştur"""
        baslik = QLabel("E-belge Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        return baslik
    
    def _ana_splitter_olustur(self) -> QSplitter:
        """Ana splitter oluştur"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Filtreler ve işlemler
        sol_panel = self._sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Sekmeli belge listeleri
        sag_panel = self._sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([300, 700])
        
        return splitter
    
    def _sol_panel_olustur(self) -> QFrame:
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
        if self.filtreleri:
            filtre_grup = self.filtreleri.filtre_grubu_olustur()
            layout.addWidget(filtre_grup)
        
        # İşlemler grubu
        if self.islemleri:
            islemler_grup = self.islemleri.islemler_grubu_olustur()
            layout.addWidget(islemler_grup)
        
        # Durum bilgisi grubu
        if self.durum:
            durum_grup = self.durum.durum_bilgisi_grubu_olustur()
            layout.addWidget(durum_grup)
        
        layout.addStretch()
        
        return panel
    
    def _sag_panel_olustur(self):
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
        
        # Sekmeleri oluştur
        self._sekmeleri_olustur()
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def _sekmeleri_olustur(self):
        """Sekmeleri oluştur"""
        # Bekleyen belgeler sekmesi
        bekleyen_tab = self.tablolar.bekleyen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(bekleyen_tab, "Bekleyen Belgeler")
        
        # Gönderilen belgeler sekmesi
        gonderilen_tab = self.tablolar.gonderilen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(gonderilen_tab, "Gönderilen Belgeler")
        
        # Hatalı belgeler sekmesi
        hatali_tab = self.tablolar.hatali_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(hatali_tab, "Hatalı Belgeler")
    
    # İş akışı delegasyon fonksiyonları - yardımcı modüle yönlendir
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
    
    # Veri yönetimi delegasyon fonksiyonları - veri yöneticisine yönlendir
    def bekleyen_listesi_yenile(self):
        """Bekleyen belgeler listesini yenile"""
        self.veri_yoneticisi.bekleyen_listesi_yenile()
    
    def gonderilen_listesi_yenile(self):
        """Gönderilen belgeler listesini yenile"""
        self.veri_yoneticisi.gonderilen_listesi_yenile()
    
    def hatali_listesi_yenile(self):
        """Hatalı belgeler listesini yenile"""
        self.veri_yoneticisi.hatali_listesi_yenile()
    
    def bekleyen_tablosunu_guncelle(self):
        """Bekleyen belgeler tablosunu güncelle"""
        self.veri_yoneticisi.bekleyen_tablosunu_guncelle()
    
    def gonderilen_tablosunu_guncelle(self):
        """Gönderilen belgeler tablosunu güncelle"""
        self.veri_yoneticisi.gonderilen_tablosunu_guncelle()
    
    def hatali_tablosunu_guncelle(self):
        """Hatalı belgeler tablosunu güncelle"""
        self.veri_yoneticisi.hatali_tablosunu_guncelle()
    
    # Yaşam döngüsü yönetimi
    def verileri_yukle(self):
        """Ekran açıldığında - tüm listeleri yükle"""
        self.bekleyen_listesi_yenile()
        self.gonderilen_listesi_yenile()
        self.hatali_listesi_yenile()
    
    def verileri_temizle(self):
        """Ekran kapandığında - temizlik işlemleri"""
        # Gerekirse temizlik işlemleri burada yapılır
        pass