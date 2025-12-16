# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.ui.iade_ekrani
# Description: POS İade Ekranı PyQt6 arayüzü
# Changelog:
# - İlk oluşturma

"""
POS İade Ekranı PyQt6 Arayüzü

İade işlemi başlatma ve kalem seçimi ekranı.
İade tutarı hesaplama ve onaylama işlemlerini destekler.
Sadece service katmanını çağırır.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QDoubleSpinBox, QFrame, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QCheckBox, QSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QKeySequence, QShortcut

from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran
from sontechsp.uygulama.moduller.pos.servisler.iade_service import IadeService
from sontechsp.uygulama.cekirdek.oturum import oturum_baglamini_al


class IadeEkrani(TabanEkran):
    """
    POS İade Ekranı
    
    İade işlemi başlatma, kalem seçimi ve tutar hesaplama işlemlerini sağlar.
    Requirements: 4.1, 4.2, 4.3
    """
    
    # Sinyaller
    iade_tamamlandi = pyqtSignal(dict)
    iade_iptal_edildi = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """İade ekranını başlatır"""
        super().__init__("POS İade", parent)
        
        # Servisler
        self.iade_service = IadeService()
        self.oturum = oturum_baglamini_al()
        
        # İade durumu
        self.orijinal_satis: Optional[Dict[str, Any]] = None
        self.iade_kalemleri: List[Dict[str, Any]] = []
        self.toplam_iade_tutari = Decimal('0.00')
        
        # Kısayolları kur
        self._kisa_yollari_kur()
        
        # İlk odaklanma
        self.satis_no_edit.setFocus()
    
    def _icerik_olustur(self):
        """Ekran içeriğini oluşturur"""
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.icerik_layout.addWidget(splitter)
        
        # Üst panel - Satış arama ve bilgileri
        ust_panel = self._ust_panel_olustur()
        splitter.addWidget(ust_panel)
        
        # Alt panel - İade kalemleri ve işlemler
        alt_panel = self._alt_panel_olustur()
        splitter.addWidget(alt_panel)
        
        # Splitter oranları
        splitter.setSizes([200, 400])
    
    def _ust_panel_olustur(self) -> QWidget:
        """Üst paneli oluşturur"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Satış arama grubu
        arama_grubu = self._satis_arama_olustur()
        layout.addWidget(arama_grubu)
        
        # Satış bilgileri grubu
        bilgi_grubu = self._satis_bilgileri_olustur()
        layout.addWidget(bilgi_grubu)
        
        return panel
    
    def _satis_arama_olustur(self) -> QGroupBox:
        """Satış arama grubunu oluşturur"""
        grup = QGroupBox("Satış Arama")
        layout = QGridLayout(grup)
        
        # Satış no
        layout.addWidget(QLabel("Satış No:"), 0, 0)
        self.satis_no_edit = QLineEdit()
        self.satis_no_edit.setPlaceholderText("Satış numarası girin...")
        self.satis_no_edit.returnPressed.connect(self._satis_ara)
        layout.addWidget(self.satis_no_edit, 0, 1)
        
        # Fiş no
        layout.addWidget(QLabel("Fiş No:"), 1, 0)
        self.fis_no_edit = QLineEdit()
        self.fis_no_edit.setPlaceholderText("Fiş numarası girin...")
        self.fis_no_edit.returnPressed.connect(self._satis_ara)
        layout.addWidget(self.fis_no_edit, 1, 1)
        
        # Arama butonu
        self.ara_buton = QPushButton("Satış Ara (F1)")
        self.ara_buton.clicked.connect(self._satis_ara)
        layout.addWidget(self.ara_buton, 2, 0, 1, 2)
        
        return grup
    
    def _satis_bilgileri_olustur(self) -> QGroupBox:
        """Satış bilgileri grubunu oluşturur"""
        grup = QGroupBox("Satış Bilgileri")
        layout = QGridLayout(grup)
        
        # Satış tarihi
        layout.addWidget(QLabel("Satış Tarihi:"), 0, 0)
        self.satis_tarihi_label = QLabel("-")
        layout.addWidget(self.satis_tarihi_label, 0, 1)
        
        # Kasiyer
        layout.addWidget(QLabel("Kasiyer:"), 1, 0)
        self.kasiyer_label = QLabel("-")
        layout.addWidget(self.kasiyer_label, 1, 1)
        
        # Toplam tutar
        layout.addWidget(QLabel("Toplam Tutar:"), 2, 0)
        self.satis_toplam_label = QLabel("-")
        self.satis_toplam_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.satis_toplam_label, 2, 1)
        
        # Durum
        layout.addWidget(QLabel("Durum:"), 3, 0)
        self.satis_durum_label = QLabel("-")
        layout.addWidget(self.satis_durum_label, 3, 1)
        
        return grup
    
    def _alt_panel_olustur(self) -> QWidget:
        """Alt paneli oluşturur"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Sol - İade kalemleri tablosu
        sol_panel = self._iade_kalemleri_olustur()
        layout.addWidget(sol_panel)
        
        # Sağ - İade işlemleri
        sag_panel = self._iade_islemleri_olustur()
        layout.addWidget(sag_panel)
        
        return panel
    
    def _iade_kalemleri_olustur(self) -> QWidget:
        """İade kalemleri panelini oluşturur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Başlık
        baslik = QLabel("Satış Kalemleri")
        baslik.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(baslik)
        
        # Kalemler tablosu
        self.kalemler_tablo = QTableWidget()
        self.kalemler_tablo.setColumnCount(6)
        self.kalemler_tablo.setHorizontalHeaderLabels([
            "Seç", "Ürün Adı", "Satılan", "İade Adet", "Birim Fiyat", "İade Tutar"
        ])
        
        # Tablo ayarları
        header = self.kalemler_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Seç
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Ürün Adı
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Satılan
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # İade Adet
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Birim Fiyat
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # İade Tutar
        
        self.kalemler_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.kalemler_tablo.setAlternatingRowColors(True)
        
        layout.addWidget(self.kalemler_tablo)
        
        return panel
    
    def _iade_islemleri_olustur(self) -> QWidget:
        """İade işlemleri panelini oluşturur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # İade nedeni
        neden_grubu = self._iade_nedeni_olustur()
        layout.addWidget(neden_grubu)
        
        # İade özeti
        ozet_grubu = self._iade_ozeti_olustur()
        layout.addWidget(ozet_grubu)
        
        # Kontrol butonları
        kontrol_grubu = self._iade_kontrolleri_olustur()
        layout.addWidget(kontrol_grubu)
        
        layout.addStretch()
        return panel
    
    def _iade_nedeni_olustur(self) -> QGroupBox:
        """İade nedeni grubunu oluşturur"""
        grup = QGroupBox("İade Nedeni")
        layout = QVBoxLayout(grup)
        
        # Neden seçimi
        self.neden_combo = QComboBox()
        self.neden_combo.addItems([
            "Müşteri memnuniyetsizliği",
            "Ürün hasarlı",
            "Yanlış ürün",
            "Boyut/renk uyumsuzluğu",
            "Kasiyer hatası",
            "Diğer"
        ])
        layout.addWidget(self.neden_combo)
        
        # Açıklama
        self.aciklama_edit = QTextEdit()
        self.aciklama_edit.setMaximumHeight(80)
        self.aciklama_edit.setPlaceholderText("İade açıklaması (opsiyonel)...")
        layout.addWidget(self.aciklama_edit)
        
        return grup
    
    def _iade_ozeti_olustur(self) -> QGroupBox:
        """İade özet grubunu oluşturur"""
        grup = QGroupBox("İade Özeti")
        layout = QGridLayout(grup)
        
        # Seçilen kalem sayısı
        layout.addWidget(QLabel("Seçilen Kalem:"), 0, 0)
        self.secilen_kalem_label = QLabel("0")
        self.secilen_kalem_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.secilen_kalem_label, 0, 1)
        
        # Toplam iade tutarı
        layout.addWidget(QLabel("İade Tutarı:"), 1, 0)
        self.iade_tutari_label = QLabel("0,00 ₺")
        self.iade_tutari_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.iade_tutari_label.setStyleSheet("color: #e74c3c; background: #ecf0f1; padding: 5px;")
        layout.addWidget(self.iade_tutari_label, 1, 1)
        
        return grup
    
    def _iade_kontrolleri_olustur(self) -> QGroupBox:
        """İade kontrol butonları grubunu oluşturur"""
        grup = QGroupBox("İşlem Kontrolleri")
        layout = QVBoxLayout(grup)
        
        # Tümünü seç/kaldır
        self.tumunu_sec_buton = QPushButton("Tümünü Seç (F2)")
        self.tumunu_sec_buton.clicked.connect(self._tumunu_sec)
        layout.addWidget(self.tumunu_sec_buton)
        
        self.secimi_kaldir_buton = QPushButton("Seçimi Kaldır (F3)")
        self.secimi_kaldir_buton.clicked.connect(self._secimi_kaldir)
        layout.addWidget(self.secimi_kaldir_buton)
        
        # İade işlemi
        self.iade_onayla_buton = QPushButton("İadeyi Onayla (F4)")
        self.iade_onayla_buton.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.iade_onayla_buton.setStyleSheet("background: #e74c3c; color: white; padding: 8px;")
        self.iade_onayla_buton.clicked.connect(self._iade_onayla)
        self.iade_onayla_buton.setEnabled(False)
        layout.addWidget(self.iade_onayla_buton)
        
        # İptal
        self.iptal_buton = QPushButton("İptal Et (Esc)")
        self.iptal_buton.clicked.connect(self._iade_iptal)
        layout.addWidget(self.iptal_buton)
        
        return grup
    
    def _kisa_yollari_kur(self):
        """Klavye kısayollarını kurar"""
        # F1 - Satış ara
        QShortcut(QKeySequence("F1"), self, self._satis_ara)
        
        # F2 - Tümünü seç
        QShortcut(QKeySequence("F2"), self, self._tumunu_sec)
        
        # F3 - Seçimi kaldır
        QShortcut(QKeySequence("F3"), self, self._secimi_kaldir)
        
        # F4 - İadeyi onayla
        QShortcut(QKeySequence("F4"), self, self._iade_onayla)
        
        # Esc - İptal
        QShortcut(QKeySequence("Escape"), self, self._iade_iptal)
        
        # Enter - Satış ara
        QShortcut(QKeySequence("Return"), self, self._satis_ara)
    
    @pyqtSlot()
    def _satis_ara(self):
        """Satış arar"""
        satis_no = self.satis_no_edit.text().strip()
        fis_no = self.fis_no_edit.text().strip()
        
        if not satis_no and not fis_no:
            self.mesaj_yoneticisi.uyari_goster("Satış no veya fiş no girin")
            return
        
        try:
            self.yukleme_basladi.emit()
            
            # Satış bilgisini ara
            if satis_no:
                satis_bilgisi = self.iade_service.satis_bilgisi_getir(int(satis_no))
            else:
                satis_bilgisi = self.iade_service.fis_no_ile_satis_getir(fis_no)
            
            if satis_bilgisi:
                self.orijinal_satis = satis_bilgisi
                self._satis_bilgilerini_goster()
                self._satis_kalemlerini_yukle()
                
                self.alt_arac_yoneticisi.durum_guncelle("Satış bulundu", 2)
            else:
                self.mesaj_yoneticisi.uyari_goster("Satış bulunamadı")
                self._satis_bilgilerini_temizle()
            
        except ValueError:
            self.mesaj_yoneticisi.uyari_goster("Geçerli bir satış numarası girin")
        except Exception as e:
            self.logger.error(f"Satış arama hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Satış aranamadı: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    def _satis_bilgilerini_goster(self):
        """Satış bilgilerini gösterir"""
        if not self.orijinal_satis:
            return
        
        # Tarih formatla (mock)
        tarih = self.orijinal_satis.get('satis_tarihi', 'Bilinmiyor')
        self.satis_tarihi_label.setText(str(tarih))
        
        # Kasiyer
        kasiyer = self.orijinal_satis.get('kasiyer_adi', 'Bilinmiyor')
        self.kasiyer_label.setText(kasiyer)
        
        # Toplam tutar
        toplam = self.orijinal_satis.get('toplam_tutar', Decimal('0'))
        self.satis_toplam_label.setText(f"{toplam:.2f} ₺")
        
        # Durum
        durum = self.orijinal_satis.get('durum', 'Bilinmiyor')
        self.satis_durum_label.setText(durum)
    
    def _satis_bilgilerini_temizle(self):
        """Satış bilgilerini temizler"""
        self.satis_tarihi_label.setText("-")
        self.kasiyer_label.setText("-")
        self.satis_toplam_label.setText("-")
        self.satis_durum_label.setText("-")
        
        self.orijinal_satis = None
        self.kalemler_tablo.setRowCount(0)
        self._iade_ozeti_guncelle()
    
    def _satis_kalemlerini_yukle(self):
        """Satış kalemlerini yükler"""
        if not self.orijinal_satis:
            return
        
        try:
            # Satış kalemlerini al (mock veri)
            kalemler = self._mock_satis_kalemleri_getir()
            
            self.kalemler_tablo.setRowCount(len(kalemler))
            
            for row, kalem in enumerate(kalemler):
                # Seçim checkbox'ı
                secim_check = QCheckBox()
                secim_check.toggled.connect(self._kalem_secim_degisti)
                self.kalemler_tablo.setCellWidget(row, 0, secim_check)
                
                # Ürün adı
                self.kalemler_tablo.setItem(row, 1, QTableWidgetItem(kalem.get('urun_adi', '')))
                
                # Satılan adet
                satilan_item = QTableWidgetItem(str(kalem.get('adet', 0)))
                satilan_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.kalemler_tablo.setItem(row, 2, satilan_item)
                
                # İade adet (spin box)
                iade_spin = QSpinBox()
                iade_spin.setMinimum(0)
                iade_spin.setMaximum(kalem.get('adet', 0))
                iade_spin.setValue(0)
                iade_spin.valueChanged.connect(self._iade_adet_degisti)
                self.kalemler_tablo.setCellWidget(row, 3, iade_spin)
                
                # Birim fiyat
                birim_fiyat = kalem.get('birim_fiyat', Decimal('0'))
                fiyat_item = QTableWidgetItem(f"{birim_fiyat:.2f} ₺")
                fiyat_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.kalemler_tablo.setItem(row, 4, fiyat_item)
                
                # İade tutar (hesaplanacak)
                tutar_item = QTableWidgetItem("0,00 ₺")
                tutar_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.kalemler_tablo.setItem(row, 5, tutar_item)
            
        except Exception as e:
            self.logger.error(f"Kalem yükleme hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Kalemler yüklenemedi: {str(e)}")
    
    def _mock_satis_kalemleri_getir(self) -> List[Dict[str, Any]]:
        """Mock satış kalemleri (gerçek implementasyonda service'den gelecek)"""
        return [
            {
                'id': 1,
                'urun_adi': 'Örnek Ürün 1',
                'adet': 2,
                'birim_fiyat': Decimal('15.50'),
                'toplam_tutar': Decimal('31.00')
            },
            {
                'id': 2,
                'urun_adi': 'Örnek Ürün 2',
                'adet': 1,
                'birim_fiyat': Decimal('25.75'),
                'toplam_tutar': Decimal('25.75')
            }
        ]
    
    @pyqtSlot(bool)
    def _kalem_secim_degisti(self, secili: bool):
        """Kalem seçimi değiştiğinde"""
        self._iade_ozeti_guncelle()
    
    @pyqtSlot(int)
    def _iade_adet_degisti(self, yeni_adet: int):
        """İade adedi değiştiğinde"""
        self._iade_ozeti_guncelle()
    
    @pyqtSlot()
    def _tumunu_sec(self):
        """Tüm kalemleri seçer"""
        for row in range(self.kalemler_tablo.rowCount()):
            checkbox = self.kalemler_tablo.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
            
            # İade adedini maksimuma ayarla
            spin = self.kalemler_tablo.cellWidget(row, 3)
            if spin:
                spin.setValue(spin.maximum())
    
    @pyqtSlot()
    def _secimi_kaldir(self):
        """Tüm seçimleri kaldırır"""
        for row in range(self.kalemler_tablo.rowCount()):
            checkbox = self.kalemler_tablo.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
            
            # İade adedini sıfırla
            spin = self.kalemler_tablo.cellWidget(row, 3)
            if spin:
                spin.setValue(0)
    
    @pyqtSlot()
    def _iade_onayla(self):
        """İadeyi onaylar"""
        # Seçim kontrolü
        secilen_kalemler = self._secilen_kalemleri_al()
        if not secilen_kalemler:
            self.mesaj_yoneticisi.uyari_goster("En az bir kalem seçmelisiniz")
            return
        
        # Neden kontrolü
        neden = self.neden_combo.currentText()
        aciklama = self.aciklama_edit.toPlainText().strip()
        
        # Onay iste
        if not self.mesaj_yoneticisi.onay_iste(
            f"İade işlemi onaylansın mı?\n"
            f"Kalem sayısı: {len(secilen_kalemler)}\n"
            f"Toplam tutar: {self.toplam_iade_tutari:.2f} ₺"
        ):
            return
        
        try:
            self.yukleme_basladi.emit()
            
            # İade işlemini gerçekleştir
            iade_bilgisi = {
                'orijinal_satis_id': self.orijinal_satis['id'],
                'kalemler': secilen_kalemler,
                'neden': neden,
                'aciklama': aciklama,
                'toplam_tutar': self.toplam_iade_tutari
            }
            
            sonuc = self.iade_service.iade_olustur(iade_bilgisi)
            
            if sonuc:
                # Başarı mesajı
                self.mesaj_yoneticisi.bilgi_goster("İade işlemi başarıyla tamamlandı!")
                
                # Sinyal gönder
                self.iade_tamamlandi.emit(iade_bilgisi)
                
                # Ekranı kapat
                self.close()
            
        except Exception as e:
            self.logger.error(f"İade onaylama hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"İade onaylanamadı: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _iade_iptal(self):
        """İade işlemini iptal eder"""
        if self.mesaj_yoneticisi.onay_iste("İade işlemi iptal edilsin mi?"):
            self.iade_iptal_edildi.emit()
            self.close()
    
    def _secilen_kalemleri_al(self) -> List[Dict[str, Any]]:
        """Seçilen kalemleri döndürür"""
        secilen_kalemler = []
        
        for row in range(self.kalemler_tablo.rowCount()):
            checkbox = self.kalemler_tablo.cellWidget(row, 0)
            spin = self.kalemler_tablo.cellWidget(row, 3)
            
            if checkbox and checkbox.isChecked() and spin and spin.value() > 0:
                # Kalem bilgilerini al
                urun_adi = self.kalemler_tablo.item(row, 1).text()
                iade_adet = spin.value()
                
                # Birim fiyatı parse et
                fiyat_text = self.kalemler_tablo.item(row, 4).text()
                birim_fiyat = Decimal(fiyat_text.replace(' ₺', '').replace(',', '.'))
                
                secilen_kalemler.append({
                    'row': row,
                    'urun_adi': urun_adi,
                    'iade_adet': iade_adet,
                    'birim_fiyat': birim_fiyat,
                    'toplam_tutar': birim_fiyat * iade_adet
                })
        
        return secilen_kalemler
    
    def _iade_ozeti_guncelle(self):
        """İade özetini günceller"""
        secilen_kalemler = self._secilen_kalemleri_al()
        
        # Seçilen kalem sayısı
        self.secilen_kalem_label.setText(str(len(secilen_kalemler)))
        
        # Toplam iade tutarı
        self.toplam_iade_tutari = sum(kalem['toplam_tutar'] for kalem in secilen_kalemler)
        self.iade_tutari_label.setText(f"{self.toplam_iade_tutari:.2f} ₺")
        
        # Tablodaki iade tutarlarını güncelle
        for row in range(self.kalemler_tablo.rowCount()):
            spin = self.kalemler_tablo.cellWidget(row, 3)
            if spin:
                iade_adet = spin.value()
                
                # Birim fiyatı al
                fiyat_text = self.kalemler_tablo.item(row, 4).text()
                birim_fiyat = Decimal(fiyat_text.replace(' ₺', '').replace(',', '.'))
                
                # İade tutarını hesapla ve güncelle
                iade_tutar = birim_fiyat * iade_adet
                tutar_item = QTableWidgetItem(f"{iade_tutar:.2f} ₺")
                tutar_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.kalemler_tablo.setItem(row, 5, tutar_item)
        
        # Onayla butonunu aktifleştir/pasifleştir
        self.iade_onayla_buton.setEnabled(len(secilen_kalemler) > 0)
    
    def yenile(self):
        """Ekranı yeniler"""
        self.logger.info("İade ekranı yenileniyor")
        self._satis_bilgilerini_temizle()
        self.satis_no_edit.clear()
        self.fis_no_edit.clear()
        self.satis_no_edit.setFocus()
        self.alt_arac_yoneticisi.durum_guncelle("Yenilendi", 2)