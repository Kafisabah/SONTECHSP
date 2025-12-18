# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ayarlar.ayarlar
# Description: Ana ayarlar ekranı - refactor edilmiş modüler yapı
# Changelog:
# - İlk sürüm oluşturuldu - modüler yapıya geçiş tamamlandı

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QLabel, QFrame, QMessageBox, QProgressBar,
                             QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from uygulama.arayuz.taban_ekran import TabanEkran
from uygulama.arayuz.ekranlar.ayarlar.ayar_formlari import AyarFormlari
from uygulama.arayuz.ekranlar.ayarlar.ayar_butonlari import AyarButonlari
from uygulama.arayuz.ekranlar.ayarlar.ayar_dogrulama import AyarDogrulama


class AyarlarEkrani(TabanEkran):
    """Ana ayarlar ekranı - modüler yapı"""
    
    ayar_degisti = pyqtSignal(str, object)  # ayar_adi, yeni_deger
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sistem Ayarları")
        self.resize(1000, 700)
        
        # Alt modüller
        self.ayar_formlari = AyarFormlari(self)
        self.ayar_butonlari = AyarButonlari(self)
        self.ayar_dogrulama = AyarDogrulama()
        
        # Değişiklik takibi
        self.degisiklikler = {}
        self.orijinal_degerler = {}
        
        # UI bileşenleri
        self.tab_widget = None
        self.degisiklik_sayaci = None
        self.progress_bar = None
        
        # Form alanları (AyarFormlari tarafından doldurulacak)
        self.form_alanlari_init()
        
        self.ui_olustur()
        self.baglantilari_kur()
        self.ayarlari_yukle()
    
    def form_alanlari_init(self):
        """Form alanlarını başlat"""
        # Şirket bilgileri
        self.sirket_adi = None
        self.vergi_no = None
        self.adres = None
        
        # Uygulama ayarları
        self.dil_combo = None
        self.tema_combo = None
        self.otomatik_yedekleme = None
        
        # Veritabanı ayarları
        self.db_host = None
        self.db_port = None
        self.db_name = None
        self.db_user = None
        self.db_password = None
        self.baglanti_havuzu = None
        self.sorgu_timeout = None
        
        # POS ayarları
        self.otomatik_fiş = None
        self.barkod_sesi = None
        self.sepet_temizle = None
        self.nakit_odeme = None
        self.kart_odeme = None
        self.veresiye_odeme = None
        
        # Stok ayarları
        self.negatif_stok = None
        self.kritik_stok_uyari = None
        self.kritik_stok_seviye = None
        self.otomatik_barkod = None
        self.stok_senkron = None
        
        # E-ticaret ayarları
        self.otomatik_siparis_cek = None
        self.siparis_cekme_araligi = None
        self.stok_senkron_eticaret = None
        
        # E-belge ayarları
        self.otomatik_gonderim = None
        self.gonderim_araligi = None
        self.hata_tekrar_deneme = None
        
        # Kargo ayarları
        self.varsayilan_tasiyici = None
        self.otomatik_etiket = None
        self.durum_sorgula_araligi = None
        
        # Kullanıcı ayarları
        self.sifre_uzunlugu = None
        self.oturum_suresi = None
        self.otomatik_kilit = None
        
        # Yetki ayarları
        self.admin_onay = None
        self.log_tutma = None
        
        # Rapor ayarları
        self.otomatik_rapor = None
        self.rapor_saati = None
        
        # Sistem ayarları
        self.log_seviye = None
        self.log_dosya_boyutu = None
        
        # Yedekleme ayarları
        self.otomatik_yedekleme_aktif = None
        self.yedekleme_araligi = None
        self.yedek_sayisi = None
    
    def ui_olustur(self):
        """Ana UI oluştur"""
        layout = QVBoxLayout(self)
        
        # Başlık
        baslik_frame = self.baslik_olustur()
        layout.addWidget(baslik_frame)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3498db;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
        """)
        
        # Sekmeleri ekle
        self.sekmeleri_ekle()
        layout.addWidget(self.tab_widget)
        
        # Alt butonlar
        alt_butonlar = self.ayar_butonlari.alt_butonlar_olustur()
        layout.addWidget(alt_butonlar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def baslik_olustur(self):
        """Başlık frame'i oluştur"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                color: white;
                padding: 15px;
                border-radius: 5px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        
        # Başlık
        baslik = QLabel("Sistem Ayarları")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        baslik.setFont(font)
        baslik.setStyleSheet("color: white;")
        layout.addWidget(baslik)
        
        layout.addStretch()
        
        # Değişiklik sayacı
        self.degisiklik_sayaci = QLabel("Değişiklik: 0")
        self.degisiklik_sayaci.setStyleSheet("""
            color: white;
            background-color: #e74c3c;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        """)
        layout.addWidget(self.degisiklik_sayaci)
        
        return frame
    
    def sekmeleri_ekle(self):
        """Sekmeleri ekle"""
        # Genel ayarlar
        genel_sayfa = self.ayar_formlari.genel_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(genel_sayfa, "Genel")
        
        # Veritabanı ayarları
        db_sayfa = self.ayar_formlari.veritabani_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(db_sayfa, "Veritabanı")
        
        # POS ayarları
        pos_sayfa = self.ayar_formlari.pos_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(pos_sayfa, "POS")
        
        # Stok ayarları
        stok_sayfa = self.ayar_formlari.stok_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(stok_sayfa, "Stok")
        
        # E-ticaret ayarları
        eticaret_sayfa = self.ayar_formlari.eticaret_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(eticaret_sayfa, "E-ticaret")
        
        # E-belge ayarları
        ebelge_sayfa = self.ayar_formlari.ebelge_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(ebelge_sayfa, "E-belge")
        
        # Kargo ayarları
        kargo_sayfa = self.ayar_formlari.kargo_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(kargo_sayfa, "Kargo")
        
        # Kullanıcı ayarları
        kullanici_sayfa = self.ayar_formlari.kullanici_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(kullanici_sayfa, "Kullanıcı")
        
        # Yetki ayarları
        yetki_sayfa = self.ayar_formlari.yetki_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(yetki_sayfa, "Yetki")
        
        # Rapor ayarları
        rapor_sayfa = self.ayar_formlari.rapor_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(rapor_sayfa, "Rapor")
        
        # Sistem ayarları
        sistem_sayfa = self.ayar_formlari.sistem_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(sistem_sayfa, "Sistem")
        
        # Yedekleme ayarları
        yedekleme_sayfa = self.ayar_formlari.yedekleme_ayarlar_sayfasi_olustur()
        self.tab_widget.addTab(yedekleme_sayfa, "Yedekleme")
    
    def baglantilari_kur(self):
        """Sinyal-slot bağlantılarını kur"""
        # Form alanları değişiklik takibi için bağlantılar kurulacak
        # Bu method AyarFormlari tarafından çağrılacak
        pass
    
    def ayarlari_yukle(self):
        """Mevcut ayarları yükle"""
        try:
            # Ayar servisinden mevcut ayarları çek
            ayar_servisi = self.servis_fabrikasi.ayar_servisi()
            ayarlar = self.servis_cagir_guvenli(ayar_servisi.tum_ayarlari_getir)
            
            if ayarlar:
                self.form_alanlarini_doldur(ayarlar)
                self.orijinal_degerler = ayarlar.copy()
            
        except Exception as e:
            self.hata_goster("Ayar Yükleme Hatası", f"Ayarlar yüklenirken hata oluştu: {str(e)}")
    
    def form_alanlarini_doldur(self, ayarlar):
        """Form alanlarını ayar değerleri ile doldur"""
        try:
            # Şirket bilgileri
            if self.sirket_adi and 'sirket_adi' in ayarlar:
                self.sirket_adi.setText(ayarlar['sirket_adi'])
            
            if self.vergi_no and 'vergi_no' in ayarlar:
                self.vergi_no.setText(ayarlar['vergi_no'])
            
            if self.adres and 'adres' in ayarlar:
                self.adres.setPlainText(ayarlar['adres'])
            
            # Uygulama ayarları
            if self.dil_combo and 'dil' in ayarlar:
                index = self.dil_combo.findText(ayarlar['dil'])
                if index >= 0:
                    self.dil_combo.setCurrentIndex(index)
            
            if self.tema_combo and 'tema' in ayarlar:
                index = self.tema_combo.findText(ayarlar['tema'])
                if index >= 0:
                    self.tema_combo.setCurrentIndex(index)
            
            if self.otomatik_yedekleme and 'otomatik_yedekleme' in ayarlar:
                self.otomatik_yedekleme.setChecked(ayarlar['otomatik_yedekleme'])
            
            # Veritabanı ayarları
            if self.db_host and 'db_host' in ayarlar:
                self.db_host.setText(ayarlar['db_host'])
            
            if self.db_port and 'db_port' in ayarlar:
                self.db_port.setValue(ayarlar['db_port'])
            
            if self.db_name and 'db_name' in ayarlar:
                self.db_name.setText(ayarlar['db_name'])
            
            if self.db_user and 'db_user' in ayarlar:
                self.db_user.setText(ayarlar['db_user'])
            
            # Diğer ayarlar için benzer şekilde devam et...
            
        except Exception as e:
            self.hata_goster("Form Doldurma Hatası", f"Form alanları doldurulurken hata: {str(e)}")
    
    def ayar_degisti_handler(self, ayar_adi, yeni_deger):
        """Ayar değişikliği handler'ı"""
        try:
            # Orijinal değer ile karşılaştır
            orijinal_deger = self.orijinal_degerler.get(ayar_adi)
            
            if orijinal_deger != yeni_deger:
                self.degisiklikler[ayar_adi] = yeni_deger
            else:
                # Değer orijinaline döndü, değişikliklerden çıkar
                if ayar_adi in self.degisiklikler:
                    del self.degisiklikler[ayar_adi]
            
            self.degisiklik_sayisini_guncelle()
            self.ayar_degisti.emit(ayar_adi, yeni_deger)
            
        except Exception as e:
            self.hata_goster("Değişiklik Takip Hatası", str(e))
    
    def degisiklik_sayisini_guncelle(self):
        """Değişiklik sayısını güncelle"""
        sayi = len(self.degisiklikler)
        self.degisiklik_sayaci.setText(f"Değişiklik: {sayi}")
        
        if sayi > 0:
            self.degisiklik_sayaci.setStyleSheet("""
                color: white;
                background-color: #e74c3c;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            """)
        else:
            self.degisiklik_sayaci.setStyleSheet("""
                color: white;
                background-color: #27ae60;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            """)
    
    def baglanti_test(self):
        """Veritabanı bağlantısını test et"""
        try:
            # Test için gerekli bilgileri topla
            test_ayarlari = {
                'host': self.db_host.text() if self.db_host else 'localhost',
                'port': self.db_port.value() if self.db_port else 5432,
                'database': self.db_name.text() if self.db_name else 'sontechsp',
                'user': self.db_user.text() if self.db_user else 'postgres',
                'password': self.db_password.text() if self.db_password else ''
            }
            
            # Doğrulama
            gecerli, hatalar = self.ayar_dogrulama.tum_ayarlari_dogrula(test_ayarlari)
            
            if not gecerli:
                self.hata_goster("Doğrulama Hatası", "\n".join(hatalar))
                return
            
            # Bağlantı testi
            self.islem_baslat("Veritabanı bağlantısı test ediliyor...")
            
            # Ayar servisini çağır
            ayar_servisi = self.servis_fabrikasi.ayar_servisi()
            sonuc = self.servis_cagir_guvenli(ayar_servisi.baglanti_test, test_ayarlari)
            
            self.islem_bitir()
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Veritabanı bağlantısı başarılı!")
            else:
                self.hata_goster("Bağlantı Hatası", "Veritabanı bağlantısı kurulamadı")
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Test Hatası", f"Bağlantı testi sırasında hata: {str(e)}")
    
    def islem_baslat(self, mesaj="İşlem yapılıyor..."):
        """İşlem başlat - progress bar göster"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.setEnabled(False)
        QApplication.processEvents()
    
    def islem_bitir(self):
        """İşlem bitir - progress bar gizle"""
        self.progress_bar.setVisible(False)
        self.setEnabled(True)
        QApplication.processEvents()
    
    def ayarlari_dogrula(self):
        """Tüm ayarları doğrula"""
        try:
            # Mevcut form değerlerini topla
            ayar_verileri = self.form_degerlerini_topla()
            
            # Doğrulama yap
            gecerli, hatalar = self.ayar_dogrulama.tum_ayarlari_dogrula(ayar_verileri)
            
            if not gecerli:
                hata_mesaji = "Aşağıdaki hatalar düzeltilmelidir:\n\n" + "\n".join(f"• {hata}" for hata in hatalar)
                self.hata_goster("Doğrulama Hataları", hata_mesaji)
                return False
            
            return True
            
        except Exception as e:
            self.hata_goster("Doğrulama Hatası", f"Ayar doğrulama sırasında hata: {str(e)}")
            return False
    
    def form_degerlerini_topla(self):
        """Form alanlarından değerleri topla"""
        degerler = {}
        
        try:
            # Şirket bilgileri
            if self.sirket_adi:
                degerler['sirket_adi'] = self.sirket_adi.text()
            if self.vergi_no:
                degerler['vergi_no'] = self.vergi_no.text()
            if self.adres:
                degerler['adres'] = self.adres.toPlainText()
            
            # Veritabanı ayarları
            if self.db_host:
                degerler['db_host'] = self.db_host.text()
            if self.db_port:
                degerler['db_port'] = self.db_port.value()
            if self.db_name:
                degerler['db_name'] = self.db_name.text()
            if self.db_user:
                degerler['db_user'] = self.db_user.text()
            if self.db_password:
                degerler['db_password'] = self.db_password.text()
            if self.baglanti_havuzu:
                degerler['baglanti_havuzu'] = self.baglanti_havuzu.value()
            if self.sorgu_timeout:
                degerler['sorgu_timeout'] = self.sorgu_timeout.value()
            
            # Güvenlik ayarları
            if self.sifre_uzunlugu:
                degerler['sifre_uzunlugu'] = self.sifre_uzunlugu.value()
            if self.oturum_suresi:
                degerler['oturum_suresi'] = self.oturum_suresi.value()
            
            # Stok ayarları
            if self.kritik_stok_seviye:
                degerler['kritik_stok_seviye'] = self.kritik_stok_seviye.value()
            
            # E-ticaret ayarları
            if self.siparis_cekme_araligi:
                degerler['siparis_cekme_araligi'] = self.siparis_cekme_araligi.value()
            
            # E-belge ayarları
            if self.gonderim_araligi:
                degerler['gonderim_araligi'] = self.gonderim_araligi.value()
            if self.hata_tekrar_deneme:
                degerler['hata_tekrar_deneme'] = self.hata_tekrar_deneme.value()
            
            # Kargo ayarları
            if self.durum_sorgula_araligi:
                degerler['durum_sorgula_araligi'] = self.durum_sorgula_araligi.value()
            
            # Sistem ayarları
            if self.log_dosya_boyutu:
                degerler['log_dosya_boyutu'] = self.log_dosya_boyutu.value()
            
            # Yedekleme ayarları
            if self.yedek_sayisi:
                degerler['yedek_sayisi'] = self.yedek_sayisi.value()
            
            return degerler
            
        except Exception as e:
            self.hata_goster("Veri Toplama Hatası", f"Form değerleri toplanırken hata: {str(e)}")
            return {}
    
    def closeEvent(self, event):
        """Pencere kapatılırken kontrol"""
        if self.degisiklikler:
            cevap = QMessageBox.question(
                self,
                "Kaydedilmemiş Değişiklikler",
                "Kaydedilmemiş değişiklikler var. Çıkmak istediğinizden emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if cevap == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        event.accept()