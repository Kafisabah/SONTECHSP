# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.refactoring_altyapi.test_koruma_sistemi
# Description: Refactoring sırasında test bütünlüğünü koruyan sistem
# Changelog:
# - İlk versiyon: TestKorumaSistemi sınıfı oluşturuldu

"""
Test Koruma Sistemi

Refactoring işlemleri sırasında test bütünlüğünü korur:
- Test coverage analizi
- Test güncelleme stratejileri
- Kırılan testlerin otomatik tespiti
- Test import güncelleme
"""

import ast
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import re


class TestDurumu(Enum):
    """Test durumları"""
    GECTI = "gecti"
    BASARISIZ = "basarisiz"
    ATLANDI = "atlandi"
    HATA = "hata"


class TestTuru(Enum):
    """Test türleri"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PROPERTY = "property"
    FUNCTIONAL = "functional"


@dataclass
class TestBilgisi:
    """Test bilgisi"""
    test_dosyasi: str
    test_adi: str
    test_turu: TestTuru
    durum: TestDurumu
    hedef_modul: Optional[str] = None
    bagimliliklar: List[str] = field(default_factory=list)
    hata_mesaji: Optional[str] = None
    calisma_suresi: float = 0.0


@dataclass
class TestCoverageRaporu:
    """Test coverage raporu"""
    toplam_satir: int
    kapsanan_satir: int
    coverage_yuzdesi: float
    dosya_coverage: Dict[str, float] = field(default_factory=dict)
    eksik_coverage_dosyalari: List[str] = field(default_factory=list)


@dataclass
class TestGuncellemePlani:
    """Test güncelleme planı"""
    guncellenecek_testler: List[str] = field(default_factory=list)
    silinecek_testler: List[str] = field(default_factory=list)
    yeni_testler: List[str] = field(default_factory=list)
    import_guncellemeleri: Dict[str, List[str]] = field(default_factory=dict)


class TestKorumaSistemi:
    """
    Test Koruma Sistemi
    
    Refactoring işlemleri sırasında test bütünlüğünü korur:
    - Mevcut testleri analiz eder
    - Test coverage'ını takip eder
    - Refactoring sonrası test güncellemelerini planlar
    - Kırılan testleri tespit eder ve düzeltme önerileri sunar
    """
    
    def __init__(
        self,
        proje_yolu: str,
        test_klasoru: str = "tests",
        minimum_coverage: float = 80.0,
        log_seviyesi: int = logging.INFO
    ):
        """
        Args:
            proje_yolu: Proje ana yolu
            test_klasoru: Test dosyalarının bulunduğu klasör
            minimum_coverage: Minimum test coverage yüzdesi
            log_seviyesi: Log seviyesi
        """
        self.proje_yolu = Path(proje_yolu)
        self.test_klasoru = self.proje_yolu / test_klasoru
        self.minimum_coverage = minimum_coverage
        
        # Logger kurulumu
        self.logger = self._logger_kurulumu(log_seviyesi)
        
        # Test bilgileri
        self.test_bilgileri: Dict[str, TestBilgisi] = {}
        self.son_coverage_raporu: Optional[TestCoverageRaporu] = None
        
        # Test çalıştırma komutları
        self.test_komutlari = {
            'pytest': ['python', '-m', 'pytest'],
            'unittest': ['python', '-m', 'unittest'],
            'coverage': ['python', '-m', 'coverage']
        }
        
        self.logger.info(f"TestKorumaSistemi başlatıldı: {self.proje_yolu}")
    
    def _logger_kurulumu(self, log_seviyesi: int) -> logging.Logger:
        """Logger kurulumu yapar"""
        logger = logging.getLogger(f"TestKorumaSistemi_{id(self)}")
        logger.setLevel(log_seviyesi)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def mevcut_testleri_analiz_et(self) -> Dict[str, TestBilgisi]:
        """
        Mevcut testleri analiz eder.
        
        Returns:
            Test bilgileri sözlüğü
        """
        self.logger.info("Mevcut testler analiz ediliyor...")
        
        self.test_bilgileri.clear()
        
        # Test dosyalarını bul
        test_dosyalari = list(self.test_klasoru.rglob('test_*.py'))
        test_dosyalari.extend(list(self.test_klasoru.rglob('*_test.py')))
        
        for test_dosyasi in test_dosyalari:
            self._test_dosyasini_analiz_et(test_dosyasi)
        
        self.logger.info(f"{len(self.test_bilgileri)} test fonksiyonu analiz edildi")
        return self.test_bilgileri
    
    def _test_dosyasini_analiz_et(self, test_dosyasi: Path):
        """
        Tek bir test dosyasını analiz eder.
        
        Args:
            test_dosyasi: Test dosyası yolu
        """
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            # AST ile analiz et
            tree = ast.parse(icerik)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_bilgisi = self._test_fonksiyonu_analiz_et(
                        test_dosyasi, node, icerik
                    )
                    if test_bilgisi:
                        test_anahtari = f"{test_dosyasi.name}::{test_bilgisi.test_adi}"
                        self.test_bilgileri[test_anahtari] = test_bilgisi
                        
        except Exception as e:
            self.logger.warning(f"Test dosyası analiz hatası {test_dosyasi}: {e}")
    
    def _test_fonksiyonu_analiz_et(
        self,
        test_dosyasi: Path,
        node: ast.FunctionDef,
        dosya_icerigi: str
    ) -> Optional[TestBilgisi]:
        """
        Test fonksiyonunu analiz eder.
        
        Args:
            test_dosyasi: Test dosyası yolu
            node: AST fonksiyon node'u
            dosya_icerigi: Dosya içeriği
            
        Returns:
            Test bilgisi
        """
        try:
            # Test türünü belirle
            test_turu = self._test_turunu_belirle(node, dosya_icerigi)
            
            # Hedef modülü bul
            hedef_modul = self._hedef_modulu_bul(test_dosyasi, node)
            
            # Bağımlılıkları bul
            bagimliliklar = self._test_bagimlilikları_bul(node, dosya_icerigi)
            
            return TestBilgisi(
                test_dosyasi=str(test_dosyasi),
                test_adi=node.name,
                test_turu=test_turu,
                durum=TestDurumu.GECTI,  # Varsayılan
                hedef_modul=hedef_modul,
                bagimliliklar=bagimliliklar
            )
            
        except Exception as e:
            self.logger.warning(f"Test fonksiyon analiz hatası {node.name}: {e}")
            return None
    
    def _test_turunu_belirle(self, node: ast.FunctionDef, dosya_icerigi: str) -> TestTuru:
        """Test türünü belirler"""
        # Fonksiyon adından çıkarım
        if 'property' in node.name.lower():
            return TestTuru.PROPERTY
        elif 'integration' in node.name.lower() or 'entegrasyon' in node.name.lower():
            return TestTuru.INTEGRATION
        elif 'functional' in node.name.lower() or 'fonksiyonel' in node.name.lower():
            return TestTuru.FUNCTIONAL
        
        # Docstring'den çıkarım
        docstring = ast.get_docstring(node)
        if docstring:
            docstring_lower = docstring.lower()
            if 'property' in docstring_lower:
                return TestTuru.PROPERTY
            elif 'integration' in docstring_lower:
                return TestTuru.INTEGRATION
            elif 'functional' in docstring_lower:
                return TestTuru.FUNCTIONAL
        
        # Varsayılan olarak unit test
        return TestTuru.UNIT
    
    def _hedef_modulu_bul(self, test_dosyasi: Path, node: ast.FunctionDef) -> Optional[str]:
        """Test fonksiyonunun hedef modülünü bulur"""
        # Test dosyası adından çıkarım
        dosya_adi = test_dosyasi.stem
        if dosya_adi.startswith('test_'):
            modul_adi = dosya_adi[5:]  # 'test_' kısmını çıkar
            return modul_adi
        elif dosya_adi.endswith('_test'):
            modul_adi = dosya_adi[:-5]  # '_test' kısmını çıkar
            return modul_adi
        
        return None
    
    def _test_bagimlilikları_bul(
        self,
        node: ast.FunctionDef,
        dosya_icerigi: str
    ) -> List[str]:
        """Test fonksiyonunun bağımlılıklarını bulur"""
        bagimliliklar = []
        
        # Import'ları bul
        try:
            tree = ast.parse(dosya_icerigi)
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    for alias in n.names:
                        bagimliliklar.append(alias.name)
                elif isinstance(n, ast.ImportFrom):
                    if n.module:
                        bagimliliklar.append(n.module)
        except:
            pass
        
        return bagimliliklar
    
    def testleri_calistir(
        self,
        test_filtresi: str = None,
        verbose: bool = True
    ) -> Dict[str, TestBilgisi]:
        """
        Testleri çalıştırır ve sonuçları analiz eder.
        
        Args:
            test_filtresi: Test filtresi (pytest formatında)
            verbose: Detaylı çıktı
            
        Returns:
            Güncellenmiş test bilgileri
        """
        self.logger.info("Testler çalıştırılıyor...")
        
        try:
            # Pytest komutunu hazırla
            komut = self.test_komutlari['pytest'].copy()
            komut.extend(['--tb=short', '--no-header'])
            
            if verbose:
                komut.append('-v')
            
            if test_filtresi:
                komut.append(test_filtresi)
            else:
                komut.append(str(self.test_klasoru))
            
            # JSON çıktı için
            komut.extend(['--json-report', '--json-report-file=test_results.json'])
            
            # Testleri çalıştır
            result = subprocess.run(
                komut,
                cwd=self.proje_yolu,
                capture_output=True,
                text=True,
                timeout=300  # 5 dakika timeout
            )
            
            # Sonuçları analiz et
            self._test_sonuclarini_analiz_et(result)
            
            return self.test_bilgileri
            
        except subprocess.TimeoutExpired:
            self.logger.error("Test çalıştırma timeout'a uğradı")
            return self.test_bilgileri
        except Exception as e:
            self.logger.error(f"Test çalıştırma hatası: {e}")
            return self.test_bilgileri
    
    def _test_sonuclarini_analiz_et(self, result: subprocess.CompletedProcess):
        """Test sonuçlarını analiz eder"""
        try:
            # JSON raporu oku
            json_dosyasi = self.proje_yolu / "test_results.json"
            if json_dosyasi.exists():
                with open(json_dosyasi, 'r', encoding='utf-8') as f:
                    test_raporu = json.load(f)
                
                # Test sonuçlarını güncelle
                for test in test_raporu.get('tests', []):
                    test_anahtari = f"{Path(test['nodeid']).name}"
                    if test_anahtari in self.test_bilgileri:
                        test_bilgisi = self.test_bilgileri[test_anahtari]
                        
                        if test['outcome'] == 'passed':
                            test_bilgisi.durum = TestDurumu.GECTI
                        elif test['outcome'] == 'failed':
                            test_bilgisi.durum = TestDurumu.BASARISIZ
                            test_bilgisi.hata_mesaji = test.get('call', {}).get('longrepr', '')
                        elif test['outcome'] == 'skipped':
                            test_bilgisi.durum = TestDurumu.ATLANDI
                        
                        test_bilgisi.calisma_suresi = test.get('duration', 0.0)
                
                # JSON dosyasını temizle
                json_dosyasi.unlink()
                
        except Exception as e:
            self.logger.warning(f"Test sonuç analiz hatası: {e}")
            
            # Fallback: stdout/stderr analizi
            self._stdout_analiz_et(result.stdout, result.stderr)
    
    def _stdout_analiz_et(self, stdout: str, stderr: str):
        """Stdout/stderr'dan test sonuçlarını analiz eder"""
        # Basit regex ile test sonuçlarını bul
        passed_pattern = r'(\w+\.py::\w+)\s+PASSED'
        failed_pattern = r'(\w+\.py::\w+)\s+FAILED'
        
        for match in re.finditer(passed_pattern, stdout):
            test_anahtari = match.group(1)
            if test_anahtari in self.test_bilgileri:
                self.test_bilgileri[test_anahtari].durum = TestDurumu.GECTI
        
        for match in re.finditer(failed_pattern, stdout):
            test_anahtari = match.group(1)
            if test_anahtari in self.test_bilgileri:
                self.test_bilgileri[test_anahtari].durum = TestDurumu.BASARISIZ
    
    def coverage_analizi_yap(self) -> TestCoverageRaporu:
        """
        Test coverage analizi yapar.
        
        Returns:
            Coverage raporu
        """
        self.logger.info("Coverage analizi yapılıyor...")
        
        try:
            # Coverage çalıştır
            komut = self.test_komutlari['coverage'].copy()
            komut.extend(['run', '--source=sontechsp', '-m', 'pytest', str(self.test_klasoru)])
            
            subprocess.run(
                komut,
                cwd=self.proje_yolu,
                capture_output=True,
                timeout=300
            )
            
            # Coverage raporu al
            rapor_komutu = self.test_komutlari['coverage'].copy()
            rapor_komutu.extend(['report', '--format=json'])
            
            result = subprocess.run(
                rapor_komutu,
                cwd=self.proje_yolu,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                rapor = self._coverage_raporunu_olustur(coverage_data)
                self.son_coverage_raporu = rapor
                return rapor
            else:
                self.logger.warning("Coverage raporu alınamadı")
                return self._bos_coverage_raporu()
                
        except Exception as e:
            self.logger.error(f"Coverage analiz hatası: {e}")
            return self._bos_coverage_raporu()
    
    def _coverage_raporunu_olustur(self, coverage_data: dict) -> TestCoverageRaporu:
        """Coverage verilerinden rapor oluşturur"""
        toplam_satir = coverage_data['totals']['num_statements']
        kapsanan_satir = coverage_data['totals']['covered_lines']
        coverage_yuzdesi = coverage_data['totals']['percent_covered']
        
        dosya_coverage = {}
        eksik_coverage_dosyalari = []
        
        for dosya, veri in coverage_data['files'].items():
            dosya_coverage_yuzdesi = veri['summary']['percent_covered']
            dosya_coverage[dosya] = dosya_coverage_yuzdesi
            
            if dosya_coverage_yuzdesi < self.minimum_coverage:
                eksik_coverage_dosyalari.append(dosya)
        
        return TestCoverageRaporu(
            toplam_satir=toplam_satir,
            kapsanan_satir=kapsanan_satir,
            coverage_yuzdesi=coverage_yuzdesi,
            dosya_coverage=dosya_coverage,
            eksik_coverage_dosyalari=eksik_coverage_dosyalari
        )
    
    def _bos_coverage_raporu(self) -> TestCoverageRaporu:
        """Boş coverage raporu oluşturur"""
        return TestCoverageRaporu(
            toplam_satir=0,
            kapsanan_satir=0,
            coverage_yuzdesi=0.0
        )
    
    def refactoring_sonrasi_test_guncelleme_plani_olustur(
        self,
        degisen_dosyalar: List[str],
        yeni_dosyalar: List[str] = None,
        silinen_dosyalar: List[str] = None
    ) -> TestGuncellemePlani:
        """
        Refactoring sonrası test güncelleme planı oluşturur.
        
        Args:
            degisen_dosyalar: Değişen dosya listesi
            yeni_dosyalar: Yeni oluşturulan dosyalar
            silinen_dosyalar: Silinen dosyalar
            
        Returns:
            Test güncelleme planı
        """
        self.logger.info("Test güncelleme planı oluşturuluyor...")
        
        plan = TestGuncellemePlani()
        
        if yeni_dosyalar is None:
            yeni_dosyalar = []
        if silinen_dosyalar is None:
            silinen_dosyalar = []
        
        # Değişen dosyalar için testleri güncelle
        for dosya in degisen_dosyalar:
            etkilenen_testler = self._dosya_icin_testleri_bul(dosya)
            plan.guncellenecek_testler.extend(etkilenen_testler)
        
        # Silinen dosyalar için testleri sil
        for dosya in silinen_dosyalar:
            etkilenen_testler = self._dosya_icin_testleri_bul(dosya)
            plan.silinecek_testler.extend(etkilenen_testler)
        
        # Yeni dosyalar için testler oluştur
        for dosya in yeni_dosyalar:
            if dosya.endswith('.py') and not dosya.startswith('test_'):
                yeni_test_dosyasi = self._yeni_test_dosyasi_adi_olustur(dosya)
                plan.yeni_testler.append(yeni_test_dosyasi)
        
        # Import güncellemelerini planla
        plan.import_guncellemeleri = self._import_guncellemelerini_planla(
            degisen_dosyalar, yeni_dosyalar, silinen_dosyalar
        )
        
        return plan
    
    def _dosya_icin_testleri_bul(self, dosya: str) -> List[str]:
        """Belirli bir dosya için testleri bulur"""
        etkilenen_testler = []
        
        dosya_path = Path(dosya)
        modul_adi = dosya_path.stem
        
        for test_anahtari, test_bilgisi in self.test_bilgileri.items():
            # Hedef modül eşleşmesi
            if test_bilgisi.hedef_modul == modul_adi:
                etkilenen_testler.append(test_anahtari)
            
            # Bağımlılık eşleşmesi
            for bagimlilik in test_bilgisi.bagimliliklar:
                if modul_adi in bagimlilik or dosya in bagimlilik:
                    etkilenen_testler.append(test_anahtari)
                    break
        
        return etkilenen_testler
    
    def _yeni_test_dosyasi_adi_olustur(self, dosya: str) -> str:
        """Yeni dosya için test dosyası adı oluşturur"""
        dosya_path = Path(dosya)
        modul_adi = dosya_path.stem
        return f"test_{modul_adi}.py"
    
    def _import_guncellemelerini_planla(
        self,
        degisen_dosyalar: List[str],
        yeni_dosyalar: List[str],
        silinen_dosyalar: List[str]
    ) -> Dict[str, List[str]]:
        """Import güncellemelerini planlar"""
        import_guncellemeleri = {}
        
        # Her test dosyası için import güncellemelerini kontrol et
        for test_anahtari, test_bilgisi in self.test_bilgileri.items():
            test_dosyasi = test_bilgisi.test_dosyasi
            guncellemeler = []
            
            # Silinen dosyalar için import'ları kaldır
            for silinen_dosya in silinen_dosyalar:
                silinen_modul = Path(silinen_dosya).stem
                if silinen_modul in test_bilgisi.bagimliliklar:
                    guncellemeler.append(f"REMOVE: {silinen_modul}")
            
            # Yeni dosyalar için import'lar ekle
            for yeni_dosya in yeni_dosyalar:
                yeni_modul = Path(yeni_dosya).stem
                if test_bilgisi.hedef_modul and yeni_modul.startswith(test_bilgisi.hedef_modul):
                    guncellemeler.append(f"ADD: {yeni_modul}")
            
            if guncellemeler:
                import_guncellemeleri[test_dosyasi] = guncellemeler
        
        return import_guncellemeleri
    
    def test_guncelleme_planini_uygula(self, plan: TestGuncellemePlani) -> bool:
        """
        Test güncelleme planını uygular.
        
        Args:
            plan: Test güncelleme planı
            
        Returns:
            Başarı durumu
        """
        self.logger.info("Test güncelleme planı uygulanıyor...")
        
        try:
            # Import güncellemelerini uygula
            for test_dosyasi, guncellemeler in plan.import_guncellemeleri.items():
                self._test_dosyasi_importlarini_guncelle(test_dosyasi, guncellemeler)
            
            # Silinecek testleri sil
            for test_dosyasi in plan.silinecek_testler:
                test_yolu = Path(test_dosyasi)
                if test_yolu.exists():
                    test_yolu.unlink()
                    self.logger.info(f"Test dosyası silindi: {test_dosyasi}")
            
            # Yeni test dosyalarını oluştur
            for yeni_test in plan.yeni_testler:
                self._yeni_test_dosyasi_olustur(yeni_test)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Test güncelleme planı uygulama hatası: {e}")
            return False
    
    def _test_dosyasi_importlarini_guncelle(
        self,
        test_dosyasi: str,
        guncellemeler: List[str]
    ):
        """Test dosyasının import'larını günceller"""
        try:
            test_yolu = Path(test_dosyasi)
            if not test_yolu.exists():
                return
            
            with open(test_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            # Güncellemeleri uygula
            for guncelleme in guncellemeler:
                if guncelleme.startswith('REMOVE:'):
                    modul = guncelleme[7:].strip()
                    # Import satırını kaldır
                    pattern = rf'^(from .* import .*{modul}.*|import .*{modul}.*)$'
                    icerik = re.sub(pattern, '', icerik, flags=re.MULTILINE)
                elif guncelleme.startswith('ADD:'):
                    modul = guncelleme[4:].strip()
                    # Import satırını ekle (dosya başına)
                    import_satiri = f"from sontechsp.uygulama import {modul}\n"
                    if import_satiri not in icerik:
                        icerik = import_satiri + icerik
            
            # Dosyayı güncelle
            with open(test_yolu, 'w', encoding='utf-8') as f:
                f.write(icerik)
                
        except Exception as e:
            self.logger.warning(f"Test import güncelleme hatası {test_dosyasi}: {e}")
    
    def _yeni_test_dosyasi_olustur(self, test_dosyasi: str):
        """Yeni test dosyası oluşturur"""
        try:
            test_yolu = self.test_klasoru / test_dosyasi
            
            # Temel test şablonu
            sablon = '''# Version: 0.1.0
# Last Update: {tarih}
# Module: tests.{modul_adi}
# Description: {modul_adi} için testler
# Changelog:
# - İlk versiyon: Otomatik oluşturuldu

"""
{modul_adi} Testleri

Bu dosya refactoring sırasında otomatik oluşturulmuştur.
Test fonksiyonlarını manuel olarak eklemeniz gerekir.
"""

import unittest


class Test{sinif_adi}(unittest.TestCase):
    """Test sınıfı"""
    
    def setUp(self):
        """Test kurulumu"""
        pass
    
    def tearDown(self):
        """Test temizliği"""
        pass
    
    def test_placeholder(self):
        """Placeholder test - silinecek"""
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
'''
            
            modul_adi = Path(test_dosyasi).stem[5:]  # 'test_' kısmını çıkar
            sinif_adi = ''.join(word.capitalize() for word in modul_adi.split('_'))
            
            icerik = sablon.format(
                tarih=datetime.now().strftime('%Y-%m-%d'),
                modul_adi=modul_adi,
                sinif_adi=sinif_adi
            )
            
            with open(test_yolu, 'w', encoding='utf-8') as f:
                f.write(icerik)
            
            self.logger.info(f"Yeni test dosyası oluşturuldu: {test_dosyasi}")
            
        except Exception as e:
            self.logger.error(f"Yeni test dosyası oluşturma hatası: {e}")
    
    def test_durumu_raporu_olustur(self) -> Dict[str, any]:
        """
        Test durumu raporu oluşturur.
        
        Returns:
            Test durumu raporu
        """
        toplam_test = len(self.test_bilgileri)
        gecen_testler = sum(1 for t in self.test_bilgileri.values() if t.durum == TestDurumu.GECTI)
        basarisiz_testler = sum(1 for t in self.test_bilgileri.values() if t.durum == TestDurumu.BASARISIZ)
        atlanan_testler = sum(1 for t in self.test_bilgileri.values() if t.durum == TestDurumu.ATLANDI)
        
        # Test türlerine göre dağılım
        test_turleri = {}
        for test_turu in TestTuru:
            test_turleri[test_turu.value] = sum(
                1 for t in self.test_bilgileri.values() if t.test_turu == test_turu
            )
        
        rapor = {
            'toplam_test': toplam_test,
            'gecen_testler': gecen_testler,
            'basarisiz_testler': basarisiz_testler,
            'atlanan_testler': atlanan_testler,
            'basari_orani': (gecen_testler / toplam_test * 100) if toplam_test > 0 else 0,
            'test_turleri': test_turleri,
            'coverage': {
                'yuzdesi': self.son_coverage_raporu.coverage_yuzdesi if self.son_coverage_raporu else 0,
                'minimum_karsilaniyor': (
                    self.son_coverage_raporu.coverage_yuzdesi >= self.minimum_coverage
                    if self.son_coverage_raporu else False
                )
            },
            'basarisiz_test_detaylari': [
                {
                    'test': anahtar,
                    'hata': bilgi.hata_mesaji
                }
                for anahtar, bilgi in self.test_bilgileri.items()
                if bilgi.durum == TestDurumu.BASARISIZ
            ]
        }
        
        return rapor