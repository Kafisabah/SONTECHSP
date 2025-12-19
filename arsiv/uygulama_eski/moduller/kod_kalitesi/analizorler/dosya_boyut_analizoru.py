# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.analizorler.dosya_boyut_analizoru
# Description: Dosya boyut analizi ve limit kontrolü
# Changelog:
# - İlk versiyon: DosyaBoyutAnalizoru sınıfı oluşturuldu

"""
Dosya Boyut Analizörü

120 satır limitini aşan Python dosyalarını tespit eder.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class DosyaRaporu:
    """Dosya analiz raporu"""
    dosya_yolu: str
    satir_sayisi: int
    limit_asimi: int
    onerilen_bolme: List[str]


class DosyaBoyutAnalizoru:
    """
    Dosya boyut analizi yapan sınıf.
    
    120 satır limitini aşan dosyaları tespit eder ve
    yorum satırlarını filtreleyerek gerçek kod satırlarını sayar.
    """
    
    SATIR_LIMITI = 120
    
    def __init__(self, satir_limiti: int = SATIR_LIMITI):
        """
        Args:
            satir_limiti: Maksimum satır sayısı (varsayılan: 120)
        """
        self.satir_limiti = satir_limiti
    
    def buyuk_dosyalari_tespit_et(
        self, 
        klasor_yolu: str,
        hariç_tutulacaklar: List[str] = None
    ) -> List[DosyaRaporu]:
        """
        Belirtilen klasördeki büyük dosyaları tespit eder.
        
        Args:
            klasor_yolu: Taranacak klasör yolu
            hariç_tutulacaklar: Hariç tutulacak klasör/dosya isimleri
            
        Returns:
            Limit aşan dosyaların rapor listesi
        """
        if hariç_tutulacaklar is None:
            hariç_tutulacaklar = [
                '__pycache__', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis'
            ]
        
        raporlar = []
        klasor = Path(klasor_yolu)
        
        for py_dosya in klasor.rglob('*.py'):
            # Hariç tutulanları atla
            if any(ht in py_dosya.parts for ht in hariç_tutulacaklar):
                continue
            
            satir_sayisi = self.satir_sayisi_hesapla(str(py_dosya))
            
            if satir_sayisi > self.satir_limiti:
                limit_asimi = satir_sayisi - self.satir_limiti
                rapor = DosyaRaporu(
                    dosya_yolu=str(py_dosya),
                    satir_sayisi=satir_sayisi,
                    limit_asimi=limit_asimi,
                    onerilen_bolme=[]
                )
                raporlar.append(rapor)
        
        return raporlar

    def satir_sayisi_hesapla(self, dosya_yolu: str) -> int:
        """
        Dosyadaki gerçek kod satırlarını sayar.
        
        Args:
            dosya_yolu: Analiz edilecek dosya yolu
            
        Returns:
            Yorum satırları hariç kod satır sayısı
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            return self.yorum_satirlarini_filtrele(icerik)
        except Exception:
            return 0
    
    def yorum_satirlarini_filtrele(self, icerik: str) -> int:
        """
        İçerikteki yorum ve boş satırları filtreler.
        
        Args:
            icerik: Dosya içeriği
            
        Returns:
            Gerçek kod satır sayısı
        """
        satirlar = icerik.split('\n')
        kod_satir_sayisi = 0
        coklu_yorum = False
        
        for satir in satirlar:
            temiz_satir = satir.strip()
            
            # Boş satırları atla
            if not temiz_satir:
                continue
            
            # Çoklu satır yorum kontrolü
            if '"""' in temiz_satir or "'''" in temiz_satir:
                tirnak_sayisi = temiz_satir.count('"""') + temiz_satir.count("'''")
                if tirnak_sayisi == 1:
                    coklu_yorum = not coklu_yorum
                    continue
                elif tirnak_sayisi == 2:
                    # Tek satırda açılıp kapanan docstring
                    continue
            
            # Çoklu yorum içindeyse atla
            if coklu_yorum:
                continue
            
            # Tek satır yorum kontrolü
            if temiz_satir.startswith('#'):
                continue
            
            # Gerçek kod satırı
            kod_satir_sayisi += 1
        
        return kod_satir_sayisi
