# Version: 0.1.0
# Last Update: 2025-01-15
# Module: test_reporter
# Description: Test raporu ve metrikleri sistemi
# Changelog:
# - İlk versiyon: Test raporu oluşturucu sınıfı

import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import xml.etree.ElementTree as ET


@dataclass
class TestResult:
    """Test sonucu sınıfı."""
    name: str
    status: str  # passed, failed, skipped, error
    duration: float
    category: str  # unit, integration, property, slow, critical, smoke
    file_path: str
    error_message: Optional[str] = None


@dataclass
class CategoryMetrics:
    """Kategori metrikleri sınıfı."""
    category: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_duration: float
    average_duration: float
    success_rate: float


@dataclass
class PerformanceReport:
    """Performans raporu sınıfı."""
    timestamp: str
    total_duration: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    success_rate: float
    coverage_percentage: float
    worker_count: int
    categories: List[CategoryMetrics]
    slowest_tests: List[TestResult]
    failed_tests_detail: List[TestResult]


class TestReporter:
    """Test raporu oluşturucu sistemi."""
    
    def __init__(self):
        """TestReporter başlatıcı."""
        self.report_dir = Path("test_reports")
        self.report_dir.mkdir(exist_ok=True)
        
        self.category_markers = {
            "unit": "unit",
            "integration": "integration", 
            "property": "property",
            "slow": "slow",
            "critical": "critical",
            "smoke": "smoke"
        }
    
    def generate_performance_report(self, junit_xml_path: str = "junit.xml") -> PerformanceReport:
        """
        Performans raporu oluştur.
        
        Args:
            junit_xml_path: JUnit XML dosya yolu
            
        Returns:
            PerformanceReport: Performans raporu
        """
        # JUnit XML'den test sonuçlarını parse et
        test_results = self._parse_junit_xml(junit_xml_path)
        
        # Kategori metrikleri hesapla
        category_metrics = self._calculate_category_metrics(test_results)
        
        # Genel metrikleri hesapla
        total_tests = len(test_results)
        passed_tests = len([t for t in test_results if t.status == "passed"])
        failed_tests = len([t for t in test_results if t.status == "failed"])
        skipped_tests = len([t for t in test_results if t.status == "skipped"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
        total_duration = sum(t.duration for t in test_results)
        
        # En yavaş testler
        slowest_tests = sorted(test_results, key=lambda x: x.duration, reverse=True)[:10]
        
        # Başarısız testler
        failed_tests_detail = [t for t in test_results if t.status == "failed"]
        
        # Coverage bilgisi al
        coverage_percentage = self._get_coverage_percentage()
        
        # Worker sayısı (environment'tan al)
        worker_count = int(os.environ.get("PYTEST_XDIST_WORKER_COUNT", "1"))
        
        return PerformanceReport(
            timestamp=datetime.now().isoformat(),
            total_duration=total_duration,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            success_rate=success_rate,
            coverage_percentage=coverage_percentage,
            worker_count=worker_count,
            categories=category_metrics,
            slowest_tests=slowest_tests,
            failed_tests_detail=failed_tests_detail
        )
    
    def save_report_json(self, report: PerformanceReport, filename: str = None) -> str:
        """
        Raporu JSON formatında kaydet.
        
        Args:
            report: Performans raporu
            filename: Dosya adı (opsiyonel)
            
        Returns:
            str: Kaydedilen dosya yolu
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        file_path = self.report_dir / filename
        
        # Dataclass'ı dict'e çevir
        report_dict = asdict(report)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def generate_html_report(self, report: PerformanceReport, filename: str = None) -> str:
        """
        HTML raporu oluştur.
        
        Args:
            report: Performans raporu
            filename: Dosya adı (opsiyonel)
            
        Returns:
            str: HTML dosya yolu
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.html"
        
        file_path = self.report_dir / filename
        
        html_content = self._generate_html_content(report)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(file_path)
    
    def generate_category_summary(self, report: PerformanceReport) -> Dict[str, Any]:
        """
        Kategori özeti oluştur.
        
        Args:
            report: Performans raporu
            
        Returns:
            Dict[str, Any]: Kategori özeti
        """
        summary = {
            "total_categories": len(report.categories),
            "categories": {},
            "performance_insights": []
        }
        
        for category in report.categories:
            summary["categories"][category.category] = {
                "total_tests": category.total_tests,
                "success_rate": category.success_rate,
                "average_duration": category.average_duration,
                "total_duration": category.total_duration
            }
            
            # Performans öngörüleri
            if category.average_duration > 5.0:
                summary["performance_insights"].append(
                    f"{category.category} kategorisi yavaş (ortalama {category.average_duration:.2f}s)"
                )
            
            if category.success_rate < 90.0:
                summary["performance_insights"].append(
                    f"{category.category} kategorisi düşük başarı oranı (%{category.success_rate:.1f})"
                )
        
        return summary
    
    def compare_reports(self, current_report: PerformanceReport, previous_report: PerformanceReport) -> Dict[str, Any]:
        """
        İki raporu karşılaştır.
        
        Args:
            current_report: Güncel rapor
            previous_report: Önceki rapor
            
        Returns:
            Dict[str, Any]: Karşılaştırma sonuçları
        """
        comparison = {
            "duration_change": current_report.total_duration - previous_report.total_duration,
            "success_rate_change": current_report.success_rate - previous_report.success_rate,
            "test_count_change": current_report.total_tests - previous_report.total_tests,
            "coverage_change": current_report.coverage_percentage - previous_report.coverage_percentage,
            "category_changes": {},
            "improvements": [],
            "regressions": []
        }
        
        # Kategori değişiklikleri
        current_categories = {c.category: c for c in current_report.categories}
        previous_categories = {c.category: c for c in previous_report.categories}
        
        for category_name in current_categories:
            if category_name in previous_categories:
                current_cat = current_categories[category_name]
                previous_cat = previous_categories[category_name]
                
                duration_change = current_cat.average_duration - previous_cat.average_duration
                success_change = current_cat.success_rate - previous_cat.success_rate
                
                comparison["category_changes"][category_name] = {
                    "duration_change": duration_change,
                    "success_rate_change": success_change
                }
                
                # İyileştirmeler ve gerileme
                if duration_change < -0.5:  # 0.5 saniye hızlanma
                    comparison["improvements"].append(f"{category_name} kategorisi hızlandı")
                elif duration_change > 0.5:  # 0.5 saniye yavaşlama
                    comparison["regressions"].append(f"{category_name} kategorisi yavaşladı")
                
                if success_change > 5.0:  # %5 başarı artışı
                    comparison["improvements"].append(f"{category_name} kategorisi başarı oranı arttı")
                elif success_change < -5.0:  # %5 başarı azalışı
                    comparison["regressions"].append(f"{category_name} kategorisi başarı oranı azaldı")
        
        return comparison
    
    def _parse_junit_xml(self, xml_path: str) -> List[TestResult]:
        """JUnit XML dosyasını parse et."""
        test_results = []
        
        if not os.path.exists(xml_path):
            return test_results
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for testcase in root.findall(".//testcase"):
                name = testcase.get("name", "")
                classname = testcase.get("classname", "")
                time_str = testcase.get("time", "0")
                
                try:
                    duration = float(time_str)
                except ValueError:
                    duration = 0.0
                
                # Test durumunu belirle
                if testcase.find("failure") is not None:
                    status = "failed"
                    error_elem = testcase.find("failure")
                    error_message = error_elem.text if error_elem is not None else None
                elif testcase.find("error") is not None:
                    status = "error"
                    error_elem = testcase.find("error")
                    error_message = error_elem.text if error_elem is not None else None
                elif testcase.find("skipped") is not None:
                    status = "skipped"
                    error_message = None
                else:
                    status = "passed"
                    error_message = None
                
                # Kategoriyi belirle (dosya adından)
                category = self._determine_category(classname, name)
                
                test_results.append(TestResult(
                    name=name,
                    status=status,
                    duration=duration,
                    category=category,
                    file_path=classname,
                    error_message=error_message
                ))
        
        except ET.ParseError:
            pass  # XML parse hatası - boş liste döndür
        
        return test_results
    
    def _determine_category(self, classname: str, test_name: str) -> str:
        """Test kategorisini belirle."""
        # Dosya adından kategori çıkarma
        if "critical" in classname.lower() or "critical" in test_name.lower():
            return "critical"
        elif "smoke" in classname.lower() or "smoke" in test_name.lower():
            return "smoke"
        elif "slow" in classname.lower() or "slow" in test_name.lower():
            return "slow"
        elif "property" in classname.lower() or "property" in test_name.lower():
            return "property"
        elif "integration" in classname.lower() or "integration" in test_name.lower():
            return "integration"
        else:
            return "unit"
    
    def _calculate_category_metrics(self, test_results: List[TestResult]) -> List[CategoryMetrics]:
        """Kategori metrikleri hesapla."""
        categories = {}
        
        for test in test_results:
            category = test.category
            if category not in categories:
                categories[category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "durations": []
                }
            
            categories[category]["total"] += 1
            categories[category]["durations"].append(test.duration)
            
            if test.status == "passed":
                categories[category]["passed"] += 1
            elif test.status == "failed":
                categories[category]["failed"] += 1
            elif test.status == "skipped":
                categories[category]["skipped"] += 1
        
        metrics = []
        for category, data in categories.items():
            total_duration = sum(data["durations"])
            average_duration = total_duration / len(data["durations"]) if data["durations"] else 0.0
            success_rate = (data["passed"] / data["total"] * 100) if data["total"] > 0 else 0.0
            
            metrics.append(CategoryMetrics(
                category=category,
                total_tests=data["total"],
                passed_tests=data["passed"],
                failed_tests=data["failed"],
                skipped_tests=data["skipped"],
                total_duration=total_duration,
                average_duration=average_duration,
                success_rate=success_rate
            ))
        
        return metrics
    
    def _get_coverage_percentage(self) -> float:
        """Coverage yüzdesini al."""
        try:
            # Coverage JSON raporu varsa oku
            coverage_json_path = Path("coverage.json")
            if coverage_json_path.exists():
                with open(coverage_json_path, 'r') as f:
                    coverage_data = json.load(f)
                    return coverage_data.get("totals", {}).get("percent_covered", 0.0)
            
            # Coverage XML raporu varsa parse et
            coverage_xml_path = Path("coverage.xml")
            if coverage_xml_path.exists():
                tree = ET.parse(coverage_xml_path)
                root = tree.getroot()
                coverage_elem = root.find(".//coverage")
                if coverage_elem is not None:
                    line_rate = coverage_elem.get("line-rate", "0")
                    return float(line_rate) * 100
            
            return 0.0
        
        except (FileNotFoundError, json.JSONDecodeError, ET.ParseError, ValueError):
            return 0.0
    
    def _generate_html_content(self, report: PerformanceReport) -> str:
        """HTML rapor içeriği oluştur."""
        return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SONTECHSP Test Performans Raporu</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
        .metric-card {{ background-color: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 5px; min-width: 200px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .category-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .category-table th, .category-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .category-table th {{ background-color: #f0f0f0; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .danger {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SONTECHSP Test Performans Raporu</h1>
        <p>Oluşturulma Zamanı: {report.timestamp}</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value {'success' if report.success_rate >= 90 else 'warning' if report.success_rate >= 70 else 'danger'}">
                {report.success_rate:.1f}%
            </div>
            <div class="metric-label">Başarı Oranı</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{report.total_tests}</div>
            <div class="metric-label">Toplam Test</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{report.total_duration:.1f}s</div>
            <div class="metric-label">Toplam Süre</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{report.coverage_percentage:.1f}%</div>
            <div class="metric-label">Kod Kapsamı</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{report.worker_count}</div>
            <div class="metric-label">Worker Sayısı</div>
        </div>
    </div>
    
    <h2>Kategori Bazlı Sonuçlar</h2>
    <table class="category-table">
        <thead>
            <tr>
                <th>Kategori</th>
                <th>Toplam Test</th>
                <th>Başarılı</th>
                <th>Başarısız</th>
                <th>Atlanan</th>
                <th>Başarı Oranı</th>
                <th>Ortalama Süre</th>
                <th>Toplam Süre</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
            <tr>
                <td>{cat.category}</td>
                <td>{cat.total_tests}</td>
                <td class="success">{cat.passed_tests}</td>
                <td class="danger">{cat.failed_tests}</td>
                <td class="warning">{cat.skipped_tests}</td>
                <td class="{'success' if cat.success_rate >= 90 else 'warning' if cat.success_rate >= 70 else 'danger'}">
                    {cat.success_rate:.1f}%
                </td>
                <td>{cat.average_duration:.2f}s</td>
                <td>{cat.total_duration:.1f}s</td>
            </tr>
            ''' for cat in report.categories])}
        </tbody>
    </table>
    
    <h2>En Yavaş Testler</h2>
    <table class="category-table">
        <thead>
            <tr>
                <th>Test Adı</th>
                <th>Kategori</th>
                <th>Süre</th>
                <th>Durum</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
            <tr>
                <td>{test.name}</td>
                <td>{test.category}</td>
                <td>{test.duration:.2f}s</td>
                <td class="{'success' if test.status == 'passed' else 'danger'}">{test.status}</td>
            </tr>
            ''' for test in report.slowest_tests[:10]])}
        </tbody>
    </table>
    
    {f'''
    <h2>Başarısız Testler</h2>
    <table class="category-table">
        <thead>
            <tr>
                <th>Test Adı</th>
                <th>Kategori</th>
                <th>Hata Mesajı</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f"""
            <tr>
                <td>{test.name}</td>
                <td>{test.category}</td>
                <td>{test.error_message[:100] + '...' if test.error_message and len(test.error_message) > 100 else test.error_message or ''}</td>
            </tr>
            """ for test in report.failed_tests_detail[:10]])}
        </tbody>
    </table>
    ''' if report.failed_tests_detail else ''}
    
</body>
</html>"""