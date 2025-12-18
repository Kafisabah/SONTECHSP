# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.rapor_uretici
# Description: Audit rapor üretimi
# Changelog:
# - İlk versiyon: Audit rapor üretici

"""
Audit Rapor Üreticisi

Audit kayıtlarından raporlar üretir.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .veri_yapilari import IslemDurumu


class AuditRaporUreticisi:
    """
    Audit Rapor Üreticisi
    
    Audit kayıtlarından çeşitli raporlar üretir.
    """
    
    def __init__(self, audit_db_yolu: str):
        """
        Args:
            audit_db_yolu: Audit veritabanı dosya yolu
        """
        self.audit_db_yolu = Path(audit_db_yolu)
    
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