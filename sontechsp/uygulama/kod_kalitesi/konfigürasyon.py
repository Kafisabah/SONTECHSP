# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kod_kalitesi.konfigürasyon
# Description: Kod kalitesi konfigürasyon yönetimi
# Changelog:
# - İlk sürüm: YAML tabanlı konfigürasyon sistemi

import os
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class DosyaKurallari:
    """Dosya kuralları konfigürasyonu"""
    max_satir_sayisi: int = 120
    hariç_tutulan_klasorler: List[str] = None
    hariç_tutulan_dosyalar: List[str] = None
    yorum_satirlari_dahil: bool = False
    
    def __post_init__(self):
        if self.hariç_tutulan_klasorler is None:
            self.hariç_tutulan_klasorler = ['__pycache__', '.git', 'venv', 'env']
        if self.hariç_tutulan_dosyalar is None:
            self.hariç_tutulan_dosyalar = ['__init__.py']


@dataclass
class FonksiyonKurallari:
    """Fonksiyon kuralları konfigürasyonu"""
    max_satir_sayisi: int = 25
    karmasiklik_esigi: int = 10
    hariç_tutulan_fonksiyonlar: List[str] = None
    
    def __post_init__(self):
        if self.hariç_tutulan_fonksiyonlar is None:
            self.hariç_tutulan_fonksiyonlar = ['__init__', '__str__', '__repr__']


@dataclass
class MimariKurallari:
    """Mimari kuralları konfigürasyonu"""
    katman_sirasi: List[str] = None
    yasak_importlar: Dict[str, List[str]] = None
    dependency_injection_zorunlu: bool = True
    
    def __post_init__(self):
        if self.katman_sirasi is None:
            self.katman_sirasi = ['ui', 'servisler', 'depolar', 'veritabani']
        if self.yasak_importlar is None:
            self.yasak_importlar = {
                'ui': ['depolar', 'veritabani'],
                'servisler': ['ui'],
                'depolar': ['ui', 'servisler']
            }


@dataclass
class KodTekrariKurallari:
    """Kod tekrarı kuralları konfigürasyonu"""
    benzerlik_esigi: float = 0.8
    minimum_satir_sayisi: int = 5
    ortak_modul_klasoru: str = 'ortak'
    
    
@dataclass
class BaslikKurallari:
    """Dosya başlık kuralları konfigürasyonu"""
    zorunlu_alanlar: List[str] = None
    tarih_formati: str = '%Y-%m-%d'
    surum_formati: str = 'X.Y.Z'
    
    def __post_init__(self):
        if self.zorunlu_alanlar is None:
            self.zorunlu_alanlar = ['Version', 'Last Update', 'Module', 'Description']


@dataclass
class TestKurallari:
    """Test kuralları konfigürasyonu"""
    test_klasoru: str = 'tests'
    minimum_coverage: float = 80.0
    property_test_iterasyon: int = 100
    test_timeout: int = 300


@dataclass
class GuvenlikKurallari:
    """Güvenlik kuralları konfigürasyonu"""
    backup_klasoru: str = '.kod-kalitesi-backup'
    max_backup_sayisi: int = 10
    otomatik_backup: bool = True
    geri_alma_timeout: int = 60


@dataclass
class KodKalitesiKonfigurasyonu:
    """Ana konfigürasyon sınıfı"""
    dosya_kurallari: DosyaKurallari
    fonksiyon_kurallari: FonksiyonKurallari
    mimari_kurallari: MimariKurallari
    kod_tekrari_kurallari: KodTekrariKurallari
    baslik_kurallari: BaslikKurallari
    test_kurallari: TestKurallari
    guvenlik_kurallari: GuvenlikKurallari
    
    @classmethod
    def varsayilan(cls) -> 'KodKalitesiKonfigurasyonu':
        """Varsayılan konfigürasyon oluştur"""
        return cls(
            dosya_kurallari=DosyaKurallari(),
            fonksiyon_kurallari=FonksiyonKurallari(),
            mimari_kurallari=MimariKurallari(),
            kod_tekrari_kurallari=KodTekrariKurallari(),
            baslik_kurallari=BaslikKurallari(),
            test_kurallari=TestKurallari(),
            guvenlik_kurallari=GuvenlikKurallari()
        )
    
    def yaml_dosyasina_kaydet(self, dosya_yolu: str):
        """Konfigürasyonu YAML dosyasına kaydet"""
        config_dict = asdict(self)
        
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, 
                     allow_unicode=True, indent=2)
    
    @classmethod
    def yaml_dosyasindan_yukle(cls, dosya_yolu: str) -> 'KodKalitesiKonfigurasyonu':
        """YAML dosyasından konfigürasyon yükle"""
        if not os.path.exists(dosya_yolu):
            raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {dosya_yolu}")
        
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(
            dosya_kurallari=DosyaKurallari(**config_dict.get('dosya_kurallari', {})),
            fonksiyon_kurallari=FonksiyonKurallari(**config_dict.get('fonksiyon_kurallari', {})),
            mimari_kurallari=MimariKurallari(**config_dict.get('mimari_kurallari', {})),
            kod_tekrari_kurallari=KodTekrariKurallari(**config_dict.get('kod_tekrari_kurallari', {})),
            baslik_kurallari=BaslikKurallari(**config_dict.get('baslik_kurallari', {})),
            test_kurallari=TestKurallari(**config_dict.get('test_kurallari', {})),
            guvenlik_kurallari=GuvenlikKurallari(**config_dict.get('guvenlik_kurallari', {}))
        )


