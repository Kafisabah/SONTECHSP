# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.audit_db
# Description: Audit veritabanı yönetimi
# Changelog:
# - İlk versiyon: Audit veritabanı işlemleri

"""
Audit Veritabanı Yöneticisi

Audit kayıtlarının veritabanı işlemlerini yönetir.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .veri_yapilari import IslemKaydi, BackupBilgisi


class AuditDbYoneticisi:
    """
    Audit Veritabanı Yöneticisi
    
    Audit kayıtlarının SQLite veritabanında saklanması
    ve sorgulanması işlemlerini yönetir.
    """
    
    def __init__(self, audit_db_yolu: str):
        """
        Args:
            audit_db_yolu: Audit veritabanı dosya yolu
        """
        self.audit_db_yolu = Path(audit_db_yolu)
        self._audit_db_baslat()
    
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
    
    def islem_kaydi_ekle(self, islem: IslemKaydi):
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
    
    def islem_kaydi_guncelle(self, islem: IslemKaydi):
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
    
    def backup_kaydet(self, backup_bilgi: BackupBilgisi):
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
    
    def backup_al(self, backup_id: str) -> Optional[BackupBilgisi]:
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