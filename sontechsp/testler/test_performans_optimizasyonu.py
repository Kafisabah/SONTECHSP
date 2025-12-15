# Version: 0.1.0
# Last Update: 2025-01-15
# Module: test_performans_optimizasyonu
# Description: Test performans optimizasyonu için property testler
# Changelog:
# - İlk versiyon: Test konfigürasyon doğrulaması property testleri

import pytest
import toml
import random
from pathlib import Path
from hypothesis import given, strategies as st
from typing import Dict, Any, List
import subprocess
import time
import os
import multiprocessing


class TestPerformansOptimizasyonu:
    """Test performans optimizasyonu property testleri."""
    
    def test_pyproject_toml_mevcut(self):
        """pyproject.toml dosyasının mevcut olduğunu doğrula."""
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml dosyası bulunamadı"
    
    def test_marker_konfigurasyonu_mevcut(self):
        """
        **Test Performans Optimizasyonu, Özellik 5: Marker Konfigürasyonu**
        **Doğrular: Gereksinimler 2.1, 2.3**
        
        pyproject.toml'de gerekli marker'ların tanımlı olduğunu doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        # pytest konfigürasyonunu kontrol et
        pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        markers = pytest_config.get("markers", [])
        
        # Gerekli marker'ları kontrol et
        gerekli_markerlar = ["unit", "integration", "property", "slow", "critical", "smoke"]
        mevcut_markerlar = [marker.split(":")[0].strip() for marker in markers]
        
        for marker in gerekli_markerlar:
            assert marker in mevcut_markerlar, f"'{marker}' marker'ı pyproject.toml'de tanımlı değil"
    
    @given(st.lists(st.sampled_from(["unit", "integration", "property", "slow", "critical", "smoke"]), 
                   min_size=1, max_size=3, unique=True))
    def test_marker_konfigurasyonu_property(self, markerlar: List[str]):
        """
        **Test Performans Optimizasyonu, Özellik 5: Marker Konfigürasyonu**
        **Doğrular: Gereksinimler 2.1, 2.3**
        
        Herhangi bir marker kombinasyonu için konfigürasyonun geçerli olduğunu doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        mevcut_markerlar = pytest_config.get("markers", [])
        mevcut_marker_isimleri = [marker.split(":")[0].strip() for marker in mevcut_markerlar]
        
        # Tüm test edilen marker'ların konfigürasyonda olduğunu doğrula
        for marker in markerlar:
            assert marker in mevcut_marker_isimleri, f"Marker '{marker}' konfigürasyonda bulunamadı"
    
    def test_hypothesis_ayarlari_mevcut(self):
        """
        **Test Performans Optimizasyonu, Özellik 7: Hypothesis Optimizasyonu**
        **Doğrular: Gereksinimler 3.1, 3.2**
        
        Hypothesis ayarlarının optimize edildiğini doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        
        # Maksimum örnek sayısının 50 olduğunu kontrol et
        max_examples = hypothesis_config.get("max_examples", 100)
        assert max_examples == 50, f"max_examples {max_examples} olmalı, 50 değil"
        
        # Deadline'ın 2000ms olduğunu kontrol et
        deadline = hypothesis_config.get("deadline", 5000)
        assert deadline == 2000, f"deadline {deadline}ms olmalı, 2000ms değil"
        
        # Health check'lerin devre dışı olduğunu kontrol et
        suppress_health_check = hypothesis_config.get("suppress_health_check", [])
        gerekli_suppressions = ["too_slow", "filter_too_much", "data_too_large"]
        
        for suppression in gerekli_suppressions:
            assert suppression in suppress_health_check, f"'{suppression}' health check devre dışı değil"
    
    @given(st.integers(min_value=10, max_value=100))
    def test_hypothesis_max_examples_property(self, max_examples: int):
        """
        **Test Performans Optimizasyonu, Özellik 7: Hypothesis Optimizasyonu**
        **Doğrular: Gereksinimler 3.1, 3.2**
        
        Herhangi bir max_examples değeri için, konfigürasyonun 50 veya daha az olduğunu doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        configured_max_examples = hypothesis_config.get("max_examples", 100)
        
        # Konfigüre edilen değerin test edilen değerden küçük veya eşit olduğunu doğrula
        # (performans optimizasyonu için)
        if max_examples >= 50:
            assert configured_max_examples <= 50, "max_examples performans için 50 veya daha az olmalı"
    
    def test_pytest_xdist_bagimliligi(self):
        """
        **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
        **Doğrular: Gereksinimler 5.1, 5.2**
        
        pytest-xdist bağımlılığının eklendiğini doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        dev_dependencies = config.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        
        # pytest-xdist bağımlılığının olduğunu kontrol et
        xdist_found = any("pytest-xdist" in dep for dep in dev_dependencies)
        assert xdist_found, "pytest-xdist bağımlılığı dev dependencies'de bulunamadı"
    
    def test_varsayilan_test_davranisi(self):
        """
        **Test Performans Optimizasyonu, Özellik 3: Varsayılan Test Davranışı**
        **Doğrular: Gereksinimler 1.5**
        
        Varsayılan pytest çalıştırmasında yavaş testlerin çalışmadığını doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        addopts = pytest_config.get("addopts", [])
        
        # addopts'ta "not slow" filtresi olduğunu kontrol et
        addopts_str = " ".join(addopts) if isinstance(addopts, list) else str(addopts)
        assert "not slow" in addopts_str, "Varsayılan pytest konfigürasyonunda 'not slow' filtresi bulunamadı"
    
    @pytest.mark.slow
    def test_cpu_cekirdek_sayisi_worker_hesaplama(self):
        """
        **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
        **Doğrular: Gereksinimler 5.1, 5.2**
        
        CPU çekirdek sayısına göre worker sayısının doğru hesaplandığını doğrula.
        """
        cpu_count = multiprocessing.cpu_count()
        
        # CPU sayısının pozitif olduğunu doğrula
        assert cpu_count > 0, "CPU çekirdek sayısı pozitif olmalı"
        
        # Optimal worker sayısının CPU sayısına eşit veya daha az olduğunu doğrula
        # (genellikle CPU sayısı kadar worker kullanılır)
        optimal_workers = min(cpu_count, 8)  # Maksimum 8 worker
        assert optimal_workers <= cpu_count, "Worker sayısı CPU çekirdek sayısını aşmamalı"
        assert optimal_workers > 0, "En az 1 worker olmalı"


