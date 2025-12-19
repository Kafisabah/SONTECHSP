# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_altyapi.konfigurasyon
# Description: Test konfigürasyon sistemi ve veri modelleri
# Changelog:
# - İlk oluşturma

"""
Test Konfigürasyon Sistemi

Bu modül test konfigürasyonu ve sonuç raporlama için veri modellerini içerir:
- TestConfig: Test konfigürasyon ayarları
- TestResult: Test sonuç raporlama
- Test veritabanı bağlantı yönetimi

Görev 8: Test altyapısı ve mock servisleri oluştur
Requirements: Test konfigürasyon sistemi
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TestKategori(Enum):
    """Test kategorileri"""

    SMOKE = "smoke"
    FAST = "fast"
    SLOW = "slow"
    CRITICAL = "critical"


class TestDurum(Enum):
    """Test durumları"""

    BASARILI = "basarili"
    BASARISIZ = "basarisiz"
    ATLANDI = "atlandi"
    HATA = "hata"


@dataclass
class TestConfig:
    """Test konfigürasyon ayarları"""

    # Veritabanı ayarları
    test_db_url: str = "postgresql://test_user:test_pass@localhost:5432/sontechsp_test"
    sqlite_test_path: str = "test_offline.db"

    # Test kategorileri
    kategori: TestKategori = TestKategori.FAST
    max_sure_saniye: int = 120

    # Mock servis ayarları
    mock_network_enabled: bool = True
    dummy_saglayici_hata_orani: float = 0.5

    # Property-based test ayarları
    hypothesis_max_examples: int = 100
    hypothesis_deadline: int = 5000  # ms

    # Raporlama ayarları
    rapor_dizini: str = "test_reports"
    detayli_log: bool = True

    @classmethod
    def from_env(cls) -> "TestConfig":
        """Çevre değişkenlerinden konfigürasyon oluştur"""
        return cls(
            test_db_url=os.getenv("TEST_DB_URL", cls.test_db_url),
            sqlite_test_path=os.getenv("SQLITE_TEST_PATH", cls.sqlite_test_path),
            kategori=TestKategori(os.getenv("TEST_KATEGORI", cls.kategori.value)),
            max_sure_saniye=int(os.getenv("TEST_MAX_SURE", cls.max_sure_saniye)),
            mock_network_enabled=os.getenv("MOCK_NETWORK", "true").lower() == "true",
            dummy_saglayici_hata_orani=float(os.getenv("DUMMY_HATA_ORANI", cls.dummy_saglayici_hata_orani)),
            hypothesis_max_examples=int(os.getenv("HYPOTHESIS_MAX_EXAMPLES", cls.hypothesis_max_examples)),
            rapor_dizini=os.getenv("TEST_RAPOR_DIZINI", cls.rapor_dizini),
            detayli_log=os.getenv("DETAYLI_LOG", "true").lower() == "true",
        )

    def to_dict(self) -> Dict[str, Any]:
        """Sözlük formatına çevir"""
        return asdict(self)


@dataclass
class TestSonuc:
    """Tek test sonucu"""

    test_adi: str
    durum: TestDurum
    sure_ms: float
    hata_mesaji: Optional[str] = None
    detaylar: Optional[Dict[str, Any]] = None


@dataclass
class TestResult:
    """Test sonuç raporlama"""

    # Genel bilgiler
    baslangic_zamani: datetime
    bitis_zamani: Optional[datetime] = None
    toplam_test_sayisi: int = 0

    # Sonuç sayıları
    basarili_sayisi: int = 0
    basarisiz_sayisi: int = 0
    atlanan_sayisi: int = 0
    hata_sayisi: int = 0

    # Test sonuçları
    test_sonuclari: List[TestSonuc] = None

    # Performans metrikleri
    toplam_sure_saniye: float = 0.0
    ortalama_test_suresi_ms: float = 0.0

    # Konfigürasyon
    kullanilan_config: Optional[TestConfig] = None

    def __post_init__(self):
        if self.test_sonuclari is None:
            self.test_sonuclari = []

    def test_sonucu_ekle(self, sonuc: TestSonuc):
        """Test sonucu ekle"""
        self.test_sonuclari.append(sonuc)
        self.toplam_test_sayisi += 1

        # Durum sayılarını güncelle
        if sonuc.durum == TestDurum.BASARILI:
            self.basarili_sayisi += 1
        elif sonuc.durum == TestDurum.BASARISIZ:
            self.basarisiz_sayisi += 1
        elif sonuc.durum == TestDurum.ATLANDI:
            self.atlanan_sayisi += 1
        elif sonuc.durum == TestDurum.HATA:
            self.hata_sayisi += 1

    def tamamla(self):
        """Test oturumunu tamamla"""
        self.bitis_zamani = datetime.now()

        if self.baslangic_zamani and self.bitis_zamani:
            delta = self.bitis_zamani - self.baslangic_zamani
            self.toplam_sure_saniye = delta.total_seconds()

        if self.toplam_test_sayisi > 0:
            toplam_ms = sum(sonuc.sure_ms for sonuc in self.test_sonuclari)
            self.ortalama_test_suresi_ms = toplam_ms / self.toplam_test_sayisi

    @property
    def basari_orani(self) -> float:
        """Başarı oranı (0-1 arası)"""
        if self.toplam_test_sayisi == 0:
            return 0.0
        return self.basarili_sayisi / self.toplam_test_sayisi

    @property
    def ozet(self) -> Dict[str, Any]:
        """Özet rapor"""
        return {
            "toplam_test": self.toplam_test_sayisi,
            "basarili": self.basarili_sayisi,
            "basarisiz": self.basarisiz_sayisi,
            "atlanan": self.atlanan_sayisi,
            "hata": self.hata_sayisi,
            "basari_orani": f"{self.basari_orani:.2%}",
            "toplam_sure": f"{self.toplam_sure_saniye:.2f}s",
            "ortalama_test_suresi": f"{self.ortalama_test_suresi_ms:.2f}ms",
        }

    def json_rapor_olustur(self, dosya_yolu: str):
        """JSON formatında rapor oluştur"""
        rapor_data = {
            "ozet": self.ozet,
            "baslangic_zamani": self.baslangic_zamani.isoformat(),
            "bitis_zamani": self.bitis_zamani.isoformat() if self.bitis_zamani else None,
            "test_sonuclari": [
                {
                    "test_adi": sonuc.test_adi,
                    "durum": sonuc.durum.value,
                    "sure_ms": sonuc.sure_ms,
                    "hata_mesaji": sonuc.hata_mesaji,
                    "detaylar": sonuc.detaylar,
                }
                for sonuc in self.test_sonuclari
            ],
            "konfigürasyon": self.kullanilan_config.to_dict() if self.kullanilan_config else None,
        }

        # Rapor dizinini oluştur
        os.makedirs(os.path.dirname(dosya_yolu), exist_ok=True)

        with open(dosya_yolu, "w", encoding="utf-8") as f:
            json.dump(rapor_data, f, indent=2, ensure_ascii=False)


class TestVeritabaniYoneticisi:
    """Test veritabanı bağlantı yönetimi"""

    def __init__(self, config: TestConfig):
        self.config = config
        self._postgresql_baglanti = None
        self._sqlite_baglanti = None

    def postgresql_baglanti_al(self):
        """PostgreSQL test veritabanı bağlantısı al"""
        try:
            import psycopg2

            if not self._postgresql_baglanti:
                self._postgresql_baglanti = psycopg2.connect(self.config.test_db_url)
            return self._postgresql_baglanti
        except ImportError:
            raise ImportError("psycopg2 kütüphanesi yüklü değil")
        except Exception as e:
            raise ConnectionError(f"PostgreSQL test veritabanına bağlanılamadı: {e}")

    def sqlite_baglanti_al(self):
        """SQLite test veritabanı bağlantısı al"""
        import sqlite3

        if not self._sqlite_baglanti:
            self._sqlite_baglanti = sqlite3.connect(self.config.sqlite_test_path)
        return self._sqlite_baglanti

    def veritabani_temizle(self):
        """Test veritabanlarını temizle"""
        # PostgreSQL temizleme
        if self._postgresql_baglanti:
            try:
                cursor = self._postgresql_baglanti.cursor()
                cursor.execute("TRUNCATE TABLE offline_kuyruk CASCADE")
                cursor.execute("TRUNCATE TABLE satis CASCADE")
                cursor.execute("TRUNCATE TABLE stok_bakiye CASCADE")
                self._postgresql_baglanti.commit()
            except Exception:
                pass  # Test ortamında hata görmezden gel

        # SQLite temizleme
        if self._sqlite_baglanti:
            try:
                cursor = self._sqlite_baglanti.cursor()
                cursor.execute("DELETE FROM offline_kuyruk")
                self._sqlite_baglanti.commit()
            except Exception:
                pass  # Test ortamında hata görmezden gel

    def baglantilari_kapat(self):
        """Tüm bağlantıları kapat"""
        if self._postgresql_baglanti:
            self._postgresql_baglanti.close()
            self._postgresql_baglanti = None

        if self._sqlite_baglanti:
            self._sqlite_baglanti.close()
            self._sqlite_baglanti = None


# Global test konfigürasyonu
TEST_CONFIG = TestConfig.from_env()
