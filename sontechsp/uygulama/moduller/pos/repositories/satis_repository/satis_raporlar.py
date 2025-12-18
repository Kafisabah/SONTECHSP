# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.satis_repository.satis_raporlar
# Description: Satış rapor işlemleri
# Changelog:
# - Refactoring: Ana dosyadan rapor işlemleri ayrıldı

"""
Satış Rapor İşlemleri

Bu modül satış raporları ve özet işlemlerini yönetir.
Günlük özetler, istatistikler ve analiz raporları sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.arayuzler import SatisDurum
from sontechsp.uygulama.moduller.pos.database.models.satis import Satis
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi
)


class SatisRaporlar:
    """
    Satış rapor işlemleri sınıfı
    
    Satış raporları ve özet işlemlerini yönetir.
    """
    
    def gunluk_satis_ozeti(self, terminal_id: int, tarih: datetime) -> Dict[str, Any]:
        """
        Günlük satış özetini getirir
        
        Args:
            terminal_id: Terminal kimliği
            tarih: Özet tarihi
            
        Returns:
            Günlük satış özeti
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if terminal_id <= 0:
            raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                # Günün başı ve sonu
                gun_baslangic = tarih.replace(hour=0, minute=0, second=0, microsecond=0)
                gun_bitis = tarih.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                # Tamamlanan satışları getir
                satislar = session.query(Satis).filter(
                    and_(
                        Satis.terminal_id == terminal_id,
                        Satis.satis_tarihi >= gun_baslangic,
                        Satis.satis_tarihi <= gun_bitis,
                        Satis.durum == SatisDurum.TAMAMLANDI
                    )
                ).all()
                
                # Özet hesapla
                toplam_satis_sayisi = len(satislar)
                toplam_tutar = sum(satis.net_tutar_hesapla() for satis in satislar)
                toplam_indirim = sum(satis.indirim_tutari for satis in satislar)
                
                # Ödeme türü bazında özet
                odeme_ozeti = {}
                for satis in satislar:
                    for odeme in satis.odemeler:
                        turu = odeme.odeme_turu.value
                        if turu not in odeme_ozeti:
                            odeme_ozeti[turu] = {'adet': 0, 'tutar': 0.0}
                        odeme_ozeti[turu]['adet'] += 1
                        odeme_ozeti[turu]['tutar'] += float(odeme.tutar)
                
                return {
                    'tarih': tarih.date().isoformat(),
                    'terminal_id': terminal_id,
                    'toplam_satis_sayisi': toplam_satis_sayisi,
                    'toplam_tutar': float(toplam_tutar),
                    'toplam_indirim': float(toplam_indirim),
                    'net_tutar': float(toplam_tutar),
                    'odeme_ozeti': odeme_ozeti
                }
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Günlük özet hatası: {str(e)}")