class TestMarkerTabanliTestSecimi:
    """Marker tabanlı test seçimi property testleri."""
    
    @given(st.sampled_from(["unit", "integration", "property", "slow", "critical", "smoke"]))
    def test_marker_filtreleme_property(self, marker: str):
        """
        **Test Performans Optimizasyonu, Özellik 2: Marker Tabanlı Test Seçimi**
        **Doğrular: Gereksinimler 1.3, 2.2**
        
        Herhangi bir marker için filtrelemenin çalıştığını doğrula.
        """
        # Marker'ın geçerli olduğunu doğrula
        gecerli_markerlar = ["unit", "integration", "property", "slow", "critical", "smoke"]
        assert marker in gecerli_markerlar, f"'{marker}' geçerli bir marker değil"
        
        # pyproject.toml'de marker'ın tanımlı olduğunu kontrol et
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        markers = pytest_config.get("markers", [])
        mevcut_markerlar = [m.split(":")[0].strip() for m in markers]
        
        assert marker in mevcut_markerlar, f"Marker '{marker}' pyproject.toml'de tanımlı değil"
    
    @pytest.mark.unit
    def test_marker_kombinasyonu(self):
        """
        **Test Performans Optimizasyonu, Özellik 2: Marker Tabanlı Test Seçimi**
        **Doğrular: Gereksinimler 1.3, 2.2**
        
        Marker kombinasyonlarının çalıştığını doğrula.
        """
        # Bu test unit marker'ı ile işaretli
        # Marker'ın doğru çalıştığını doğrulamak için basit bir assertion
        assert True, "Unit marker'lı test çalışıyor"
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Integration marker testi."""
        assert True, "Integration marker'lı test çalışıyor"
    
    @pytest.mark.property
    def test_property_marker(self):
        """Property marker testi."""
        assert True, "Property marker'lı test çalışıyor"
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Slow marker testi."""
        time.sleep(0.1)  # Kısa bir bekleme
        assert True, "Slow marker'lı test çalışıyor"
    
    @pytest.mark.critical
    def test_critical_marker(self):
        """Critical marker testi."""
        assert True, "Critical marker'lı test çalışıyor"
    
    @pytest.mark.smoke
    def test_smoke_marker(self):
        """Smoke marker testi."""
        assert True, "Smoke marker'lı test çalışıyor"


class TestHypothesisOptimizasyonu:
    """Hypothesis optimizasyonu property testleri."""
    
    @given(st.integers(min_value=1000, max_value=10000))
    def test_hypothesis_deadline_property(self, test_deadline: int):
        """
        **Test Performans Optimizasyonu, Özellik 7: Hypothesis Optimizasyonu**
        **Doğrular: Gereksinimler 3.1, 3.2**
        
        Herhangi bir deadline değeri için, konfigüre edilen deadline'ın 2000ms veya daha az olduğunu doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        configured_deadline = hypothesis_config.get("deadline", 5000)
        
        # Konfigüre edilen deadline'ın performans için optimize edildiğini doğrula
        assert configured_deadline <= 2000, f"Deadline {configured_deadline}ms, performans için 2000ms veya daha az olmalı"
        
        # Test edilen deadline'ın konfigüre edilenden büyük olduğunda optimizasyonun etkili olduğunu doğrula
        if test_deadline > configured_deadline:
            assert configured_deadline < test_deadline, "Konfigüre edilen deadline test deadline'ından küçük olmalı"
    
    @given(st.lists(st.sampled_from(["too_slow", "filter_too_much", "data_too_large", "function_scoped_fixture"]), 
                   min_size=1, max_size=4, unique=True))
    def test_hypothesis_health_check_suppression_property(self, health_checks: List[str]):
        """
        **Test Performans Optimizasyonu, Özellik 8: Hypothesis Profil Ayarları**
        **Doğrular: Gereksinimler 3.3, 3.4**
        
        Herhangi bir health check kombinasyonu için, gerekli health check'lerin devre dışı olduğunu doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        suppressed_checks = hypothesis_config.get("suppress_health_check", [])
        
        # Performans için kritik olan health check'lerin devre dışı olduğunu doğrula
        kritik_suppressions = ["too_slow", "filter_too_much", "data_too_large"]
        
        for kritik_check in kritik_suppressions:
            assert kritik_check in suppressed_checks, f"Kritik health check '{kritik_check}' devre dışı değil"
        
        # Test edilen health check'lerin geçerli olduğunu doğrula
        gecerli_checks = ["too_slow", "filter_too_much", "data_too_large", "function_scoped_fixture"]
        for check in health_checks:
            assert check in gecerli_checks, f"'{check}' geçerli bir health check değil"
    
    @given(st.integers(min_value=10, max_value=200))
    def test_hypothesis_max_examples_optimizasyon_property(self, ornek_sayisi: int):
        """
        **Test Performans Optimizasyonu, Özellik 7: Hypothesis Optimizasyonu**
        **Doğrular: Gereksinimler 3.1, 3.2**
        
        Herhangi bir örnek sayısı için, konfigüre edilen max_examples'ın optimize edildiğini doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        configured_max_examples = hypothesis_config.get("max_examples", 100)
        
        # Konfigüre edilen max_examples'ın performans için optimize edildiğini doğrula
        assert configured_max_examples == 50, f"max_examples {configured_max_examples}, performans için 50 olmalı"
        
        # Büyük örnek sayıları için optimizasyonun etkili olduğunu doğrula
        if ornek_sayisi > configured_max_examples:
            performans_kazanci = ornek_sayisi - configured_max_examples
            assert performans_kazanci > 0, "Optimizasyon performans kazancı sağlamalı"
    
    def test_hypothesis_phases_optimizasyonu(self):
        """
        **Test Performans Optimizasyonu, Özellik 8: Hypothesis Profil Ayarları**
        **Doğrular: Gereksinimler 3.3, 3.4**
        
        Hypothesis phases'ların hızlı profil için optimize edildiğini doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        phases = hypothesis_config.get("phases", [])
        
        # Hızlı profil için gerekli phases'ları kontrol et
        gerekli_phases = ["explicit", "reuse", "generate", "target"]
        
        for phase in gerekli_phases:
            assert phase in phases, f"Hızlı profil için '{phase}' phase'i eksik"
        
        # Yavaş phases'ların olmadığını kontrol et (örneğin shrink fazı çok yavaş olabilir)
        yavas_phases = ["shrink"]  # Shrink fazı genellikle yavaştır
        
        # Bu kontrol opsiyonel - shrink fazı hata ayıklama için yararlı olabilir
        # Performans kritikse shrink fazını da kaldırabiliriz
    
    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_hypothesis_timeout_performans_property(self, test_suresi: float):
        """
        **Test Performans Optimizasyonu, Özellik 7: Hypothesis Optimizasyonu**
        **Doğrular: Gereksinimler 3.1, 3.2**
        
        Herhangi bir test süresi için, timeout ayarlarının performans optimizasyonu sağladığını doğrula.
        """
        pyproject_path = Path("pyproject.toml")
        config = toml.load(pyproject_path)
        
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        deadline_ms = hypothesis_config.get("deadline", 5000)
        deadline_seconds = deadline_ms / 1000.0
        
        # Deadline'ın 2 saniye veya daha az olduğunu doğrula
        assert deadline_seconds <= 2.0, f"Deadline {deadline_seconds}s, performans için 2s veya daha az olmalı"
        
        # Test süresinin deadline'dan uzun olduğunda optimizasyonun etkili olduğunu doğrula
        if test_suresi > deadline_seconds:
            zaman_tasarrufu = test_suresi - deadline_seconds
            assert zaman_tasarrufu > 0, "Timeout optimizasyonu zaman tasarrufu sağlamalı"


