# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ana_pencere
# Description: Ana pencere ve navigasyon sistemi
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QStackedWidget, QListWidgetItem, 
                             QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .servis_fabrikasi import ServisFabrikasi


class AnaPencere(QMainWindow):
    """SONTECHSP ana pencere sınıfı"""
    
    # Ekran değişim sinyali
    ekran_degisti = pyqtSignal(str)
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi):
        super().__init__()
        self.servis_fabrikasi = servis_fabrikasi
        self.ekranlar = {}
        self.aktif_ekran = None
        self.onceki_ekran = None
        
        self.pencereyi_hazirla()
        self.menu_olustur()
        self.ekranlari_yukle()
    
    def pencereyi_hazirla(self):
        """Ana pencere ayarlarını yap"""
        self.setWindowTitle("SONTECHSP - POS & ERP Sistemi")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget ve layout
        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)
        
        # Ana layout (yatay)
        ana_layout = QHBoxLayout(ana_widget)
        ana_layout.setContentsMargins(0, 0, 0, 0)
        ana_layout.setSpacing(0)
        
        # Sol menü paneli
        self.menu_paneli = self.sol_menu_olustur()
        ana_layout.addWidget(self.menu_paneli)
        
        # İçerik alanı (QStackedWidget)
        self.icerik_alani = QStackedWidget()
        ana_layout.addWidget(self.icerik_alani)
        
        # Layout oranları
        ana_layout.setStretch(0, 0)  # Sol menü sabit genişlik
        ana_layout.setStretch(1, 1)  # İçerik alanı esnek
    
    def sol_menu_olustur(self):
        """Sol menü panelini oluştur"""
        menu_frame = QFrame()
        menu_frame.setFixedWidth(250)
        menu_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)
        
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        # Başlık
        baslik = QLabel("SONTECHSP")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                border-bottom: 1px solid #2c3e50;
            }
        """)
        menu_layout.addWidget(baslik)
        
        # Menü listesi
        self.menu_listesi = QListWidget()
        self.menu_listesi.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                border: none;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px 20px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
            QListWidget::item:selected {
                background-color: #3498db;
            }
        """)
        self.menu_listesi.itemClicked.connect(self.menu_tiklandi)
        menu_layout.addWidget(self.menu_listesi)
        
        return menu_frame
    
    def menu_olustur(self):
        """Menü öğelerini oluştur"""
        menu_ogeleri = [
            ("Gösterge Paneli", "gosterge_paneli"),
            ("POS Satış", "pos_satis"),
            ("Ürünler & Stok", "urunler_stok"),
            ("Müşteriler", "musteriler"),
            ("E-ticaret", "eticaret"),
            ("E-belge", "ebelge"),
            ("Kargo", "kargo"),
            ("Raporlar", "raporlar"),
            ("Ayarlar", "ayarlar")
        ]
        
        for ad, anahtar in menu_ogeleri:
            item = QListWidgetItem(ad)
            item.setData(Qt.ItemDataRole.UserRole, anahtar)
            self.menu_listesi.addItem(item)
    
    def ekranlari_yukle(self):
        """Ekran modüllerini yükle"""
        # Gösterge paneli ekranını yükle
        from .ekranlar.gosterge_paneli import GostergePaneli
        gosterge_paneli = GostergePaneli(self.servis_fabrikasi)
        gosterge_paneli.ekran_degistir_istegi.connect(self.ekran_degistir)
        self.ekranlar["gosterge_paneli"] = gosterge_paneli
        self.icerik_alani.addWidget(gosterge_paneli)
        
        # POS satış ekranını yükle
        from .ekranlar.pos_satis import PosSatis
        pos_satis = PosSatis(self.servis_fabrikasi)
        self.ekranlar["pos_satis"] = pos_satis
        self.icerik_alani.addWidget(pos_satis)
        
        # Ürünler stok ekranını yükle
        from .ekranlar.urunler_stok import UrunlerStok
        urunler_stok = UrunlerStok(self.servis_fabrikasi)
        self.ekranlar["urunler_stok"] = urunler_stok
        self.icerik_alani.addWidget(urunler_stok)
        
        # Müşteriler ekranını yükle
        from .ekranlar.musteriler import Musteriler
        musteriler = Musteriler(self.servis_fabrikasi)
        self.ekranlar["musteriler"] = musteriler
        self.icerik_alani.addWidget(musteriler)
        
        # E-ticaret ekranını yükle
        from .ekranlar.eticaret import Eticaret
        eticaret = Eticaret(self.servis_fabrikasi)
        self.ekranlar["eticaret"] = eticaret
        self.icerik_alani.addWidget(eticaret)
        
        # E-belge ekranını yükle
        from .ekranlar.ebelge import Ebelge
        ebelge = Ebelge(self.servis_fabrikasi)
        self.ekranlar["ebelge"] = ebelge
        self.icerik_alani.addWidget(ebelge)
        
        # Kargo ekranını yükle
        from .ekranlar.kargo import Kargo
        kargo = Kargo(self.servis_fabrikasi)
        self.ekranlar["kargo"] = kargo
        self.icerik_alani.addWidget(kargo)
        
        # Raporlar ekranını yükle
        from .ekranlar.raporlar import Raporlar
        raporlar = Raporlar(self.servis_fabrikasi)
        self.ekranlar["raporlar"] = raporlar
        self.icerik_alani.addWidget(raporlar)
        
        # Ayarlar ekranını yükle
        from .ekranlar.ayarlar import Ayarlar
        ayarlar = Ayarlar(self.servis_fabrikasi)
        self.ekranlar["ayarlar"] = ayarlar
        self.icerik_alani.addWidget(ayarlar)
        
        # İlk ekranı göster
        self.ekran_degistir("gosterge_paneli")
    
    def yer_tutucu_ekran_olustur(self, ekran_adi: str):
        """Yer tutucu ekran oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        baslik = QLabel(f"{ekran_adi.replace('_', ' ').title()} Ekranı")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 24))
        baslik.setStyleSheet("color: #2c3e50; margin: 50px;")
        
        aciklama = QLabel("Bu ekran henüz geliştirilmemiştir.")
        aciklama.setAlignment(Qt.AlignmentFlag.AlignCenter)
        aciklama.setStyleSheet("color: #7f8c8d; font-size: 16px;")
        
        layout.addWidget(baslik)
        layout.addWidget(aciklama)
        layout.addStretch()
        
        return widget
    
    def menu_tiklandi(self, item: QListWidgetItem):
        """Menü öğesi tıklandığında çağrılır"""
        ekran_adi = item.data(Qt.ItemDataRole.UserRole)
        self.ekran_degistir(ekran_adi)
    
    def ekran_degistir(self, ekran_adi: str):
        """Aktif ekranı değiştir"""
        if ekran_adi in self.ekranlar:
            # Önceki ekranı kaydet
            self.onceki_ekran = self.aktif_ekran
            self.aktif_ekran = ekran_adi
            
            # Ekranı göster
            widget = self.ekranlar[ekran_adi]
            self.icerik_alani.setCurrentWidget(widget)
            
            # Sinyal gönder
            self.ekran_degisti.emit(ekran_adi)
            
            # Menü seçimini güncelle
            self.menu_secimini_guncelle(ekran_adi)
    
    def menu_secimini_guncelle(self, ekran_adi: str):
        """Menü seçimini görsel olarak güncelle"""
        for i in range(self.menu_listesi.count()):
            item = self.menu_listesi.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == ekran_adi:
                self.menu_listesi.setCurrentItem(item)
                break
    
    def servis_al(self, servis_tipi: str):
        """Servis fabrikasından servis al"""
        try:
            if servis_tipi == "stok":
                return self.servis_fabrikasi.stok_servisi()
            elif servis_tipi == "pos":
                return self.servis_fabrikasi.pos_servisi()
            elif servis_tipi == "crm":
                return self.servis_fabrikasi.crm_servisi()
            elif servis_tipi == "eticaret":
                return self.servis_fabrikasi.eticaret_servisi()
            elif servis_tipi == "ebelge":
                return self.servis_fabrikasi.ebelge_servisi()
            elif servis_tipi == "kargo":
                return self.servis_fabrikasi.kargo_servisi()
            elif servis_tipi == "rapor":
                return self.servis_fabrikasi.rapor_servisi()
            elif servis_tipi == "ayar":
                return self.servis_fabrikasi.ayar_servisi()
            else:
                raise ValueError(f"Bilinmeyen servis tipi: {servis_tipi}")
        except Exception as e:
            print(f"Servis alma hatası: {e}")
            return None