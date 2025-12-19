# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.test_entegrasyon.test_dogrulayici
# Description: Test doğrulama ve coverage koruma sistemi
# Changelog:
# - İlk versiyon: TestDogrulayici sınıfı oluşturuldu

"""
Test Doğrulayıcı

Refactoring sonrası testlerin çalıştırılması,
coverage hesaplanması ve korunması için sistem.
"""

import subprocess
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class TestSonucu:
    """Test çalıştırma sonucu"""
    basarili: bool
    toplam_test: int = 0
    basarili_test: int = 0
    basarisiz_test: int = 0
    atlanan_test: int = 0
    sure: float = 0.0
    hata_mesajlari: List[str] = field(default_factory=list)
    coverage_yuzdesi: Optional[float] = None


@dataclass
class CoverageRaporu:
    """Coverage raporu"""
    toplam_satir: int
    kapsanan_satir: int
    yuzde: float
    dosya_bazli: Dict[str, float] = field(default_factory=dict)


class TestDogrulayici:
    """
    Test doğrulama ve coverage koruma sınıfı.
    
    Refactoring işlemleri sonrasında testlerin çalıştırılması,
    başarı durumunun kontrol edilmesi ve coverage'ın korunması
    için sistemler sağlar.
    """
    
    def __init__(
        self,
        test_klasoru: str = "tests",
        min_coverage: float = 80.0
    ):
        """
        Args:
            test_klasoru: Test dosyalarının bulunduğu klasör
            min_coverage: Minimum kabul edilebilir coverage yüzdesi
        """
        self.test_klasoru = test_klasoru
        self.min_coverage = min_coverage
        self._onceki_coverage: Optional[float] = None
    
    def tum_testleri_calistir(
        self,
        coverage_hesapla: bool = True
    ) -> TestSonucu:
        """
        Tüm testleri çalıştırır.
        
        Args:
            coverage_hesapla: Coverage hesaplansın mı
            
        Returns:
            Test sonucu
        """
        try:
            # pytest komutunu hazırla
            komut = ['pytest', self.test_klasoru, '-v', '--tb=short']
            
            if coverage_hesapla:
                komut.extend(['--cov=uygulama', '--cov-report=json'])
            
            # Testleri çalıştır
            sonuc = subprocess.run(
                komut,
                capture_output=True,
                text=True,
                timeout=300  # 5 dakika timeout
            )
            
            # Sonuçları parse et
            test_sonucu = self._pytest_sonucunu_parse_et(sonuc)
            
            # Coverage hesapla
            if coverage_hesapla:
                coverage = self._coverage_hesapla()
                if coverage:
                    test_sonucu.coverage_yuzdesi = coverage.yuzde
            
            return test_sonucu
            
        except subprocess.TimeoutExpired:
            return TestSonucu(
                basarili=False,
                hata_mesajlari=["Testler timeout süresini aştı"]
            )
        except Exception as e:
            return TestSonucu(
                basarili=False,
                hata_mesajlari=[f"Test çalıştırma hatası: {str(e)}"]
            )
    
    def belirli_testleri_calistir(
        self,
        test_dosyalari: List[str]
    ) -> TestSonucu:
        """
        Belirli test dosyalarını çalıştırır.
        
        Args:
            test_dosyalari: Çalıştırılacak test dosyaları
            
        Returns:
            Test sonucu
        """
        try:
            # pytest komutunu hazırla
            komut = ['pytest'] + test_dosyalari + ['-v', '--tb=short']
            
            # Testleri çalıştır
            sonuc = subprocess.run(
                komut,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Sonuçları parse et
            return self._pytest_sonucunu_parse_et(sonuc)
            
        except Exception as e:
            return TestSonucu(
                basarili=False,
                hata_mesajlari=[f"Test çalıştırma hatası: {str(e)}"]
            )
    
    def coverage_hesapla(self) -> Optional[CoverageRaporu]:
        """
        Coverage hesaplar.
        
        Returns:
            Coverage raporu veya None
        """
        return self._coverage_hesapla()
    
    def coverage_korundu_mu(
        self,
        onceki_coverage: float,
        yeni_coverage: float,
        tolerans: float = 1.0
    ) -> bool:
        """
        Coverage'ın korunup korunmadığını kontrol eder.
        
        Args:
            onceki_coverage: Önceki coverage yüzdesi
            yeni_coverage: Yeni coverage yüzdesi
            tolerans: İzin verilen düşüş yüzdesi
            
        Returns:
            Coverage korundu mu
        """
        # Yeni coverage, önceki coverage'dan tolerans kadar
        # düşük olabilir
        return yeni_coverage >= (onceki_coverage - tolerans)
    
    def onceki_coverage_kaydet(self, coverage: float) -> None:
        """
        Önceki coverage değerini kaydeder.
        
        Args:
            coverage: Coverage yüzdesi
        """
        self._onceki_coverage = coverage
    
    def onceki_coverage_al(self) -> Optional[float]:
        """
        Önceki coverage değerini alır.
        
        Returns:
            Önceki coverage veya None
        """
        return self._onceki_coverage
    
    def _pytest_sonucunu_parse_et(
        self,
        sonuc: subprocess.CompletedProcess
    ) -> TestSonucu:
        """
        pytest çıktısını parse eder.
        
        Args:
            sonuc: subprocess sonucu
            
        Returns:
            Test sonucu
        """
        cikti = sonuc.stdout + sonuc.stderr
        
        # Test sayılarını bul
        toplam = 0
        basarili = 0
        basarisiz = 0
        atlanan = 0
        
        # pytest çıktısından sayıları çıkar
        import re
        
        # "X passed" formatı
        passed_match = re.search(r'(\d+) passed', cikti)
        if passed_match:
            basarili = int(passed_match.group(1))
            toplam += basarili
        
        # "X failed" formatı
        failed_match = re.search(r'(\d+) failed', cikti)
        if failed_match:
            basarisiz = int(failed_match.group(1))
            toplam += basarisiz
        
        # "X skipped" formatı
        skipped_match = re.search(r'(\d+) skipped', cikti)
        if skipped_match:
            atlanan = int(skipped_match.group(1))
            toplam += atlanan
        
        # Süreyi bul
        sure = 0.0
        time_match = re.search(r'in ([\d.]+)s', cikti)
        if time_match:
            sure = float(time_match.group(1))
        
        # Hata mesajlarını topla
        hata_mesajlari = []
        if basarisiz > 0:
            # FAILED satırlarını bul
            for satir in cikti.split('\n'):
                if 'FAILED' in satir or 'ERROR' in satir:
                    hata_mesajlari.append(satir.strip())
        
        return TestSonucu(
            basarili=(sonuc.returncode == 0),
            toplam_test=toplam,
            basarili_test=basarili,
            basarisiz_test=basarisiz,
            atlanan_test=atlanan,
            sure=sure,
            hata_mesajlari=hata_mesajlari
        )
    
    def _coverage_hesapla(self) -> Optional[CoverageRaporu]:
        """
        Coverage raporunu okur ve parse eder.
        
        Returns:
            Coverage raporu veya None
        """
        coverage_dosyasi = 'coverage.json'
        
        if not os.path.exists(coverage_dosyasi):
            return None
        
        try:
            with open(coverage_dosyasi, 'r', encoding='utf-8') as f:
                veri = json.load(f)
            
            # Toplam coverage
            toplam_satir = veri['totals']['num_statements']
            kapsanan_satir = veri['totals']['covered_lines']
            yuzde = veri['totals']['percent_covered']
            
            # Dosya bazlı coverage
            dosya_bazli = {}
            for dosya, bilgi in veri['files'].items():
                dosya_bazli[dosya] = bilgi['summary']['percent_covered']
            
            return CoverageRaporu(
                toplam_satir=toplam_satir,
                kapsanan_satir=kapsanan_satir,
                yuzde=yuzde,
                dosya_bazli=dosya_bazli
            )
            
        except Exception as e:
            print(f"Coverage okuma hatası: {e}")
            return None