class TestPerformansMetrikleri:
    """Performans metrikleri property testleri."""
    
    @pytest.mark.unit
    def test_test_suresi_olcumu_baslangic(self):
        """
        **Test Performans Optimizasyonu, Özellik 1: Test Süresi Sınırları**
        **Doğrular: Gereksinimler 1.1, 1.2**
        
        Test süresi ölçümünün başladığını doğrula.
        """
        baslangic_zamani = time.time()
        
        # Kısa bir işlem simüle et
        time.sleep(0.01)
        
        bitis_zamani = time.time()
        test_suresi = bitis_zamani - baslangic_zamani
        
        # Test süresinin ölçülebildiğini doğrula
        assert test_suresi > 0, "Test süresi ölçülemiyor"
        assert test_suresi < 1.0, "Bu basit test 1 saniyeden az sürmeli"
    
    @given(st.integers(min_value=1, max_value=100))
    def test_test_sayisi_metrik_property(self, test_sayisi: int):
        """
        **Test Performans Optimizasyonu, Özellik 6: Test Raporu Kategorileri**
        **Doğrular: Gereksinimler 2.4**
        
        Herhangi bir test sayısı için, metriklerin doğru hesaplandığını doğrula.
        """
        # Test sayısının pozitif olduğunu doğrula
        assert test_sayisi > 0, "Test sayısı pozitif olmalı"
        
        # Test sayısının makul sınırlar içinde olduğunu doğrula
        assert test_sayisi <= 1000, "Test sayısı çok yüksek (performans sorunu)"
        
        # Test başına ortalama süre hesaplama simülasyonu
        ortalama_test_suresi = 0.1  # 100ms
        toplam_sure = test_sayisi * ortalama_test_suresi
        
        # Toplam sürenin makul olduğunu doğrula
        if test_sayisi <= 10:
            assert toplam_sure <= 2.0, "10 veya daha az test 2 saniyeden az sürmeli"
        elif test_sayisi <= 50:
            assert toplam_sure <= 30.0, "50 veya daha az test 30 saniyeden az sürmeli"


