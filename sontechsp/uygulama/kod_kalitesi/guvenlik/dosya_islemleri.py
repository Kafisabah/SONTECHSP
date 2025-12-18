# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.dosya_islemleri
# Description: Dosya kopyalama ve hash işlemleri
# Changelog:
# - İlk versiyon: Dosya işlemleri yardımcıları

"""
Dosya İşlemleri Yardımcıları

Backup işlemleri için dosya kopyalama ve hash hesaplama
işlemlerini içerir.
"""

import hashlib
import shutil
from pathlib import Path
from typing import List, Tuple


class DosyaIslemleri:
    """
    Dosya İşlemleri Yardımcıları
    
    Backup işlemleri için gerekli dosya operasyonlarını sağlar.
    """
    
    @staticmethod
    def proje_kopyala(
        kaynak: Path,
        hedef: Path,
        hariç_tutulacaklar: List[str]
    ) -> Tuple[int, int]:
        """
        Proje dosyalarını kopyalar.
        
        Args:
            kaynak: Kaynak klasör
            hedef: Hedef klasör
            hariç_tutulacaklar: Hariç tutulacak desenler
            
        Returns:
            (dosya_sayisi, toplam_boyut)
        """
        dosya_sayisi = 0
        toplam_boyut = 0
        
        def ignore_patterns(dir_path, names):
            ignored = []
            for name in names:
                for pattern in hariç_tutulacaklar:
                    if pattern in name or name.endswith(pattern.replace('*', '')):
                        ignored.append(name)
                        break
            return ignored
        
        shutil.copytree(
            kaynak,
            hedef,
            ignore=ignore_patterns
        )
        
        # Dosya sayısı ve boyut hesapla
        for dosya in hedef.rglob('*'):
            if dosya.is_file():
                dosya_sayisi += 1
                toplam_boyut += dosya.stat().st_size
        
        return dosya_sayisi, toplam_boyut
    
    @staticmethod
    def hash_hesapla(klasor_yolu: Path) -> str:
        """
        Klasörün hash değerini hesaplar.
        
        Args:
            klasor_yolu: Hash hesaplanacak klasör
            
        Returns:
            MD5 hash değeri
        """
        hash_md5 = hashlib.md5()
        
        for dosya in sorted(klasor_yolu.rglob('*')):
            if dosya.is_file():
                hash_md5.update(str(dosya.relative_to(klasor_yolu)).encode())
                with open(dosya, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        
        return hash_md5.hexdigest()