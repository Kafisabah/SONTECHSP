# Version: 0.1.0
# Last Update: 2025-01-15
# Module: parallel_test_manager
# Description: Paralel test yöneticisi sistemi
# Changelog:
# - İlk versiyon: ParallelTestManager sınıfı ve konfigürasyonları

import os
import multiprocessing
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import tempfile
import shutil


@dataclass
class TestConfig:
    """Test konfigürasyon sınıfı."""
    markers: Dict[str, str]
    hypothesis_settings: Dict[str, Any]
    parallel_settings: Dict[str, Any]
    sampling_ratio: float
    timeout_settings: Dict[str, int]


class ParallelTestManager:
    """Paralel test yöneticisi sistemi."""
    
    def __init__(self):
        """ParallelTestManager başlatıcı."""
        self.cpu_count = multiprocessing.cpu_count()
        self.max_workers = min(self.cpu_count, 8)  # Maksimum 8 worker
        self.temp_dirs = []
    
    def get_optimal_worker_count(self) -> int:
        """
        Optimal worker sayısını hesapla.
        
        Returns:
            int: Optimal worker sayısı
        """
        # CPU çekirdek sayısına göre optimal worker sayısı
        if self.cpu_count <= 2:
            return 1
        elif self.cpu_count <= 4:
            return self.cpu_count - 1
        else:
            return min(self.cpu_count, 8)  # Maksimum 8 worker
    
    def configure_xdist(self) -> Dict[str, Any]:
        """
        pytest-xdist konfigürasyonunu oluştur.
        
        Returns:
            Dict[str, Any]: xdist konfigürasyon ayarları
        """
        optimal_workers = self.get_optimal_worker_count()
        
        config = {
            "workers": optimal_workers,
            "dist": "loadscope",  # Test scope'una göre dağıt
            "tx": f"popen//python={self._get_python_executable()}",
            "rsyncdir": "sontechsp",  # Senkronize edilecek dizin
            "rsyncignore": [
                "*.pyc",
                "__pycache__",
                ".pytest_cache",
                "htmlcov",
                "logs",
                ".hypothesis"
            ]
        }
        
        return config
    
    def ensure_test_isolation(self) -> None:
        """
        Test izolasyonunu sağla.
        """
        # Geçici dizinleri temizle
        self._cleanup_temp_dirs()
        
        # Test veritabanı izolasyonu için geçici dizinler oluştur
        self._setup_test_isolation()
        
        # Environment variables'ı temizle
        self._clean_environment()
    
    def run_parallel_tests(self, test_files: List[str], markers: Optional[str] = None) -> Dict[str, Any]:
        """
        Paralel testleri çalıştır.
        
        Args:
            test_files: Çalıştırılacak test dosyaları
            markers: Test marker'ları (örn: "not slow")
            
        Returns:
            Dict[str, Any]: Test sonuçları
        """
        config = self.configure_xdist()
        
        # pytest komutunu oluştur
        cmd = [
            "python", "-m", "pytest",
            f"-n", str(config["workers"]),
            "--dist", config["dist"],
            "-v",
            "--tb=short"
        ]
        
        # Marker filtresi ekle
        if markers:
            cmd.extend(["-m", markers])
        
        # Test dosyalarını ekle
        if test_files:
            cmd.extend(test_files)
        
        # Test izolasyonunu sağla
        self.ensure_test_isolation()
        
        try:
            # Testleri çalıştır
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 dakika timeout
            )
            end_time = time.time()
            
            return {
                "success": result.returncode == 0,
                "duration": end_time - start_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "worker_count": config["workers"],
                "test_files": test_files
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "duration": 300,
                "stdout": "",
                "stderr": "Test timeout (5 dakika)",
                "worker_count": config["workers"],
                "test_files": test_files
            }
        finally:
            # Temizlik
            self._cleanup_temp_dirs()
    
    def merge_coverage_reports(self, worker_count: int) -> Dict[str, Any]:
        """
        Coverage raporlarını birleştir.
        
        Args:
            worker_count: Worker sayısı
            
        Returns:
            Dict[str, Any]: Birleştirilmiş coverage raporu
        """
        coverage_files = []
        
        # Worker'lardan coverage dosyalarını topla
        for i in range(worker_count):
            coverage_file = f".coverage.worker_{i}"
            if os.path.exists(coverage_file):
                coverage_files.append(coverage_file)
        
        if not coverage_files:
            return {"coverage_percentage": 0.0, "files": []}
        
        try:
            # Coverage raporlarını birleştir
            cmd = ["python", "-m", "coverage", "combine"] + coverage_files
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Coverage raporu oluştur
                report_cmd = ["python", "-m", "coverage", "report", "--format=json"]
                report_result = subprocess.run(report_cmd, capture_output=True, text=True)
                
                if report_result.returncode == 0:
                    coverage_data = json.loads(report_result.stdout)
                    return {
                        "coverage_percentage": coverage_data.get("totals", {}).get("percent_covered", 0.0),
                        "files": list(coverage_data.get("files", {}).keys()),
                        "summary": coverage_data.get("totals", {})
                    }
            
            return {"coverage_percentage": 0.0, "files": []}
            
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return {"coverage_percentage": 0.0, "files": []}
        finally:
            # Coverage dosyalarını temizle
            for coverage_file in coverage_files:
                try:
                    os.remove(coverage_file)
                except OSError:
                    pass
    
    def get_test_config(self) -> TestConfig:
        """
        Test konfigürasyonunu al.
        
        Returns:
            TestConfig: Test konfigürasyon objesi
        """
        return TestConfig(
            markers={
                "unit": "Birim testler (hızlı, izole)",
                "integration": "Entegrasyon testleri (orta hız)",
                "property": "Property-based testler (değişken hız)",
                "slow": "Yavaş çalışan testler (> 30 saniye)",
                "critical": "Kritik path testleri (CI/CD için)",
                "smoke": "Temel işlevsellik testleri"
            },
            hypothesis_settings={
                "max_examples": 50,
                "deadline": 2000,
                "suppress_health_check": ["too_slow", "filter_too_much", "data_too_large"],
                "phases": ["explicit", "reuse", "generate", "target"]
            },
            parallel_settings={
                "workers": self.get_optimal_worker_count(),
                "dist": "loadscope",
                "timeout": 300
            },
            sampling_ratio=0.3,
            timeout_settings={
                "unit": 30,
                "integration": 60,
                "slow": 300,
                "property": 120
            }
        )
    
    def _get_python_executable(self) -> str:
        """Python executable path'ini al."""
        import sys
        return sys.executable
    
    def _cleanup_temp_dirs(self) -> None:
        """Geçici dizinleri temizle."""
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except OSError:
                pass
        self.temp_dirs.clear()
    
    def _setup_test_isolation(self) -> None:
        """Test izolasyonu için geçici dizinler oluştur."""
        # Her worker için ayrı geçici dizin
        for i in range(self.get_optimal_worker_count()):
            temp_dir = tempfile.mkdtemp(prefix=f"sontechsp_test_worker_{i}_")
            self.temp_dirs.append(temp_dir)
            
            # Worker-specific environment variable
            os.environ[f"SONTECHSP_TEST_WORKER_{i}_DIR"] = temp_dir
    
    def _clean_environment(self) -> None:
        """Test environment'ını temizle."""
        # Test-specific environment variables'ı temizle
        env_vars_to_clean = [
            "SONTECHSP_TEST_DB",
            "SONTECHSP_TEST_MODE",
            "PYTEST_CURRENT_TEST"
        ]
        
        for var in env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
    
    def validate_parallel_setup(self) -> Dict[str, Any]:
        """
        Paralel test kurulumunu doğrula.
        
        Returns:
            Dict[str, Any]: Doğrulama sonuçları
        """
        validation_results = {
            "cpu_count": self.cpu_count,
            "optimal_workers": self.get_optimal_worker_count(),
            "pytest_xdist_available": False,
            "python_executable": self._get_python_executable(),
            "temp_dir_writable": False,
            "issues": []
        }
        
        # pytest-xdist kurulu mu kontrol et
        try:
            import xdist
            validation_results["pytest_xdist_available"] = True
        except ImportError:
            validation_results["issues"].append("pytest-xdist kurulu değil")
        
        # Geçici dizin yazılabilir mi kontrol et
        try:
            test_temp_dir = tempfile.mkdtemp(prefix="sontechsp_validation_")
            test_file = os.path.join(test_temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            os.rmdir(test_temp_dir)
            validation_results["temp_dir_writable"] = True
        except OSError:
            validation_results["issues"].append("Geçici dizin oluşturulamıyor")
        
        # Worker sayısı kontrolü
        if validation_results["optimal_workers"] < 1:
            validation_results["issues"].append("Geçersiz worker sayısı")
        
        return validation_results


class TestExecutionStrategy:
    """Test yürütme stratejisi sınıfı."""
    
    def __init__(self, parallel_manager: ParallelTestManager):
        """TestExecutionStrategy başlatıcı."""
        self.parallel_manager = parallel_manager
    
    def execute_fast_tests(self) -> Dict[str, Any]:
        """
        Hızlı testleri çalıştır.
        
        Returns:
            Dict[str, Any]: Test sonuçları
        """
        return self.parallel_manager.run_parallel_tests(
            test_files=[],
            markers="not slow"
        )
    
    def execute_critical_tests(self) -> Dict[str, Any]:
        """
        Kritik testleri çalıştır.
        
        Returns:
            Dict[str, Any]: Test sonuçları
        """
        return self.parallel_manager.run_parallel_tests(
            test_files=[],
            markers="critical"
        )
    
    def execute_smoke_tests(self) -> Dict[str, Any]:
        """
        Smoke testleri çalıştır.
        
        Returns:
            Dict[str, Any]: Test sonuçları
        """
        return self.parallel_manager.run_parallel_tests(
            test_files=[],
            markers="smoke"
        )
    
    def execute_all_tests_parallel(self) -> Dict[str, Any]:
        """
        Tüm testleri paralel çalıştır.
        
        Returns:
            Dict[str, Any]: Test sonuçları
        """
        return self.parallel_manager.run_parallel_tests(
            test_files=[],
            markers=None
        )
    
    def get_execution_plan(self, strategy: str = "fast") -> Dict[str, Any]:
        """
        Yürütme planını al.
        
        Args:
            strategy: Yürütme stratejisi ("fast", "critical", "smoke", "all")
            
        Returns:
            Dict[str, Any]: Yürütme planı
        """
        config = self.parallel_manager.get_test_config()
        
        plans = {
            "fast": {
                "markers": "not slow",
                "expected_duration": 30,
                "worker_count": config.parallel_settings["workers"],
                "description": "Hızlı testler (30 saniye hedef)"
            },
            "critical": {
                "markers": "critical",
                "expected_duration": 60,
                "worker_count": min(2, config.parallel_settings["workers"]),
                "description": "Kritik testler (CI/CD için)"
            },
            "smoke": {
                "markers": "smoke",
                "expected_duration": 15,
                "worker_count": 1,
                "description": "Smoke testler (temel işlevsellik)"
            },
            "all": {
                "markers": None,
                "expected_duration": 120,
                "worker_count": config.parallel_settings["workers"],
                "description": "Tüm testler (2 dakika hedef)"
            }
        }
        
        return plans.get(strategy, plans["fast"])