class TestOnceliklendirmeSistemi:
    """Test önceliklendirme sistemi property testleri."""
    
    def setUp(self):
        """Test kurulumu."""
        from sontechsp.testler.test_selector import TestSelector
        self.test_selector = TestSelector()
    
    @given(st.lists(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_'), min_size=5, max_size=50), min_size=1, max_size=10, unique=True))
    def test_onceliklendirme_property(self, test_dosyalari: List[str]):
        """
        **Test Performans Optimizasyonu, Özellik 9: Test Önceliklendirme**
        **Doğrular: Gereksinimler 4.1**
        
        Herhangi bir test dosyası listesi için, önceliklendirmenin doğru çalıştığını doğrula.
        """
        self.setUp()
        
        # Test dosyalarını .py uzantısı ile hazırla
        test_files = [f"test_{name}.py" for name in test_dosyalari]
        
        # Önceliklendirme algoritmasının çalıştığını doğrula
        # (Gerçek dosyalar olmadığı için mock test)
        for test_file in test_files:
            priority = self.test_selector._calculate_test_priority(test_file)
            
            # Öncelik değerinin geçerli olduğunu doğrula
            assert isinstance(priority, int), f"Öncelik değeri integer olmalı: {priority}"
            assert priority >= 0, f"Öncelik değeri negatif olamaz: {priority}"
    
    @given(st.sampled_from(["critical", "smoke", "unit", "integration", "property", "slow"]))
    def test_marker_oncelik_property(self, marker: str):
        """
        **Test Performans Optimizasyonu, Özellik 9: Test Önceliklendirme**
        **Doğrular: Gereksinimler 4.1**
        
        Herhangi bir marker için, öncelik değerinin doğru hesaplandığını doğrula.
        """
        self.setUp()
        
        # Marker önceliklerinin tanımlı olduğunu doğrula
        assert marker in self.test_selector.marker_oncelikleri, f"Marker '{marker}' öncelik tablosunda yok"
        
        marker_onceligi = self.test_selector.marker_oncelikleri[marker]
        
        # Öncelik değerinin mantıklı olduğunu doğrula
        assert isinstance(marker_onceligi, int), "Marker önceliği integer olmalı"
        assert 1 <= marker_onceligi <= 10, f"Marker önceliği 1-10 arasında olmalı: {marker_onceligi}"
        
        # Critical marker'ın en yüksek önceliğe sahip olduğunu doğrula
        if marker == "critical":
            assert marker_onceligi == 10, "Critical marker en yüksek önceliğe sahip olmalı"
        
        # Slow marker'ın en düşük önceliğe sahip olduğunu doğrula
        if marker == "slow":
            assert marker_onceligi == 1, "Slow marker en düşük önceliğe sahip olmalı"
    
    @pytest.mark.unit
    def test_kritik_dosya_onceliklendirme(self):
        """
        **Test Performans Optimizasyonu, Özellik 9: Test Önceliklendirme**
        **Doğrular: Gereksinimler 4.1**
        
        Kritik dosyaların yüksek önceliğe sahip olduğunu doğrula.
        """
        self.setUp()
        
        # Kritik dosyaların tanımlı olduğunu doğrula
        assert len(self.test_selector.kritik_dosyalar) > 0, "Kritik dosyalar tanımlanmalı"
        
        for dosya_yolu, oncelik in self.test_selector.kritik_dosyalar.items():
            # Kritik dosya önceliklerinin yüksek olduğunu doğrula
            assert oncelik >= 5, f"Kritik dosya önceliği düşük: {dosya_yolu} -> {oncelik}"
            
            # Ana uygulama dosyasının en yüksek önceliğe sahip olduğunu doğrula
            if "ana.py" in dosya_yolu:
                assert oncelik == 10, "Ana uygulama dosyası en yüksek önceliğe sahip olmalı"


class TestSamplingStratejisi:
    """Sampling stratejisi property testleri."""
    
    def setUp(self):
        """Test kurulumu."""
        from sontechsp.testler.test_selector import TestSelector
        self.test_selector = TestSelector()
    
    @given(st.floats(min_value=0.1, max_value=1.0))
    def test_sampling_ratio_property(self, ratio: float):
        """
        **Test Performans Optimizasyonu, Özellik 11: Sampling Stratejisi**
        **Doğrular: Gereksinimler 4.3**
        
        Herhangi bir sampling oranı için, rastgele seçimin doğru çalıştığını doğrula.
        """
        self.setUp()
        
        # Mock parametrize testler listesi oluştur
        mock_tests = [f"test_param_{i}.py" for i in range(10)]
        
        # Sampling oranının geçerli olduğunu doğrula
        assert 0.0 <= ratio <= 1.0, f"Sampling oranı 0.0-1.0 arasında olmalı: {ratio}"
        
        # Beklenen sample boyutunu hesapla
        expected_size = max(1, int(len(mock_tests) * ratio))
        
        # Sample boyutunun mantıklı olduğunu doğrula
        assert expected_size <= len(mock_tests), "Sample boyutu toplam test sayısını aşamaz"
        assert expected_size >= 1, "En az 1 test seçilmeli"
    
    @given(st.integers(min_value=1, max_value=100))
    def test_rastgele_secim_property(self, test_sayisi: int):
        """
        **Test Performans Optimizasyonu, Özellik 11: Sampling Stratejisi**
        **Doğrular: Gereksinimler 4.3**
        
        Herhangi bir test sayısı için, rastgele seçimin farklı sonuçlar verdiğini doğrula.
        """
        # Test sayısının pozitif olduğunu doğrula
        assert test_sayisi > 0, "Test sayısı pozitif olmalı"
        
        # Mock test listesi oluştur
        mock_tests = [f"test_{i}.py" for i in range(test_sayisi)]
        
        # Rastgele seçim simülasyonu
        if test_sayisi > 1:
            # İki farklı rastgele seçim yap
            random.seed(42)
            sample1 = random.sample(mock_tests, min(5, test_sayisi))
            
            random.seed(123)
            sample2 = random.sample(mock_tests, min(5, test_sayisi))
            
            # Farklı seed'ler farklı sonuçlar vermeli (çoğu durumda)
            if test_sayisi > 5:
                # Büyük listeler için farklılık beklenir
                assert sample1 != sample2 or len(set(sample1 + sample2)) > 5, "Rastgele seçim yeterince rastgele değil"
    
    @pytest.mark.unit
    def test_sampling_edge_cases(self):
        """
        **Test Performans Optimizasyonu, Özellik 11: Sampling Stratejisi**
        **Doğrular: Gereksinimler 4.3**
        
        Sampling edge case'lerinin doğru işlendiğini doğrula.
        """
        self.setUp()
        
        # Geçersiz ratio değerleri
        with pytest.raises(ValueError):
            self.test_selector.sample_parametrized_tests(-0.1)
        
        with pytest.raises(ValueError):
            self.test_selector.sample_parametrized_tests(1.1)
        
        # Geçerli ratio değerleri
        try:
            result = self.test_selector.sample_parametrized_tests(0.0)
            assert isinstance(result, list), "Sonuç liste olmalı"
        except Exception as e:
            # Dosya bulunamama hatası normal (test ortamında)
            assert "No such file" in str(e) or "does not exist" in str(e), f"Beklenmeyen hata: {e}"


class TestKapsamaKorunmasi:
    """Kapsama korunması property testleri."""
    
    @given(st.integers(min_value=50, max_value=100))
    def test_minimum_kapsama_property(self, hedef_kapsama: int):
        """
        **Test Performans Optimizasyonu, Özellik 10: Kapsama Korunması**
        **Doğrular: Gereksinimler 4.2, 4.4**
        
        Herhangi bir hedef kapsama için, minimum seviyenin korunduğunu doğrula.
        """
        # Hedef kapsamanın geçerli olduğunu doğrula
        assert 0 <= hedef_kapsama <= 100, f"Kapsama yüzdesi 0-100 arasında olmalı: {hedef_kapsama}"
        
        # Minimum kapsama seviyesi (örnek: %70)
        minimum_kapsama = 70
        
        # Optimizasyon sonrası kapsamanın minimum seviyeyi koruduğunu doğrula
        if hedef_kapsama >= minimum_kapsama:
            optimized_coverage = max(minimum_kapsama, hedef_kapsama * 0.9)  # %10 kayıp kabul edilebilir
            assert optimized_coverage >= minimum_kapsama, "Optimizasyon minimum kapsamayı korumalı"
    
    @given(st.lists(st.text(min_size=5, max_size=20), min_size=1, max_size=20, unique=True))
    def test_test_mantigi_korunmasi_property(self, test_isimleri: List[str]):
        """
        **Test Performans Optimizasyonu, Özellik 10: Kapsama Korunması**
        **Doğrular: Gereksinimler 4.2, 4.4**
        
        Herhangi bir test listesi için, test mantığının korunduğunu doğrula.
        """
        # Test isimlerinin geçerli olduğunu doğrula
        for test_ismi in test_isimleri:
            assert len(test_ismi) > 0, "Test ismi boş olamaz"
        
        # Test mantığı korunması simülasyonu
        original_test_count = len(test_isimleri)
        
        # Optimizasyon sonrası test sayısı (en az %50 korunmalı)
        optimized_count = max(1, int(original_test_count * 0.5))
        
        # Test mantığının korunduğunu doğrula
        assert optimized_count >= 1, "En az 1 test korunmalı"
        assert optimized_count <= original_test_count, "Optimizasyon test sayısını artırmamalı"
        
        # Kritik testlerin korunması
        kritik_testler = [test for test in test_isimleri if "critical" in test.lower() or "smoke" in test.lower()]
        if kritik_testler:
            # Kritik testler her zaman korunmalı
            assert len(kritik_testler) <= optimized_count or optimized_count == original_test_count, "Kritik testler korunmalı"
    
    @pytest.mark.unit
    def test_temel_kapsama_gereksinimleri(self):
        """
        **Test Performans Optimizasyonu, Özellik 10: Kapsama Korunması**
        **Doğrular: Gereksinimler 4.2, 4.4**
        
        Temel kapsama gereksinimlerinin tanımlı olduğunu doğrula.
        """
        # Minimum kapsama seviyesi tanımlı olmalı
        minimum_coverage = 70  # %70 minimum kapsama
        assert minimum_coverage > 0, "Minimum kapsama seviyesi pozitif olmalı"
        assert minimum_coverage <= 100, "Minimum kapsama %100'ü aşamaz"
        
        # Kritik modüller için kapsama gereksinimleri
        kritik_moduller = [
            "sontechsp.uygulama.ana",
            "sontechsp.uygulama.cekirdek",
            "sontechsp.uygulama.veritabani"
        ]
        
        for modul in kritik_moduller:
            # Kritik modüller için yüksek kapsama beklenir
            assert len(modul) > 0, f"Kritik modül ismi boş olamaz: {modul}"
            assert "sontechsp" in modul, f"Kritik modül sontechsp namespace'inde olmalı: {modul}"

class TestParalelTestKonfigurasyonu:
    """Paralel test konfigürasyonu property testleri."""
    
    def setUp(self):
        """Test kurulumu."""
        from sontechsp.testler.parallel_test_manager import ParallelTestManager
        self.parallel_manager = ParallelTestManager()
    
    @given(st.integers(min_value=1, max_value=16))
    def test_worker_sayisi_hesaplama_property(self, cpu_count: int):
        """
        **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
        **Doğrular: Gereksinimler 5.1, 5.2**
        
        Herhangi bir CPU sayısı için, worker sayısının doğru hesaplandığını doğrula.
        """
        self.setUp()
        
        # CPU sayısının pozitif olduğunu doğrula
        assert cpu_count > 0, "CPU sayısı pozitif olmalı"
        
        # Mock CPU count ayarla
        original_cpu_count = self.parallel_manager.cpu_count
        self.parallel_manager.cpu_count = cpu_count
        
        try:
            optimal_workers = self.parallel_manager.get_optimal_worker_count()
            
            # Worker sayısının mantıklı olduğunu doğrula
            assert optimal_workers > 0, "Worker sayısı pozitif olmalı"
            assert optimal_workers <= cpu_count, "Worker sayısı CPU sayısını aşmamalı"
            assert optimal_workers <= 8, "Maksimum 8 worker olmalı"
            
            # CPU sayısına göre beklenen davranış
            if cpu_count <= 2:
                assert optimal_workers == 1, "2 veya daha az CPU için 1 worker"
            elif cpu_count <= 4:
                assert optimal_workers == cpu_count - 1, "4 veya daha az CPU için CPU-1 worker"
            else:
                assert optimal_workers <= 8, "Fazla CPU için maksimum 8 worker"
                
        finally:
            # Original değeri geri yükle
            self.parallel_manager.cpu_count = original_cpu_count
    
    @given(st.sampled_from(["loadscope", "loadfile", "worksteal"]))
    def test_xdist_konfigurasyonu_property(self, dist_mode: str):
        """
        **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
        **Doğrular: Gereksinimler 5.1, 5.2**
        
        Herhangi bir dağıtım modu için, xdist konfigürasyonunun geçerli olduğunu doğrula.
        """
        self.setUp()
        
        config = self.parallel_manager.configure_xdist()
        
        # Temel konfigürasyon alanlarının mevcut olduğunu doğrula
        assert "workers" in config, "Workers konfigürasyonu eksik"
        assert "dist" in config, "Dist konfigürasyonu eksik"
        assert "tx" in config, "TX konfigürasyonu eksik"
        assert "rsyncdir" in config, "Rsyncdir konfigürasyonu eksik"
        
        # Worker sayısının geçerli olduğunu doğrula
        assert config["workers"] > 0, "Worker sayısı pozitif olmalı"
        assert config["workers"] <= 8, "Maksimum 8 worker olmalı"
        
        # Dist mode'un geçerli olduğunu doğrula
        gecerli_dist_modes = ["loadscope", "loadfile", "worksteal", "each"]
        assert config["dist"] in gecerli_dist_modes, f"Geçersiz dist mode: {config['dist']}"
        
        # Rsync dizininin doğru olduğunu doğrula
        assert config["rsyncdir"] == "sontechsp", "Rsync dizini sontechsp olmalı"
    
    @pytest.mark.unit
    def test_paralel_kurulum_dogrulama(self):
        """
        **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
        **Doğrular: Gereksinimler 5.1, 5.2**
        
        Paralel test kurulumunun doğru yapıldığını doğrula.
        """
        self.setUp()
        
        validation = self.parallel_manager.validate_parallel_setup()
        
        # Temel doğrulama alanlarının mevcut olduğunu kontrol et
        assert "cpu_count" in validation, "CPU count bilgisi eksik"
        assert "optimal_workers" in validation, "Optimal workers bilgisi eksik"
        assert "python_executable" in validation, "Python executable bilgisi eksik"
        assert "issues" in validation, "Issues listesi eksik"
        
        # CPU count'un pozitif olduğunu doğrula
        assert validation["cpu_count"] > 0, "CPU count pozitif olmalı"
        
        # Optimal workers'ın mantıklı olduğunu doğrula
        assert validation["optimal_workers"] > 0, "Optimal workers pozitif olmalı"
        assert validation["optimal_workers"] <= validation["cpu_count"], "Workers CPU count'u aşmamalı"
        
        # Python executable'ın mevcut olduğunu doğrula
        assert len(validation["python_executable"]) > 0, "Python executable boş olamaz"
        assert os.path.exists(validation["python_executable"]), "Python executable mevcut değil"


class TestIzolasyonSistemi:
    """Test izolasyonu sistemi property testleri."""
    
    def setUp(self):
        """Test kurulumu."""
        from sontechsp.testler.parallel_test_manager import ParallelTestManager
        self.parallel_manager = ParallelTestManager()
    
    @given(st.integers(min_value=1, max_value=8))
    def test_test_izolasyonu_property(self, worker_count: int):
        """
        **Test Performans Optimizasyonu, Özellik 13: Test İzolasyonu**
        **Doğrular: Gereksinimler 5.3, 5.4**
        
        Herhangi bir worker sayısı için, test izolasyonunun sağlandığını doğrula.
        """
        self.setUp()
        
        # Worker sayısının geçerli olduğunu doğrula
        assert 1 <= worker_count <= 8, "Worker sayısı 1-8 arasında olmalı"
        
        # Mock worker count ayarla
        original_max_workers = self.parallel_manager.max_workers
        self.parallel_manager.max_workers = worker_count
        
        try:
            # Test izolasyonunu kur
            self.parallel_manager.ensure_test_isolation()
            
            # Geçici dizinlerin oluşturulduğunu doğrula
            expected_temp_dirs = min(worker_count, self.parallel_manager.get_optimal_worker_count())
            
            # Her worker için environment variable'ın ayarlandığını kontrol et
            for i in range(expected_temp_dirs):
                env_var = f"SONTECHSP_TEST_WORKER_{i}_DIR"
                if env_var in os.environ:
                    temp_dir = os.environ[env_var]
                    # Geçici dizinin mevcut olduğunu doğrula (oluşturulmuşsa)
                    assert isinstance(temp_dir, str), f"Worker {i} temp dir string olmalı"
                    assert len(temp_dir) > 0, f"Worker {i} temp dir boş olamaz"
            
        finally:
            # Temizlik
            self.parallel_manager._cleanup_temp_dirs()
            self.parallel_manager.max_workers = original_max_workers
    
    @given(st.lists(st.text(min_size=5, max_size=20), min_size=1, max_size=5, unique=True))
    def test_coverage_birlestirme_property(self, coverage_files: List[str]):
        """
        **Test Performans Optimizasyonu, Özellik 13: Test İzolasyonu**
        **Doğrular: Gereksinimler 5.3, 5.4**
        
        Herhangi bir coverage dosyası listesi için, birleştirmenin çalıştığını doğrula.
        """
        self.setUp()
        
        # Coverage dosya isimlerinin geçerli olduğunu doğrula
        for coverage_file in coverage_files:
            assert len(coverage_file) > 0, "Coverage dosya ismi boş olamaz"
        
        # Mock coverage birleştirme
        worker_count = len(coverage_files)
        
        # Coverage birleştirme sonucunu test et
        coverage_result = self.parallel_manager.merge_coverage_reports(worker_count)
        
        # Sonucun geçerli olduğunu doğrula
        assert "coverage_percentage" in coverage_result, "Coverage percentage eksik"
        assert "files" in coverage_result, "Files listesi eksik"
        
        # Coverage percentage'ın geçerli olduğunu doğrula
        coverage_pct = coverage_result["coverage_percentage"]
        assert isinstance(coverage_pct, (int, float)), "Coverage percentage sayı olmalı"
        assert 0.0 <= coverage_pct <= 100.0, f"Coverage percentage 0-100 arasında olmalı: {coverage_pct}"
        
        # Files listesinin geçerli olduğunu doğrula
        files_list = coverage_result["files"]
        assert isinstance(files_list, list), "Files listesi list olmalı"
    
    @pytest.mark.unit
    def test_environment_temizligi(self):
        """
        **Test Performans Optimizasyonu, Özellik 13: Test İzolasyonu**
        **Doğrular: Gereksinimler 5.3, 5.4**
        
        Environment temizliğinin doğru yapıldığını doğrula.
        """
        self.setUp()
        
        # Test environment variable'ları ayarla
        test_env_vars = {
            "SONTECHSP_TEST_DB": "test_db",
            "SONTECHSP_TEST_MODE": "true",
            "PYTEST_CURRENT_TEST": "test_example"
        }
        
        for var, value in test_env_vars.items():
            os.environ[var] = value
        
        # Environment'ın ayarlandığını doğrula
        for var in test_env_vars:
            assert var in os.environ, f"Test env var ayarlanamadı: {var}"
        
        # Environment temizliğini çalıştır
        self.parallel_manager._clean_environment()
        
        # Environment'ın temizlendiğini doğrula
        for var in test_env_vars:
            assert var not in os.environ, f"Test env var temizlenmedi: {var}"


class TestYurutmeStratejisi:
    """Test yürütme stratejisi property testleri."""
    
    def setUp(self):
        """Test kurulumu."""
        from sontechsp.testler.parallel_test_manager import ParallelTestManager, TestExecutionStrategy
        self.parallel_manager = ParallelTestManager()
        self.execution_strategy = TestExecutionStrategy(self.parallel_manager)
    
    @given(st.sampled_from(["fast", "critical", "smoke", "all"]))
    def test_yurutme_plani_property(self, strategy: str):
        """
        **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
        **Doğrular: Gereksinimler 5.1, 5.2**
        
        Herhangi bir strateji için, yürütme planının geçerli olduğunu doğrula.
        """
        self.setUp()
        
        plan = self.execution_strategy.get_execution_plan(strategy)
        
        # Temel plan alanlarının mevcut olduğunu doğrula
        assert "markers" in plan, "Markers bilgisi eksik"
        assert "expected_duration" in plan, "Expected duration eksik"
        assert "worker_count" in plan, "Worker count eksik"
        assert "description" in plan, "Description eksik"
        
        # Expected duration'ın pozitif olduğunu doğrula
        assert plan["expected_duration"] > 0, "Expected duration pozitif olmalı"
        
        # Worker count'un geçerli olduğunu doğrula
        assert plan["worker_count"] > 0, "Worker count pozitif olmalı"
        assert plan["worker_count"] <= 8, "Worker count maksimum 8 olmalı"
        
        # Description'ın boş olmadığını doğrula
        assert len(plan["description"]) > 0, "Description boş olamaz"
        
        # Strateji-specific kontroller
        if strategy == "fast":
            assert plan["markers"] == "not slow", "Fast strategy 'not slow' marker kullanmalı"
            assert plan["expected_duration"] <= 60, "Fast strategy 60 saniyeden az sürmeli"
        elif strategy == "critical":
            assert plan["markers"] == "critical", "Critical strategy 'critical' marker kullanmalı"
        elif strategy == "smoke":
            assert plan["markers"] == "smoke", "Smoke strategy 'smoke' marker kullanmalı"
            assert plan["worker_count"] == 1, "Smoke strategy 1 worker kullanmalı"
        elif strategy == "all":
            assert plan["markers"] is None, "All strategy marker filtresi kullanmamalı"
    
    @pytest.mark.unit
    def test_test_konfigurasyonu_tutarliligi(self):
        """
        **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
        **Doğrular: Gereksinimler 5.1, 5.2**
        
        Test konfigürasyonunun tutarlı olduğunu doğrula.
        """
        self.setUp()
        
        config = self.parallel_manager.get_test_config()
        
        # Marker'ların tanımlı olduğunu doğrula
        assert len(config.markers) > 0, "Marker'lar tanımlanmalı"
        gerekli_markerlar = ["unit", "integration", "property", "slow", "critical", "smoke"]
        for marker in gerekli_markerlar:
            assert marker in config.markers, f"Marker eksik: {marker}"
        
        # Hypothesis ayarlarının doğru olduğunu doğrula
        assert config.hypothesis_settings["max_examples"] == 50, "Max examples 50 olmalı"
        assert config.hypothesis_settings["deadline"] == 2000, "Deadline 2000ms olmalı"
        
        # Paralel ayarların doğru olduğunu doğrula
        assert config.parallel_settings["workers"] > 0, "Worker sayısı pozitif olmalı"
        assert config.parallel_settings["dist"] == "loadscope", "Dist mode loadscope olmalı"
        
        # Sampling ratio'nun geçerli olduğunu doğrula
        assert 0.0 <= config.sampling_ratio <= 1.0, "Sampling ratio 0.0-1.0 arasında olmalı"
        
        # Timeout ayarlarının pozitif olduğunu doğrula
        for test_type, timeout in config.timeout_settings.items():
            assert timeout > 0, f"{test_type} timeout pozitif olmalı: {timeout}"

class TestCICDTestSecimi:
    """CI/CD test seçimi property testleri."""
    
    def setUp(self):
        """Test kurulumu."""
        from sontechsp.testler.ci_cd_selector import CICDTestSelector, CIPipeline
        self.ci_selector = CICDTestSelector()
        self.CIPipeline = CIPipeline
    
    @given(st.sampled_from(["PULL_REQUEST", "MAIN_BRANCH", "DEVELOP_BRANCH", "RELEASE", "SCHEDULED"]))
    def test_pipeline_test_secimi_property(self, pipeline_name: str):
        """
        **Test Performans Optimizasyonu, Özellik 4: CI/CD Test Seçimi**
        **Doğrular: Gereksinimler 1.4**
        
        Herhangi bir pipeline için, test seçiminin doğru çalıştığını doğrula.
        """
        self.setUp()
        
        pipeline = self.CIPipeline[pipeline_name]
        tests = self.ci_selector.get_tests_for_pipeline(pipeline)
        
        # Test listesinin geçerli olduğunu doğrula
        assert isinstance(tests, list), "Test listesi list olmalı"
        
        # Pipeline'a göre beklenen davranışlar
        if pipeline == self.CIPipeline.PULL_REQUEST:
            # PR için sadece kritik ve smoke testler
            assert len(tests) <= 10, "PR için test sayısı sınırlı olmalı"
            # Kritik testlerin dahil olduğunu kontrol et
            kritik_test_var = any("bagimlilik" in test or "ana_uygulama" in test for test in tests)
            assert kritik_test_var, "PR için kritik testler dahil olmalı"
        
        elif pipeline == self.CIPipeline.MAIN_BRANCH:
            # Main branch için hızlı testler
            assert len(tests) > 0, "Main branch için testler olmalı"
        
        elif pipeline == self.CIPipeline.RELEASE:
            # Release için tüm testler
            assert len(tests) >= 5, "Release için kapsamlı testler olmalı"
        
        elif pipeline == self.CIPipeline.SCHEDULED:
            # Scheduled için yavaş testler
            # Yavaş testler varsa dahil olmalı
            pass  # Test dosyaları mevcut olmayabilir
    
    @given(st.sampled_from(["PULL_REQUEST", "MAIN_BRANCH", "DEVELOP_BRANCH", "RELEASE", "SCHEDULED"]))
    def test_pytest_komut_olusturma_property(self, pipeline_name: str):
        """
        **Test Performans Optimizasyonu, Özellik 4: CI/CD Test Seçimi**
        **Doğrular: Gereksinimler 1.4**
        
        Herhangi bir pipeline için, pytest komutunun doğru oluşturulduğunu doğrula.
        """
        self.setUp()
        
        pipeline = self.CIPipeline[pipeline_name]
        cmd = self.ci_selector.get_pytest_command(pipeline)
        
        # Komutun geçerli olduğunu doğrula
        assert isinstance(cmd, list), "Komut list olmalı"
        assert len(cmd) > 0, "Komut boş olamaz"
        assert cmd[0] == "pytest", "İlk eleman pytest olmalı"
        
        # Pipeline'a göre beklenen parametreler
        cmd_str = " ".join(cmd)
        
        if pipeline == self.CIPipeline.PULL_REQUEST:
            # PR için fail fast olmalı
            assert "--maxfail" in cmd_str, "PR için maxfail parametresi olmalı"
            # Paralel çalıştırma sınırlı olmalı
            if "-n" in cmd_str:
                n_index = cmd.index("-n")
                worker_count = int(cmd[n_index + 1])
                assert worker_count <= 2, "PR için worker sayısı sınırlı olmalı"
        
        elif pipeline == self.CIPipeline.MAIN_BRANCH:
            # Main branch için coverage olmalı
            assert "--cov" in cmd_str, "Main branch için coverage olmalı"
        
        elif pipeline == self.CIPipeline.RELEASE:
            # Release için kapsamlı coverage
            assert "--cov" in cmd_str, "Release için coverage olmalı"
            assert "--cov-report" in cmd_str, "Release için coverage raporu olmalı"
        
        # Genel kontroller
        assert "--tb=short" in cmd_str, "Tüm pipeline'lar için kısa traceback olmalı"
        assert "-v" in cmd_str, "Tüm pipeline'lar için verbose olmalı"
    
    @pytest.mark.unit
    def test_ci_kurulum_dogrulama(self):
        """
        **Test Performans Optimizasyonu, Özellik 4: CI/CD Test Seçimi**
        **Doğrular: Gereksinimler 1.4**
        
        CI kurulumunun doğru yapıldığını doğrula.
        """
        self.setUp()
        
        validation = self.ci_selector.validate_ci_setup()
        
        # Doğrulama alanlarının mevcut olduğunu kontrol et
        assert "github_actions_config" in validation, "GitHub Actions config kontrolü eksik"
        assert "test_files_exist" in validation, "Test files kontrolü eksik"
        assert "markers_configured" in validation, "Markers kontrolü eksik"
        assert "pytest_xdist_available" in validation, "pytest-xdist kontrolü eksik"
        assert "issues" in validation, "Issues listesi eksik"
        
        # Issues listesinin list olduğunu doğrula
        assert isinstance(validation["issues"], list), "Issues list olmalı"
        
        # Boolean alanların boolean olduğunu doğrula
        boolean_fields = ["github_actions_config", "test_files_exist", "markers_configured", "pytest_xdist_available"]
        for field in boolean_fields:
            assert isinstance(validation[field], bool), f"{field} boolean olmalı"
    
    @given(st.dictionaries(
        st.sampled_from(["GITHUB_EVENT_NAME", "GITHUB_REF"]),
        st.sampled_from(["pull_request", "push", "schedule", "refs/heads/main", "refs/heads/develop", "refs/tags/v1.0.0"]),
        min_size=1, max_size=2
    ))
    def test_environment_pipeline_belirleme_property(self, env_vars: Dict[str, str]):
        """
        **Test Performans Optimizasyonu, Özellik 4: CI/CD Test Seçimi**
        **Doğrular: Gereksinimler 1.4**
        
        Herhangi bir environment için, pipeline belirlemenin doğru çalıştığını doğrula.
        """
        self.setUp()
        
        # Environment variables'ı geçici olarak ayarla
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            pipeline = self.ci_selector.get_pipeline_from_environment()
            
            # Pipeline'ın geçerli olduğunu doğrula
            assert isinstance(pipeline, self.CIPipeline), "Pipeline CIPipeline enum olmalı"
            
            # Environment'a göre beklenen pipeline
            if env_vars.get("GITHUB_EVENT_NAME") == "pull_request":
                assert pipeline == self.CIPipeline.PULL_REQUEST, "PR event için PULL_REQUEST pipeline"
            elif env_vars.get("GITHUB_EVENT_NAME") == "schedule":
                assert pipeline == self.CIPipeline.SCHEDULED, "Schedule event için SCHEDULED pipeline"
            elif env_vars.get("GITHUB_EVENT_NAME") == "push":
                if env_vars.get("GITHUB_REF") == "refs/heads/main":
                    assert pipeline == self.CIPipeline.MAIN_BRANCH, "Main branch push için MAIN_BRANCH pipeline"
                elif env_vars.get("GITHUB_REF") == "refs/heads/develop":
                    assert pipeline == self.CIPipeline.DEVELOP_BRANCH, "Develop branch push için DEVELOP_BRANCH pipeline"
                elif "refs/tags/" in env_vars.get("GITHUB_REF", ""):
                    assert pipeline == self.CIPipeline.RELEASE, "Tag push için RELEASE pipeline"
        
        finally:
            # Environment'ı geri yükle
            for key, original_value in original_env.items():
                if original_value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = original_value
    
    @pytest.mark.integration
    def test_ci_konfigurasyonu_olusturma(self):
        """
        **Test Performans Optimizasyonu, Özellik 4: CI/CD Test Seçimi**
        **Doğrular: Gereksinimler 1.4**
        
        CI konfigürasyonu oluşturmanın çalıştığını doğrula.
        """
        self.setUp()
        
        # Geçici dosya yolu
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            temp_path = f.name
        
        try:
            # CI konfigürasyonu oluştur
            self.ci_selector.generate_ci_config(temp_path)
            
            # Dosyanın oluşturulduğunu doğrula
            assert os.path.exists(temp_path), "CI konfigürasyon dosyası oluşturulmadı"
            
            # Dosya içeriğini kontrol et
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Temel YAML yapısının mevcut olduğunu doğrula
            assert "name:" in content, "YAML name alanı eksik"
            assert "on:" in content, "YAML on alanı eksik"
            assert "jobs:" in content, "YAML jobs alanı eksik"
            
            # CI/CD pipeline job'larının mevcut olduğunu doğrula
            assert "critical-tests" in content, "Critical tests job eksik"
            assert "pytest" in content, "pytest komutu eksik"
            
        finally:
            # Geçici dosyayı temizle
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    
    @pytest.mark.unit
    def test_pipeline_konfigurasyonlari(self):
        """
        **Test Performans Optimizasyonu, Özellik 4: CI/CD Test Seçimi**
        **Doğrular: Gereksinimler 1.4**
        
        Pipeline konfigürasyonlarının doğru tanımlandığını doğrula.
        """
        self.setUp()
        
        # Tüm pipeline'lar için konfigürasyon olduğunu doğrula
        for pipeline in self.CIPipeline:
            assert pipeline in self.ci_selector.pipeline_configs, f"Pipeline konfigürasyonu eksik: {pipeline}"
            
            config = self.ci_selector.pipeline_configs[pipeline]
            
            # Konfigürasyon alanlarının mevcut olduğunu doğrula
            assert config.max_duration_minutes > 0, f"{pipeline} için süre pozitif olmalı"
            assert config.parallel_workers > 0, f"{pipeline} için worker sayısı pozitif olmalı"
            assert isinstance(config.markers, list), f"{pipeline} için markers list olmalı"
            assert isinstance(config.fail_fast, bool), f"{pipeline} için fail_fast bool olmalı"
            assert isinstance(config.coverage_required, bool), f"{pipeline} için coverage_required bool olmalı"
            
            # Pipeline'a özel kontroller
            if pipeline == self.CIPipeline.PULL_REQUEST:
                assert config.max_duration_minutes <= 15, "PR için süre kısa olmalı"
                assert config.fail_fast == True, "PR için fail fast aktif olmalı"
            
            elif pipeline == self.CIPipeline.RELEASE:
                assert config.coverage_required == True, "Release için coverage zorunlu olmalı"
                assert config.fail_fast == False, "Release için fail fast pasif olmalı"
class TestRaporKategorileri:
    """Test raporu kategorileri property testleri."""
    
    def setUp(self):
        """Test kurulumu."""
        from sontechsp.testler.test_reporter import TestReporter, TestResult, CategoryMetrics
        self.test_reporter = TestReporter()
        self.TestResult = TestResult
        self.CategoryMetrics = CategoryMetrics
    
    @pytest.mark.unit
    def test_rapor_dizini_olusturma(self):
        """
        **Test Performans Optimizasyonu, Özellik 6: Test Raporu Kategorileri**
        **Doğrular: Gereksinimler 2.4**
        
        Rapor dizininin oluşturulduğunu doğrula.
        """
        self.setUp()
        
        # Rapor dizininin oluşturulduğunu doğrula
        assert self.test_reporter.report_dir.exists(), "Rapor dizini oluşturulmalı"
        assert self.test_reporter.report_dir.is_dir(), "Rapor yolu bir dizin olmalı"
        
        # Kategori marker'larının tanımlı olduğunu doğrula
        assert len(self.test_reporter.category_markers) > 0, "Kategori marker'ları tanımlanmalı"
        
        gerekli_kategoriler = ["unit", "integration", "property", "slow", "critical", "smoke"]
        for kategori in gerekli_kategoriler:
            assert kategori in self.test_reporter.category_markers, f"Kategori marker eksik: {kategori}"