# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.guvenlik_sistemi
# Description: Güvenlik ve geri alma sistemi
# Changelog:
# - İlk versiyon: GuvenlikSistemi sınıfı oluşturuldu

"""
Güvenlik Sistemi

Refactoring işlemleri için güvenlik, backup ve geri alma
mekanizmalarını sağlar. İşlem logları ve audit trail sistemi içerir.
"""

import json
import logging
import os
import shutil
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class IslemTuru(Enum):
    """İşlem türleri"""
    BACKUP_OLUSTUR = "backup_olustur"
    DOSYA_BOL = "dosya_bol"
    FONKSIYON_BOL = "fonksiyon_bol"
    IMPORT_DUZENLE = "import_duzenle"
    BASLIK_EKLE = "baslik_ekle"
    GERI_AL = "geri_al"
    DOGRULA = "dogrula"


class IslemDurumu(Enum):
    """İşlem durumları"""
    BASLADI = "basladi"
    DEVAM_EDIYOR = "devam_ediyor"
    TAMAMLANDI = "tamamlandi"
    HATA = "hata"
    GERI_ALINDI = "geri_alindi"


@dataclass
class IslemKaydi:
    """İşlem kaydı"""
    islem_id: str
    islem_turu: IslemTuru
    durum: IslemDurumu
    baslangic_zamani: datetime
    bitis_zamani: Optional[datetime] = None
    hedef_dosyalar: List[str] = field(default_factory=list)
    degisiklikler: Dict[str, Any] = field(default_factory=dict)
    hata_mesaji: Optional[str] = None
    kullanici: str = "sistem"
    backup_yolu: Optional[str] = None


@dataclass
class BackupBilgisi:
    """Backup bilgisi"""
    backup_id: str
    olusturma_zamani: datetime
    proje_yolu: str
    backup_yolu: str
    dosya_sayisi: int
    toplam_boyut: int
    hash_degeri: str
    aciklama: str = ""


