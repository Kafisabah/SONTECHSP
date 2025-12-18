# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.iade_repository.raporlar
# Description: İade rapor işlemleri
# Changelog:
# - Refactoring: Ana dosyadan rapor işlemleri ayrıldı

"""
İade Rapor İşlemleri

Bu modül iade raporları ve listeleme işlemlerini yönetir.
İade listesi, filtreleme ve rapor operasyonları sağlar.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.database.models.iade import Iade
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi
)


class Raporlar:
    """
    İade rapor işlemleri sınıfı
    
    İade raporları ve listeleme operasyonlarını yönetir.
    """
    
    def iade_listesi_getir(self, terminal_id: Optional[int] = None,
                          kasiyer_id: Optional[int] = None,
                          baslangic_tarihi: Optional[datetime] = None,
                          bitis_tarihi: Optional[datetime] = None,
                          limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        İade listesini getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            kasiyer_id: Kasiyer kimliği (opsiyonel)
            baslangic_tarihi: Başlangıç tarihi (opsiyonel)
            bitis_tarihi: Bitiş tarihi (opsiyonel)
            limit: Maksimum kayıt sayısı
            offset: Başlangıç offset'i
            
        Returns:
            İade listesi
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if limit <= 0 or limit > 1000:
            raise DogrulamaHatasi("Limit 1-1000 arasında olmalıdır")
        
        if offset < 0:
            raise DogrulamaHatasi("Offset negatif olamaz")
        
        with postgresql_session() as session:
            try:
                query = session.query(Iade).options(joinedload(Iade.satirlar))
                
                # Filtreleri uygula
                if terminal_id:
                    query = query.filter(Iade.terminal_id == terminal_id)
                
                if kasiyer_id:
                    query = query.filter(Iade.kasiyer_id == kasiyer_id)
                
                if baslangic_tarihi:
                    query = query.filter(Iade.iade_tarihi >= baslangic_tarihi)
                
                if bitis_tarihi:
                    query = query.filter(Iade.iade_tarihi <= bitis_tarihi)
                
                # Sıralama ve sayfalama
                query = query.order_by(desc(Iade.iade_tarihi))
                query = query.offset(offset).limit(limit)
                
                iadeler = query.all()
                
                # Dict formatına çevir
                sonuc = []
                for iade in iadeler:
                    iade_dict = {
                        'id': iade.id,
                        'orijinal_satis_id': iade.orijinal_satis_id,
                        'terminal_id': iade.terminal_id,
                        'kasiyer_id': iade.kasiyer_id,
                        'iade_tarihi': iade.iade_tarihi.isoformat(),
                        'toplam_tutar': float(iade.toplam_tutar),
                        'neden': iade.neden,
                        'fis_no': iade.fis_no,
                        'musteri_id': iade.musteri_id,
                        'satir_sayisi': iade.satir_sayisi(),
                        'toplam_adet': iade.toplam_adet()
                    }
                    sonuc.append(iade_dict)
                
                return sonuc
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"İade listesi getirme hatası: {str(e)}")