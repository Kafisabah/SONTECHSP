# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.refactoring_altyapi.yedek_yoneticisi
# Description: Refactoring için optimize edilmiş yedekleme ve geri alma sistemi
# Changelog:
# - İlk versiyon: YedekYoneticisi sınıfı oluşturuldu
Yedek Yöneticisi

Refactoring işlemleri için optimize edilmiş yedekleme sistemi.
Git tabanlı yedekleme ve hızlı geri alma mekanizmaları sağlar.
"""

import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class YedekTuru(Enum):
    """Yedek türleri"""
    OTOMATIK = "otomatik"
    MANUEL = "manuel"
    REFACTORING_ONCESI = "refactoring_oncesi"
    ACIL_DURUM = "acil_durum"


class YedekDurumu(Enum):
    """Yedek durumları"""
    OLUSTURULUYOR = "olusturuluyor"
    TAMAMLANDI = "tamamlandi"
    HATA = "hata"
    SILINDI = "silindi"


@dataclass
class YedekBilgisi:
    """Yedek bilgisi"""
    yedek_id: str
    yedek_turu: YedekTuru
    durum: YedekDurumu
    olusturma_zamani: datetime
    proje_yolu: str
    yedek_yolu: str
    git_commit_hash: Optional[str] = None
    dosya_sayisi: int = 0
    toplam_boyut: int = 0
    hash_degeri: str = ""
    aciklama: str = ""
    etiketler: List[str] = field(default_factory=list)


@dataclass
class GeriAlmaBilgisi:
    """Geri alma bilgisi"""
    geri_alma_id: str
    yedek_id: str
    geri_alma_zamani: datetime
    basarili: bool
    hata_mesaji: Optional[str] = None


class YedekYoneticisi:
    """
    Yedek Yöneticisi
    
    Refactoring işlemleri için optimize edilmiş yedekleme sistemi:
    - Git tabanlı yedekleme (varsa)
    - Hızlı dosya tabanlı yedekleme
    - Artımlı yedekleme desteği
    - Otomatik temizlik
    """
    
    def __init__(
        self,
        proje_yolu: str,
        yedek_klasoru: str = None,
        git_kullan: bool = True,
        log_seviyesi: int = logging.INFO
    ):
        """
        Args:
            proje_yolu: Yedeklenecek proje yolu
            yedek_klasoru: Yedeklerin saklanacağı klasör
            git_kullan: Git tabanlı yedekleme kullanılsın mı
            log_seviyesi: Log seviyesi
        """
        self.proje_yolu = Path(proje_yolu)
        self.yedek_klasoru = Path(
            yedek_klasoru or self.proje_yolu / ".refactoring_yedekler"
        )
        self.git_kullan = git_kullan
        
        # Yedek klasörünü oluştur
        self.yedek_klasoru.mkdir(parents=True, exist_ok=True)
        
        # Logger kurulumu
        self.logger = self._logger_kurulumu(log_seviyesi)
        
        # Git durumunu kontrol et
        self.git_mevcut = self._git_durumu_kontrol_et()
        
        # Yedek kayıtları dosyası
        self.kayit_dosyasi = self.yedek_klasoru / "yedek_kayitlari.json"
        self.yedek_kayitlari = self._kayitlari_yukle()
        
        self.logger.info(f"YedekYoneticisi başlatıldı: {self.proje_yolu}")
        if self.git_mevcut:
            self.logger.info("Git tabanlı yedekleme aktif")
    
    def _logger_kurulumu(self, log_seviyesi: int) -> logging.Logger:
        """Logger kurulumu yapar"""
        logger = logging.getLogger(f"YedekYoneticisi_{id(self)}")
        logger.setLevel(log_seviyesi)
        
        if not logger.handlers:
            # Dosya handler
            log_dosyasi = self.yedek_klasoru / "yedek_yoneticisi.log"
            file_handler = logging.FileHandler(log_dosyasi, encoding='utf-8')
            file_handler.setLevel(log_seviyesi)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_seviyesi)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _git_durumu_kontrol_et(self) -> bool:
        """Git durumunu kontrol eder"""
        if not self.git_kullan:
            return False
        
        try:
            # Git repository var mı?
            git_klasoru = self.proje_yolu / ".git"
            if not git_klasoru.exists():
                return False
            
            # Git komutu çalışıyor mu?
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.proje_yolu,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
            
        except Exception as e:
            self.logger.warning(f"Git kontrolü başarısız: {e}")
            return False
    
    def _kayitlari_yukle(self) -> Dict[str, YedekBilgisi]:
        """Yedek kayıtlarını yükler"""
        if not self.kayit_dosyasi.exists():
            return {}
        
        try:
            with open(self.kayit_dosyasi, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            kayitlar = {}
            for yedek_id, bilgi in data.items():
                kayitlar[yedek_id] = YedekBilgisi(
                    yedek_id=bilgi['yedek_id'],
                    yedek_turu=YedekTuru(bilgi['yedek_turu']),
                    durum=YedekDurumu(bilgi['durum']),
                    olusturma_zamani=datetime.fromisoformat(bilgi['olusturma_zamani']),
                    proje_yolu=bilgi['proje_yolu'],
                    yedek_yolu=bilgi['yedek_yolu'],
                    git_commit_hash=bilgi.get('git_commit_hash'),
                    dosya_sayisi=bilgi.get('dosya_sayisi', 0),
                    toplam_boyut=bilgi.get('toplam_boyut', 0),
                    hash_degeri=bilgi.get('hash_degeri', ''),
                    aciklama=bilgi.get('aciklama', ''),
                    etiketler=bilgi.get('etiketler', [])
                )
            
            return kayitlar
            
        except Exception as e:
            self.logger.error(f"Kayıt yükleme hatası: {e}")
            return {}
    
    def _kayitlari_kaydet(self):
        """Yedek kayıtlarını kaydeder"""
        try:
            data = {}
            for yedek_id, bilgi in self.yedek_kayitlari.items():
                data[yedek_id] = {
                    'yedek_id': bilgi.yedek_id,
                    'yedek_turu': bilgi.yedek_turu.value,
                    'durum': bilgi.durum.value,
                    'olusturma_zamani': bilgi.olusturma_zamani.isoformat(),
                    'proje_yolu': bilgi.proje_yolu,
                    'yedek_yolu': bilgi.yedek_yolu,
                    'git_commit_hash': bilgi.git_commit_hash,
                    'dosya_sayisi': bilgi.dosya_sayisi,
                    'toplam_boyut': bilgi.toplam_boyut,
                    'hash_degeri': bilgi.hash_degeri,
                    'aciklama': bilgi.aciklama,
                    'etiketler': bilgi.etiketler
                }
            
            with open(self.kayit_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Kayıt kaydetme hatası: {e}")
    
    def yedek_olustur(
        self,
        yedek_turu: YedekTuru = YedekTuru.MANUEL,
        aciklama: str = "",
        etiketler: List[str] = None,
        hariç_tutulacaklar: List[str] = None
    ) -> YedekBilgisi:
        """
        Yeni yedek oluşturur.
        
        Args:
            yedek_turu: Yedek türü
            aciklama: Yedek açıklaması
            etiketler: Yedek etiketleri
            hariç_tutulacaklar: Hariç tutulacak dosya/klasör desenleri
            
        Returns:
            Yedek bilgisi
        """
        yedek_id = f"yedek_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.logger.info(f"Yedek oluşturuluyor: {yedek_id}")
        
        # Yedek bilgisi oluştur
        yedek_bilgisi = YedekBilgisi(
            yedek_id=yedek_id,
            yedek_turu=yedek_turu,
            durum=YedekDurumu.OLUSTURULUYOR,
            olusturma_zamani=datetime.now(),
            proje_yolu=str(self.proje_yolu),
            yedek_yolu=str(self.yedek_klasoru / yedek_id),
            aciklama=aciklama,
            etiketler=etiketler or []
        )
        
        try:
            # Git commit oluştur (varsa)
            if self.git_mevcut:
                git_commit = self._git_commit_olustur(aciklama)
                yedek_bilgisi.git_commit_hash = git_commit
            
            # Dosya tabanlı yedek oluştur
            self._dosya_yedegi_olustur(yedek_bilgisi, hariç_tutulacaklar)
            
            # Durumu güncelle
            yedek_bilgisi.durum = YedekDurumu.TAMAMLANDI
            
            # Kayıtlara ekle
            self.yedek_kayitlari[yedek_id] = yedek_bilgisi
            self._kayitlari_kaydet()
            
            self.logger.info(f"Yedek oluşturuldu: {yedek_id}")
            return yedek_bilgisi
            
        except Exception as e:
            yedek_bilgisi.durum = YedekDurumu.HATA
            self.logger.error(f"Yedek oluşturma hatası: {e}")
            raise
    
    def _git_commit_olustur(self, aciklama: str) -> Optional[str]:
        """
        Git commit oluşturur.
        
        Args:
            aciklama: Commit mesajı
            
        Returns:
            Commit hash'i
        """
        try:
            # Değişiklikleri stage'e al
            subprocess.run(
                ["git", "add", "."],
                cwd=self.proje_yolu,
                check=True,
                capture_output=True
            )
            
            # Commit oluştur
            commit_mesaji = f"Refactoring yedek: {aciklama}"
            result = subprocess.run(
                ["git", "commit", "-m", commit_mesaji],
                cwd=self.proje_yolu,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Commit hash'ini al
                hash_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.proje_yolu,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return hash_result.stdout.strip()
            else:
                self.logger.warning(f"Git commit başarısız: {result.stderr}")
                return None
                
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Git commit hatası: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Git işlemi hatası: {e}")
            return None
    
    def _dosya_yedegi_olustur(
        self,
        yedek_bilgisi: YedekBilgisi,
        hariç_tutulacaklar: List[str] = None
    ):
        """
        Dosya tabanlı yedek oluşturur.
        
        Args:
            yedek_bilgisi: Yedek bilgisi
            hariç_tutulacaklar: Hariç tutulacak dosya/klasör desenleri
        """
        yedek_yolu = Path(yedek_bilgisi.yedek_yolu)
        yedek_yolu.mkdir(parents=True, exist_ok=True)
        
        if hariç_tutulacaklar is None:
            hariç_tutulacaklar = [
                '__pycache__', '*.pyc', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis', '.refactoring_yedekler',
                '*.log', 'logs', '.coverage', 'htmlcov'
            ]
        
        def ignore_patterns(dir_path, names):
            ignored = []
            for name in names:
                for pattern in hariç_tutulacaklar:
                    if pattern in name or name.endswith(pattern.replace('*', '')):
                        ignored.append(name)
                        break
            return ignored
        
        # Proje dosyalarını kopyala
        proje_yedek_yolu = yedek_yolu / "proje"
        shutil.copytree(
            self.proje_yolu,
            proje_yedek_yolu,
            ignore=ignore_patterns
        )
        
        # İstatistikleri hesapla
        dosya_sayisi, toplam_boyut = self._yedek_istatistikleri_hesapla(proje_yedek_yolu)
        yedek_bilgisi.dosya_sayisi = dosya_sayisi
        yedek_bilgisi.toplam_boyut = toplam_boyut
        
        # Hash hesapla
        yedek_bilgisi.hash_degeri = self._yedek_hash_hesapla(proje_yedek_yolu)
        
        # Metadata dosyası oluştur
        metadata = {
            'yedek_id': yedek_bilgisi.yedek_id,
            'yedek_turu': yedek_bilgisi.yedek_turu.value,
            'olusturma_zamani': yedek_bilgisi.olusturma_zamani.isoformat(),
            'proje_yolu': yedek_bilgisi.proje_yolu,
            'git_commit_hash': yedek_bilgisi.git_commit_hash,
            'dosya_sayisi': yedek_bilgisi.dosya_sayisi,
            'toplam_boyut': yedek_bilgisi.toplam_boyut,
            'hash_degeri': yedek_bilgisi.hash_degeri,
            'aciklama': yedek_bilgisi.aciklama,
            'etiketler': yedek_bilgisi.etiketler
        }
        
        with open(yedek_yolu / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _yedek_istatistikleri_hesapla(self, yedek_yolu: Path) -> tuple[int, int]:
        """
        Yedek istatistiklerini hesaplar.
        
        Returns:
            (dosya_sayisi, toplam_boyut)
        """
        dosya_sayisi = 0
        toplam_boyut = 0
        
        for dosya in yedek_yolu.rglob('*'):
            if dosya.is_file():
                dosya_sayisi += 1
                toplam_boyut += dosya.stat().st_size
        
        return dosya_sayisi, toplam_boyut
    
    def _yedek_hash_hesapla(self, yedek_yolu: Path) -> str:
        """Yedek klasörünün hash değerini hesaplar"""
        hash_md5 = hashlib.md5()
        
        for dosya in sorted(yedek_yolu.rglob('*')):
            if dosya.is_file():
                hash_md5.update(str(dosya.relative_to(yedek_yolu)).encode())
                with open(dosya, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def geri_al(self, yedek_id: str, dogrulama_yap: bool = True) -> GeriAlmaBilgisi:
        """
        Yedekten geri alma yapar.
        
        Args:
            yedek_id: Geri alınacak yedek ID'si
            dogrulama_yap: Hash doğrulaması yapılsın mı
            
        Returns:
            Geri alma bilgisi
        """
        geri_alma_id = f"geri_alma_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.logger.info(f"Geri alma başlatılıyor: {yedek_id}")
        
        try:
            # Yedek bilgisini al
            if yedek_id not in self.yedek_kayitlari:
                raise ValueError(f"Yedek bulunamadı: {yedek_id}")
            
            yedek_bilgisi = self.yedek_kayitlari[yedek_id]
            yedek_yolu = Path(yedek_bilgisi.yedek_yolu)
            proje_yedek_yolu = yedek_yolu / "proje"
            
            if not proje_yedek_yolu.exists():
                raise FileNotFoundError(f"Yedek dosyaları bulunamadı: {proje_yedek_yolu}")
            
            # Hash doğrulaması
            if dogrulama_yap and yedek_bilgisi.hash_degeri:
                mevcut_hash = self._yedek_hash_hesapla(proje_yedek_yolu)
                if mevcut_hash != yedek_bilgisi.hash_degeri:
                    self.logger.warning(f"Yedek hash uyumsuzluğu: {yedek_id}")
            
            # Acil durum yedegi oluştur
            acil_yedek = self.yedek_olustur(
                yedek_turu=YedekTuru.ACIL_DURUM,
                aciklama=f"Geri alma öncesi acil yedek: {yedek_id}"
            )
            
            # Git ile geri alma (varsa)
            git_basarili = False
            if self.git_mevcut and yedek_bilgisi.git_commit_hash:
                git_basarili = self._git_geri_al(yedek_bilgisi.git_commit_hash)
            
            # Dosya tabanlı geri alma (git başarısız ise veya git yoksa)
            if not git_basarili:
                self._dosya_geri_alma(proje_yedek_yolu)
            
            geri_alma_bilgisi = GeriAlmaBilgisi(
                geri_alma_id=geri_alma_id,
                yedek_id=yedek_id,
                geri_alma_zamani=datetime.now(),
                basarili=True
            )
            
            self.logger.info(f"Geri alma tamamlandı: {yedek_id}")
            return geri_alma_bilgisi
            
        except Exception as e:
            geri_alma_bilgisi = GeriAlmaBilgisi(
                geri_alma_id=geri_alma_id,
                yedek_id=yedek_id,
                geri_alma_zamani=datetime.now(),
                basarili=False,
                hata_mesaji=str(e)
            )
            
            self.logger.error(f"Geri alma hatası: {e}")
            return geri_alma_bilgisi
    
    def _git_geri_al(self, commit_hash: str) -> bool:
        """
        Git ile geri alma yapar.
        
        Args:
            commit_hash: Geri alınacak commit hash'i
            
        Returns:
            Başarı durumu
        """
        try:
            # Hard reset ile geri al
            subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                cwd=self.proje_yolu,
                check=True,
                capture_output=True
            )
            
            self.logger.info(f"Git geri alma başarılı: {commit_hash}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Git geri alma başarısız: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Git geri alma hatası: {e}")
            return False
    
    def _dosya_geri_alma(self, proje_yedek_yolu: Path):
        """
        Dosya tabanlı geri alma yapar.
        
        Args:
            proje_yedek_yolu: Yedek proje yolu
        """
        # Mevcut projeyi sil
        if self.proje_yolu.exists():
            shutil.rmtree(self.proje_yolu)
        
        # Yedekten geri yükle
        shutil.copytree(proje_yedek_yolu, self.proje_yolu)
    
    def yedek_listesi_al(
        self,
        yedek_turu: YedekTuru = None,
        etiket: str = None
    ) -> List[YedekBilgisi]:
        """
        Yedek listesini alır.
        
        Args:
            yedek_turu: Filtrelenecek yedek türü
            etiket: Filtrelenecek etiket
            
        Returns:
            Yedek listesi
        """
        yedekler = list(self.yedek_kayitlari.values())
        
        # Filtrele
        if yedek_turu:
            yedekler = [y for y in yedekler if y.yedek_turu == yedek_turu]
        
        if etiket:
            yedekler = [y for y in yedekler if etiket in y.etiketler]
        
        # Tarihe göre sırala (en yeni önce)
        yedekler.sort(key=lambda x: x.olusturma_zamani, reverse=True)
        
        return yedekler
    
    def yedek_sil(self, yedek_id: str, dosyalari_da_sil: bool = True) -> bool:
        """
        Yedek siler.
        
        Args:
            yedek_id: Silinecek yedek ID'si
            dosyalari_da_sil: Yedek dosyaları da silinsin mi
            
        Returns:
            Başarı durumu
        """
        try:
            if yedek_id not in self.yedek_kayitlari:
                return False
            
            yedek_bilgisi = self.yedek_kayitlari[yedek_id]
            
            # Dosyaları sil
            if dosyalari_da_sil:
                yedek_yolu = Path(yedek_bilgisi.yedek_yolu)
                if yedek_yolu.exists():
                    shutil.rmtree(yedek_yolu)
            
            # Kayıttan çıkar
            yedek_bilgisi.durum = YedekDurumu.SILINDI
            del self.yedek_kayitlari[yedek_id]
            self._kayitlari_kaydet()
            
            self.logger.info(f"Yedek silindi: {yedek_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Yedek silme hatası: {e}")
            return False
    
    def otomatik_temizlik(self, gun_sayisi: int = 7, maksimum_yedek: int = 10):
        """
        Otomatik yedek temizliği yapar.
        
        Args:
            gun_sayisi: Kaç günden eski yedekler silinecek
            maksimum_yedek: Maksimum tutulacak yedek sayısı
        """
        self.logger.info("Otomatik yedek temizliği başlatılıyor...")
        
        kesim_tarihi = datetime.now().replace(hour=0, minute=0, second=0)
        kesim_tarihi = kesim_tarihi.replace(day=kesim_tarihi.day - gun_sayisi)
        
        # Eski yedekleri sil
        eski_yedekler = [
            yedek for yedek in self.yedek_kayitlari.values()
            if yedek.olusturma_zamani < kesim_tarihi
            and yedek.yedek_turu == YedekTuru.OTOMATIK
        ]
        
        for yedek in eski_yedekler:
            self.yedek_sil(yedek.yedek_id)
        
        # Fazla yedekleri sil (en eskiler)
        tum_yedekler = sorted(
            self.yedek_kayitlari.values(),
            key=lambda x: x.olusturma_zamani,
            reverse=True
        )
        
        if len(tum_yedekler) > maksimum_yedek:
            fazla_yedekler = tum_yedekler[maksimum_yedek:]
            for yedek in fazla_yedekler:
                if yedek.yedek_turu == YedekTuru.OTOMATIK:
                    self.yedek_sil(yedek.yedek_id)
        
        self.logger.info(f"Temizlik tamamlandı: {len(eski_yedekler)} yedek silindi")
    
    def yedek_test_et(self, yedek_id: str) -> bool:
        """
        Yedek bütünlüğünü test eder.
        
        Args:
            yedek_id: Test edilecek yedek ID'si
            
        Returns:
            Test sonucu
        """
        try:
            if yedek_id not in self.yedek_kayitlari:
                return False
            
            yedek_bilgisi = self.yedek_kayitlari[yedek_id]
            yedek_yolu = Path(yedek_bilgisi.yedek_yolu)
            proje_yedek_yolu = yedek_yolu / "proje"
            
            # Dosyalar mevcut mu?
            if not proje_yedek_yolu.exists():
                return False
            
            # Hash kontrolü
            if yedek_bilgisi.hash_degeri:
                mevcut_hash = self._yedek_hash_hesapla(proje_yedek_yolu)
                if mevcut_hash != yedek_bilgisi.hash_degeri:
                    return False
            
            # Python dosyalarının syntax kontrolü
            for py_dosya in proje_yedek_yolu.rglob('*.py'):
                try:
                    with open(py_dosya, 'r', encoding='utf-8') as f:
                        compile(f.read(), str(py_dosya), 'exec')
                except SyntaxError:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Yedek test hatası: {e}")
            return False