class GuvenlikSistemi:
    """
    Güvenlik Sistemi
    
    Refactoring işlemleri için güvenlik önlemleri sağlar:
    - Backup ve restore mekanizması
    - İşlem logları ve audit trail
    - Dosya bütünlüğü kontrolü
    - Geri alma işlemleri
    """
    
    def __init__(
        self,
        proje_yolu: str,
        guvenlik_klasoru: str = None,
        log_seviyesi: int = logging.INFO
    ):
        """
        Args:
            proje_yolu: Korunacak proje yolu
            guvenlik_klasoru: Güvenlik dosyalarının saklanacağı klasör
            log_seviyesi: Log seviyesi
        """
        self.proje_yolu = Path(proje_yolu)
        self.guvenlik_klasoru = Path(
            guvenlik_klasoru or self.proje_yolu / ".guvenlik"
        )
        
        # Güvenlik klasörünü oluştur
        self.guvenlik_klasoru.mkdir(parents=True, exist_ok=True)
        
        # Alt klasörleri oluştur
        self.backup_klasoru = self.guvenlik_klasoru / "backups"
        self.log_klasoru = self.guvenlik_klasoru / "logs"
        self.audit_klasoru = self.guvenlik_klasoru / "audit"
        
        for klasor in [self.backup_klasoru, self.log_klasoru, self.audit_klasoru]:
            klasor.mkdir(exist_ok=True)
        
        # Logger kurulumu
        self.logger = self._logger_kurulumu(log_seviyesi)
        
        # Audit veritabanını başlat
        self.audit_db_yolu = self.audit_klasoru / "audit.db"
        self._audit_db_baslat()
        
        # Aktif işlemler
        self.aktif_islemler: Dict[str, IslemKaydi] = {}
        
        self.logger.info(f"GuvenlikSistemi başlatıldı: {self.proje_yolu}")
    
    def _logger_kurulumu(self, log_seviyesi: int) -> logging.Logger:
        """Logger kurulumu yapar"""
        logger = logging.getLogger(f"GuvenlikSistemi_{id(self)}")
        logger.setLevel(log_seviyesi)
        
        if not logger.handlers:
            # Dosya handler
            log_dosyasi = self.log_klasoru / f"guvenlik_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_dosyasi, encoding='utf-8')
            file_handler.setLevel(log_seviyesi)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_seviyesi)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _audit_db_baslat(self):
        """Audit veritabanını başlatır"""
        with sqlite3.connect(self.audit_db_yolu) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS islem_kayitlari (
                    islem_id TEXT PRIMARY KEY,
                    islem_turu TEXT NOT NULL,
                    durum TEXT NOT NULL,
                    baslangic_zamani TEXT NOT NULL,
                    bitis_zamani TEXT,
                    hedef_dosyalar TEXT,
                    degisiklikler TEXT,
                    hata_mesaji TEXT,
                    kullanici TEXT,
                    backup_yolu TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS backup_kayitlari (
                    backup_id TEXT PRIMARY KEY,
                    olusturma_zamani TEXT NOT NULL,
                    proje_yolu TEXT NOT NULL,
                    backup_yolu TEXT NOT NULL,
                    dosya_sayisi INTEGER,
                    toplam_boyut INTEGER,
                    hash_degeri TEXT,
                    aciklama TEXT
                )
            ''')
            
            conn.commit()
    
    def backup_olustur(
        self,
        aciklama: str = "",
        hariç_tutulacaklar: List[str] = None
    ) -> BackupBilgisi:
        """
        Proje backup'ı oluşturur.
        
        Args:
            aciklama: Backup açıklaması
            hariç_tutulacaklar: Hariç tutulacak dosya/klasör desenleri
            
        Returns:
            Backup bilgisi
        """
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        islem_id = self._islem_baslat(IslemTuru.BACKUP_OLUSTUR, [str(self.proje_yolu)])
        
        try:
            self.logger.info(f"Backup oluşturuluyor: {backup_id}")
            
            # Backup klasörü oluştur
            backup_yolu = self.backup_klasoru / backup_id
            backup_yolu.mkdir(exist_ok=True)
            
            # Proje dosyalarını kopyala
            if hariç_tutulacaklar is None:
                hariç_tutulacaklar = [
                    '__pycache__', '*.pyc', '.git', '.pytest_cache',
                    'venv', 'env', '.hypothesis', '.guvenlik'
                ]
            
            dosya_sayisi, toplam_boyut = self._proje_kopyala(
                self.proje_yolu,
                backup_yolu / "proje",
                hariç_tutulacaklar
            )
            
            # Hash hesapla
            hash_degeri = self._backup_hash_hesapla(backup_yolu / "proje")
            
            # Backup bilgilerini kaydet
            backup_bilgi = BackupBilgisi(
                backup_id=backup_id,
                olusturma_zamani=datetime.now(),
                proje_yolu=str(self.proje_yolu),
                backup_yolu=str(backup_yolu),
                dosya_sayisi=dosya_sayisi,
                toplam_boyut=toplam_boyut,
                hash_degeri=hash_degeri,
                aciklama=aciklama
            )
            
            self._backup_bilgisini_kaydet(backup_bilgi)
            
            # Metadata dosyası oluştur
            metadata = {
                'backup_id': backup_id,
                'olusturma_zamani': backup_bilgi.olusturma_zamani.isoformat(),
                'proje_yolu': str(self.proje_yolu),
                'dosya_sayisi': dosya_sayisi,
                'toplam_boyut': toplam_boyut,
                'hash_degeri': hash_degeri,
                'aciklama': aciklama
            }
            
            with open(backup_yolu / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self._islem_tamamla(islem_id, backup_yolu=str(backup_yolu))
            self.logger.info(f"Backup oluşturuldu: {backup_yolu}")
            
            return backup_bilgi
            
        except Exception as e:
            self._islem_hata(islem_id, str(e))
            self.logger.error(f"Backup oluşturma hatası: {e}")
            raise
    
    def _proje_kopyala(
        self,
        kaynak: Path,
        hedef: Path,
        hariç_tutulacaklar: List[str]
    ) -> tuple[int, int]:
        """
        Proje dosyalarını kopyalar.
        
        Returns:
            (dosya_sayisi, toplam_boyut)
        """
        dosya_sayisi = 0
        toplam_boyut = 0
        
        def ignore_patterns(dir_path, names):
            ignored = []
            for name in names:
                for pattern in hariç_tutulacaklar:
                    if pattern in name or name.endswith(pattern.replace('*', '')):
                        ignored.append(name)
                        break
            return ignored
        
        shutil.copytree(
            kaynak,
            hedef,
            ignore=ignore_patterns
        )
        
        # Dosya sayısı ve boyut hesapla
        for dosya in hedef.rglob('*'):
            if dosya.is_file():
                dosya_sayisi += 1
                toplam_boyut += dosya.stat().st_size
        
        return dosya_sayisi, toplam_boyut
    
    def _backup_hash_hesapla(self, backup_yolu: Path) -> str:
        """Backup klasörünün hash değerini hesaplar"""
        hash_md5 = hashlib.md5()
        
        for dosya in sorted(backup_yolu.rglob('*')):
            if dosya.is_file():
                hash_md5.update(str(dosya.relative_to(backup_yolu)).encode())
                with open(dosya, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def geri_al(self, backup_id: str) -> bool:
        """
        Backup'tan geri alma yapar.
        
        Args:
            backup_id: Geri alınacak backup ID'si
            
        Returns:
            Başarı durumu
        """
        islem_id = self._islem_baslat(IslemTuru.GERI_AL, [backup_id])
        
        try:
            self.logger.info(f"Geri alma başlatılıyor: {backup_id}")
            
            # Backup bilgisini al
            backup_bilgi = self._backup_bilgisini_al(backup_id)
            if not backup_bilgi:
                raise ValueError(f"Backup bulunamadı: {backup_id}")
            
            backup_yolu = Path(backup_bilgi.backup_yolu)
            proje_backup_yolu = backup_yolu / "proje"
            
            if not proje_backup_yolu.exists():
                raise FileNotFoundError(f"Backup dosyaları bulunamadı: {proje_backup_yolu}")
            
            # Hash kontrolü
            mevcut_hash = self._backup_hash_hesapla(proje_backup_yolu)
            if mevcut_hash != backup_bilgi.hash_degeri:
                self.logger.warning(f"Backup hash uyumsuzluğu: {backup_id}")
            
            # Mevcut projeyi yedekle (güvenlik için)
            acil_backup = self.backup_olustur(f"Acil backup - geri alma öncesi: {backup_id}")
            
            # Mevcut projeyi sil
            if self.proje_yolu.exists():
                shutil.rmtree(self.proje_yolu)
            
            # Backup'tan geri yükle
            shutil.copytree(proje_backup_yolu, self.proje_yolu)
            
            self._islem_tamamla(islem_id)
            self.logger.info(f"Geri alma tamamlandı: {backup_id}")
            
            return True
            
        except Exception as e:
            self._islem_hata(islem_id, str(e))
            self.logger.error(f"Geri alma hatası: {e}")
            return False
    
    def dosya_butunlugu_kontrol_et(self, dosya_yolu: str) -> bool:
        """
        Dosya bütünlüğünü kontrol eder.
        
        Args:
            dosya_yolu: Kontrol edilecek dosya yolu
            
        Returns:
            Bütünlük durumu
        """
        try:
            dosya = Path(dosya_yolu)
            if not dosya.exists():
                return False
            
            # Dosya okunabilir mi?
            with open(dosya, 'r', encoding='utf-8') as f:
                f.read()
            
            # Python dosyası ise syntax kontrolü
            if dosya.suffix == '.py':
                with open(dosya, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(dosya), 'exec')
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Dosya bütünlük hatası {dosya_yolu}: {e}")
            return False
    
    def _islem_baslat(
        self,
        islem_turu: IslemTuru,
        hedef_dosyalar: List[str]
    ) -> str:
        """Yeni işlem başlatır"""
        islem_id = f"{islem_turu.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        islem_kaydi = IslemKaydi(
            islem_id=islem_id,
            islem_turu=islem_turu,
            durum=IslemDurumu.BASLADI,
            baslangic_zamani=datetime.now(),
            hedef_dosyalar=hedef_dosyalar
        )
        
        self.aktif_islemler[islem_id] = islem_kaydi
        self._audit_kaydi_ekle(islem_kaydi)
        
        return islem_id
    
    def _islem_tamamla(
        self,
        islem_id: str,
        degisiklikler: Dict[str, Any] = None,
        backup_yolu: str = None
    ):
        """İşlemi tamamlar"""
        if islem_id in self.aktif_islemler:
            islem = self.aktif_islemler[islem_id]
            islem.durum = IslemDurumu.TAMAMLANDI
            islem.bitis_zamani = datetime.now()
            
            if degisiklikler:
                islem.degisiklikler = degisiklikler
            
            if backup_yolu:
                islem.backup_yolu = backup_yolu
            
            self._audit_kaydi_guncelle(islem)
            del self.aktif_islemler[islem_id]
    
    def _islem_hata(self, islem_id: str, hata_mesaji: str):
        """İşlem hatasını kaydeder"""
        if islem_id in self.aktif_islemler:
            islem = self.aktif_islemler[islem_id]
            islem.durum = IslemDurumu.HATA
            islem.bitis_zamani = datetime.now()
            islem.hata_mesaji = hata_mesaji
            
            self._audit_kaydi_guncelle(islem)
            del self.aktif_islemler[islem_id]
    
    def _audit_kaydi_ekle(self, islem: IslemKaydi):
        """Audit kaydı ekler"""
        with sqlite3.connect(self.audit_db_yolu) as conn:
            conn.execute('''
                INSERT INTO islem_kayitlari 
                (islem_id, islem_turu, durum, baslangic_zamani, hedef_dosyalar, kullanici)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                islem.islem_id,
                islem.islem_turu.value,
                islem.durum.value,
                islem.baslangic_zamani.isoformat(),
                json.dumps(islem.hedef_dosyalar),
                islem.kullanici
            ))
            conn.commit()
    
    def _audit_kaydi_guncelle(self, islem: IslemKaydi):
        """Audit kaydını günceller"""
        with sqlite3.connect(self.audit_db_yolu) as conn:
            conn.execute('''
                UPDATE islem_kayitlari 
                SET durum = ?, bitis_zamani = ?, degisiklikler = ?, 
                    hata_mesaji = ?, backup_yolu = ?
                WHERE islem_id = ?
            ''', (
                islem.durum.value,
                islem.bitis_zamani.isoformat() if islem.bitis_zamani else None,
                json.dumps(islem.degisiklikler),
                islem.hata_mesaji,
                islem.backup_yolu,
                islem.islem_id
            ))
            conn.commit()
    
    def _backup_bilgisini_kaydet(self, backup_bilgi: BackupBilgisi):
        """Backup bilgisini veritabanına kaydeder"""
        with sqlite3.connect(self.audit_db_yolu) as conn:
            conn.execute('''
                INSERT INTO backup_kayitlari 
                (backup_id, olusturma_zamani, proje_yolu, backup_yolu, 
                 dosya_sayisi, toplam_boyut, hash_degeri, aciklama)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                backup_bilgi.backup_id,
                backup_bilgi.olusturma_zamani.isoformat(),
                backup_bilgi.proje_yolu,
                backup_bilgi.backup_yolu,
                backup_bilgi.dosya_sayisi,
                backup_bilgi.toplam_boyut,
                backup_bilgi.hash_degeri,
                backup_bilgi.aciklama
            ))
            conn.commit()
    
    def _backup_bilgisini_al(self, backup_id: str) -> Optional[BackupBilgisi]:
        """Backup bilgisini veritabanından alır"""
        with sqlite3.connect(self.audit_db_yolu) as conn:
            cursor = conn.execute('''
                SELECT * FROM backup_kayitlari WHERE backup_id = ?
            ''', (backup_id,))
            
            row = cursor.fetchone()
            if row:
                return BackupBilgisi(
                    backup_id=row[0],
                    olusturma_zamani=datetime.fromisoformat(row[1]),
                    proje_yolu=row[2],
                    backup_yolu=row[3],
                    dosya_sayisi=row[4],
                    toplam_boyut=row[5],
                    hash_degeri=row[6],
                    aciklama=row[7] or ""
                )
            return None
    
    def backup_listesi_al(self) -> List[BackupBilgisi]:
        """Tüm backup'ların listesini alır"""
        backuplar = []
        
        with sqlite3.connect(self.audit_db_yolu) as conn:
            cursor = conn.execute('''
                SELECT * FROM backup_kayitlari 
                ORDER BY olusturma_zamani DESC
            ''')
            
            for row in cursor.fetchall():
                backup = BackupBilgisi(
                    backup_id=row[0],
                    olusturma_zamani=datetime.fromisoformat(row[1]),
                    proje_yolu=row[2],
                    backup_yolu=row[3],
                    dosya_sayisi=row[4],
                    toplam_boyut=row[5],
                    hash_degeri=row[6],
                    aciklama=row[7] or ""
                )
                backuplar.append(backup)
        
        return backuplar
    
    def audit_raporu_olustur(
        self,
        baslangic_tarihi: datetime = None,
        bitis_tarihi: datetime = None
    ) -> Dict[str, Any]:
        """
        Audit raporu oluşturur.
        
        Args:
            baslangic_tarihi: Rapor başlangıç tarihi
            bitis_tarihi: Rapor bitiş tarihi
            
        Returns:
            Audit raporu
        """
        if baslangic_tarihi is None:
            baslangic_tarihi = datetime.now().replace(hour=0, minute=0, second=0)
        
        if bitis_tarihi is None:
            bitis_tarihi = datetime.now()
        
        rapor = {
            'rapor_tarihi': datetime.now().isoformat(),
            'baslangic_tarihi': baslangic_tarihi.isoformat(),
            'bitis_tarihi': bitis_tarihi.isoformat(),
            'toplam_islem': 0,
            'basarili_islem': 0,
            'basarisiz_islem': 0,
            'islem_turleri': {},
            'son_islemler': []
        }
        
        with sqlite3.connect(self.audit_db_yolu) as conn:
            # Toplam istatistikler
            cursor = conn.execute('''
                SELECT durum, COUNT(*) FROM islem_kayitlari 
                WHERE baslangic_zamani BETWEEN ? AND ?
                GROUP BY durum
            ''', (baslangic_tarihi.isoformat(), bitis_tarihi.isoformat()))
            
            for durum, sayi in cursor.fetchall():
                rapor['toplam_islem'] += sayi
                if durum == IslemDurumu.TAMAMLANDI.value:
                    rapor['basarili_islem'] = sayi
                elif durum == IslemDurumu.HATA.value:
                    rapor['basarisiz_islem'] = sayi
            
            # İşlem türleri
            cursor = conn.execute('''
                SELECT islem_turu, COUNT(*) FROM islem_kayitlari 
                WHERE baslangic_zamani BETWEEN ? AND ?
                GROUP BY islem_turu
            ''', (baslangic_tarihi.isoformat(), bitis_tarihi.isoformat()))
            
            for turu, sayi in cursor.fetchall():
                rapor['islem_turleri'][turu] = sayi
            
            # Son işlemler
            cursor = conn.execute('''
                SELECT * FROM islem_kayitlari 
                WHERE baslangic_zamani BETWEEN ? AND ?
                ORDER BY baslangic_zamani DESC
                LIMIT 10
            ''', (baslangic_tarihi.isoformat(), bitis_tarihi.isoformat()))
            
            for row in cursor.fetchall():
                islem = {
                    'islem_id': row[0],
                    'islem_turu': row[1],
                    'durum': row[2],
                    'baslangic_zamani': row[3],
                    'bitis_zamani': row[4],
                    'hata_mesaji': row[7]
                }
                rapor['son_islemler'].append(islem)
        
        return rapor
    
    def temizlik_yap(self, gun_sayisi: int = 30):
        """
        Eski backup ve log dosyalarını temizler.
        
        Args:
            gun_sayisi: Kaç günden eski dosyalar silinecek
        """
        kesim_tarihi = datetime.now().replace(hour=0, minute=0, second=0)
        kesim_tarihi = kesim_tarihi.replace(day=kesim_tarihi.day - gun_sayisi)
        
        self.logger.info(f"Temizlik başlatılıyor: {kesim_tarihi} öncesi")
        
        # Eski backup'ları sil
        with sqlite3.connect(self.audit_db_yolu) as conn:
            cursor = conn.execute('''
                SELECT backup_id, backup_yolu FROM backup_kayitlari 
                WHERE olusturma_zamani < ?
            ''', (kesim_tarihi.isoformat(),))
            
            silinen_backup_sayisi = 0
            for backup_id, backup_yolu in cursor.fetchall():
                try:
                    if os.path.exists(backup_yolu):
                        shutil.rmtree(backup_yolu)
                    silinen_backup_sayisi += 1
                except Exception as e:
                    self.logger.warning(f"Backup silme hatası {backup_id}: {e}")
            
            # Veritabanından da sil
            conn.execute('''
                DELETE FROM backup_kayitlari 
                WHERE olusturma_zamani < ?
            ''', (kesim_tarihi.isoformat(),))
            
            conn.execute('''
                DELETE FROM islem_kayitlari 
                WHERE baslangic_zamani < ?
            ''', (kesim_tarihi.isoformat(),))
            
            conn.commit()
        
        self.logger.info(f"Temizlik tamamlandı: {silinen_backup_sayisi} backup silindi")