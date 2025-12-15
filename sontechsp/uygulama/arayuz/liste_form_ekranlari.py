# Version: 0.1.0
# Last Update: 2024-12-15
# Module: liste_form_ekranlari
# Description: SONTECHSP özelleşmiş ekran sınıfları (Liste ve Form)
# Changelog:
# - İlk oluşturma
# - taban_ekran.py'den ayrıldı (kod kalitesi için)

"""
SONTECHSP Özelleşmiş Ekran Sınıfları

Liste ve Form görünümleri için özelleşmiş ekran sınıfları.
TabanEkran sınıfından türetilmiştir.

Sorumluluklar:
- Liste görünümü yönetimi
- Form görünümü yönetimi
- CRUD işlem arayüzleri
- Veri doğrulama arayüzleri
"""

from abc import abstractmethod
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran


class ListeEkrani(TabanEkran):
    """
    Liste görünümü için temel ekran sınıfı
    
    Veri listesi gösterimi ve temel CRUD işlemleri için kullanılır.
    """
    
    # Sinyaller
    kayit_secildi = pyqtSignal(dict)  # Kayıt seçildiğinde
    kayit_eklendi = pyqtSignal(dict)  # Kayıt eklendiğinde
    kayit_guncellendi = pyqtSignal(dict)  # Kayıt güncellendiğinde
    kayit_silindi = pyqtSignal(int)   # Kayıt silindiğinde
    
    def __init__(self, ekran_adi: str, parent: Optional[QWidget] = None):
        super().__init__(ekran_adi, parent)
        
        # Liste verisi
        self._kayitlar: List[Dict[str, Any]] = []
        self._secili_kayit: Optional[Dict[str, Any]] = None
    
    def _icerik_olustur(self):
        """Liste ekranı içeriğini oluşturur"""
        # Filtre alanı
        self._filtre_alani_olustur()
        
        # Liste alanı
        self._liste_alani_olustur()
        
        # Detay alanı (opsiyonel)
        self._detay_alani_olustur()
    
    @abstractmethod
    def _filtre_alani_olustur(self):
        """Filtre alanını oluşturur (alt sınıflar implement etmeli)"""
        pass
    
    @abstractmethod
    def _liste_alani_olustur(self):
        """Liste alanını oluşturur (alt sınıflar implement etmeli)"""
        pass
    
    def _detay_alani_olustur(self):
        """Detay alanını oluşturur (opsiyonel)"""
        # Alt sınıflar gerekirse override edebilir
        pass
    
    def kayitlari_yukle(self, kayitlar: List[Dict[str, Any]]):
        """
        Kayıtları yükler
        
        Args:
            kayitlar: Yüklenecek kayıt listesi
        """
        self._kayitlar = kayitlar
        self._liste_guncelle()
        self.logger.debug(f"{len(kayitlar)} kayıt yüklendi")
    
    def secili_kayit_al(self) -> Optional[Dict[str, Any]]:
        """
        Seçili kaydı döndürür
        
        Returns:
            Optional[Dict[str, Any]]: Seçili kayıt
        """
        return self._secili_kayit
    
    def kayit_sec(self, kayit: Dict[str, Any]):
        """
        Kayıt seçer
        
        Args:
            kayit: Seçilecek kayıt
        """
        self._secili_kayit = kayit
        self.kayit_secildi.emit(kayit)
        self.logger.debug(f"Kayıt seçildi: {kayit.get('id', 'N/A')}")
    
    @abstractmethod
    def _liste_guncelle(self):
        """Liste görünümünü günceller (alt sınıflar implement etmeli)"""
        pass


class FormEkrani(TabanEkran):
    """
    Form görünümü için temel ekran sınıfı
    
    Veri girişi ve düzenleme işlemleri için kullanılır.
    """
    
    # Sinyaller
    form_kaydedildi = pyqtSignal(dict)  # Form kaydedildiğinde
    form_iptal_edildi = pyqtSignal()    # Form iptal edildiğinde
    
    def __init__(self, ekran_adi: str, parent: Optional[QWidget] = None):
        super().__init__(ekran_adi, parent)
        
        # Form verisi
        self._form_verisi: Dict[str, Any] = {}
        self._duzenle_modu = False
    
    def _icerik_olustur(self):
        """Form ekranı içeriğini oluşturur"""
        # Form alanları
        self._form_alanlari_olustur()
        
        # Form butonları
        self._form_butonlari_olustur()
    
    @abstractmethod
    def _form_alanlari_olustur(self):
        """Form alanlarını oluşturur (alt sınıflar implement etmeli)"""
        pass
    
    def _form_butonlari_olustur(self):
        """Form butonlarını oluşturur"""
        buton_layout = QHBoxLayout()
        
        # Kaydet butonu
        self.kaydet_buton = QPushButton("Kaydet")
        self.kaydet_buton.clicked.connect(self._kaydet)
        buton_layout.addWidget(self.kaydet_buton)
        
        # İptal butonu
        self.iptal_buton = QPushButton("İptal")
        self.iptal_buton.clicked.connect(self._iptal)
        buton_layout.addWidget(self.iptal_buton)
        
        buton_layout.addStretch()
        
        self.icerik_layout.addLayout(buton_layout)
    
    def form_verisi_yukle(self, veri: Dict[str, Any], duzenle_modu: bool = False):
        """
        Form verisini yükler
        
        Args:
            veri: Yüklenecek veri
            duzenle_modu: Düzenleme modu mu
        """
        self._form_verisi = veri.copy()
        self._duzenle_modu = duzenle_modu
        self._form_doldur()
        
        self.logger.debug(f"Form verisi yüklendi: {duzenle_modu and 'düzenleme' or 'yeni'} modu")
    
    @abstractmethod
    def _form_doldur(self):
        """Formu veri ile doldurur (alt sınıflar implement etmeli)"""
        pass
    
    @abstractmethod
    def _form_verisi_al(self) -> Dict[str, Any]:
        """Form verisini alır (alt sınıflar implement etmeli)"""
        pass
    
    @abstractmethod
    def _form_dogrula(self) -> bool:
        """Formu doğrular (alt sınıflar implement etmeli)"""
        pass
    
    def _kaydet(self):
        """Form kaydetme işlemi"""
        if not self._form_dogrula():
            return
        
        try:
            form_verisi = self._form_verisi_al()
            self.form_kaydedildi.emit(form_verisi)
            self.veri_degisiklik_sifirla()
            self.durum_mesaji_goster("Kaydedildi", 3)
            
        except Exception as e:
            self.hata_goster(f"Kaydetme hatası: {str(e)}")
    
    def _iptal(self):
        """Form iptal işlemi"""
        if self._veri_degisti_mi:
            if not self.onay_iste("Değişiklikler kaydedilmedi. İptal etmek istediğinizden emin misiniz?"):
                return
        
        self.form_iptal_edildi.emit()
        self.veri_degisiklik_sifirla()
    
    def yenile(self):
        """Form ekranını yeniler"""
        if self._duzenle_modu and self._form_verisi.get('id'):
            # Düzenleme modundaysa veriyi yeniden yükle
            self.durum_mesaji_goster("Yenileniyor...", 2)
        else:
            # Yeni kayıt modundaysa formu temizle
            self._form_verisi = {}
            self._form_doldur()