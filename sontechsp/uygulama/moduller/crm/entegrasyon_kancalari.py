# Version: 0.1.0
# Last Update: 2024-12-17
# Module: crm_entegrasyon_kancalari
# Description: CRM modülü entegrasyon hook'ları - diğer modüllerle etkileşim
# Changelog:
# - İlk oluşturma: POS ve satış belgeleri entegrasyon fonksiyonları iskelet
# - Servisler implement edildi, aktif hale getirildi

from typing import Optional
from sqlalchemy.orm import Session
from .servisler.crm_servisler import SadakatServisi
from .dto import PuanIslemDTO
from .sabitler import ReferansTuru, PUAN_HESAPLAMA_ORANI
from ...cekirdek.kayit import logger
from ...cekirdek.hatalar import DogrulamaHatasi, VeritabaniHatasi


def pos_satis_tamamlandi(
    db: Session,
    musteri_id: Optional[int],
    toplam_tutar: float,
    satis_id: int
) -> bool:
    """
    POS satış tamamlandığında müşteriye puan kazandırır
    
    Args:
        db: Veritabanı session
        musteri_id: Müşteri ID (None olabilir)
        toplam_tutar: Satış toplam tutarı
        satis_id: POS satış ID'si
    
    Returns:
        bool: İşlem başarılı ise True
    """
    try:
        # Müşteri yoksa sessizce atla
        if not musteri_id:
            return True
        
        # Puan hesapla (1 TL = 1 puan)
        puan = int(toplam_tutar * PUAN_HESAPLAMA_ORANI)
        
        if puan <= 0:
            return True
        
        # Puan kazanım işlemi
        dto = PuanIslemDTO(
            musteri_id=musteri_id,
            puan=puan,
            aciklama=f"POS Satış - Tutar: {toplam_tutar} TL",
            referans_turu=ReferansTuru.POS_SATIS,
            referans_id=satis_id
        )
        
        # Sadakat servisi ile puan kazandır
        sadakat_servisi = SadakatServisi(db)
        sadakat_servisi.puan_kazan(dto)
        
        logger.info(f"POS satış puan kazanımı: Müşteri {musteri_id}, Puan {puan}")
        return True
        
    except (DogrulamaHatasi, VeritabaniHatasi) as e:
        # İş kuralı hataları logla ama POS işlemini durdurma
        logger.warning(f"POS puan kazanım iş kuralı hatası: {str(e)}")
        return False
    except Exception as e:
        # Beklenmeyen hataları logla ama POS işlemini durdurma
        logger.error(f"POS puan kazanım beklenmeyen hatası: {str(e)}")
        return False


def satis_belgesi_olustu(
    db: Session,
    musteri_id: Optional[int],
    belge_tutari: float,
    belge_id: int
) -> bool:
    """
    Satış belgesi oluşturulduğunda müşteriye puan kazandırır
    
    Args:
        db: Veritabanı session
        musteri_id: Müşteri ID (None olabilir)
        belge_tutari: Belge tutarı
        belge_id: Satış belgesi ID'si
    
    Returns:
        bool: İşlem başarılı ise True
    """
    try:
        # Müşteri yoksa sessizce atla
        if not musteri_id:
            return True
        
        # Puan hesapla (1 TL = 1 puan)
        puan = int(belge_tutari * PUAN_HESAPLAMA_ORANI)
        
        if puan <= 0:
            return True
        
        # Puan kazanım işlemi
        dto = PuanIslemDTO(
            musteri_id=musteri_id,
            puan=puan,
            aciklama=f"Satış Belgesi - Tutar: {belge_tutari} TL",
            referans_turu=ReferansTuru.SATIS_BELGESI,
            referans_id=belge_id
        )
        
        # Sadakat servisi ile puan kazandır
        sadakat_servisi = SadakatServisi(db)
        sadakat_servisi.puan_kazan(dto)
        
        logger.info(f"Satış belgesi puan kazanımı: Müşteri {musteri_id}, Puan {puan}")
        return True
        
    except (DogrulamaHatasi, VeritabaniHatasi) as e:
        # İş kuralı hataları logla ama belge işlemini durdurma
        logger.warning(f"Satış belgesi puan kazanım iş kuralı hatası: {str(e)}")
        return False
    except Exception as e:
        # Beklenmeyen hataları logla ama belge işlemini durdurma
        logger.error(f"Satış belgesi puan kazanım beklenmeyen hatası: {str(e)}")
        return False