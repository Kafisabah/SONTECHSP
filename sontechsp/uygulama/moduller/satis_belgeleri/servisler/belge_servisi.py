# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.servisler.belge_servisi
# Description: Ana belge işlemleri servisi
# Changelog:
# - İlk oluşturma
# - Syntax hatası düzeltildi (kaynak_belge_turu satırı)

"""
SONTECHSP Ana Belge Servisi

Bu servis belge yaşam döngüsü yönetimini sağlar:
- Sipariş oluşturma
- İrsaliye oluşturma
- Fatura oluşturma (sipariş ve POS'tan)
- Belge silme ve güncelleme işlemleri
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from ....cekirdek.hatalar import IsKuraliHatasi, VeriTabaniHatasi
from ..modeller import SatisBelgesi, BelgeSatiri, BelgeTuru, BelgeDurumu
from ..depolar.belge_deposu import IBelgeDeposu
from ..depolar.belge_satir_deposu import IBelgeSatirDeposu
from .numara_servisi import NumaraServisi
from .durum_akis_servisi import DurumAkisServisi
from .dogrulama_servisi import DogrulamaServisi

logger = logging.getLogger(__name__)


class SiparisBilgileriDTO:
    """Sipariş oluşturma için veri transfer nesnesi"""
    
    def __init__(
        self,
        magaza_id: int,
        magaza_kodu: str,
        olusturan_kullanici_id: int,
        musteri_id: Optional[int] = None,
        satirlar: Optional[List[Dict[str, Any]]] = None,
        aciklama: Optional[str] = None
    ):
        self.magaza_id = magaza_id
        self.magaza_kodu = magaza_kodu
        self.olusturan_kullanici_id = olusturan_kullanici_id
        self.musteri_id = musteri_id
        self.satirlar = satirlar or []
        self.aciklama = aciklama


class BelgeDTO:
    """Belge veri transfer nesnesi"""
    
    def __init__(self, belge: SatisBelgesi):
        self.belge_id = belge.belge_id
        self.belge_numarasi = belge.belge_numarasi
        self.belge_turu = belge.belge_turu.value
        self.belge_durumu = belge.belge_durumu.value
        self.magaza_id = belge.magaza_id
        self.musteri_id = belge.musteri_id
        self.toplam_tutar = belge.toplam_tutar
        self.kdv_tutari = belge.kdv_tutari
        self.genel_toplam = belge.genel_toplam
        self.olusturma_tarihi = belge.olusturma_tarihi
        self.guncelleme_tarihi = belge.guncelleme_tarihi
        self.satirlar = [self._satir_to_dict(satir) for satir in belge.satirlar]
    
    def _satir_to_dict(self, satir: BelgeSatiri) -> Dict[str, Any]:
        """Belge satırını dict'e dönüştür"""
        return {
            'satir_id': satir.satir_id,
            'urun_id': satir.urun_id,
            'miktar': satir.miktar,
            'birim_fiyat': satir.birim_fiyat,
            'kdv_orani': satir.kdv_orani,
            'satir_tutari': satir.satir_tutari,
            'kdv_tutari': satir.kdv_tutari,
            'satir_toplami': satir.satir_toplami,
            'sira_no': satir.sira_no
        }


