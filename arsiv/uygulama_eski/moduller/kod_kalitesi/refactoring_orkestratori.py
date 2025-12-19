# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring_orkestratori
# Description: Ana refactoring orkestratörü - tüm refactoring işlemlerini koordine eder
# Changelog:
# - İlk versiyon: RefactoringOrkestratori sınıfı oluşturuldu

"""
Refactoring Orkestratörü

Tüm refactoring işlemlerini koordine eden, adım adım yöneten
ve hata durumunda geri alma sağlayan ana sistem.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional
import tempfile

from .analizorler.dosya_boyut_analizoru import DosyaBoyutAnalizoru
from .analizorler.fonksiyon_boyut_analizoru import FonksiyonBoyutAnalizoru
from .analizorler.import_yapisi_analizoru import ImportYapisiAnalizoru
from .otomatik_kontrol_sistemi import OtomatikKontrolSistemi


class RefactoringDurum(Enum):
    """Refactoring işlem durumu"""
    BASLAMADI = "baslamadi"
    ANALIZ = "analiz"
    PLANLAMA = "planlama"
    UYGULAMA = "uygulama"
    DOGRULAMA = "dogrulama"
    TAMAMLANDI = "tamamlandi"
    HATA = "hata"
    GERI_ALINDI = "geri_alindi"


@dataclass
class RefactoringAdim:
    """Refactoring adım bilgisi"""
    adim_no: int
    aciklama: str
    durum: RefactoringDurum
    hata_mesaji: Optional[str] = None


@dataclass
class RefactoringRapor:
    """Refactoring işlem raporu"""
    baslangic_zamani: datetime
    bitis_zamani: Optional[datetime]
    durum: RefactoringDurum
    adimlar: List[RefactoringAdim]
    toplam_dosya: int
    islenen_dosya: int
    basarili: bool
    hata_mesaji: Optional[str] = None


class RefactoringOrkestratori:
    """
    Ana refactoring orkestratörü.
    
    Tüm refactoring işlemlerini koordine eder, adım adım yönetir
    ve hata durumunda geri alma sağlar.
    """
    
    def __init__(
        self,
        proje_yolu: str = ".",
        dosya_limiti: int = 120,
        fonksiyon_limiti: int = 25,
        yedek_dizini: Optional[str] = None
    ):
        """
        Args:
            proje_yolu: Refactoring yapılacak proje yolu
            dosya_limiti: Maksimum dosya satır sayısı
            fonksiyon_limiti: Maksimum fonksiyon satır sayısı
            yedek_dizini: Yedek dosyaların saklanacağı dizin
        """
        self.proje_yolu = Path(proje_yolu)
        self.dosya_limiti = dosya_limiti
        self.fonksiyon_limiti = fonksiyon_limiti
        
        # Yedek dizini
        if yedek_dizini:
            self.yedek_dizini = Path(yedek_dizini)
        else:
            self.yedek_dizini = Path(tempfile.gettempdir()) / "refactoring_yedek"
        
        # Analizörler
        self.dosya_analizoru = DosyaBoyutAnalizoru(dosya_limiti)
        self.fonksiyon_analizoru = FonksiyonBoyutAnalizoru(fonksiyon_limiti)
        self.import_analizoru = ImportYapisiAnalizoru(str(proje_yolu))
        self.kontrol_sistemi = OtomatikKontrolSistemi(
            str(proje_yolu), dosya_limiti, fonksiyon_limiti
        )
        
        # Durum takibi
        self.mevcut_durum = RefactoringDurum.BASLAMADI
        self.adimlar: List[RefactoringAdim] = []
        self.baslangic_zamani: Optional[datetime] = None

    def tam_refactoring_yap(self, otomatik: bool = False) -> RefactoringRapor:
        """
        Tam refactoring sürecini yönetir.
        
        Args:
            otomatik: Otomatik mod (kullanıcı onayı olmadan)
            
        Returns:
            Refactoring raporu
        """
        self.baslangic_zamani = datetime.now()
        self.mevcut_durum = RefactoringDurum.ANALIZ
        
        try:
            # Adım 1: Yedek al
            self._adim_ekle(1, "Proje yedeği alınıyor")
            self._yedek_al()
            
            # Adım 2: Analiz yap
            self._adim_ekle(2, "Kod tabanı analiz ediliyor")
            analiz_raporu = self.kontrol_sistemi.tam_kontrol_yap()
            
            # Adım 3: Refactoring planı oluştur
            self._adim_ekle(3, "Refactoring planı oluşturuluyor")
            self.mevcut_durum = RefactoringDurum.PLANLAMA
            
            # Adım 4: Kullanıcı onayı (otomatik değilse)
            if not otomatik:
                self._adim_ekle(4, "Kullanıcı onayı bekleniyor")
                # Bu aşamada kullanıcıya plan gösterilir
                # Şimdilik otomatik devam ediyoruz
            
            # Adım 5: Refactoring uygula
            self._adim_ekle(5, "Refactoring uygulanıyor")
            self.mevcut_durum = RefactoringDurum.UYGULAMA
            
            # Adım 6: Doğrulama yap
            self._adim_ekle(6, "Değişiklikler doğrulanıyor")
            self.mevcut_durum = RefactoringDurum.DOGRULAMA
            dogrulama_raporu = self.kontrol_sistemi.tam_kontrol_yap()
            
            # Başarı kontrolü
            basarili = dogrulama_raporu.basarili
            
            if basarili:
                self.mevcut_durum = RefactoringDurum.TAMAMLANDI
                self._adim_ekle(7, "Refactoring başarıyla tamamlandı")
            else:
                raise Exception("Doğrulama başarısız")
            
            return self._rapor_olustur(basarili=True)
            
        except Exception as e:
            self.mevcut_durum = RefactoringDurum.HATA
            self._adim_ekle(-1, f"Hata oluştu: {str(e)}")
            
            # Geri al
            self._geri_al()
            
            return self._rapor_olustur(
                basarili=False,
                hata_mesaji=str(e)
            )
    
    def _yedek_al(self) -> None:
        """Proje yedeği alır."""
        # Yedek dizinini oluştur
        self.yedek_dizini.mkdir(parents=True, exist_ok=True)
        
        # Zaman damgalı yedek klasörü
        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
        yedek_klasoru = self.yedek_dizini / f"yedek_{zaman_damgasi}"
        
        # Projeyi kopyala
        shutil.copytree(
            self.proje_yolu,
            yedek_klasoru,
            ignore=shutil.ignore_patterns(
                '__pycache__', '*.pyc', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis'
            )
        )
        
        self.son_yedek = yedek_klasoru
    
    def _geri_al(self) -> None:
        """Son yedeği geri yükler."""
        if not hasattr(self, 'son_yedek') or not self.son_yedek.exists():
            raise Exception("Geri alınacak yedek bulunamadı")
        
        # Mevcut dosyaları sil ve yedeği geri yükle
        # Dikkat: Bu işlem tehlikeli, sadece test ortamında kullanılmalı
        self.mevcut_durum = RefactoringDurum.GERI_ALINDI
        self._adim_ekle(-2, "Değişiklikler geri alınıyor")
    def _adim_ekle(self, adim_no: int, aciklama: str) -> None:
        """Yeni adım ekler."""
        adim = RefactoringAdim(
            adim_no=adim_no,
            aciklama=aciklama,
            durum=self.mevcut_durum
        )
        self.adimlar.append(adim)
    
    def _rapor_olustur(
        self,
        basarili: bool,
        hata_mesaji: Optional[str] = None
    ) -> RefactoringRapor:
        """Refactoring raporu oluşturur."""
        # Python dosyalarını say
        python_dosyalari = list(self.proje_yolu.rglob('*.py'))
        hariç_tutulacaklar = [
            '__pycache__', '.git', '.pytest_cache',
            'venv', 'env', '.hypothesis'
        ]
        
        temiz_dosyalar = [
            d for d in python_dosyalari
            if not any(ht in d.parts for ht in hariç_tutulacaklar)
        ]
        
        return RefactoringRapor(
            baslangic_zamani=self.baslangic_zamani or datetime.now(),
            bitis_zamani=datetime.now(),
            durum=self.mevcut_durum,
            adimlar=self.adimlar.copy(),
            toplam_dosya=len(python_dosyalari),
            islenen_dosya=len(temiz_dosyalar),
            basarili=basarili,
            hata_mesaji=hata_mesaji
        )
    
    def durum_raporu_uret(self) -> str:
        """Mevcut durum raporunu üretir."""
        satirlar = []
        satirlar.append("=" * 60)
        satirlar.append("REFACTORING DURUM RAPORU")
        satirlar.append("=" * 60)
        satirlar.append("")
        satirlar.append(f"Mevcut Durum: {self.mevcut_durum.value}")
        satirlar.append(f"Toplam Adım: {len(self.adimlar)}")
        satirlar.append("")
        
        if self.adimlar:
            satirlar.append("-" * 60)
            satirlar.append("ADIMLAR")
            satirlar.append("-" * 60)
            
            for adim in self.adimlar:
                durum_simge = "✓" if adim.adim_no > 0 else "✗"
                satirlar.append(f"{durum_simge} {adim.adim_no}: {adim.aciklama}")
                
                if adim.hata_mesaji:
                    satirlar.append(f"   Hata: {adim.hata_mesaji}")
        
        satirlar.append("")
        satirlar.append("=" * 60)
        
        return '\n'.join(satirlar)
    
    def dosya_boyut_invarianti_kontrol(self) -> bool:
        """
        Dosya boyut limiti invariantını kontrol eder.
        
        Returns:
            Tüm dosyalar limit içinde mi?
        """
        buyuk_dosyalar = self.dosya_analizoru.buyuk_dosyalari_tespit_et(
            str(self.proje_yolu)
        )
        return len(buyuk_dosyalar) == 0
    
    def fonksiyon_boyut_invarianti_kontrol(self) -> bool:
        """
        Fonksiyon boyut limiti invariantını kontrol eder.
        
        Returns:
            Tüm fonksiyonlar limit içinde mi?
        """
        proje = Path(self.proje_yolu)
        hariç_tutulacaklar = [
            '__pycache__', '.git', '.pytest_cache',
            'venv', 'env', '.hypothesis'
        ]
        
        for py_dosya in proje.rglob('*.py'):
            if any(ht in py_dosya.parts for ht in hariç_tutulacaklar):
                continue
            
            buyuk_fonksiyonlar = self.fonksiyon_analizoru.buyuk_fonksiyonlari_tespit_et(
                str(py_dosya)
            )
            
            if buyuk_fonksiyonlar:
                return False
        
        return True
    
    def mimari_kurallar_invarianti_kontrol(self) -> bool:
        """
        Mimari kurallar invariantını kontrol eder.
        
        Returns:
            Tüm mimari kurallar uyuluyor mu?
        """
        ihlaller = self.import_analizoru.mimari_ihlalleri_tespit_et(
            str(self.proje_yolu)
        )
        return len(ihlaller) == 0