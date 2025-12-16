# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.ui.odeme_ekrani
# Description: POS Ödeme Ekranı PyQt6 arayüzü
# Changelog:
# - İlk oluşturma

"""
POS Ödeme Ekranı PyQt6 Arayüzü

Ödeme yöntemi seçimi ve tutar girişi ekranı.
Tek ve parçalı ödeme işlemlerini destekler.
Sadece service katmanını çağırır.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QDoubleSpinBox, QFrame, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QKeySequence, QShortcut

from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran
from sontechsp.uygulama.moduller.pos.servisler.odeme_service import OdemeService
from sontechsp.uygulama.cekirdek.oturum import oturum_baglamini_al


class OdemeEkrani(TabanEkran):
    """
    POS Ödeme Ekranı
    
    Ödeme yöntemi seçimi ve tutar doğrulama işlemlerini sağlar.
    Requirements: 3.1, 3.2, 3.3
    """
    
    # Sinyaller
    odeme_tamamlandi = pyqtSignal(dict)
    odeme_iptal_edildi = pyqtSignal()
    
    def __init__(self, sepet_bilgisi: Dict[str, Any], parent: Optional[QWidget] = None):
        """Ödeme ekranını başlatır"""
        # Sepet bilgisi önce atanmalı (TabanEkran __init__ içinde _icerik_olustur çağrılıyor)
        self.sepet_bilgisi = sepet_bilgisi
        self.sepet_toplami = Decimal(str(sepet_bilgisi.get('toplam_tutar', '0.00')))
        
        super().__init__("POS Ödeme", parent)
        
        # Servisler
        self.odeme_service = OdemeService()
        self.oturum = oturum_baglamini_al()
        
        # Ödeme durumu
        self.odemeler: List[Dict[str, Any]] = []
        self.toplam_odenen = Decimal('0.00')
        
        # Kısayolları kur
        self._kisa_yollari_kur()
        
        # İlk özet güncelleme
        self._ozet_guncelle()
        
        # İlk odaklanma
        self.odeme_tutari_spin.setFocus()
    
    def _icerik_olustur(self):
        """Ekran içeriğini oluşturur"""
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.icerik_layout.addWidget(splitter)
        
        # Sol panel - Ödeme girişi
        sol_panel = self._sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Ödeme listesi ve özet
        sag_panel = self._sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([400, 300])
    
    def _sol_panel_olustur(self) -> QWidget:
        """Sol paneli oluşturur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Sepet özeti
        sepet_grubu = self._sepet_ozeti_olustur()
        layout.addWidget(sepet_grubu)
        
        # Ödeme girişi
        odeme_grubu = self._odeme_girisi_olustur()
        layout.addWidget(odeme_grubu)
        
        # Kontrol butonları
        kontrol_grubu = self._kontrol_butonlari_olustur()
        layout.addWidget(kontrol_grubu)
        
        layout.addStretch()
        return panel
    
    def _sepet_ozeti_olustur(self) -> QGroupBox:
        """Sepet özet grubunu oluşturur"""
        grup = QGroupBox("Sepet Özeti")
        layout = QGridLayout(grup)
        
        # Sepet ID
        layout.addWidget(QLabel("Sepet No:"), 0, 0)
        sepet_id_label = QLabel(str(self.sepet_bilgisi.get('id', 'N/A')))
        sepet_id_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(sepet_id_label, 0, 1)
        
        # Toplam tutar
        layout.addWidget(QLabel("Toplam Tutar:"), 1, 0)
        self.sepet_toplam_label = QLabel(f"{self.sepet_toplami:.2f} ₺")
        self.sepet_toplam_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.sepet_toplam_label.setStyleSheet("color: #2c3e50; background: #ecf0f1; padding: 8px;")
        layout.addWidget(self.sepet_toplam_label, 1, 1)
        
        return grup
    
    def _odeme_girisi_olustur(self) -> QGroupBox:
        """Ödeme giriş grubunu oluşturur"""
        grup = QGroupBox("Ödeme Bilgileri")
        layout = QGridLayout(grup)
        
        # Ödeme türü
        layout.addWidget(QLabel("Ödeme Türü:"), 0, 0)
        self.odeme_turu_combo = QComboBox()
        self.odeme_turu_combo.addItems([
            "Nakit", "Kredi Kartı", "Banka Kartı", 
            "Çek", "Senet", "Havale/EFT"
        ])
        layout.addWidget(self.odeme_turu_combo, 0, 1, 1, 2)
        
        # Ödeme tutarı
        layout.addWidget(QLabel("Tutar:"), 1, 0)
        self.odeme_tutari_spin = QDoubleSpinBox()
        self.odeme_tutari_spin.setMinimum(0.01)
        self.odeme_tutari_spin.setMaximum(999999.99)
        self.odeme_tutari_spin.setDecimals(2)
        self.odeme_tutari_spin.setSuffix(" ₺")
        self.odeme_tutari_spin.setValue(float(self.sepet_toplami))
        layout.addWidget(self.odeme_tutari_spin, 1, 1)
        
        # Hızlı tutar butonu
        self.tam_tutar_buton = QPushButton("Tam Tutar")
        self.tam_tutar_buton.clicked.connect(self._tam_tutar_ayarla)
        layout.addWidget(self.tam_tutar_buton, 1, 2)
        
        # Referans no (kart ödemeleri için)
        layout.addWidget(QLabel("Referans No:"), 2, 0)
        self.referans_edit = QLineEdit()
        self.referans_edit.setPlaceholderText("Kart ödemeleri için...")
        layout.addWidget(self.referans_edit, 2, 1, 1, 2)
        
        # Parçalı ödeme seçeneği
        self.parcali_odeme_check = QCheckBox("Parçalı Ödeme")
        self.parcali_odeme_check.toggled.connect(self._parcali_odeme_degisti)
        layout.addWidget(self.parcali_odeme_check, 3, 0, 1, 3)
        
        # Ödeme ekle butonu
        self.odeme_ekle_buton = QPushButton("Ödeme Ekle (F1)")
        self.odeme_ekle_buton.clicked.connect(self._odeme_ekle)
        layout.addWidget(self.odeme_ekle_buton, 4, 0, 1, 3)
        
        return grup
    
    def _kontrol_butonlari_olustur(self) -> QGroupBox:
        """Kontrol butonları grubunu oluşturur"""
        grup = QGroupBox("İşlem Kontrolleri")
        layout = QVBoxLayout(grup)
        
        # Satışı tamamla
        self.tamamla_buton = QPushButton("Satışı Tamamla (F2)")
        self.tamamla_buton.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.tamamla_buton.setStyleSheet("background: #27ae60; color: white; padding: 10px;")
        self.tamamla_buton.clicked.connect(self._satisi_tamamla)
        layout.addWidget(self.tamamla_buton)
        
        # İptal et
        self.iptal_buton = QPushButton("İptal Et (Esc)")
        self.iptal_buton.setStyleSheet("background: #e74c3c; color: white; padding: 8px;")
        self.iptal_buton.clicked.connect(self._odeme_iptal)
        layout.addWidget(self.iptal_buton)
        
        return grup
    
    def _sag_panel_olustur(self) -> QWidget:
        """Sağ paneli oluşturur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Ödeme listesi başlığı
        baslik = QLabel("Ödeme Listesi")
        baslik.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(baslik)
        
        # Ödeme tablosu
        self.odeme_tablo = QTableWidget()
        self.odeme_tablo.setColumnCount(4)
        self.odeme_tablo.setHorizontalHeaderLabels([
            "Ödeme Türü", "Tutar", "Referans", "İşlem"
        ])
        
        # Tablo ayarları
        header = self.odeme_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.odeme_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.odeme_tablo.setAlternatingRowColors(True)
        
        layout.addWidget(self.odeme_tablo)
        
        # Ödeme özeti
        ozet_grubu = self._odeme_ozeti_olustur()
        layout.addWidget(ozet_grubu)
        
        return panel
    
    def _odeme_ozeti_olustur(self) -> QGroupBox:
        """Ödeme özet grubunu oluşturur"""
        grup = QGroupBox("Ödeme Özeti")
        layout = QGridLayout(grup)
        
        # Toplam ödenen
        layout.addWidget(QLabel("Toplam Ödenen:"), 0, 0)
        self.toplam_odenen_label = QLabel("0,00 ₺")
        self.toplam_odenen_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.toplam_odenen_label, 0, 1)
        
        # Kalan tutar
        layout.addWidget(QLabel("Kalan Tutar:"), 1, 0)
        self.kalan_tutar_label = QLabel(f"{self.sepet_toplami:.2f} ₺")
        self.kalan_tutar_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.kalan_tutar_label.setStyleSheet("color: #e74c3c;")
        layout.addWidget(self.kalan_tutar_label, 1, 1)
        
        # Para üstü
        layout.addWidget(QLabel("Para Üstü:"), 2, 0)
        self.para_ustu_label = QLabel("0,00 ₺")
        self.para_ustu_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.para_ustu_label.setStyleSheet("color: #27ae60;")
        layout.addWidget(self.para_ustu_label, 2, 1)
        
        return grup
    
    def _kisa_yollari_kur(self):
        """Klavye kısayollarını kurar"""
        # F1 - Ödeme ekle
        QShortcut(QKeySequence("F1"), self, self._odeme_ekle)
        
        # F2 - Satışı tamamla
        QShortcut(QKeySequence("F2"), self, self._satisi_tamamla)
        
        # Esc - İptal
        QShortcut(QKeySequence("Escape"), self, self._odeme_iptal)
        
        # Enter - Ödeme ekle
        QShortcut(QKeySequence("Return"), self, self._odeme_ekle)
    
    @pyqtSlot()
    def _tam_tutar_ayarla(self):
        """Kalan tutarı ödeme tutarı olarak ayarlar"""
        kalan = self.sepet_toplami - self.toplam_odenen
        if kalan > 0:
            self.odeme_tutari_spin.setValue(float(kalan))
    
    @pyqtSlot(bool)
    def _parcali_odeme_degisti(self, aktif: bool):
        """Parçalı ödeme seçeneği değiştiğinde"""
        if not aktif and len(self.odemeler) > 0:
            # Parçalı ödeme kapatılırsa mevcut ödemeleri temizle
            if self.mesaj_yoneticisi.onay_iste("Mevcut ödemeler silinecek. Devam edilsin mi?"):
                self.odemeler.clear()
                self._odeme_listesi_guncelle()
    
    @pyqtSlot()
    def _odeme_ekle(self):
        """Ödeme ekler"""
        odeme_turu = self.odeme_turu_combo.currentText()
        tutar = Decimal(str(self.odeme_tutari_spin.value()))
        referans = self.referans_edit.text().strip()
        
        # Validasyon
        if tutar <= 0:
            self.mesaj_yoneticisi.uyari_goster("Ödeme tutarı pozitif olmalıdır")
            return
        
        # Parçalı ödeme kontrolü
        if not self.parcali_odeme_check.isChecked():
            # Tek ödeme - tam tutar olmalı
            if tutar != self.sepet_toplami:
                self.mesaj_yoneticisi.uyari_goster(
                    f"Tek ödemede tutar sepet toplamına eşit olmalıdır: {self.sepet_toplami:.2f} ₺"
                )
                return
        else:
            # Parçalı ödeme - toplam aşmamalı
            if self.toplam_odenen + tutar > self.sepet_toplami:
                self.mesaj_yoneticisi.uyari_goster("Ödeme tutarı sepet toplamını aşamaz")
                return
        
        try:
            self.yukleme_basladi.emit()
            
            # Ödeme bilgisi oluştur
            odeme_bilgisi = {
                'odeme_turu': odeme_turu,
                'tutar': tutar,
                'referans_no': referans or None
            }
            
            # Listeye ekle
            self.odemeler.append(odeme_bilgisi)
            self.toplam_odenen += tutar
            
            # Alanları temizle
            self.odeme_tutari_spin.setValue(0.00)
            self.referans_edit.clear()
            
            # Listesi güncelle
            self._odeme_listesi_guncelle()
            
            # Başarı mesajı
            self.alt_arac_yoneticisi.durum_guncelle(f"Ödeme eklendi: {tutar:.2f} ₺", 2)
            
        except Exception as e:
            self.logger.error(f"Ödeme ekleme hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Ödeme eklenemedi: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _satisi_tamamla(self):
        """Satışı tamamlar"""
        # Ödeme kontrolü
        if len(self.odemeler) == 0:
            self.mesaj_yoneticisi.uyari_goster("En az bir ödeme eklemelisiniz")
            return
        
        # Tutar kontrolü
        if self.toplam_odenen < self.sepet_toplami:
            kalan = self.sepet_toplami - self.toplam_odenen
            self.mesaj_yoneticisi.uyari_goster(f"Eksik ödeme: {kalan:.2f} ₺")
            return
        
        # Onay iste
        if not self.mesaj_yoneticisi.onay_iste("Satış tamamlansın mı?"):
            return
        
        try:
            self.yukleme_basladi.emit()
            
            # Ödeme işlemini tamamla
            sonuc = self.odeme_service.odeme_tamamla(
                sepet_id=self.sepet_bilgisi['id'],
                odemeler=self.odemeler
            )
            
            if sonuc:
                # Başarı mesajı
                self.mesaj_yoneticisi.bilgi_goster("Satış başarıyla tamamlandı!")
                
                # Sinyal gönder
                self.odeme_tamamlandi.emit({
                    'sepet_id': self.sepet_bilgisi['id'],
                    'toplam_tutar': self.sepet_toplami,
                    'odemeler': self.odemeler,
                    'para_ustu': self.toplam_odenen - self.sepet_toplami
                })
                
                # Ekranı kapat
                self.close()
            
        except Exception as e:
            self.logger.error(f"Satış tamamlama hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Satış tamamlanamadı: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _odeme_iptal(self):
        """Ödeme işlemini iptal eder"""
        if self.mesaj_yoneticisi.onay_iste("Ödeme işlemi iptal edilsin mi?"):
            self.odeme_iptal_edildi.emit()
            self.close()
    
    def _odeme_listesi_guncelle(self):
        """Ödeme listesini günceller"""
        self.odeme_tablo.setRowCount(len(self.odemeler))
        
        for row, odeme in enumerate(self.odemeler):
            # Ödeme türü
            self.odeme_tablo.setItem(row, 0, QTableWidgetItem(odeme['odeme_turu']))
            
            # Tutar
            tutar_item = QTableWidgetItem(f"{odeme['tutar']:.2f} ₺")
            tutar_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.odeme_tablo.setItem(row, 1, tutar_item)
            
            # Referans
            referans = odeme.get('referans_no', '') or '-'
            self.odeme_tablo.setItem(row, 2, QTableWidgetItem(referans))
            
            # İşlem butonu (placeholder)
            islem_item = QTableWidgetItem("Sil")
            self.odeme_tablo.setItem(row, 3, islem_item)
        
        # Özet güncelle
        self._ozet_guncelle()
    
    def _ozet_guncelle(self):
        """Ödeme özetini günceller"""
        # Toplam ödenen
        self.toplam_odenen_label.setText(f"{self.toplam_odenen:.2f} ₺")
        
        # Kalan tutar
        kalan = self.sepet_toplami - self.toplam_odenen
        self.kalan_tutar_label.setText(f"{kalan:.2f} ₺")
        
        if kalan <= 0:
            self.kalan_tutar_label.setStyleSheet("color: #27ae60;")
        else:
            self.kalan_tutar_label.setStyleSheet("color: #e74c3c;")
        
        # Para üstü
        para_ustu = max(Decimal('0'), self.toplam_odenen - self.sepet_toplami)
        self.para_ustu_label.setText(f"{para_ustu:.2f} ₺")
        
        # Tamamla butonunu aktifleştir/pasifleştir
        self.tamamla_buton.setEnabled(self.toplam_odenen >= self.sepet_toplami)
    
    def yenile(self):
        """Ekranı yeniler"""
        self.logger.info("Ödeme ekranı yenileniyor")
        self._ozet_guncelle()
        self.alt_arac_yoneticisi.durum_guncelle("Yenilendi", 2)