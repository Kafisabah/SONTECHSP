# Version: 0.1.0
# Last Update: 2024-12-17
# Module: raporlar.sorgular
# Description: Raporlama modülü optimize edilmiş veritabanı sorguları
# Changelog:
# - İlk oluşturma
# - Satış özeti sorgusu eklendi
# - Kritik stok sorgusu eklendi
# - En çok satan ürünler sorgusu eklendi
# - Karlılık sorgusu placeholder eklendi

"""
SONTECHSP Raporlar Sorgu Katmanı

Bu modül raporlama sisteminin optimize edilmiş veritabanı sorgularını içerir:
- Satış özeti sorguları
- Kritik stok sorguları
- Ürün performans sorguları
- Karlılık sorguları (MVP placeholder)

Tüm sorgular salt okunur oturum kullanır ve performans optimizasyonu içerir.
"""

import logging
import time
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from decimal import Decimal

from .dto import TarihAraligiDTO
from .sabitler import SatisDurumu, RaporSabitleri, LogMesajlari

logger = logging.getLogger(__name__)


def satis_ozeti(session: Session, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> Dict:
    """
    Mağaza bazında satış özeti sorgusu
    
    Args:
        session: Salt okunur veritabanı oturumu
        magaza_id: Mağaza ID
        tarih_araligi: Tarih aralığı DTO
        
    Returns:
        Dict: Satış özeti verileri
        
    Raises:
        Exception: Sorgu hatası durumunda
    """
    baslangic_zamani = time.time()
    
    try:
        # Optimize edilmiş satış özeti sorgusu
        sorgu = text("""
            SELECT 
                COALESCE(SUM(brut_tutar), 0) as brut_satis,
                COALESCE(SUM(indirim_tutar), 0) as indirim_toplam,
                COALESCE(SUM(net_tutar), 0) as net_satis,
                COUNT(*) as satis_adedi,
                COALESCE(SUM(CASE WHEN durum = 'IADE' THEN net_tutar ELSE 0 END), 0) as iade_toplam
            FROM pos_satislar 
            WHERE magaza_id = :magaza_id 
                AND durum = :durum
                AND tarih BETWEEN :baslangic AND :bitis
        """)
        
        sonuc = session.execute(sorgu, {
            'magaza_id': magaza_id,
            'durum': SatisDurumu.TAMAMLANDI.value,
            'baslangic': tarih_araligi.baslangic_tarihi,
            'bitis': tarih_araligi.bitis_tarihi
        }).fetchone()
        
        # Performans loglaması
        gecen_sure = (time.time() - baslangic_zamani) * 1000
        if gecen_sure > RaporSabitleri.YAVAS_SORGU_ESIGI_SANIYE * 1000:
            logger.warning(LogMesajlari.YAVAS_SORGU_UYARISI.format(gecen_sure, "satis_ozeti"))
        
        if sonuc:
            return {
                'brut_satis': Decimal(str(sonuc.brut_satis or 0)),
                'indirim_toplam': Decimal(str(sonuc.indirim_toplam or 0)),
                'net_satis': Decimal(str(sonuc.net_satis or 0)),
                'satis_adedi': int(sonuc.satis_adedi or 0),
                'iade_toplam': Decimal(str(sonuc.iade_toplam or 0))
            }
        else:
            # Veri bulunamadığında sıfır değerler döndür
            return {
                'brut_satis': Decimal('0'),
                'indirim_toplam': Decimal('0'),
                'net_satis': Decimal('0'),
                'satis_adedi': 0,
                'iade_toplam': Decimal('0')
            }
            
    except Exception as e:
        logger.error(f"Satış özeti sorgu hatası: {e}")
        raise


def kritik_stok_listesi(session: Session, depo_id: Optional[int] = None) -> List[Dict]:
    """
    Kritik stok seviyesindeki ürünler sorgusu
    
    Args:
        session: Salt okunur veritabanı oturumu
        depo_id: Opsiyonel depo ID filtresi
        
    Returns:
        List[Dict]: Kritik stok ürün listesi
        
    Raises:
        Exception: Sorgu hatası durumunda
    """
    baslangic_zamani = time.time()
    
    try:
        # Temel sorgu
        sorgu_metni = """
            SELECT 
                u.id as urun_id,
                u.ad as urun_adi,
                sb.depo_id,
                sb.miktar,
                u.kritik_seviye
            FROM urunler u
            INNER JOIN stok_bakiyeleri sb ON u.id = sb.urun_id
            WHERE sb.miktar <= u.kritik_seviye
        """
        
        parametreler = {}
        
        # Depo filtresi ekle
        if depo_id is not None:
            sorgu_metni += " AND sb.depo_id = :depo_id"
            parametreler['depo_id'] = depo_id
            
        sorgu_metni += " ORDER BY sb.miktar ASC, u.ad ASC"
        
        sorgu = text(sorgu_metni)
        sonuclar = session.execute(sorgu, parametreler).fetchall()
        
        # Performans loglaması
        gecen_sure = (time.time() - baslangic_zamani) * 1000
        if gecen_sure > RaporSabitleri.YAVAS_SORGU_ESIGI_SANIYE * 1000:
            logger.warning(LogMesajlari.YAVAS_SORGU_UYARISI.format(gecen_sure, "kritik_stok_listesi"))
        
        # Sonuçları dict listesine çevir
        return [
            {
                'urun_id': int(row.urun_id),
                'urun_adi': str(row.urun_adi),
                'depo_id': int(row.depo_id),
                'miktar': int(row.miktar),
                'kritik_seviye': int(row.kritik_seviye)
            }
            for row in sonuclar
        ]
        
    except Exception as e:
        logger.error(f"Kritik stok sorgu hatası: {e}")
        raise


def en_cok_satan_urunler(session: Session, magaza_id: int, tarih_araligi: TarihAraligiDTO, limit: int = 20) -> List[Dict]:
    """
    En çok satan ürünler sorgusu
    
    Args:
        session: Salt okunur veritabanı oturumu
        magaza_id: Mağaza ID
        tarih_araligi: Tarih aralığı DTO
        limit: Sonuç limiti
        
    Returns:
        List[Dict]: En çok satan ürün listesi
        
    Raises:
        Exception: Sorgu hatası durumunda
    """
    baslangic_zamani = time.time()
    
    try:
        sorgu = text("""
            SELECT 
                u.id as urun_id,
                u.ad as urun_adi,
                SUM(pss.miktar) as miktar_toplam,
                SUM(pss.tutar) as ciro_toplam
            FROM pos_satis_satirlari pss
            INNER JOIN pos_satislar ps ON pss.satis_id = ps.id
            INNER JOIN urunler u ON pss.urun_id = u.id
            WHERE ps.magaza_id = :magaza_id
                AND ps.durum = :durum
                AND ps.tarih BETWEEN :baslangic AND :bitis
            GROUP BY u.id, u.ad
            ORDER BY miktar_toplam DESC, ciro_toplam DESC
            LIMIT :limit
        """)
        
        sonuclar = session.execute(sorgu, {
            'magaza_id': magaza_id,
            'durum': SatisDurumu.TAMAMLANDI.value,
            'baslangic': tarih_araligi.baslangic_tarihi,
            'bitis': tarih_araligi.bitis_tarihi,
            'limit': limit
        }).fetchall()
        
        # Performans loglaması
        gecen_sure = (time.time() - baslangic_zamani) * 1000
        if gecen_sure > RaporSabitleri.YAVAS_SORGU_ESIGI_SANIYE * 1000:
            logger.warning(LogMesajlari.YAVAS_SORGU_UYARISI.format(gecen_sure, "en_cok_satan_urunler"))
        
        # Sonuçları dict listesine çevir
        return [
            {
                'urun_id': int(row.urun_id),
                'urun_adi': str(row.urun_adi),
                'miktar_toplam': int(row.miktar_toplam or 0),
                'ciro_toplam': Decimal(str(row.ciro_toplam or 0))
            }
            for row in sonuclar
        ]
        
    except Exception as e:
        logger.error(f"En çok satan ürünler sorgu hatası: {e}")
        raise


def karlilik_ozeti(session: Session, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> List[Dict]:
    """
    Karlılık özeti sorgusu (MVP placeholder)
    
    Args:
        session: Salt okunur veritabanı oturumu
        magaza_id: Mağaza ID
        tarih_araligi: Tarih aralığı DTO
        
    Returns:
        List[Dict]: Karlılık özeti verileri (placeholder)
        
    Note:
        Bu fonksiyon MVP'de placeholder olarak çalışır
    """
    logger.warning(LogMesajlari.MVP_PLACEHOLDER_UYARISI.format("karlilik_ozeti"))
    
    try:
        # MVP için basit ürün listesi döndür
        sorgu = text("""
            SELECT 
                u.id as urun_id,
                u.ad as urun_adi,
                0 as maliyet,
                0 as kar_marji,
                0 as kar_tutari
            FROM urunler u
            LIMIT 10
        """)
        
        sonuclar = session.execute(sorgu).fetchall()
        
        return [
            {
                'urun_id': int(row.urun_id),
                'urun_adi': str(row.urun_adi),
                'maliyet': Decimal('0'),
                'kar_marji': Decimal('0'),
                'kar_tutari': Decimal('0')
            }
            for row in sonuclar
        ]
        
    except Exception as e:
        logger.error(f"Karlılık özeti sorgu hatası: {e}")
        raise