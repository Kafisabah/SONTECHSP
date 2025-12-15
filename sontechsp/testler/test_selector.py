# Version: 0.1.0
# Last Update: 2025-01-15
# Module: test_selector
# Description: Test seçici ve önceliklendirme sistemi
# Changelog:
# - İlk versiyon: TestSelector sınıfı ve algoritmaları

import os
import random
import time
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import subprocess
import json


@dataclass
class TestMetadata:
    """Test metadata sınıfı."""
    name: str
    markers: List[str]
    estimated_duration: float
    priority: int
    dependencies: List[str]
    file_path: str


@dataclass
class PerformanceMetrics:
    """Performans metrikleri sınıfı."""
    total_duration: float
    test_count: int
    worker_count: int
    coverage_percentage: float
    failed_tests: List[str]
    slow_tests: List[str]


class TestSelector:
    """Test seçici ve önceliklendirme sistemi."""
    
    def __init__(self):
        """TestSelector başlatıcı."""
        self.kritik_dosyalar = {
            "sontechsp/uygulama/ana.py": 10,
            "sontechsp/uygulama/cekirdek/": 9,
            "sontechsp/uygulama/veritabani/": 8,
            "sontechsp/testler/test_bagimlilik_standardi.py": 7,
            "sontechsp/testler/test_ana_uygulama.py": 6,
        }
        
        self.marker_oncelikleri = {
            "critical": 10,
            "smoke": 9,
            "unit": 8,
            "integration": 6,
            "property": 5,
            "slow": 1,
        }
    
    def select_fast_tests(self) -> List[str]:
        """
        Hızlı testleri seç.
        
        Returns:
            List[str]: Hızlı test dosyalarının listesi
        """
        test_dosyalari = self._get_all_test_files()
        hizli_testler = []
        
        for test_dosyasi in test_dosyalari:
            # Slow marker'ı olmayan testleri seç
            if not self._has_slow_marker(test_dosyasi):
                hizli_testler.append(test_dosyasi)
        
        return hizli_testler
    
    def select_critical_tests(self) -> List[str]:
        """
        Kritik testleri seç.
        
        Returns:
            List[str]: Kritik test dosyalarının listesi
        """
        test_dosyalari = self._get_all_test_files()
        kritik_testler = []
        
        for test_dosyasi in test_dosyalari:
            # Critical marker'ı olan testleri seç
            if self._has_critical_marker(test_dosyasi):
                kritik_testler.append(test_dosyasi)
        
        # Kritik dosya isimlerine göre de seç
        for dosya_yolu, oncelik in self.kritik_dosyalar.items():
            if oncelik >= 7:  # Yüksek öncelikli dosyalar
                test_dosyasi = f"sontechsp/testler/test_{Path(dosya_yolu).stem}.py"
                if os.path.exists(test_dosyasi) and test_dosyasi not in kritik_testler:
                    kritik_testler.append(test_dosyasi)
        
        return kritik_testler
    
    def sample_parametrized_tests(self, ratio: float = 0.3) -> List[str]:
        """
        Parametrize testlerin örneklemesini yap.
        
        Args:
            ratio: Seçilecek testlerin oranı (0.0-1.0)
            
        Returns:
            List[str]: Örneklenmiş test dosyalarının listesi
        """
        if not 0.0 <= ratio <= 1.0:
            raise ValueError("Ratio 0.0 ile 1.0 arasında olmalı")
        
        parametrize_testler = self._get_parametrized_tests()
        
        # Rastgele örnekleme yap
        sample_size = max(1, int(len(parametrize_testler) * ratio))
        return random.sample(parametrize_testler, min(sample_size, len(parametrize_testler)))
    
    def prioritize_tests(self) -> List[str]:
        """
        Testleri öncelik sırasına göre sırala.
        
        Returns:
            List[str]: Öncelik sırasına göre sıralanmış test dosyaları
        """
        test_dosyalari = self._get_all_test_files()
        test_oncelikleri = []
        
        for test_dosyasi in test_dosyalari:
            oncelik = self._calculate_test_priority(test_dosyasi)
            test_oncelikleri.append((test_dosyasi, oncelik))
        
        # Öncelik sırasına göre sırala (yüksek öncelik önce)
        test_oncelikleri.sort(key=lambda x: x[1], reverse=True)
        
        return [test_dosyasi for test_dosyasi, _ in test_oncelikleri]
    
    def _get_all_test_files(self) -> List[str]:
        """Tüm test dosyalarını al."""
        test_klasoru = Path("sontechsp/testler")
        if not test_klasoru.exists():
            return []
        
        test_dosyalari = []
        for dosya in test_klasoru.glob("test_*.py"):
            test_dosyalari.append(str(dosya))
        
        return test_dosyalari
    
    def _has_slow_marker(self, test_dosyasi: str) -> bool:
        """Test dosyasında slow marker'ı var mı kontrol et."""
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
                return "@pytest.mark.slow" in icerik
        except (FileNotFoundError, UnicodeDecodeError):
            return False
    
    def _has_critical_marker(self, test_dosyasi: str) -> bool:
        """Test dosyasında critical marker'ı var mı kontrol et."""
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
                return "@pytest.mark.critical" in icerik
        except (FileNotFoundError, UnicodeDecodeError):
            return False
    
    def _get_parametrized_tests(self) -> List[str]:
        """Parametrize testleri al."""
        test_dosyalari = self._get_all_test_files()
        parametrize_testler = []
        
        for test_dosyasi in test_dosyalari:
            try:
                with open(test_dosyasi, 'r', encoding='utf-8') as f:
                    icerik = f.read()
                    if "@pytest.mark.parametrize" in icerik:
                        parametrize_testler.append(test_dosyasi)
            except (FileNotFoundError, UnicodeDecodeError):
                continue
        
        return parametrize_testler
    
    def _calculate_test_priority(self, test_dosyasi: str) -> int:
        """Test dosyasının önceliğini hesapla."""
        oncelik = 0
        
        # Dosya adına göre öncelik
        dosya_adi = Path(test_dosyasi).name
        for kritik_dosya, kritik_oncelik in self.kritik_dosyalar.items():
            if Path(kritik_dosya).stem in dosya_adi:
                oncelik += kritik_oncelik
        
        # Marker'lara göre öncelik
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
                
                for marker, marker_oncelik in self.marker_oncelikleri.items():
                    if f"@pytest.mark.{marker}" in icerik:
                        oncelik += marker_oncelik
        except (FileNotFoundError, UnicodeDecodeError):
            pass
        
        return oncelik
    
    def get_test_metadata(self, test_dosyasi: str) -> TestMetadata:
        """Test dosyası için metadata al."""
        markers = self._extract_markers(test_dosyasi)
        estimated_duration = self._estimate_test_duration(test_dosyasi)
        priority = self._calculate_test_priority(test_dosyasi)
        dependencies = self._extract_dependencies(test_dosyasi)
        
        return TestMetadata(
            name=Path(test_dosyasi).stem,
            markers=markers,
            estimated_duration=estimated_duration,
            priority=priority,
            dependencies=dependencies,
            file_path=test_dosyasi
        )
    
    def _extract_markers(self, test_dosyasi: str) -> List[str]:
        """Test dosyasından marker'ları çıkar."""
        markers = []
        
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
                
                for marker in self.marker_oncelikleri.keys():
                    if f"@pytest.mark.{marker}" in icerik:
                        markers.append(marker)
        except (FileNotFoundError, UnicodeDecodeError):
            pass
        
        return markers
    
    def _estimate_test_duration(self, test_dosyasi: str) -> float:
        """Test dosyası için tahmini süre hesapla."""
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
                
                # Basit tahmin algoritması
                test_sayisi = icerik.count("def test_")
                parametrize_sayisi = icerik.count("@pytest.mark.parametrize")
                property_sayisi = icerik.count("@given")
                
                # Temel süre hesaplama
                base_duration = test_sayisi * 0.1  # Test başına 100ms
                
                # Parametrize testler daha uzun sürer
                if parametrize_sayisi > 0:
                    base_duration *= (parametrize_sayisi * 2)
                
                # Property testler değişken sürer
                if property_sayisi > 0:
                    base_duration += property_sayisi * 0.5
                
                # Slow marker varsa daha uzun
                if self._has_slow_marker(test_dosyasi):
                    base_duration *= 5
                
                return base_duration
        except (FileNotFoundError, UnicodeDecodeError):
            return 1.0  # Varsayılan 1 saniye
    
    def _extract_dependencies(self, test_dosyasi: str) -> List[str]:
        """Test dosyasından bağımlılıkları çıkar."""
        dependencies = []
        
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
                
                # Import satırlarından bağımlılıkları çıkar
                lines = icerik.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('from sontechsp') or line.startswith('import sontechsp'):
                        # sontechsp modül bağımlılıklarını ekle
                        if 'from sontechsp' in line:
                            module = line.split('from ')[1].split(' import')[0]
                            dependencies.append(module)
        except (FileNotFoundError, UnicodeDecodeError):
            pass
        
        return dependencies


