# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge.servisler.ebelge_servisi
# Description: E-belge ana servis sınıfı
# Changelog:
# - İlk versiyon: EBelgeServisi sınıfı oluşturuldu

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from ..dto import EBelgeOlusturDTO, EBelgeSonucDTO, EBelgeGonderDTO
from ..depolar.ebelge_deposu import EBelgeDeposu
from ..saglayici_fabrikasi import SaglayiciFabrikasi
from ..sabitler import OutboxDurumu, BelgeTuru, KaynakTuru, DEFAULT_BATCH_SIZE
from ..hatalar import DogrulamaHatasi, EntegrasyonHatasi, JSONHatasi

logger = logging.getLogger(__name__)


class EBelgeServisi:
    """E-belge ana servis sınıfı"""
    
    def __init__(self, session: Session, saglayici_config: Optional[dict] = None):
        self.session = session
        self.depo = EBelgeDeposu(session)
        self.saglayici_config = saglayici_config or {'saglayici': 'dummy'}
    
    def cikis_olustur(self, dto: EBelgeOlusturDTO) -> int:
        """Yeni e-belge çıkış kaydı oluşturur"""
        logger.info(f"E-belge çıkış kaydı oluşturuluyor: {dto.kaynak_turu}-{dto.kaynak_id}-{dto.belge_turu}")
        
        # Validation
        self._validate_dto(dto)
        
        try:
            # Çıkış kaydı oluştur
            cikis_id = self.depo.cikis_kaydi_olustur(dto)
            logger.info(f"E-belge çıkış kaydı oluşturuldu: {cikis_id}")
            return cikis_id
            
        except EntegrasyonHatasi:
            # Mükerrer kayıt hatası, mevcut kaydın ID'sini döndür
            mevcut_kayit = self.depo.kaynak_ile_getir(
                dto.kaynak_turu, dto.kaynak_id, dto.belge_turu
            )
            if mevcut_kayit:
                logger.warning(f"Mükerrer kayıt tespit edildi, mevcut ID döndürülüyor: {mevcut_kayit.id}")
                return mevcut_kayit.id
            raise
    
    def bekleyenleri_gonder(self, limit: int = DEFAULT_BATCH_SIZE) -> List[int]:
        """Bekleyen belgeleri entegratöre gönderir"""
        logger.info(f"Bekleyen belgeler gönderiliyor, limit: {limit}")
        
        # Bekleyen kayıtları getir
        bekleyen_kayitlar = self.depo.bekleyenleri_getir(limit)
        gonderilen_ids = []
        
        for kayit in bekleyen_kayitlar:
            try:
                # Durumu GONDERILIYOR olarak güncelle
                self.depo.durum_guncelle(
                    kayit.id, 
                    OutboxDurumu.GONDERILIYOR.value,
                    "Gönderim başlatıldı"
                )
                
                # Sağlayıcıdan belge gönder
                saglayici = SaglayiciFabrikasi.saglayici_olustur(
                    self.saglayici_config.get('saglayici', 'dummy'),
                    self.saglayici_config
                )
                
                gonder_dto = EBelgeGonderDTO(
                    cikis_id=kayit.id,
                    belge_json=json.loads(kayit.belge_json)
                )
                
                sonuc = saglayici.gonder(gonder_dto)
                
                if sonuc.basarili_mi:
                    # Başarılı gönderim
                    self.depo.durum_guncelle(
                        kayit.id,
                        OutboxDurumu.GONDERILDI.value,
                        sonuc.mesaj,
                        sonuc.dis_belge_no
                    )
                    gonderilen_ids.append(kayit.id)
                    logger.info(f"Belge başarıyla gönderildi: {kayit.id}")
                else:
                    # Başarısız gönderim
                    self._handle_failed_send(kayit.id, sonuc.mesaj)
                    
            except Exception as e:
                logger.error(f"Belge gönderim hatası: {kayit.id} - {str(e)}")
                self._handle_failed_send(kayit.id, str(e))
        
        logger.info(f"Toplam {len(gonderilen_ids)} belge başarıyla gönderildi")
        return gonderilen_ids
    
    def durum_sorgula(self, cikis_id: int) -> EBelgeSonucDTO:
        """Belge durumunu sorgular ve günceller"""
        logger.info(f"Belge durumu sorgulanıyor: {cikis_id}")
        
        kayit = self.depo.cikis_kaydi_getir(cikis_id)
        if not kayit:
            raise DogrulamaHatasi(f"Belge bulunamadı: {cikis_id}")
        
        # Dış belge numarası varsa entegratörden sorgula
        if kayit.dis_belge_no:
            try:
                saglayici = SaglayiciFabrikasi.saglayici_olustur(
                    self.saglayici_config.get('saglayici', 'dummy'),
                    self.saglayici_config
                )
                
                sonuc = saglayici.durum_sorgula(kayit.dis_belge_no)
                
                # Durum güncelle
                if sonuc.basarili_mi and sonuc.durum_kodu:
                    self.depo.durum_guncelle(
                        cikis_id,
                        sonuc.durum_kodu,
                        sonuc.mesaj
                    )
                
                return sonuc
                
            except Exception as e:
                logger.error(f"Entegratör durum sorgu hatası: {cikis_id} - {str(e)}")
                # Hata durumunda mevcut durumu döndür
        
        # Mevcut durumu döndür
        return EBelgeSonucDTO(
            basarili_mi=True,
            dis_belge_no=kayit.dis_belge_no,
            durum_kodu=kayit.durum,
            mesaj=kayit.mesaj
        )
    
    def _validate_dto(self, dto: EBelgeOlusturDTO):
        """DTO validation"""
        if not dto.kaynak_turu:
            raise DogrulamaHatasi("Kaynak türü zorunludur")
        
        if dto.kaynak_turu not in [kt.value for kt in KaynakTuru]:
            raise DogrulamaHatasi(f"Geçersiz kaynak türü: {dto.kaynak_turu}")
        
        if not dto.kaynak_id or dto.kaynak_id <= 0:
            raise DogrulamaHatasi("Geçerli kaynak ID zorunludur")
        
        if not dto.belge_turu:
            raise DogrulamaHatasi("Belge türü zorunludur")
        
        if dto.belge_turu not in [bt.value for bt in BelgeTuru]:
            raise DogrulamaHatasi(f"Geçersiz belge türü: {dto.belge_turu}")
        
        if not dto.musteri_ad or not dto.musteri_ad.strip():
            raise DogrulamaHatasi("Müşteri adı zorunludur")
        
        if not dto.vergi_no or not dto.vergi_no.strip():
            raise DogrulamaHatasi("Vergi numarası zorunludur")
        
        if not dto.belge_json:
            raise DogrulamaHatasi("Belge JSON verisi zorunludur")
        
        # JSON format kontrolü
        try:
            json.dumps(dto.belge_json)
        except (TypeError, ValueError) as e:
            raise JSONHatasi(f"Geçersiz JSON formatı: {str(e)}")
    
    def _handle_failed_send(self, cikis_id: int, hata_mesaji: str):
        """Başarısız gönderim işlemi"""
        # Deneme sayısını artır
        self.depo.deneme_arttir(cikis_id)
        
        # Durum güncelle
        self.depo.durum_guncelle(
            cikis_id,
            OutboxDurumu.HATA.value,
            hata_mesaji
        )
        
        logger.warning(f"Belge gönderim başarısız: {cikis_id} - {hata_mesaji}")