# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.ui.sepet_ekrani
# Description: POS Sepet Ekranı PyQt6 arayüzü
# Changelog:
# - İlk oluşturma
# - Import yolları düzeltildi
# - Repository entegrasyonu eklendi

"""
POS Sepet Ekranı PyQt6 Arayüzü

Sepet görüntüleme ve yönetim ekranı.
Barkod okuma arayüzü içerir.
Sadece service katmanını çağırır.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QSpinBox, QDoubleSpinBox, QFrame, QGroupBox, QGridLayout,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut

from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran
from sontechsp.uygulama.moduller.pos.servisler.sepet_service import SepetService
from sontechsp.uygulama.cekirdek.oturum import oturum_baglamini_al


class SepetEkrani(TabanEkran):
    """
    POS Sepet Ekranı
    
    Sepet yönetimi ve barkod okuma işlemlerini sağlar.
    Requirements: 1.1, 1.2, 2.1, 2.2
    """
    
    # Sinyaller
    urun_eklendi = pyqtSignal(dict)
    sepet_guncellendi = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Sepet ekranını başlatır"""
        super().__init__("POS Sepet", parent)
        
        # Servisler
        self.sepet_service = SepetService()
        self.oturum = oturum_baglamini_al()
        
        # Durum değişkenleri
        self.aktif_sepet_id: Optional[int] = None
        self.sepet_satirlari: List[Dict[str, Any]] = []
        
        # Barkod okuma için timer
        self.barkod_timer = QTimer()
        self.barkod_timer.setSingleShot(True)
        self.barkod_timer.timeout.connect(self._barkod_isle)
        
        # Başlangıç işlemleri
        self._yeni_sepet_olustur()
        self._kisa_yollari_kur()
        
        # Barkod alanına odaklan
        self.barkod_edit.setFocus()
    
    def _icerik_olustur(self):
        """Ekran içeriğini oluşturur"""
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.icerik_layout.addWidget(splitter)
        
        # Sol panel - Barkod ve kontroller
        sol_panel = self._sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Sepet tablosu
        sag_panel = self._sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([300, 500])
    
    def _sol_panel_olustur(self) -> QWidget:
        """Sol paneli oluşturur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Barkod okuma grubu
        barkod_grubu = self._barkod_grubu_olustur()
        layout.addWidget(barkod_grubu)
        
        # Sepet kontrolleri grubu
        kontrol_grubu = self._kontrol_grubu_olustur()
        layout.addWidget(kontrol_grubu)
        
        # Özet bilgiler grubu
        ozet_grubu = self._ozet_grubu_olustur()
        layout.addWidget(ozet_grubu)
        
        layout.addStretch()
        return panel
    
    def _barkod_grubu_olustur(self) -> QGroupBox:
        """Barkod okuma grubunu oluşturur"""
        grup = QGroupBox("Barkod Okuma")
        layout = QVBoxLayout(grup)
        
        # Barkod giriş alanı
        self.barkod_edit = QLineEdit()
        self.barkod_edit.setPlaceholderText("Barkod okutun veya yazın...")
        self.barkod_edit.setFont(QFont("Arial", 12))
        self.barkod_edit.textChanged.connect(self._barkod_degisti)
        self.barkod_edit.returnPressed.connect(self._barkod_isle)
        layout.addWidget(self.barkod_edit)
        
        # Barkod ekle butonu
        self.barkod_ekle_buton = QPushButton("Ürün Ekle (F1)")
        self.barkod_ekle_buton.clicked.connect(self._barkod_isle)
        layout.addWidget(self.barkod_ekle_buton)
        
        return grup
    
    def _kontrol_grubu_olustur(self) -> QGroupBox:
        """Kontrol grubunu oluşturur"""
        grup = QGroupBox("Sepet Kontrolleri")
        layout = QGridLayout(grup)
        
        # Adet değiştirme
        layout.addWidget(QLabel("Adet:"), 0, 0)
        self.adet_spin = QSpinBox()
        self.adet_spin.setMinimum(1)
        self.adet_spin.setMaximum(999)
        self.adet_spin.setValue(1)
        layout.addWidget(self.adet_spin, 0, 1)
        
        self.adet_degistir_buton = QPushButton("Adet Değiştir (F2)")
        self.adet_degistir_buton.clicked.connect(self._adet_degistir)
        layout.addWidget(self.adet_degistir_buton, 0, 2)
        
        # İndirim uygulama
        layout.addWidget(QLabel("İndirim:"), 1, 0)
        self.indirim_spin = QDoubleSpinBox()
        self.indirim_spin.setMinimum(0.00)
        self.indirim_spin.setMaximum(9999.99)
        self.indirim_spin.setDecimals(2)
        self.indirim_spin.setSuffix(" ₺")
        layout.addWidget(self.indirim_spin, 1, 1)
        
        self.indirim_uygula_buton = QPushButton("İndirim Uygula (F3)")
        self.indirim_uygula_buton.clicked.connect(self._indirim_uygula)
        layout.addWidget(self.indirim_uygula_buton, 1, 2)
        
        # Satır silme
        self.satir_sil_buton = QPushButton("Satır Sil (Del)")
        self.satir_sil_buton.clicked.connect(self._satir_sil)
        layout.addWidget(self.satir_sil_buton, 2, 0, 1, 3)
        
        # Sepet boşaltma
        self.sepet_bosalt_buton = QPushButton("Sepeti Boşalt (F4)")
        self.sepet_bosalt_buton.clicked.connect(self._sepet_bosalt)
        layout.addWidget(self.sepet_bosalt_buton, 3, 0, 1, 3)
        
        return grup
    
    def _ozet_grubu_olustur(self) -> QGroupBox:
        """Özet bilgiler grubunu oluşturur"""
        grup = QGroupBox("Sepet Özeti")
        layout = QGridLayout(grup)
        
        # Toplam kalem
        layout.addWidget(QLabel("Toplam Kalem:"), 0, 0)
        self.toplam_kalem_label = QLabel("0")
        self.toplam_kalem_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.toplam_kalem_label, 0, 1)
        
        # Toplam adet
        layout.addWidget(QLabel("Toplam Adet:"), 1, 0)
        self.toplam_adet_label = QLabel("0")
        self.toplam_adet_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.toplam_adet_label, 1, 1)
        
        # Toplam tutar
        layout.addWidget(QLabel("Toplam Tutar:"), 2, 0)
        self.toplam_tutar_label = QLabel("0,00 ₺")
        self.toplam_tutar_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.toplam_tutar_label.setStyleSheet("color: #2c3e50; background: #ecf0f1; padding: 5px;")
        layout.addWidget(self.toplam_tutar_label, 2, 1)
        
        return grup
    
    def _sag_panel_olustur(self) -> QWidget:
        """Sağ paneli oluşturur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Sepet tablosu başlığı
        baslik = QLabel("Sepet İçeriği")
        baslik.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(baslik)
        
        # Sepet tablosu
        self.sepet_tablo = QTableWidget()
        self.sepet_tablo.setColumnCount(6)
        self.sepet_tablo.setHorizontalHeaderLabels([
            "Barkod", "Ürün Adı", "Adet", "Birim Fiyat", "Toplam", "İşlem"
        ])
        
        # Tablo ayarları
        header = self.sepet_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Barkod
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Ürün Adı
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Adet
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Birim Fiyat
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Toplam
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # İşlem
        
        self.sepet_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sepet_tablo.setAlternatingRowColors(True)
        self.sepet_tablo.selectionModel().selectionChanged.connect(self._tablo_secim_degisti)
        
        layout.addWidget(self.sepet_tablo)
        
        return panel
    
    def _kisa_yollari_kur(self):
        """Klavye kısayollarını kurar"""
        # F1 - Ürün ekle
        QShortcut(QKeySequence("F1"), self, self._barkod_isle)
        
        # F2 - Adet değiştir
        QShortcut(QKeySequence("F2"), self, self._adet_degistir)
        
        # F3 - İndirim uygula
        QShortcut(QKeySequence("F3"), self, self._indirim_uygula)
        
        # F4 - Sepeti boşalt
        QShortcut(QKeySequence("F4"), self, self._sepet_bosalt)
        
        # Delete - Satır sil
        QShortcut(QKeySequence("Delete"), self, self._satir_sil)
        
        # Enter - Barkod işle
        QShortcut(QKeySequence("Return"), self, self._barkod_isle)
    
    def _yeni_sepet_olustur(self):
        """Yeni sepet oluşturur"""
        try:
            # Oturum bilgilerini al
            terminal_id = getattr(self.oturum, 'terminal_id', 1)
            kasiyer_id = getattr(self.oturum, 'kullanici_id', 1)
            
            # Yeni sepet oluştur
            self.aktif_sepet_id = self.sepet_service.yeni_sepet_olustur(terminal_id, kasiyer_id)
            self.logger.info(f"Yeni sepet oluşturuldu: {self.aktif_sepet_id}")
            
            # Ekranı güncelle
            self._sepet_guncelle()
            
        except Exception as e:
            self.logger.error(f"Sepet oluşturma hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Sepet oluşturulamadı: {str(e)}")
    
    @pyqtSlot()
    def _barkod_degisti(self):
        """Barkod değiştiğinde çağrılır"""
        # Otomatik işleme için timer başlat (500ms bekle)
        self.barkod_timer.stop()
        if self.barkod_edit.text().strip():
            self.barkod_timer.start(500)
    
    @pyqtSlot()
    def _barkod_isle(self):
        """Barkod işleme"""
        barkod = self.barkod_edit.text().strip()
        if not barkod:
            self.mesaj_yoneticisi.uyari_goster("Lütfen barkod girin")
            return
        
        if not self.aktif_sepet_id:
            self.mesaj_yoneticisi.hata_goster("Aktif sepet bulunamadı")
            return
        
        try:
            self.yukleme_basladi.emit()
            
            # Barkod ile ürün ekle
            basarili = self.sepet_service.barkod_ekle(self.aktif_sepet_id, barkod)
            
            if basarili:
                # Barkod alanını temizle
                self.barkod_edit.clear()
                
                # Sepeti güncelle
                self._sepet_guncelle()
                
                # Başarı mesajı
                self.alt_arac_yoneticisi.durum_guncelle(f"Ürün eklendi: {barkod}", 2)
                
                # Sinyal gönder
                self.urun_eklendi.emit({'barkod': barkod})
            
        except Exception as e:
            self.logger.error(f"Barkod işleme hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Ürün eklenemedi: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _adet_degistir(self):
        """Seçili satırın adedini değiştirir"""
        secili_satirlar = self.sepet_tablo.selectionModel().selectedRows()
        if not secili_satirlar:
            self.mesaj_yoneticisi.uyari_goster("Lütfen bir satır seçin")
            return
        
        satir_index = secili_satirlar[0].row()
        if satir_index >= len(self.sepet_satirlari):
            return
        
        satir_data = self.sepet_satirlari[satir_index]
        yeni_adet = self.adet_spin.value()
        
        try:
            self.yukleme_basladi.emit()
            
            # Adet değiştir
            basarili = self.sepet_service.urun_adedi_degistir(satir_data['id'], yeni_adet)
            
            if basarili:
                # Sepeti güncelle
                self._sepet_guncelle()
                
                # Başarı mesajı
                self.alt_arac_yoneticisi.durum_guncelle(f"Adet güncellendi: {yeni_adet}", 2)
            
        except Exception as e:
            self.logger.error(f"Adet değiştirme hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Adet değiştirilemedi: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _indirim_uygula(self):
        """İndirim uygular"""
        if not self.aktif_sepet_id:
            self.mesaj_yoneticisi.hata_goster("Aktif sepet bulunamadı")
            return
        
        indirim_tutari = Decimal(str(self.indirim_spin.value()))
        
        if indirim_tutari <= 0:
            self.mesaj_yoneticisi.uyari_goster("İndirim tutarı pozitif olmalıdır")
            return
        
        try:
            self.yukleme_basladi.emit()
            
            # İndirim uygula
            basarili = self.sepet_service.indirim_uygula(self.aktif_sepet_id, indirim_tutari)
            
            if basarili:
                # İndirim alanını temizle
                self.indirim_spin.setValue(0.00)
                
                # Sepeti güncelle
                self._sepet_guncelle()
                
                # Başarı mesajı
                self.alt_arac_yoneticisi.durum_guncelle(f"İndirim uygulandı: {indirim_tutari} ₺", 2)
            
        except Exception as e:
            self.logger.error(f"İndirim uygulama hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"İndirim uygulanamadı: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _satir_sil(self):
        """Seçili satırı siler"""
        secili_satirlar = self.sepet_tablo.selectionModel().selectedRows()
        if not secili_satirlar:
            self.mesaj_yoneticisi.uyari_goster("Lütfen bir satır seçin")
            return
        
        satir_index = secili_satirlar[0].row()
        if satir_index >= len(self.sepet_satirlari):
            return
        
        satir_data = self.sepet_satirlari[satir_index]
        
        # Onay iste
        if not self.mesaj_yoneticisi.onay_iste(
            f"'{satir_data.get('urun_adi', 'Bilinmeyen')}' ürünü sepetten silinsin mi?"
        ):
            return
        
        try:
            self.yukleme_basladi.emit()
            
            # Satır sil
            basarili = self.sepet_service.satir_sil(satir_data['id'])
            
            if basarili:
                # Sepeti güncelle
                self._sepet_guncelle()
                
                # Başarı mesajı
                self.alt_arac_yoneticisi.durum_guncelle("Satır silindi", 2)
            
        except Exception as e:
            self.logger.error(f"Satır silme hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Satır silinemedi: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _sepet_bosalt(self):
        """Sepeti boşaltır"""
        if not self.aktif_sepet_id:
            self.mesaj_yoneticisi.hata_goster("Aktif sepet bulunamadı")
            return
        
        # Onay iste
        if not self.mesaj_yoneticisi.onay_iste("Sepet tamamen boşaltılsın mı?"):
            return
        
        try:
            self.yukleme_basladi.emit()
            
            # Sepeti boşalt
            basarili = self.sepet_service.sepet_bosalt(self.aktif_sepet_id)
            
            if basarili:
                # Sepeti güncelle
                self._sepet_guncelle()
                
                # Başarı mesajı
                self.alt_arac_yoneticisi.durum_guncelle("Sepet boşaltıldı", 2)
            
        except Exception as e:
            self.logger.error(f"Sepet boşaltma hatası: {str(e)}")
            self.mesaj_yoneticisi.hata_goster(f"Sepet boşaltılamadı: {str(e)}")
        
        finally:
            self.yukleme_bitti.emit()
    
    @pyqtSlot()
    def _tablo_secim_degisti(self):
        """Tablo seçimi değiştiğinde çağrılır"""
        secili_satirlar = self.sepet_tablo.selectionModel().selectedRows()
        
        if secili_satirlar and len(self.sepet_satirlari) > 0:
            satir_index = secili_satirlar[0].row()
            if satir_index < len(self.sepet_satirlari):
                satir_data = self.sepet_satirlari[satir_index]
                # Adet spin'ini güncelle
                self.adet_spin.setValue(satir_data.get('adet', 1))
    
    def _sepet_guncelle(self):
        """Sepet bilgilerini günceller"""
        if not self.aktif_sepet_id:
            return
        
        try:
            # Sepet bilgilerini al
            sepet_bilgisi = self.sepet_service.sepet_bilgisi_getir(self.aktif_sepet_id)
            if not sepet_bilgisi:
                return
            
            # Sepet satırlarını al (mock veri)
            self.sepet_satirlari = self._mock_sepet_satirlari_getir()
            
            # Tabloyu güncelle
            self._tablo_guncelle()
            
            # Özet bilgileri güncelle
            self._ozet_guncelle()
            
            # Sinyal gönder
            self.sepet_guncellendi.emit(sepet_bilgisi)
            
        except Exception as e:
            self.logger.error(f"Sepet güncelleme hatası: {str(e)}")
    
    def _mock_sepet_satirlari_getir(self) -> List[Dict[str, Any]]:
        """Mock sepet satırları (gerçek implementasyonda repository'den gelecek)"""
        # Bu mock veri, gerçek implementasyonda sepet_repository'den gelecek
        return [
            {
                'id': 1,
                'barkod': '1234567890123',
                'urun_adi': 'Örnek Ürün 1',
                'adet': 2,
                'birim_fiyat': Decimal('10.50'),
                'toplam_tutar': Decimal('21.00')
            },
            {
                'id': 2,
                'barkod': '9876543210987',
                'urun_adi': 'Örnek Ürün 2',
                'adet': 1,
                'birim_fiyat': Decimal('25.75'),
                'toplam_tutar': Decimal('25.75')
            }
        ]
    
    def _tablo_guncelle(self):
        """Sepet tablosunu günceller"""
        self.sepet_tablo.setRowCount(len(self.sepet_satirlari))
        
        for row, satir in enumerate(self.sepet_satirlari):
            # Barkod
            self.sepet_tablo.setItem(row, 0, QTableWidgetItem(str(satir.get('barkod', ''))))
            
            # Ürün adı
            self.sepet_tablo.setItem(row, 1, QTableWidgetItem(str(satir.get('urun_adi', ''))))
            
            # Adet
            adet_item = QTableWidgetItem(str(satir.get('adet', 0)))
            adet_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sepet_tablo.setItem(row, 2, adet_item)
            
            # Birim fiyat
            birim_fiyat = satir.get('birim_fiyat', Decimal('0'))
            fiyat_item = QTableWidgetItem(f"{birim_fiyat:.2f} ₺")
            fiyat_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.sepet_tablo.setItem(row, 3, fiyat_item)
            
            # Toplam
            toplam = satir.get('toplam_tutar', Decimal('0'))
            toplam_item = QTableWidgetItem(f"{toplam:.2f} ₺")
            toplam_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.sepet_tablo.setItem(row, 4, toplam_item)
            
            # İşlem butonu (placeholder)
            islem_item = QTableWidgetItem("Düzenle")
            self.sepet_tablo.setItem(row, 5, islem_item)
    
    def _ozet_guncelle(self):
        """Özet bilgilerini günceller"""
        toplam_kalem = len(self.sepet_satirlari)
        toplam_adet = sum(satir.get('adet', 0) for satir in self.sepet_satirlari)
        toplam_tutar = sum(satir.get('toplam_tutar', Decimal('0')) for satir in self.sepet_satirlari)
        
        self.toplam_kalem_label.setText(str(toplam_kalem))
        self.toplam_adet_label.setText(str(toplam_adet))
        self.toplam_tutar_label.setText(f"{toplam_tutar:.2f} ₺")
    
    def yenile(self):
        """Ekranı yeniler"""
        self.logger.info("Sepet ekranı yenileniyor")
        self._sepet_guncelle()
        self.alt_arac_yoneticisi.durum_guncelle("Yenilendi", 2)
    
    def aktif_sepet_id_getir(self) -> Optional[int]:
        """Aktif sepet ID'sini döndürür"""
        return self.aktif_sepet_id
    
    def barkod_odakla(self):
        """Barkod alanına odaklanır"""
        self.barkod_edit.setFocus()
        self.barkod_edit.selectAll()