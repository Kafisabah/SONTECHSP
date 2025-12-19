# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.otomatik_kontrol_sistemi
# Description: Otomatik kalite kontrol sistemi
# Changelog:
# - İlk versiyon: OtomatikKontrolSistemi sınıfı oluşturuldu

"""
Otomatik Kalite Kontrol Sistemi

Tüm kalite kontrol işlemlerini otomatik yapan ve raporlayan sistem.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import sys

from .analizorler.dosya_boyut_analizoru import (
    DosyaBoyutAnalizoru, DosyaRaporu
)
from .analizorler.fonksiyon_boyut_analizoru import (
    FonksiyonBoyutAnalizoru, FonksiyonRaporu
)
from .analizorler.import_yapisi_analizoru import (
    ImportYapisiAnalizoru, MimariIhlal
)


@dataclass
class KaliteKontrolRaporu:
    """Kalite kontrol raporu"""
    dosya_boyut_ihlalleri: List[DosyaRaporu]
    fonksiyon_boyut_ihlalleri: List[FonksiyonRaporu]
    mimari_ihlaller: List[MimariIhlal]
    pep8_ihlalleri: List[Dict[str, Any]]
    toplam_ihlal_sayisi: int
    basarili: bool


class OtomatikKontrolSistemi:
    """
    Otomatik kalite kontrol sistemi.
    
    Dosya boyutu, fonksiyon boyutu, mimari kurallar ve
    PEP8 uyumluluğunu otomatik kontrol eder.
    """
    
    def __init__(
        self,
        proje_yolu: str = ".",
        dosya_limiti: int = 120,
        fonksiyon_limiti: int = 25
    ):
        """
        Args:
            proje_yolu: Kontrol edilecek proje yolu
            dosya_limiti: Maksimum dosya satır sayısı
            fonksiyon_limiti: Maksimum fonksiyon satır sayısı
        """
        self.proje_yolu = proje_yolu
        self.dosya_analizoru = DosyaBoyutAnalizoru(dosya_limiti)
        self.fonksiyon_analizoru = FonksiyonBoyutAnalizoru(fonksiyon_limiti)
        self.import_analizoru = ImportYapisiAnalizoru(proje_yolu)
    
    def tam_kontrol_yap(self) -> KaliteKontrolRaporu:
        """
        Tüm kalite kontrollerini yapar.
        
        Returns:
            Kapsamlı kalite kontrol raporu
        """
        # Dosya boyut kontrolü
        dosya_ihlalleri = self.dosya_boyut_kontrolu()
        
        # Fonksiyon boyut kontrolü
        fonksiyon_ihlalleri = self.fonksiyon_boyut_kontrolu()
        
        # Mimari ihlal kontrolü
        mimari_ihlaller = self.mimari_ihlal_kontrolu()
        
        # PEP8 kontrolü
        pep8_ihlalleri = self.pep8_kontrolu()
        
        # Toplam ihlal sayısı
        toplam_ihlal = (
            len(dosya_ihlalleri) +
            len(fonksiyon_ihlalleri) +
            len(mimari_ihlaller) +
            len(pep8_ihlalleri)
        )
        
        rapor = KaliteKontrolRaporu(
            dosya_boyut_ihlalleri=dosya_ihlalleri,
            fonksiyon_boyut_ihlalleri=fonksiyon_ihlalleri,
            mimari_ihlaller=mimari_ihlaller,
            pep8_ihlalleri=pep8_ihlalleri,
            toplam_ihlal_sayisi=toplam_ihlal,
            basarili=(toplam_ihlal == 0)
        )
        
        return rapor
    
    def dosya_boyut_kontrolu(self) -> List[DosyaRaporu]:
        """
        Otomatik dosya boyut kontrolü yapar.
        
        Returns:
            Limit aşan dosyaların listesi
        """
        return self.dosya_analizoru.buyuk_dosyalari_tespit_et(
            self.proje_yolu
        )
    
    def fonksiyon_boyut_kontrolu(self) -> List[FonksiyonRaporu]:
        """
        Otomatik fonksiyon boyut kontrolü yapar.
        
        Returns:
            Limit aşan fonksiyonların listesi
        """
        tum_ihlaller = []
        proje = Path(self.proje_yolu)
        
        hariç_tutulacaklar = [
            '__pycache__', '.git', '.pytest_cache',
            'venv', 'env', '.hypothesis'
        ]
        
        for py_dosya in proje.rglob('*.py'):
            # Hariç tutulanları atla
            if any(ht in py_dosya.parts for ht in hariç_tutulacaklar):
                continue
            
            ihlaller = self.fonksiyon_analizoru.buyuk_fonksiyonlari_tespit_et(
                str(py_dosya)
            )
            tum_ihlaller.extend(ihlaller)
        
        return tum_ihlaller
    
    def mimari_ihlal_kontrolu(self) -> List[MimariIhlal]:
        """
        Otomatik mimari ihlal kontrolü yapar.
        
        Returns:
            Mimari ihlal listesi
        """
        return self.import_analizoru.mimari_ihlalleri_tespit_et(
            self.proje_yolu
        )
    
    def pep8_kontrolu(self) -> List[Dict[str, Any]]:
        """
        Otomatik PEP8 uyumluluk kontrolü yapar.
        
        flake8 veya pycodestyle kullanarak PEP8 kontrolü yapar.
        
        Returns:
            PEP8 ihlal listesi
        """
        ihlaller = []
        
        try:
            # flake8 ile kontrol
            sonuc = subprocess.run(
                [sys.executable, '-m', 'flake8', self.proje_yolu,
                 '--exclude=__pycache__,.git,.pytest_cache,venv,env,.hypothesis',
                 '--max-line-length=120',
                 '--format=json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if sonuc.returncode != 0 and sonuc.stdout:
                # JSON formatında sonuçları parse et
                import json
                try:
                    ihlaller = json.loads(sonuc.stdout)
                except json.JSONDecodeError:
                    # JSON parse edilemezse, text formatında işle
                    for satir in sonuc.stdout.split('\n'):
                        if satir.strip():
                            ihlaller.append({
                                'dosya': 'bilinmeyen',
                                'satir': 0,
                                'mesaj': satir
                            })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # flake8 yoksa veya timeout olursa, basit kontrol yap
            ihlaller = self._basit_pep8_kontrolu()
        
        return ihlaller
    
    def _basit_pep8_kontrolu(self) -> List[Dict[str, Any]]:
        """
        Basit PEP8 kontrolü yapar (flake8 yoksa).
        
        Returns:
            Basit PEP8 ihlal listesi
        """
        ihlaller = []
        proje = Path(self.proje_yolu)
        
        hariç_tutulacaklar = [
            '__pycache__', '.git', '.pytest_cache',
            'venv', 'env', '.hypothesis'
        ]
        
        for py_dosya in proje.rglob('*.py'):
            if any(ht in py_dosya.parts for ht in hariç_tutulacaklar):
                continue
            
            try:
                with open(py_dosya, 'r', encoding='utf-8') as f:
                    satirlar = f.readlines()
                
                for i, satir in enumerate(satirlar, 1):
                    # Satır uzunluğu kontrolü
                    if len(satir.rstrip()) > 120:
                        ihlaller.append({
                            'dosya': str(py_dosya),
                            'satir': i,
                            'mesaj': f'Satır çok uzun ({len(satir.rstrip())} > 120)'
                        })
                    
                    # Trailing whitespace kontrolü
                    if satir.rstrip() != satir.rstrip('\n').rstrip('\r'):
                        ihlaller.append({
                            'dosya': str(py_dosya),
                            'satir': i,
                            'mesaj': 'Satır sonunda boşluk var'
                        })
            except Exception:
                continue
        
        return ihlaller
    
    def rapor_uret(self, rapor: KaliteKontrolRaporu) -> str:
        """
        Kalite kontrol raporunu metin formatında üretir.
        
        Args:
            rapor: Kalite kontrol raporu
            
        Returns:
            Metin formatında rapor
        """
        satirlar = []
        satirlar.append("=" * 80)
        satirlar.append("KALİTE KONTROL RAPORU")
        satirlar.append("=" * 80)
        satirlar.append("")
        
        # Özet
        satirlar.append(f"Toplam İhlal Sayısı: {rapor.toplam_ihlal_sayisi}")
        satirlar.append(f"Durum: {'✓ BAŞARILI' if rapor.basarili else '✗ BAŞARISIZ'}")
        satirlar.append("")
        
        # Dosya boyut ihlalleri
        if rapor.dosya_boyut_ihlalleri:
            satirlar.append("-" * 80)
            satirlar.append(f"DOSYA BOYUT İHLALLERİ ({len(rapor.dosya_boyut_ihlalleri)})")
            satirlar.append("-" * 80)
            for ihlal in rapor.dosya_boyut_ihlalleri:
                satirlar.append(
                    f"  • {ihlal.dosya_yolu}: "
                    f"{ihlal.satir_sayisi} satır (+{ihlal.limit_asimi})"
                )
            satirlar.append("")
        
        # Fonksiyon boyut ihlalleri
        if rapor.fonksiyon_boyut_ihlalleri:
            satirlar.append("-" * 80)
            satirlar.append(
                f"FONKSİYON BOYUT İHLALLERİ ({len(rapor.fonksiyon_boyut_ihlalleri)})"
            )
            satirlar.append("-" * 80)
            for ihlal in rapor.fonksiyon_boyut_ihlalleri:
                satirlar.append(
                    f"  • {ihlal.dosya_yolu}::{ihlal.fonksiyon_adi}: "
                    f"{ihlal.satir_sayisi} satır"
                )
            satirlar.append("")
        
        # Mimari ihlaller
        if rapor.mimari_ihlaller:
            satirlar.append("-" * 80)
            satirlar.append(f"MİMARİ İHLALLER ({len(rapor.mimari_ihlaller)})")
            satirlar.append("-" * 80)
            for ihlal in rapor.mimari_ihlaller:
                satirlar.append(f"  • {ihlal.kaynak_dosya}")
                satirlar.append(f"    → {ihlal.hedef_dosya}")
                satirlar.append(f"    Tür: {ihlal.ihlal_turu}")
                satirlar.append(f"    Çözüm: {ihlal.cozum_onerisi}")
            satirlar.append("")
        
        # PEP8 ihlalleri (ilk 20 tanesi)
        if rapor.pep8_ihlalleri:
            satirlar.append("-" * 80)
            satirlar.append(
                f"PEP8 İHLALLERİ ({len(rapor.pep8_ihlalleri)} - ilk 20 gösteriliyor)"
            )
            satirlar.append("-" * 80)
            for ihlal in rapor.pep8_ihlalleri[:20]:
                satirlar.append(
                    f"  • {ihlal.get('dosya', 'bilinmeyen')}:"
                    f"{ihlal.get('satir', 0)} - {ihlal.get('mesaj', '')}"
                )
            satirlar.append("")
        
        satirlar.append("=" * 80)
        
        return '\n'.join(satirlar)
