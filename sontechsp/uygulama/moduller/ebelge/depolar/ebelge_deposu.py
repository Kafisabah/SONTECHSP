# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge.depolar.ebelge_deposu
# Description: E-belge repository sınıfı
# Changelog:
# - İlk versiyon: EBelgeDeposu sınıfı oluşturuldu

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from sontechsp.uygulama.veritabani.modeller.ebelge import (
    EbelgeCikisKuyrugu,
    EbelgeDurumlari
)
from sontechsp.uygulama.moduller.ebelge.dto import EBelgeOlusturDTO
from sontechsp.uygulama.moduller.ebelge.sabitler import (
    OutboxDurumu,
    MAX_RETRY_COUNT,
    DEFAULT_BATCH_SIZE
)
from sontechsp.uygulama.moduller.ebelge.hatalar import (
    EntegrasyonHatasi,
    DogrulamaHatasi
)


class EBelgeDeposu:
    """E-belge veri erişim katmanı"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def cikis_kaydi_olustur(self, dto: EBelgeOlusturDTO) -> int:
        """Yeni çıkış kaydı oluşturur"""
        try:
            # Yeni kayıt oluştur
            kayit = EbelgeCikisKuyrugu(
                kaynak_turu=dto.kaynak_turu,
                kaynak_id=dto.kaynak_id,
                belge_turu=dto.belge_turu,
                musteri_ad=dto.musteri_ad,
                vergi_no=dto.vergi_no,
                toplam_tutar=dto.toplam_tutar,
                para_birimi=dto.para_birimi,
                belge_json=str(dto.belge_json),  # JSON string olarak sakla
                durum=OutboxDurumu.BEKLIYOR.value,
                aciklama=dto.aciklama
            )
            
            self.session.add(kayit)
            self.session.flush()  # ID'yi al
            
            # İlk durum kaydını oluştur
            self.tarihce_ekle(kayit.id, OutboxDurumu.BEKLIYOR.value, "Kayıt oluşturuldu")
            
            self.session.commit()
            return kayit.id
            
        except Exception as e:
            self.session.rollback()
            # UNIQUE constraint ihlali kontrolü
            if "uq_ebelge_kaynak" in str(e):
                raise EntegrasyonHatasi(
                    f"Aynı kaynak için belge zaten mevcut: "
                    f"{dto.kaynak_turu}-{dto.kaynak_id}-{dto.belge_turu}"
                )
            raise
    
    def cikis_kaydi_getir(self, cikis_id: int) -> Optional[EbelgeCikisKuyrugu]:
        """Tekil çıkış kaydını getirir"""
        return self.session.query(EbelgeCikisKuyrugu).filter(
            EbelgeCikisKuyrugu.id == cikis_id
        ).first()
    
    def bekleyenleri_getir(self, limit: int = DEFAULT_BATCH_SIZE) -> List[EbelgeCikisKuyrugu]:
        """Bekleyen kayıtları getirir"""
        return self.session.query(EbelgeCikisKuyrugu).filter(
            or_(
                EbelgeCikisKuyrugu.durum == OutboxDurumu.BEKLIYOR.value,
                and_(
                    EbelgeCikisKuyrugu.durum == OutboxDurumu.HATA.value,
                    EbelgeCikisKuyrugu.deneme_sayisi < MAX_RETRY_COUNT
                )
            )
        ).order_by(EbelgeCikisKuyrugu.olusturulma_zamani).limit(limit).all()
    
    def durum_guncelle(
        self, 
        cikis_id: int, 
        yeni_durum: str, 
        mesaj: Optional[str] = None,
        dis_belge_no: Optional[str] = None
    ) -> bool:
        """Kayıt durumunu günceller"""
        try:
            kayit = self.cikis_kaydi_getir(cikis_id)
            if not kayit:
                raise DogrulamaHatasi(f"Çıkış kaydı bulunamadı: {cikis_id}")
            
            # Durum güncelle
            kayit.durum = yeni_durum
            kayit.mesaj = mesaj
            kayit.guncellenme_zamani = datetime.utcnow()
            
            if dis_belge_no:
                kayit.dis_belge_no = dis_belge_no
            
            # Durum geçmişine ekle
            self.tarihce_ekle(cikis_id, yeni_durum, mesaj)
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise
    
    def deneme_arttir(self, cikis_id: int) -> bool:
        """Deneme sayısını artırır"""
        try:
            kayit = self.cikis_kaydi_getir(cikis_id)
            if not kayit:
                raise DogrulamaHatasi(f"Çıkış kaydı bulunamadı: {cikis_id}")
            
            kayit.deneme_sayisi += 1
            kayit.guncellenme_zamani = datetime.utcnow()
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise
    
    def tarihce_ekle(self, cikis_id: int, durum: str, mesaj: Optional[str] = None) -> bool:
        """Durum geçmişine kayıt ekler"""
        try:
            durum_kaydi = EbelgeDurumlari(
                cikis_id=cikis_id,
                durum=durum,
                mesaj=mesaj
            )
            
            self.session.add(durum_kaydi)
            # Commit burada yapılmaz, çağıran metot yapar
            return True
            
        except Exception as e:
            raise
    
    def durum_gecmisi_getir(self, cikis_id: int) -> List[EbelgeDurumlari]:
        """Belge durum geçmişini getirir"""
        return self.session.query(EbelgeDurumlari).filter(
            EbelgeDurumlari.cikis_id == cikis_id
        ).order_by(EbelgeDurumlari.olusturulma_zamani).all()
    
    def kaynak_ile_getir(
        self, 
        kaynak_turu: str, 
        kaynak_id: int, 
        belge_turu: str
    ) -> Optional[EbelgeCikisKuyrugu]:
        """Kaynak bilgileri ile kaydı getirir"""
        return self.session.query(EbelgeCikisKuyrugu).filter(
            and_(
                EbelgeCikisKuyrugu.kaynak_turu == kaynak_turu,
                EbelgeCikisKuyrugu.kaynak_id == kaynak_id,
                EbelgeCikisKuyrugu.belge_turu == belge_turu
            )
        ).first()