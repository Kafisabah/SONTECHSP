# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.orkestrator.uygulama_yoneticisi
# Description: Refactoring adımlarının uygulanması
# Changelog:
# - İlk versiyon: Uygulama yöneticisi sınıfı

"""
Uygulama Yöneticisi

Refactoring adımlarını uygular ve araçları koordine eder.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from uygulama.moduller.kod_kalitesi.refactoring.dosya_bolucu import DosyaBolucu
from uygulama.moduller.kod_kalitesi.refactoring.fonksiyon_bolucu import FonksiyonBolucu
from uygulama.moduller.kod_kalitesi.refactoring.import_duzenleyici import ImportDuzenleyici
from uygulama.moduller.kod_kalitesi.analizorler.baslik_analizoru import BaslikAnalizoru

from .veri_yapilari import RefactoringPlani, RefactoringAdimi


class UygulamaYoneticisi:
    """
    Uygulama Yöneticisi
    
    Refactoring adımlarını uygular ve refactoring araçlarını
    koordine eder.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Args:
            logger: Logger instance
        """
        self.logger = logger
        
        # Refactoring araçlarını başlat
        self.dosya_bolucu = DosyaBolucu()
        self.fonksiyon_bolucu = FonksiyonBolucu()
        self.import_duzenleyici = ImportDuzenleyici()
        self.baslik_analizoru = BaslikAnalizoru()
    
    def plani_uygula(self, plan: RefactoringPlani) -> int:
        """
        Refactoring planını uygular.
        
        Args:
            plan: Refactoring planı
            
        Returns:
            Başarılı adım sayısı
        """
        basarili_adimlar = 0
        
        for adim in plan.adimlar:
            try:
                self.logger.info(f"Adım uygulanıyor: {adim.aciklama}")
                adim.baslangic_zamani = datetime.now()
                adim.durum = "uygulanıyor"
                
                # Adım türüne göre uygun aracı çağır
                if adim.adim_id.startswith('dosya_bol_'):
                    self._dosya_bolme_adimi_uygula(adim)
                elif adim.adim_id.startswith('fonksiyon_bol_'):
                    self._fonksiyon_bolme_adimi_uygula(adim)
                elif adim.adim_id.startswith('import_duzelt_'):
                    self._import_duzeltme_adimi_uygula(adim)
                elif adim.adim_id.startswith('kod_tekrar_cikart_'):
                    self._kod_tekrar_cikarma_adimi_uygula(adim)
                elif adim.adim_id.startswith('baslik_ekle_'):
                    self._baslik_ekleme_adimi_uygula(adim)
                
                adim.durum = "tamamlandı"
                adim.bitis_zamani = datetime.now()
                basarili_adimlar += 1
                
                self.logger.info(f"Adım tamamlandı: {adim.aciklama}")
                
            except Exception as e:
                adim.durum = "hata"
                adim.hata_mesaji = str(e)
                adim.bitis_zamani = datetime.now()
                
                self.logger.error(f"Adım hatası: {adim.aciklama} - {e}")
        
        return basarili_adimlar
    
    def _dosya_bolme_adimi_uygula(self, adim: RefactoringAdimi):
        """Dosya bölme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        yeni_dosyalar = self.dosya_bolucu.dosyayi_bol(dosya_yolu)
        
        # Yeni dosyaları diske yaz
        for yeni_dosya in yeni_dosyalar:
            with open(yeni_dosya.dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(yeni_dosya.icerik)
        
        # __init__.py'yi güncelle
        modul_yolu = str(Path(dosya_yolu).parent)
        self.dosya_bolucu.init_dosyasini_guncelle(modul_yolu, yeni_dosyalar)
        
        # Orijinal dosyayı sil
        os.remove(dosya_yolu)
    
    def _fonksiyon_bolme_adimi_uygula(self, adim: RefactoringAdimi):
        """Fonksiyon bölme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        
        # Dosyayı oku
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # Büyük fonksiyonları böl
        yeni_icerik = self.fonksiyon_bolucu.buyuk_fonksiyonlari_bol(icerik)
        
        # Dosyayı güncelle
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(yeni_icerik)
    
    def _import_duzeltme_adimi_uygula(self, adim: RefactoringAdimi):
        """Import düzeltme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        self.import_duzenleyici.dosya_importlarini_duzenle(dosya_yolu)
    
    def _kod_tekrar_cikarma_adimi_uygula(self, adim: RefactoringAdimi):
        """Kod tekrarı çıkarma adımını uygular"""
        # Bu adım daha karmaşık olduğu için şimdilik placeholder
        self.logger.warning(f"Kod tekrarı çıkarma henüz uygulanmadı: {adim.aciklama}")
    
    def _baslik_ekleme_adimi_uygula(self, adim: RefactoringAdimi):
        """Başlık ekleme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        # Dosya yolundan modül adını çıkar
        dosya_adi = Path(dosya_yolu).stem
        self.baslik_analizoru.baslik_ekle(dosya_yolu, dosya_adi, "Otomatik oluşturuldu")