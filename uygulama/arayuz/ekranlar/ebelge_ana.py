# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge_ana
# Description: E-belge ana koordinasyon sınıfı
# Changelog:
# - İlk sürüm oluşturuldu

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QHeaderView, QLabel, 
                             QPushButton, QSplitter, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout)

from ..servis_fabrikasi import ServisFabrikasi
from .ebelge_durum import EbelgeDurum
from .ebelge_filtreleri import EbelgeFiltreleri
from .ebelge_islemleri import EbelgeIslemleri
from .temel_ekran import TemelEkran


class Ebelge(TemelEkran):
    """E-belge yönetimi ana ekranı"""
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.bekleyen_tablo: Optional[QTableWidget] = None
        self.gonderilen_tablo: Optional[QTableWidget] = None
        self.hatali_tablo: Optional[QTableWidget] = None
        self.bekleyen_verileri: list = []
        self.gonderilen_verileri: list = []
        self.hatali_verileri: list = []
        
        # Bileşenler
        self.filtreler: Optional[EbelgeFiltreleri] = None
        self.islemler: Optional[EbelgeIslemleri] = None
        self.durum: Optional[EbelgeDurum] = None
        
        super().__init__(servis_fabrikasi, parent)
    
    def ekrani_hazirla(self):
        """E-belge ekranını hazırla"""
        # Bileşenleri başlat
        self._bilesenleri_baslat()
        
        # Ana başlık
        self._ana_baslik_olustur()
        
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Filtreler ve işlemler
        sol_panel = self._sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Sekmeli belge listeleri
        sag_panel = self._sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Layout'a ekle
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def _bilesenleri_baslat(self):
        """Alt bileşenleri başlat"""
        self.filtreler = EbelgeFiltreleri(self.servis_fabrikasi, self)
        self.islemler = EbelgeIslemleri(self.servis_fabrikasi, self)
        self.durum = EbelgeDurum(self.servis_fabrikasi, self)
    
    def _ana_baslik_olustur(self):
        """Ana başlık oluştur"""
        baslik = QLabel("E-Belge Yönetimi")
        baslik.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return baslik
    
    def _sol_panel_olustur(self) -> QFrame:
        """Sol panel oluştur"""
        panel = QFrame()
        layout = QVBoxLayout()
        
        # Filtreler bölümü
        if self.filtreler:
            layout.addWidget(self.filtreler)
        
        # İşlemler bölümü
        if self.islemler:
            layout.addWidget(self.islemler)
        
        # Durum bölümü
        if self.durum:
            layout.addWidget(self.durum)
        
        panel.setLayout(layout)
        panel.setMaximumWidth(300)
        return panel
    
    def _sag_panel_olustur(self) -> QTabWidget:
        """Sağ panel sekmeli belge listeleri oluştur"""
        tab_widget = QTabWidget()
        
        # Bekleyen belgeler sekmesi
        self.bekleyen_tablo = self._tablo_olustur()
        tab_widget.addTab(self.bekleyen_tablo, "Bekleyen")
        
        # Gönderilen belgeler sekmesi
        self.gonderilen_tablo = self._tablo_olustur()
        tab_widget.addTab(self.gonderilen_tablo, "Gönderilen")
        
        # Hatalı belgeler sekmesi
        self.hatali_tablo = self._tablo_olustur()
        tab_widget.addTab(self.hatali_tablo, "Hatalı")
        
        return tab_widget
    
    def _tablo_olustur(self) -> QTableWidget:
        """Belge tablosu oluştur"""
        tablo = QTableWidget()
        tablo.setColumnCount(6)
        tablo.setHorizontalHeaderLabels([
            "Belge No", "Tip", "Tarih", "Tutar", "Durum", "Hata"
        ])
        
        # Tablo ayarları
        header = tablo.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tablo.setAlternatingRowColors(True)
        tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return tablo
        
        # Splitter oranları
        splitter.setSizes([300, 700])
        
        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True
    
    def _bilesenleri_baslat(self):
        """Bileşenleri başlat"""
        self.filtreler = EbelgeFiltreleri(self)
        self.islemler = EbelgeIslemleri(self)
        self.durum = EbelgeDurum(self)
    
    def _ana_baslik_olustur(self):
        """Ana başlık oluştur"""
        baslik = QLabel("E-belge Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)
    
    def _sol_panel_olustur(self):
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
        filtre_grup = self.filtreler.filtre_grubu_olustur()
        layout.addWidget(filtre_grup)
        
        # İşlemler grubu
        islemler_grup = self.islemler.islemler_grubu_olustur()
        layout.addWidget(islemler_grup)
        
        # Durum bilgisi grubu
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
        
        # Sekmeler
        self._sekmeleri_olustur()
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def _sekmeleri_olustur(self):
        """Sekmeleri oluştur"""
        # Bekleyen belgeler sekmesi
        bekleyen_tab = self._bekleyen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(bekleyen_tab, "Bekleyen Belgeler")
        
        # Gönderilen belgeler sekmesi
        gonderilen_tab = self._gonderilen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(gonderilen_tab, "Gönderilen Belgeler")
        
        # Hatalı belgeler sekmesi
        hatali_tab = self._hatali_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(hatali_tab, "Hatalı Belgeler")
    
    def _bekleyen_belgeler_sekmesi_olustur(self):
        """Bekleyen belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self._bekleyen_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Bekleyen belgeler tablosu
        self.bekleyen_tablo = self._tablo_olustur([
            "Belge No", "Tür", "Müşteri", "Tutar", "Tarih", "Durum", "Deneme", "İşlemler"
        ])
        layout.addWidget(self.bekleyen_tablo)
        
        return widget
    
    def _gonderilen_belgeler_sekmesi_olustur(self):
        """Gönderilen belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self._gonderilen_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Gönderilen belgeler tablosu
        self.gonderilen_tablo = self._tablo_olustur([
            "Belge No", "Tür", "Müşteri", "Tutar", "Gönderim Tarihi", "UUID", "Durum", "Yanıt", "İşlemler"
        ])
        layout.addWidget(self.gonderilen_tablo)
        
        return widget
    
    def _hatali_belgeler_sekmesi_olustur(self):
        """Hatalı belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self._hatali_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Hatalı belgeler tablosu
        self.hatali_tablo = self._tablo_olustur([
            "Belge No", "Tür", "Müşteri", "Tutar", "Hata Tarihi", "Hata Kodu", "Hata Açıklaması", "İşlemler"
        ])
        layout.addWidget(self.hatali_tablo)
        
        return widget
    
    def _tablo_olustur(self, basliklar):
        """Tablo oluştur"""
        tablo = QTableWidget()
        tablo.setColumnCount(len(basliklar))
        tablo.setHorizontalHeaderLabels(basliklar)
        
        # Tablo ayarları
        self._tablo_ayarlarini_uygula(tablo)
        
        return tablo
    
    def _tablo_ayarlarini_uygula(self, tablo):
        """Tablo ayarlarını uygula"""
        header = tablo.horizontalHeader()
        for i in range(tablo.columnCount()):
            if i == 2:  # Müşteri sütunu
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            elif i == tablo.columnCount() - 1:  # İşlemler sütunu
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        tablo.setAlternatingRowColors(True)
        tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tablo.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
    
    # İş mantığı metodları (orijinal dosyadan alınacak)
    def filtre_uygula(self):
        """Filtre uygula"""
        try:
            # Tüm listeleri yenile
            self.bekleyen_listesi_yenile()
            self.gonderilen_listesi_yenile()
            self.hatali_listesi_yenile()
            
        except Exception as e:
            self.hata_goster("Filtre Hatası", str(e))
    
    def belge_gonder(self):
        """Belge gönderme işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Belgeler gönderiliyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.gonder)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Belgeler başarıyla gönderildi")
                self.bekleyen_listesi_yenile()
                self.gonderilen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Belge Gönderme Hatası", str(e))
    
    def durum_sorgula(self):
        """Durum sorgulama işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Durum sorgulanıyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.durum_sorgula)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Durum sorgulaması tamamlandı")
                self.gonderilen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Durum Sorgulama Hatası", str(e))
    
    def tekrar_dene(self):
        """Tekrar deneme işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Hatalı belgeler tekrar gönderiliyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.tekrar_dene)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Hatalı belgeler tekrar gönderildi")
                self.hatali_listesi_yenile()
                self.bekleyen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Tekrar Deneme Hatası", str(e))
    
    def toplu_gonder(self):
        """Toplu gönderme işlemi"""
        try:
            if not self.onay_iste("Onay", "Tüm bekleyen belgeler gönderilecek. Emin misiniz?"):
                return
            
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Toplu gönderim yapılıyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.gonder)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Toplu gönderim tamamlandı")
                self.bekleyen_listesi_yenile()
                self.gonderilen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Toplu Gönderim Hatası", str(e))
    
    def xml_goruntule(self):
        """XML görüntüleme"""
        try:
            # XML görüntüleme dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "XML görüntüleme dialog'u açılacak")
            
        except Exception as e:
            self.hata_goster("XML Görüntüleme Hatası", str(e))
    
    def islem_baslat(self, mesaj):
        """İşlem başlat"""
        self.durum.durum_guncelle(mesaj, "#f39c12")
        self.durum.progress_goster(True)
        self.durum.progress_guncelle(0)
    
    def islem_bitir(self):
        """İşlem bitir"""
        self.durum.durum_guncelle("Hazır")
        self.durum.progress_goster(False)
    
    # Stub metodlar (orijinal dosyadan alınacak)
    def _bekleyen_ust_butonlar_olustur(self):
        """Bekleyen belgeler üst butonları (stub)"""
        return QFrame()
    
    def _gonderilen_ust_butonlar_olustur(self):
        """Gönderilen belgeler üst butonları (stub)"""
        return QFrame()
    
    def _hatali_ust_butonlar_olustur(self):
        """Hatalı belgeler üst butonları (stub)"""
        return QFrame()
    
    def bekleyen_listesi_yenile(self):
        """Bekleyen belgeler listesini yenile (stub)"""
        pass
    
    def gonderilen_listesi_yenile(self):
        """Gönderilen belgeler listesini yenile (stub)"""
        pass
    
    def hatali_listesi_yenile(self):
        """Hatalı belgeler listesini yenile (stub)"""
        pass