class BelgeServisi:
    """
    Ana belge servisi
    
    Bu servis belge yaşam döngüsünü yönetir ve tüm belge işlemlerini koordine eder.
    """
    
    def __init__(
        self,
        belge_deposu: IBelgeDeposu,
        belge_satir_deposu: IBelgeSatirDeposu,
        numara_servisi: NumaraServisi,
        durum_akis_servisi: DurumAkisServisi,
        dogrulama_servisi: DogrulamaServisi
    ):
        self._belge_deposu = belge_deposu
        self._belge_satir_deposu = belge_satir_deposu
        self._numara_servisi = numara_servisi
        self._durum_akis_servisi = durum_akis_servisi
        self._dogrulama_servisi = dogrulama_servisi
    
    def siparis_olustur(self, siparis_bilgileri: SiparisBilgileriDTO) -> BelgeDTO:
        """
        Yeni sipariş oluştur
        
        Args:
            siparis_bilgileri: Sipariş bilgileri
            
        Returns:
            Oluşturulan sipariş DTO
            
        Raises:
            IsKuraliHatasi: Geçersiz sipariş bilgileri
            VeriTabaniHatasi: Veritabanı hatası
        """
        try:
            logger.info(f"Sipariş oluşturma başlatıldı: Mağaza {siparis_bilgileri.magaza_id}")
            
            # Belge numarası üret
            belge_numarasi = self._numara_servisi.numara_uret(
                siparis_bilgileri.magaza_id,
                siparis_bilgileri.magaza_kodu,
                BelgeTuru.SIPARIS
            )
            
            # Sipariş belgesi oluştur
            siparis = SatisBelgesi(
                belge_numarasi=belge_numarasi,
                belge_turu=BelgeTuru.SIPARIS,
                belge_durumu=BelgeDurumu.TASLAK,
                magaza_id=siparis_bilgileri.magaza_id,
                musteri_id=siparis_bilgileri.musteri_id,
                olusturan_kullanici_id=siparis_bilgileri.olusturan_kullanici_id,
                olusturma_tarihi=datetime.now()
            )
            
            # Satırları ekle
            for satir_bilgisi in siparis_bilgileri.satirlar:
                satir = self._satir_bilgisinden_satir_olustur(satir_bilgisi)
                siparis.satir_ekle(satir)
            
            # Doğrulama
            hatalar = self._dogrulama_servisi.belge_dogrula(siparis)
            if hatalar:
                raise IsKuraliHatasi(f"Sipariş doğrulama hatası: {', '.join(hatalar)}")
            
            # Veritabanına kaydet
            kaydedilen_siparis = self._belge_deposu.ekle(siparis)
            
            # Satırları kaydet
            for satir in kaydedilen_siparis.satirlar:
                satir.belge_id = kaydedilen_siparis.belge_id
                self._belge_satir_deposu.ekle(satir)
            
            logger.info(
                f"Sipariş başarıyla oluşturuldu: {kaydedilen_siparis.belge_numarasi} "
                f"(ID: {kaydedilen_siparis.belge_id})"
            )
            
            return BelgeDTO(kaydedilen_siparis)
            
        except Exception as e:
            logger.error(f"Sipariş oluşturma hatası: {e}")
            if isinstance(e, (IsKuraliHatasi, VeriTabaniHatasi)):
                raise
            raise VeriTabaniHatasi(f"Sipariş oluşturulamadı: {e}")
    
    def irsaliye_olustur(self, siparis_id: int, olusturan_kullanici_id: int) -> BelgeDTO:
        """
        Siparişten irsaliye oluştur
        
        Args:
            siparis_id: Kaynak sipariş ID
            olusturan_kullanici_id: İrsaliye oluşturan kullanıcı ID
            
        Returns:
            Oluşturulan irsaliye DTO
            
        Raises:
            IsKuraliHatasi: Geçersiz sipariş durumu
            VeriTabaniHatasi: Veritabanı hatası
        """
        try:
            logger.info(f"İrsaliye oluşturma başlatıldı: Sipariş ID {siparis_id}")
            
            # Kaynak siparişi al
            siparis = self._belge_deposu.bul(siparis_id)
            if not siparis:
                raise IsKuraliHatasi(f"Sipariş bulunamadı: {siparis_id}")
            
            # Sipariş durumu kontrolü
            if siparis.belge_durumu != BelgeDurumu.ONAYLANDI:
                raise IsKuraliHatasi(
                    f"İrsaliye sadece onaylanmış siparişlerden oluşturulabilir. "
                    f"Mevcut durum: {siparis.belge_durumu.value}"
                )
            
            # Mağaza kodunu al (basit implementasyon)
            magaza_kodu = f"M{siparis.magaza_id:03d}"
            
            # İrsaliye numarası üret
            irsaliye_numarasi = self._numara_servisi.numara_uret(
                siparis.magaza_id,
                magaza_kodu,
                BelgeTuru.IRSALIYE
            )
            
            # İrsaliye belgesi oluştur
            irsaliye = SatisBelgesi(
                belge_numarasi=irsaliye_numarasi,
                belge_turu=BelgeTuru.IRSALIYE,
                belge_durumu=BelgeDurumu.ONAYLANDI,
                magaza_id=siparis.magaza_id,
                musteri_id=siparis.musteri_id,
                olusturan_kullanici_id=olusturan_kullanici_id,
                kaynak_belge_id=siparis.belge_id,
                kaynak_belge_turu=BelgeTuru.SIPARIS.value,
                olusturma_tarihi=datetime.now()
            )
            
            # Sipariş satırlarını kopyala
            for siparis_satiri in siparis.satirlar:
                irsaliye_satiri = BelgeSatiri(
                    urun_id=siparis_satiri.urun_id,
                    miktar=siparis_satiri.miktar,
                    birim_fiyat=siparis_satiri.birim_fiyat,
                    kdv_orani=siparis_satiri.kdv_orani
                )
                irsaliye.satir_ekle(irsaliye_satiri)
            
            # Doğrulama
            hatalar = self._dogrulama_servisi.belge_dogrula(irsaliye)
            if hatalar:
                raise IsKuraliHatasi(f"İrsaliye doğrulama hatası: {', '.join(hatalar)}")
            
            # Veritabanına kaydet
            kaydedilen_irsaliye = self._belge_deposu.ekle(irsaliye)
            
            # Satırları kaydet
            for satir in kaydedilen_irsaliye.satirlar:
                satir.belge_id = kaydedilen_irsaliye.belge_id
                self._belge_satir_deposu.ekle(satir)
            
            # Sipariş durumunu güncelle
            self._durum_akis_servisi.durum_guncelle(
                siparis,
                BelgeDurumu.FATURALANDI,
                olusturan_kullanici_id,
                f"İrsaliye oluşturuldu: {irsaliye_numarasi}"
            )
            self._belge_deposu.guncelle(siparis)
            
            logger.info(
                f"İrsaliye başarıyla oluşturuldu: {kaydedilen_irsaliye.belge_numarasi} "
                f"(ID: {kaydedilen_irsaliye.belge_id})"
            )
            
            return BelgeDTO(kaydedilen_irsaliye)
            
        except Exception as e:
            logger.error(f"İrsaliye oluşturma hatası: {e}")
            if isinstance(e, (IsKuraliHatasi, VeriTabaniHatasi)):
                raise
            raise VeriTabaniHatasi(f"İrsaliye oluşturulamadı: {e}")
    
    def fatura_olustur(
        self, 
        kaynak_belge_id: int, 
        kaynak_tip: str,
        olusturan_kullanici_id: int
    ) -> BelgeDTO:
        """
        Kaynak belgeden fatura oluştur
        
        Args:
            kaynak_belge_id: Kaynak belge ID
            kaynak_tip: Kaynak belge tipi ("SIPARIS" veya "POS")
            olusturan_kullanici_id: Fatura oluşturan kullanıcı ID
            
        Returns:
            Oluşturulan fatura DTO
            
        Raises:
            IsKuraliHatasi: Geçersiz kaynak belge
            VeriTabaniHatasi: Veritabanı hatası
        """
        try:
            logger.info(
                f"Fatura oluşturma başlatıldı: Kaynak {kaynak_tip} ID {kaynak_belge_id}"
            )
            
            if kaynak_tip == "SIPARIS":
                return self._siparisten_fatura_olustur(kaynak_belge_id, olusturan_kullanici_id)
            elif kaynak_tip == "POS":
                return self._pos_satisinden_fatura_olustur(kaynak_belge_id, olusturan_kullanici_id)
            else:
                raise IsKuraliHatasi(f"Desteklenmeyen kaynak tip: {kaynak_tip}")
                
        except Exception as e:
            logger.error(f"Fatura oluşturma hatası: {e}")
            if isinstance(e, (IsKuraliHatasi, VeriTabaniHatasi)):
                raise
            raise VeriTabaniHatasi(f"Fatura oluşturulamadı: {e}")
    
    def belge_sil(self, belge_id: int, silen_kullanici_id: int) -> bool:
        """
        Belgeyi sil
        
        Args:
            belge_id: Silinecek belge ID
            silen_kullanici_id: Silen kullanıcı ID
            
        Returns:
            Silme başarılı mı?
            
        Raises:
            IsKuraliHatasi: Silinemeyen belge durumu
        """
        try:
            logger.info(f"Belge silme başlatıldı: ID {belge_id}")
            
            # Belgeyi al
            belge = self._belge_deposu.bul(belge_id)
            if not belge:
                raise IsKuraliHatasi(f"Belge bulunamadı: {belge_id}")
            
            # Silme kontrolü
            if belge.belge_durumu not in [BelgeDurumu.TASLAK, BelgeDurumu.IPTAL]:
                raise IsKuraliHatasi(
                    f"Sadece taslak veya iptal durumundaki belgeler silinebilir. "
                    f"Mevcut durum: {belge.belge_durumu.value}"
                )
            
            # Bağımlı kayıtları kontrol et
            bagimli_belgeler = self._belge_deposu.bagimli_belgeleri_bul(belge_id)
            if bagimli_belgeler:
                raise IsKuraliHatasi(
                    f"Belgeye bağımlı {len(bagimli_belgeler)} belge bulunduğu için silinemez"
                )
            
            # Satırları sil
            for satir in belge.satirlar:
                self._belge_satir_deposu.sil(satir.satir_id)
            
            # Belgeyi sil
            silindi = self._belge_deposu.sil(belge_id)
            
            if silindi:
                logger.info(f"Belge başarıyla silindi: {belge.belge_numarasi} (ID: {belge_id})")
            
            return silindi
            
        except Exception as e:
            logger.error(f"Belge silme hatası: {e}")
            if isinstance(e, IsKuraliHatasi):
                raise
            raise VeriTabaniHatasi(f"Belge silinemedi: {e}")
    
    def _siparisten_fatura_olustur(self, siparis_id: int, olusturan_kullanici_id: int) -> BelgeDTO:
        """Siparişten fatura oluştur"""
        # Kaynak siparişi al
        siparis = self._belge_deposu.bul(siparis_id)
        if not siparis:
            raise IsKuraliHatasi(f"Sipariş bulunamadı: {siparis_id}")
        
        # Sipariş durumu kontrolü
        if siparis.belge_durumu != BelgeDurumu.ONAYLANDI:
            raise IsKuraliHatasi(
                f"Fatura sadece onaylanmış siparişlerden oluşturulabilir. "
                f"Mevcut durum: {siparis.belge_durumu.value}"
            )
        
        # Mağaza kodunu al
        magaza_kodu = f"M{siparis.magaza_id:03d}"
        
        # Fatura numarası üret
        fatura_numarasi = self._numara_servisi.numara_uret(
            siparis.magaza_id,
            magaza_kodu,
            BelgeTuru.FATURA
        )
        
        # Fatura belgesi oluştur
        fatura = SatisBelgesi(
            belge_numarasi=fatura_numarasi,
            belge_turu=BelgeTuru.FATURA,
            belge_durumu=BelgeDurumu.ONAYLANDI,
            magaza_id=siparis.magaza_id,
            musteri_id=siparis.musteri_id,
            olusturan_kullanici_id=olusturan_kullanici_id,
            kaynak_belge_id=siparis.belge_id,
            kaynak_belge_turu=BelgeTuru.SIPARIS.value,
            olusturma_tarihi=datetime.now()
        )
        
        # Sipariş satırlarını kopyala ve KDV hesapla
        for siparis_satiri in siparis.satirlar:
            fatura_satiri = BelgeSatiri(
                urun_id=siparis_satiri.urun_id,
                miktar=siparis_satiri.miktar,
                birim_fiyat=siparis_satiri.birim_fiyat,
                kdv_orani=siparis_satiri.kdv_orani
            )
            fatura.satir_ekle(fatura_satiri)
        
        # Doğrulama
        hatalar = self._dogrulama_servisi.belge_dogrula(fatura)
        if hatalar:
            raise IsKuraliHatasi(f"Fatura doğrulama hatası: {', '.join(hatalar)}")
        
        # Veritabanına kaydet
        kaydedilen_fatura = self._belge_deposu.ekle(fatura)
        
        # Satırları kaydet
        for satir in kaydedilen_fatura.satirlar:
            satir.belge_id = kaydedilen_fatura.belge_id
            self._belge_satir_deposu.ekle(satir)
        
        # Sipariş durumunu güncelle
        self._durum_akis_servisi.durum_guncelle(
            siparis,
            BelgeDurumu.FATURALANDI,
            olusturan_kullanici_id,
            f"Fatura oluşturuldu: {fatura_numarasi}"
        )
        self._belge_deposu.guncelle(siparis)
        
        return BelgeDTO(kaydedilen_fatura)
    
    def _pos_satisinden_fatura_olustur(self, pos_satis_id: int, olusturan_kullanici_id: int) -> BelgeDTO:
        """POS satışından fatura oluştur"""
        # Bu metod POS entegrasyonu tamamlandığında implement edilecek
        raise IsKuraliHatasi("POS satışından fatura oluşturma henüz desteklenmiyor")
    
    def _satir_bilgisinden_satir_olustur(self, satir_bilgisi: Dict[str, Any]) -> BelgeSatiri:
        """Satır bilgisinden BelgeSatiri oluştur"""
        return BelgeSatiri(
            urun_id=satir_bilgisi['urun_id'],
            miktar=Decimal(str(satir_bilgisi['miktar'])),
            birim_fiyat=Decimal(str(satir_bilgisi['birim_fiyat'])),
            kdv_orani=Decimal(str(satir_bilgisi.get('kdv_orani', '18.00')))
        )