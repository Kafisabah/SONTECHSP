# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo.servisler
# Description: Kargo modülü servis katmanı
# Changelog:
# - KargoServisi class'ı eklendi
# - etiket_olustur metodu implement edildi
# - Benzersizlik kontrolü ve doğrulama eklendi
# - Carrier seçimi ve orchestration eklendi

"""
Kargo modülü servis katmanı.

Bu modül, kargo işlemlerinin iş kurallarını ve orchestration'ını içerir.
Repository katmanını kullanarak veritabanı işlemlerini yönetir.
"""

import logging
import decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .dto import KargoEtiketOlusturDTO, KargoEtiketSonucDTO, KargoDurumDTO
from .depolar import KargoDeposu
from .tasiyici_fabrikasi import TasiyiciFabrikasi
from .sabitler import (
    KaynakTurleri, EtiketDurumlari, Tasiyicilar, 
    MAKSIMUM_DENEME_SAYISI
)


# Hata sınıfları
class DogrulamaHatasi(Exception):
    """Veri doğrulama hatası."""
    pass


class EntegrasyonHatasi(Exception):
    """Taşıyıcı entegrasyon hatası."""
    pass


class BenzersizlikHatasi(Exception):
    """Benzersizlik kısıtlaması hatası."""
    pass


class KargoServisi:
    """
    Kargo işlemleri için servis sınıfı.
    
    İş kurallarını uygular ve repository katmanını orchestrate eder.
    """
    
    def __init__(self, session: Session):
        """
        Servisi başlatır.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.depo = KargoDeposu(session)
        self.logger = logging.getLogger(__name__)
    
    def etiket_olustur(self, dto: KargoEtiketOlusturDTO) -> KargoEtiketSonucDTO:
        """
        Kargo etiket oluşturur.
        
        Args:
            dto: Etiket oluşturma verisi
        
        Returns:
            KargoEtiketSonucDTO: Etiket oluşturma sonucu
        
        Raises:
            DogrulamaHatasi: Geçersiz veri durumunda
            BenzersizlikHatasi: Duplicate etiket durumunda
            EntegrasyonHatasi: Taşıyıcı hatası durumunda
        """
        try:
            # 1. Veri doğrulama
            self._dto_dogrula(dto)
            
            # 2. Benzersizlik kontrolü
            mevcut_etiket = self.depo.etiket_kaynaktan_bul(
                dto.kaynak_turu, dto.kaynak_id, dto.tasiyici
            )
            if mevcut_etiket:
                raise BenzersizlikHatasi(
                    f"Bu kaynak için zaten etiket mevcut: "
                    f"{dto.kaynak_turu}-{dto.kaynak_id}-{dto.tasiyici}"
                )
            
            # 3. Etiket kaydı oluştur
            etiket = self.depo.etiket_kaydi_olustur(dto)
            
            # 4. Taşıyıcı seç ve etiket oluştur
            try:
                tasiyici = TasiyiciFabrikasi.tasiyici_olustur(dto.tasiyici)
                
                # Carrier payload hazırla
                payload = self._carrier_payload_hazirla(dto)
                
                # Carrier'dan etiket oluştur
                sonuc = tasiyici.etiket_olustur(payload)
                
                # Sonucu işle
                if sonuc.get('durum') == EtiketDurumlari.OLUSTURULDU:
                    # Başarılı durum
                    self.depo.etiket_durum_guncelle(
                        etiket.id,
                        EtiketDurumlari.OLUSTURULDU,
                        sonuc.get('mesaj'),
                        sonuc.get('takip_no')
                    )
                    
                    self.session.commit()
                    
                    return KargoEtiketSonucDTO(
                        etiket_id=etiket.id,
                        durum=EtiketDurumlari.OLUSTURULDU,
                        takip_no=sonuc.get('takip_no'),
                        mesaj=sonuc.get('mesaj')
                    )
                else:
                    # Hata durumu
                    self.depo.etiket_durum_guncelle(
                        etiket.id,
                        EtiketDurumlari.HATA,
                        sonuc.get('mesaj')
                    )
                    
                    self.session.commit()
                    
                    return KargoEtiketSonucDTO(
                        etiket_id=etiket.id,
                        durum=EtiketDurumlari.HATA,
                        mesaj=sonuc.get('mesaj')
                    )
                    
            except Exception as e:
                # Carrier hatası
                self.logger.error(f"Carrier hatası: {e}")
                
                self.depo.etiket_durum_guncelle(
                    etiket.id,
                    EtiketDurumlari.HATA,
                    f"Taşıyıcı hatası: {str(e)}"
                )
                
                self.session.commit()
                
                raise EntegrasyonHatasi(f"Taşıyıcı hatası: {str(e)}")
                
        except IntegrityError as e:
            self.session.rollback()
            self.logger.error(f"Veritabanı kısıtlama hatası: {e}")
            raise BenzersizlikHatasi("Etiket zaten mevcut")
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Etiket oluşturma hatası: {e}")
            raise
    
    def _dto_dogrula(self, dto: KargoEtiketOlusturDTO) -> None:
        """
        DTO verilerini doğrular.
        
        Args:
            dto: Doğrulanacak DTO
        
        Raises:
            DogrulamaHatasi: Geçersiz veri durumunda
        """
        # Kaynak türü kontrolü
        if not KaynakTurleri.gecerli_mi(dto.kaynak_turu):
            raise DogrulamaHatasi(f"Geçersiz kaynak türü: {dto.kaynak_turu}")
        
        # Taşıyıcı kontrolü
        if not Tasiyicilar.gecerli_mi(dto.tasiyici):
            raise DogrulamaHatasi(f"Geçersiz taşıyıcı: {dto.tasiyici}")
        
        # Zorunlu alanlar kontrolü
        zorunlu_alanlar = [
            ('kaynak_id', dto.kaynak_id),
            ('alici_ad', dto.alici_ad),
            ('alici_telefon', dto.alici_telefon),
            ('alici_adres', dto.alici_adres),
            ('alici_il', dto.alici_il),
            ('alici_ilce', dto.alici_ilce)
        ]
        
        for alan_adi, deger in zorunlu_alanlar:
            if not deger or (isinstance(deger, str) and not deger.strip()):
                raise DogrulamaHatasi(f"Zorunlu alan eksik: {alan_adi}")
        
        # Kaynak ID pozitif olmalı
        if dto.kaynak_id <= 0:
            raise DogrulamaHatasi("Kaynak ID pozitif olmalıdır")
        
        # Paket ağırlığı pozitif olmalı
        try:
            if dto.paket_agirlik_kg <= 0:
                raise DogrulamaHatasi("Paket ağırlığı pozitif olmalıdır")
        except (TypeError, ValueError, decimal.InvalidOperation):
            raise DogrulamaHatasi("Geçersiz paket ağırlığı değeri")
    
    def _carrier_payload_hazirla(self, dto: KargoEtiketOlusturDTO) -> dict:
        """
        Carrier için payload hazırlar.
        
        Args:
            dto: Etiket oluşturma verisi
        
        Returns:
            dict: Carrier payload'ı
        """
        return {
            'alici_ad': dto.alici_ad,
            'alici_telefon': dto.alici_telefon,
            'alici_adres': dto.alici_adres,
            'alici_il': dto.alici_il,
            'alici_ilce': dto.alici_ilce,
            'paket_agirlik_kg': dto.paket_agirlik_kg,
            'gonderen_ad': dto.gonderen_ad,
            'gonderen_telefon': dto.gonderen_telefon,
            'servis_kodu': dto.servis_kodu,
            'aciklama': dto.aciklama
        }
    
    def bekleyen_etiketleri_isle(self, limit: int = 10) -> dict:
        """
        Bekleyen etiketleri yeniden dener.
        
        Args:
            limit: İşlenecek maksimum etiket sayısı
        
        Returns:
            dict: İşlem sonuç özeti
        """
        sonuc = {
            'toplam_islenen': 0,
            'basarili': 0,
            'basarisiz': 0,
            'maksimum_deneme_asilan': 0
        }
        
        try:
            # Bekleyen etiketleri al
            bekleyen_etiketler = self.depo.bekleyen_etiketleri_al(limit)
            sonuc['toplam_islenen'] = len(bekleyen_etiketler)
            
            for etiket in bekleyen_etiketler:
                try:
                    # Maksimum deneme kontrolü
                    if etiket.deneme_sayisi >= MAKSIMUM_DENEME_SAYISI:
                        self.logger.warning(
                            f"Etiket {etiket.id} maksimum deneme sayısına ulaştı"
                        )
                        sonuc['maksimum_deneme_asilan'] += 1
                        continue
                    
                    # Deneme sayısını artır
                    self.depo.deneme_sayisi_artir(etiket.id)
                    
                    # Taşıyıcı ile yeniden dene
                    tasiyici = TasiyiciFabrikasi.tasiyici_olustur(etiket.tasiyici)
                    
                    # Payload hazırla
                    payload = self._etiket_payload_hazirla(etiket)
                    
                    # Carrier'dan etiket oluştur
                    carrier_sonuc = tasiyici.etiket_olustur(payload)
                    
                    if carrier_sonuc.get('durum') == EtiketDurumlari.OLUSTURULDU:
                        # Başarılı
                        self.depo.etiket_durum_guncelle(
                            etiket.id,
                            EtiketDurumlari.OLUSTURULDU,
                            carrier_sonuc.get('mesaj'),
                            carrier_sonuc.get('takip_no')
                        )
                        sonuc['basarili'] += 1
                        
                        self.logger.info(
                            f"Etiket {etiket.id} başarıyla oluşturuldu "
                            f"(deneme: {etiket.deneme_sayisi + 1})"
                        )
                    else:
                        # Hata
                        self.depo.etiket_durum_guncelle(
                            etiket.id,
                            EtiketDurumlari.HATA,
                            carrier_sonuc.get('mesaj')
                        )
                        sonuc['basarisiz'] += 1
                        
                        self.logger.warning(
                            f"Etiket {etiket.id} yeniden deneme başarısız "
                            f"(deneme: {etiket.deneme_sayisi + 1})"
                        )
                
                except Exception as e:
                    # Etiket bazlı hata
                    self.logger.error(f"Etiket {etiket.id} retry hatası: {e}")
                    
                    self.depo.etiket_durum_guncelle(
                        etiket.id,
                        EtiketDurumlari.HATA,
                        f"Retry hatası: {str(e)}"
                    )
                    sonuc['basarisiz'] += 1
            
            # Değişiklikleri kaydet
            self.session.commit()
            
            self.logger.info(f"Retry işlemi tamamlandı: {sonuc}")
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Retry işlemi genel hatası: {e}")
            raise
        
        return sonuc
    
    def _etiket_payload_hazirla(self, etiket) -> dict:
        """
        Mevcut etiket kaydından carrier payload hazırlar.
        
        Args:
            etiket: KargoEtiketleri modeli
        
        Returns:
            dict: Carrier payload'ı
        """
        return {
            'alici_ad': etiket.alici_ad,
            'alici_telefon': etiket.alici_telefon,
            'alici_adres': etiket.alici_adres,
            'alici_il': etiket.alici_il,
            'alici_ilce': etiket.alici_ilce,
            'paket_agirlik_kg': etiket.paket_agirlik_kg,
            'servis_kodu': etiket.servis_kodu
        }
    
    def durum_sorgula(self, etiket_id: int) -> Optional[KargoDurumDTO]:
        """
        Etiket durumunu sorgular ve takip geçmişi ekler.
        
        Args:
            etiket_id: Etiket ID'si
        
        Returns:
            Optional[KargoDurumDTO]: Durum bilgisi veya None
        
        Raises:
            EntegrasyonHatasi: Taşıyıcı hatası durumunda
        """
        try:
            # Etiket kaydını al
            etiket = self.depo.etiket_getir(etiket_id)
            if not etiket:
                self.logger.warning(f"Etiket bulunamadı: {etiket_id}")
                return None
            
            # Takip numarası yoksa sorgulama yapılamaz
            if not etiket.takip_no:
                self.logger.warning(
                    f"Etiket {etiket_id} için takip numarası yok"
                )
                return None
            
            try:
                # Taşıyıcıdan durum sorgula
                tasiyici = TasiyiciFabrikasi.tasiyici_olustur(etiket.tasiyici)
                carrier_sonuc = tasiyici.durum_sorgula(etiket.takip_no)
                
                # Takip geçmişine ekle
                takip_kaydi = self.depo.takip_kaydi_ekle(
                    etiket_id=etiket.id,
                    takip_no=etiket.takip_no,
                    durum=carrier_sonuc.get('durum'),
                    aciklama=carrier_sonuc.get('aciklama'),
                    zaman=carrier_sonuc.get('zaman')
                )
                
                self.session.commit()
                
                # DTO oluştur
                durum_dto = KargoDurumDTO(
                    etiket_id=etiket.id,
                    takip_no=etiket.takip_no,
                    durum=carrier_sonuc.get('durum'),
                    aciklama=carrier_sonuc.get('aciklama'),
                    zaman=carrier_sonuc.get('zaman')
                )
                
                self.logger.info(
                    f"Etiket {etiket_id} durum sorgulandı: "
                    f"{carrier_sonuc.get('durum')}"
                )
                
                return durum_dto
                
            except Exception as e:
                # Carrier hatası
                self.logger.error(
                    f"Etiket {etiket_id} durum sorgulama hatası: {e}"
                )
                
                # Hata kaydını da takip geçmişine ekle
                self.depo.takip_kaydi_ekle(
                    etiket_id=etiket.id,
                    takip_no=etiket.takip_no,
                    durum="HATA",
                    aciklama=f"Durum sorgulama hatası: {str(e)}"
                )
                
                self.session.commit()
                
                raise EntegrasyonHatasi(
                    f"Durum sorgulama hatası: {str(e)}"
                )
                
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Durum sorgulama genel hatası: {e}")
            raise
    
    def takip_no_ile_durum_sorgula(self, takip_no: str) -> Optional[KargoDurumDTO]:
        """
        Takip numarası ile durum sorgular.
        
        Args:
            takip_no: Takip numarası
        
        Returns:
            Optional[KargoDurumDTO]: Durum bilgisi veya None
        """
        # Takip numarası ile etiket bul
        etiket = self.depo.etiket_takip_no_ile_bul(takip_no)
        if not etiket:
            self.logger.warning(f"Takip numarası bulunamadı: {takip_no}")
            return None
        
        # Etiket ID ile durum sorgula
        return self.durum_sorgula(etiket.id)
    
    def etiket_gecmisi_getir(self, etiket_id: int) -> list:
        """
        Etiketin takip geçmişini getirir.
        
        Args:
            etiket_id: Etiket ID'si
        
        Returns:
            list: Takip geçmişi listesi (KargoDurumDTO)
        """
        takip_kayitlari = self.depo.takip_gecmisi_getir(etiket_id)
        
        gecmis = []
        for kayit in takip_kayitlari:
            dto = KargoDurumDTO(
                etiket_id=kayit.etiket_id,
                takip_no=kayit.takip_no,
                durum=kayit.durum,
                aciklama=kayit.aciklama,
                zaman=kayit.zaman
            )
            gecmis.append(dto)
        
        return gecmis