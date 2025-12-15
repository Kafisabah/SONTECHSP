# Version: 0.1.0
# Last Update: 2025-01-15
# Module: ci_cd_selector
# Description: CI/CD test seçimi sistemi
# Changelog:
# - İlk versiyon: CI/CD test seçici sınıfı

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from enum import Enum


class CIPipeline(Enum):
    """CI Pipeline türleri."""
    PULL_REQUEST = "pull_request"
    MAIN_BRANCH = "main_branch"
    DEVELOP_BRANCH = "develop_branch"
    RELEASE = "release"
    SCHEDULED = "scheduled"


@dataclass
class CITestConfig:
    """CI test konfigürasyonu."""
    pipeline: CIPipeline
    max_duration_minutes: int
    parallel_workers: int
    markers: List[str]
    fail_fast: bool
    coverage_required: bool


class CICDTestSelector:
    """CI/CD test seçici sistemi."""
    
    def __init__(self):
        """CICDTestSelector başlatıcı."""
        self.kritik_testler = [
            "test_bagimlilik_standardi.py",
            "test_ana_uygulama.py",
            "test_cekirdek_modul_bagimsizligi.py",
            "test_performans_optimizasyonu.py"
        ]
        
        self.smoke_testler = [
            "test_klasor_hiyerarsisi.py",
            "test_katmanli_mimari.py"
        ]
        
        self.pipeline_configs = {
            CIPipeline.PULL_REQUEST: CITestConfig(
                pipeline=CIPipeline.PULL_REQUEST,
                max_duration_minutes=10,
                parallel_workers=2,
                markers=["critical", "smoke"],
                fail_fast=True,
                coverage_required=False
            ),
            CIPipeline.MAIN_BRANCH: CITestConfig(
                pipeline=CIPipeline.MAIN_BRANCH,
                max_duration_minutes=30,
                parallel_workers=4,
                markers=["not slow"],
                fail_fast=False,
                coverage_required=True
            ),
            CIPipeline.DEVELOP_BRANCH: CITestConfig(
                pipeline=CIPipeline.DEVELOP_BRANCH,
                max_duration_minutes=20,
                parallel_workers=3,
                markers=["critical", "unit", "integration"],
                fail_fast=False,
                coverage_required=True
            ),
            CIPipeline.RELEASE: CITestConfig(
                pipeline=CIPipeline.RELEASE,
                max_duration_minutes=45,
                parallel_workers=4,
                markers=[],  # Tüm testler
                fail_fast=False,
                coverage_required=True
            ),
            CIPipeline.SCHEDULED: CITestConfig(
                pipeline=CIPipeline.SCHEDULED,
                max_duration_minutes=60,
                parallel_workers=4,
                markers=["slow"],  # Sadece yavaş testler
                fail_fast=False,
                coverage_required=True
            )
        }
    
    def get_tests_for_pipeline(self, pipeline: CIPipeline) -> List[str]:
        """
        Pipeline için testleri seç.
        
        Args:
            pipeline: CI pipeline türü
            
        Returns:
            List[str]: Seçilen test dosyaları
        """
        config = self.pipeline_configs.get(pipeline)
        if not config:
            return []
        
        if pipeline == CIPipeline.PULL_REQUEST:
            # PR için sadece kritik ve smoke testler
            return self.kritik_testler + self.smoke_testler
        
        elif pipeline == CIPipeline.MAIN_BRANCH:
            # Main branch için hızlı testler
            return self._get_fast_tests()
        
        elif pipeline == CIPipeline.DEVELOP_BRANCH:
            # Develop için kritik + unit + integration
            return self._get_development_tests()
        
        elif pipeline == CIPipeline.RELEASE:
            # Release için tüm testler
            return self._get_all_tests()
        
        elif pipeline == CIPipeline.SCHEDULED:
            # Scheduled için yavaş testler
            return self._get_slow_tests()
        
        return []
    
    def get_pytest_command(self, pipeline: CIPipeline) -> List[str]:
        """
        Pipeline için pytest komutunu oluştur.
        
        Args:
            pipeline: CI pipeline türü
            
        Returns:
            List[str]: pytest komutu
        """
        config = self.pipeline_configs.get(pipeline)
        if not config:
            return ["pytest"]
        
        cmd = ["pytest"]
        
        # Marker filtresi
        if config.markers:
            if len(config.markers) == 1:
                cmd.extend(["-m", config.markers[0]])
            else:
                # Birden fazla marker için OR operatörü
                marker_expr = " or ".join(config.markers)
                cmd.extend(["-m", marker_expr])
        
        # Paralel çalıştırma
        if config.parallel_workers > 1:
            cmd.extend(["-n", str(config.parallel_workers)])
        
        # Fail fast
        if config.fail_fast:
            cmd.extend(["--maxfail", "5"])
        
        # Coverage
        if config.coverage_required:
            cmd.extend([
                "--cov=sontechsp",
                "--cov-report=html",
                "--cov-report=xml"
            ])
        
        # Genel ayarlar
        cmd.extend([
            "--tb=short",
            "-v"
        ])
        
        return cmd
    
    def get_pipeline_from_environment(self) -> CIPipeline:
        """
        Environment'tan pipeline türünü belirle.
        
        Returns:
            CIPipeline: Belirlenen pipeline türü
        """
        # GitHub Actions environment variables
        github_event_name = os.environ.get("GITHUB_EVENT_NAME", "")
        github_ref = os.environ.get("GITHUB_REF", "")
        
        if github_event_name == "pull_request":
            return CIPipeline.PULL_REQUEST
        
        elif github_event_name == "push":
            if "refs/heads/main" in github_ref:
                return CIPipeline.MAIN_BRANCH
            elif "refs/heads/develop" in github_ref:
                return CIPipeline.DEVELOP_BRANCH
            elif "refs/tags/" in github_ref:
                return CIPipeline.RELEASE
        
        elif github_event_name == "schedule":
            return CIPipeline.SCHEDULED
        
        # Varsayılan olarak develop branch
        return CIPipeline.DEVELOP_BRANCH
    
    def generate_ci_config(self, output_path: str = ".github/workflows/ci.yml") -> None:
        """
        CI konfigürasyon dosyasını oluştur.
        
        Args:
            output_path: Çıktı dosyası yolu
        """
        config_content = self._generate_github_actions_config()
        
        # Dizini oluştur
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Dosyayı yaz
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    def validate_ci_setup(self) -> Dict[str, Any]:
        """
        CI kurulumunu doğrula.
        
        Returns:
            Dict[str, Any]: Doğrulama sonuçları
        """
        validation = {
            "github_actions_config": False,
            "test_files_exist": False,
            "markers_configured": False,
            "pytest_xdist_available": False,
            "issues": []
        }
        
        # GitHub Actions konfigürasyonu
        github_config_path = Path(".github/workflows/test.yml")
        validation["github_actions_config"] = github_config_path.exists()
        if not validation["github_actions_config"]:
            validation["issues"].append("GitHub Actions konfigürasyonu bulunamadı")
        
        # Test dosyalarının varlığı
        test_files_exist = True
        for test_file in self.kritik_testler:
            test_path = Path(f"sontechsp/testler/{test_file}")
            if not test_path.exists():
                test_files_exist = False
                validation["issues"].append(f"Kritik test dosyası bulunamadı: {test_file}")
        
        validation["test_files_exist"] = test_files_exist
        
        # Marker konfigürasyonu
        try:
            import toml
            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                config = toml.load(pyproject_path)
                markers = config.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("markers", [])
                required_markers = ["critical", "smoke", "unit", "integration", "slow"]
                
                marker_names = [marker.split(":")[0].strip() for marker in markers]
                markers_ok = all(marker in marker_names for marker in required_markers)
                validation["markers_configured"] = markers_ok
                
                if not markers_ok:
                    validation["issues"].append("Gerekli marker'lar konfigüre edilmemiş")
            else:
                validation["issues"].append("pyproject.toml bulunamadı")
        except ImportError:
            validation["issues"].append("toml kütüphanesi bulunamadı")
        
        # pytest-xdist kontrolü
        try:
            import xdist
            validation["pytest_xdist_available"] = True
        except ImportError:
            validation["issues"].append("pytest-xdist kurulu değil")
        
        return validation
    
    def _get_fast_tests(self) -> List[str]:
        """Hızlı testleri al."""
        test_dir = Path("sontechsp/testler")
        if not test_dir.exists():
            return []
        
        fast_tests = []
        for test_file in test_dir.glob("test_*.py"):
            # Yavaş testleri hariç tut
            if not self._is_slow_test(test_file):
                fast_tests.append(str(test_file))
        
        return fast_tests
    
    def _get_development_tests(self) -> List[str]:
        """Development testlerini al."""
        return self.kritik_testler + [
            "test_bagimlilik_standardi.py",
            "test_klasor_hiyerarsisi.py",
            "test_katmanli_mimari.py"
        ]
    
    def _get_all_tests(self) -> List[str]:
        """Tüm testleri al."""
        test_dir = Path("sontechsp/testler")
        if not test_dir.exists():
            return []
        
        all_tests = []
        for test_file in test_dir.glob("test_*.py"):
            all_tests.append(str(test_file))
        
        return all_tests
    
    def _get_slow_tests(self) -> List[str]:
        """Yavaş testleri al."""
        test_dir = Path("sontechsp/testler")
        if not test_dir.exists():
            return []
        
        slow_tests = []
        for test_file in test_dir.glob("test_*.py"):
            if self._is_slow_test(test_file):
                slow_tests.append(str(test_file))
        
        return slow_tests
    
    def _is_slow_test(self, test_file: Path) -> bool:
        """Test dosyasının yavaş olup olmadığını kontrol et."""
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return "@pytest.mark.slow" in content
        except (FileNotFoundError, UnicodeDecodeError):
            return False
    
    def _generate_github_actions_config(self) -> str:
        """GitHub Actions konfigürasyonu oluştur."""
        return """name: CI Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * 0'  # Haftalık pazar gecesi

jobs:
  critical-tests:
    runs-on: windows-latest
    timeout-minutes: 10
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    - name: Run critical tests
      run: |
        pytest -m "critical or smoke" -n 2 --maxfail=5 --tb=short -v

  fast-tests:
    runs-on: windows-latest
    timeout-minutes: 20
    needs: critical-tests
    if: github.event_name != 'schedule'
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    - name: Run fast tests
      run: |
        pytest -m "not slow" -n auto --cov=sontechsp --cov-report=xml --tb=short -v

  slow-tests:
    runs-on: windows-latest
    timeout-minutes: 60
    if: github.event_name == 'schedule'
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    - name: Run slow tests
      run: |
        pytest -m slow -n auto --cov=sontechsp --cov-report=xml --tb=short -v
"""


def main():
    """Ana fonksiyon - CLI kullanımı için."""
    import sys
    
    selector = CICDTestSelector()
    
    if len(sys.argv) > 1:
        pipeline_name = sys.argv[1].upper()
        try:
            pipeline = CIPipeline[pipeline_name]
            tests = selector.get_tests_for_pipeline(pipeline)
            cmd = selector.get_pytest_command(pipeline)
            
            print(f"Pipeline: {pipeline.value}")
            print(f"Tests: {len(tests)}")
            print(f"Command: {' '.join(cmd)}")
            
        except KeyError:
            print(f"Geçersiz pipeline: {pipeline_name}")
            print(f"Geçerli pipeline'lar: {[p.name for p in CIPipeline]}")
    else:
        # Environment'tan pipeline belirle
        pipeline = selector.get_pipeline_from_environment()
        cmd = selector.get_pytest_command(pipeline)
        print(" ".join(cmd))


if __name__ == "__main__":
    main()