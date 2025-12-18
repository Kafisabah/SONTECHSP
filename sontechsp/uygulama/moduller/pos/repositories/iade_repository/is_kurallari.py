# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.iade_repository.is_kurallari
# Description: İade iş kuralları
# Changelog:
# - Refactoring: Ana dosyadan iş kuralları ayrıldı

"""
İade İş Kuralları

Bu modül iade iş kuralları ve doğrulama işlemlerini yönetir.
Orijinal satış doğrulama ve iade edilebilirlik kontrolü sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.arayuzler import SatisDurum
from sontechsp.uygulama.moduller.pos.database.models.iade import Iade
from sontechsp.uygulama.moduller.pos.database.models.satis import Satis
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class IsKurallari:
    """
    İade iş kuralları sınıfı
    
    İade iş kuralları ve doğrulama işlemlerini yönetir.
    """
    
    def orijinal_satis_dogrula(self, satis_id: int) -> Dict[str, Any]:
        """
        Orijinal satışı doğrular ve iade edilebilirlik kontrolü yapar
        
        Args:
            satis_id: Satış kimliği
            
        Returns:
            Satış bilgileri ve iade edilebilirlik durumu
            
        Raises:
            DogrulamaHatasi: Geçersiz satış ID
            SontechHatasi: Satış bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if satis_id <= 0:
            raise DogrulamaHatasi("Satış ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                satis = session.query(Satis).filter(Satis.id == satis_id).first()
                if not satis:
                    raise SontechHatasi(f"Satış bulunamadı: {satis_id}")
                
                # Mevcut iadeleri kontrol et
                mevcut_iadeler = session.query(Iade).filter(
                    Iade.orijinal_satis_id == satis_id
                ).all()
                
                toplam_iade_tutari = sum(iade.toplam_tutar for iade in mevcut_iadeler)
                
                # İade edilebilirlik kontrolü
                iade_edilebilir = (
                    satis.durum == SatisDurum.TAMAMLANDI and
                    toplam_iade_tutari < satis.net_tutar_hesapla()
                )
                
                return {
                    'satis_id': satis.id,
                    'fis_no': satis.fis_no,
                    'satis_tarihi': satis.satis_tarihi.isoformat(),
                    'toplam_tutar': float(satis.toplam_tutar),
                    'indirim_tutari': float(satis.indirim_tutari),
                    'net_tutar': float(satis.net_tutar_hesapla()),
                    'durum': satis.durum.value,
                    'iade_edilebilir': iade_edilebilir,
                    'toplam_iade_tutari': float(toplam_iade_tutari),
                    'kalan_iade_tutari': float(satis.net_tutar_hesapla() - toplam_iade_tutari),
                    'mevcut_iade_sayisi': len(mevcut_iadeler)
                }
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Orijinal satış doğrulama hatası: {str(e)}")