class KonfigürasyonYoneticisi:
    """Konfigürasyon yönetim sınıfı"""
    
    VARSAYILAN_CONFIG_DOSYASI = 'kod-kalitesi-config.yaml'
    
    def __init__(self, proje_yolu: str):
        self.proje_yolu = Path(proje_yolu)
        self.config_dosya_yolu = self.proje_yolu / self.VARSAYILAN_CONFIG_DOSYASI
        self._config: Optional[KodKalitesiKonfigurasyonu] = None
    
    def konfigürasyonu_yukle(self) -> KodKalitesiKonfigurasyonu:
        """Konfigürasyonu yükle veya varsayılan oluştur"""
        if self._config is not None:
            return self._config
        
        if self.config_dosya_yolu.exists():
            try:
                self._config = KodKalitesiKonfigurasyonu.yaml_dosyasindan_yukle(
                    str(self.config_dosya_yolu)
                )
                print(f"✅ Konfigürasyon yüklendi: {self.config_dosya_yolu}")
            except Exception as e:
                print(f"⚠️ Konfigürasyon yükleme hatası: {e}")
                print("📝 Varsayılan konfigürasyon kullanılıyor...")
                self._config = KodKalitesiKonfigurasyonu.varsayilan()
        else:
            print("📝 Konfigürasyon dosyası bulunamadı, varsayılan kullanılıyor...")
            self._config = KodKalitesiKonfigurasyonu.varsayilan()
        
        return self._config
    
    def varsayilan_konfigürasyon_olustur(self) -> str:
        """Varsayılan konfigürasyon dosyası oluştur"""
        config = KodKalitesiKonfigurasyonu.varsayilan()
        config.yaml_dosyasina_kaydet(str(self.config_dosya_yolu))
        
        print(f"✅ Varsayılan konfigürasyon oluşturuldu: {self.config_dosya_yolu}")
        return str(self.config_dosya_yolu)
    
    def konfigürasyonu_guncelle(self, yeni_config: KodKalitesiKonfigurasyonu):
        """Konfigürasyonu güncelle ve kaydet"""
        self._config = yeni_config
        yeni_config.yaml_dosyasina_kaydet(str(self.config_dosya_yolu))
        print(f"✅ Konfigürasyon güncellendi: {self.config_dosya_yolu}")
    
    def konfigürasyon_dosyasi_var_mi(self) -> bool:
        """Konfigürasyon dosyasının varlığını kontrol et"""
        return self.config_dosya_yolu.exists()
    
    def konfigürasyon_dogrula(self) -> List[str]:
        """Konfigürasyon doğrulaması yap"""
        hatalar = []
        config = self.konfigürasyonu_yukle()
        
        # Dosya kuralları doğrulama
        if config.dosya_kurallari.max_satir_sayisi <= 0:
            hatalar.append("Dosya maksimum satır sayısı pozitif olmalı")
        
        # Fonksiyon kuralları doğrulama
        if config.fonksiyon_kurallari.max_satir_sayisi <= 0:
            hatalar.append("Fonksiyon maksimum satır sayısı pozitif olmalı")
        
        # Kod tekrarı kuralları doğrulama
        if not (0 < config.kod_tekrari_kurallari.benzerlik_esigi <= 1):
            hatalar.append("Benzerlik eşiği 0-1 arasında olmalı")
        
        # Test kuralları doğrulama
        if not (0 <= config.test_kurallari.minimum_coverage <= 100):
            hatalar.append("Minimum coverage 0-100 arasında olmalı")
        
        return hatalar