class PerformanceAnalyzer:
    """Performans analizi sınıfı."""
    
    def __init__(self):
        """PerformanceAnalyzer başlatıcı."""
        self.test_selector = TestSelector()
    
    def analyze_test_performance(self) -> PerformanceMetrics:
        """Test performansını analiz et."""
        start_time = time.time()
        
        # Test bilgilerini topla
        test_dosyalari = self.test_selector._get_all_test_files()
        test_count = len(test_dosyalari)
        
        # Yavaş testleri belirle
        slow_tests = []
        for test_dosyasi in test_dosyalari:
            if self.test_selector._has_slow_marker(test_dosyasi):
                slow_tests.append(test_dosyasi)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return PerformanceMetrics(
            total_duration=total_duration,
            test_count=test_count,
            worker_count=1,  # Varsayılan
            coverage_percentage=0.0,  # Hesaplanacak
            failed_tests=[],
            slow_tests=slow_tests
        )
    
    def get_optimization_suggestions(self) -> List[str]:
        """Optimizasyon önerileri al."""
        suggestions = []
        
        # Yavaş testleri kontrol et
        slow_tests = []
        test_dosyalari = self.test_selector._get_all_test_files()
        
        for test_dosyasi in test_dosyalari:
            if self.test_selector._has_slow_marker(test_dosyasi):
                slow_tests.append(test_dosyasi)
        
        if len(slow_tests) > len(test_dosyalari) * 0.3:
            suggestions.append("Çok fazla yavaş test var. Bazıları optimize edilebilir.")
        
        # Parametrize test sayısını kontrol et
        parametrize_tests = self.test_selector._get_parametrized_tests()
        if len(parametrize_tests) > 10:
            suggestions.append("Parametrize testlerin sayısı azaltılabilir.")
        
        # Genel öneriler
        suggestions.extend([
            "Paralel test çalıştırma kullanın: pytest -n auto",
            "Hızlı testleri önce çalıştırın: pytest -m 'not slow'",
            "CI/CD için sadece kritik testleri çalıştırın: pytest -m critical"
        ])
        
        return suggestions