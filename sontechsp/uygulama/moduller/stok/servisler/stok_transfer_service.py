# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.stok_transfer_service
# Description: SONTECHSP stok transfer servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Transfer Servisi

Bu modül stok transfer işlemlerini yöneten servis sınıfını içerir.
Depolar arası stok transfer işlemlerini gerçekleştirir.
"""

from typing import Optional, Dict, List
from decimal import Decimal
from datetime import datetime
import uuid

from ..dto import StokHareketDTO, StokBakiyeDTO
from ..depolar.arayuzler import IStokHareketRepository, IStokBakiyeRepository
from ..hatalar.stok_hatalari import StokValidationError, StokYetersizError, EsZamanliErisimError


class StokTransferService:
    """Stok transfer servisi implementasyonu"""
    
    def __init__(self, 
                 hareket_repository: IStokHareketRepository,
                 bakiye_repository: IStokBakiyeRepository):
        """
        Stok transfer servisi constructor
        
        Args:
            hareket_repository: Stok hareket repository
            bakiye_repository: Stok bakiye repository
        """
        self._hareket_repository = hareket_repository
        self._bakiye_repository = bakiye_repository
    
    def transfer_yap(self,
                    urun_id: int,
                    kaynak_magaza_id: int,
                    hedef_magaza_id: int,
                    miktar: Decimal,
                    kaynak_depo_id: Optional[int] = None,
                    hedef_depo_id: Optional[int] = None,
                    kullanici_id: Optional[int] = None,
                    aciklama: Optional[str] = None) -> str:
        """
        Stok transfer işlemi gerçekleştirir
        
        Args:
            urun_id: Transfer edilecek ürün ID
            kaynak_magaza_id: Kaynak mağaza ID
            hedef_magaza_id: Hedef mağaza ID
            miktar: Transfer miktarı
            kaynak_depo_id: Kaynak depo ID (opsiyonel)
            hedef_depo_id: Hedef depo ID (opsiyonel)
            kullanici_id: Transfer işlemini yapan kullanıcı ID
            aciklama: Transfer açıklaması
            
        Returns:
            str: Transfer referans numarası
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
            StokYetersizError: Yetersiz stok durumunda
            EsZamanliErisimError: Eş zamanlı erişim hatası durumunda
        """
        # Validasyon
        self._validate_transfer_parametreleri(
            urun_id, kaynak_magaza_id, hedef_magaza_id, miktar
        )
        
        # Transfer referans numarası oluştur
        transfer_ref = f"TRF_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Kaynak stok kontrolü ve kilitleme
        kaynak_bakiye = self._bakiye_repository.kilitle_ve_bakiye_getir(
            urun_id, kaynak_magaza_id, kaynak_depo_id
        )
        
        if not kaynak_bakiye:
            raise StokYetersizError(
                f"Kaynak lokasyonda stok bulunamadı",
                urun_kodu=f"ID:{urun_id}",
                kullanilabilir_stok=Decimal('0'),
                talep_edilen_miktar=miktar
            )
        
        if kaynak_bakiye.kullanilabilir_miktar < miktar:
            raise StokYetersizError(
                f"Yetersiz stok. Mevcut: {kaynak_bakiye.kullanilabilir_miktar}, Talep: {miktar}",
                urun_kodu=f"ID:{urun_id}",
                kullanilabilir_stok=kaynak_bakiye.kullanilabilir_miktar,
                talep_edilen_miktar=miktar
            )
        
        try:
            # Çıkış hareketi (kaynak)
            cikis_hareket = StokHareketDTO(
                urun_id=urun_id,
                magaza_id=kaynak_magaza_id,
                depo_id=kaynak_depo_id,
                hareket_tipi="TRANSFER_CIKIS",
                miktar=-miktar,  # Negatif (çıkış)
                aciklama=f"Transfer çıkışı - Ref: {transfer_ref} - Hedef: M{hedef_magaza_id}D{hedef_depo_id or 0}",
                kullanici_id=kullanici_id,
                referans_tablo="stok_transferleri",
                referans_id=None  # Transfer tablosu ID'si olabilir
            )
            
            # Giriş hareketi (hedef)
            giris_hareket = StokHareketDTO(
                urun_id=urun_id,
                magaza_id=hedef_magaza_id,
                depo_id=hedef_depo_id,
                hareket_tipi="TRANSFER_GIRIS",
                miktar=miktar,  # Pozitif (giriş)
                aciklama=f"Transfer girişi - Ref: {transfer_ref} - Kaynak: M{kaynak_magaza_id}D{kaynak_depo_id or 0}",
                kullanici_id=kullanici_id,
                referans_tablo="stok_transferleri",
                referans_id=None
            )
            
            # Hareketleri kaydet
            cikis_hareket_id = self._hareket_repository.hareket_ekle(cikis_hareket)
            giris_hareket_id = self._hareket_repository.hareket_ekle(giris_hareket)
            
            # Kaynak bakiyeyi güncelle
            yeni_kaynak_miktar = kaynak_bakiye.miktar - miktar
            yeni_kaynak_kullanilabilir = kaynak_bakiye.kullanilabilir_miktar - miktar
            
            self._bakiye_repository.bakiye_guncelle(
                kaynak_bakiye.id,
                yeni_kaynak_miktar,
                kaynak_bakiye.rezerve_miktar,
                yeni_kaynak_kullanilabilir,
                None,  # birim_fiyat
                datetime.utcnow()
            )
            
            # Hedef bakiyeyi güncelle veya oluştur
            hedef_bakiye = self._bakiye_repository.bakiye_getir(
                urun_id, hedef_magaza_id, hedef_depo_id
            )
            
            if hedef_bakiye:
                # Mevcut bakiyeyi güncelle
                yeni_hedef_miktar = hedef_bakiye.miktar + miktar
                yeni_hedef_kullanilabilir = hedef_bakiye.kullanilabilir_miktar + miktar
                
                self._bakiye_repository.bakiye_guncelle(
                    hedef_bakiye.id,
                    yeni_hedef_miktar,
                    hedef_bakiye.rezerve_miktar,
                    yeni_hedef_kullanilabilir,
                    None,  # birim_fiyat
                    datetime.utcnow()
                )
            else:
                # Yeni bakiye oluştur
                yeni_hedef_bakiye = StokBakiyeDTO(
                    urun_id=urun_id,
                    magaza_id=hedef_magaza_id,
                    depo_id=hedef_depo_id,
                    miktar=miktar,
                    rezerve_miktar=Decimal('0'),
                    kullanilabilir_miktar=miktar,
                    son_hareket_tarihi=datetime.utcnow()
                )
                
                self._bakiye_repository.bakiye_ekle(yeni_hedef_bakiye)
            
            return transfer_ref
            
        except Exception as e:
            # Hata durumunda rollback yapılacak (repository seviyesinde)
            raise EsZamanliErisimError(
                f"Transfer işlemi sırasında hata oluştu: {str(e)}",
                kaynak=f"Transfer: {transfer_ref}"
            )
    
    def transfer_iptal(self, transfer_ref: str, kullanici_id: Optional[int] = None) -> bool:
        """
        Transfer işlemini iptal eder (ters hareket yapar)
        
        Args:
            transfer_ref: Transfer referans numarası
            kullanici_id: İptal işlemini yapan kullanıcı ID
            
        Returns:
            bool: İptal başarılı mı
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if not transfer_ref:
            raise StokValidationError("Transfer referans numarası gereklidir")
        
        # Transfer hareketlerini bul
        transfer_hareketleri = self._hareket_repository.referans_ile_hareket_bul(
            "stok_transferleri", transfer_ref
        )
        
        if not transfer_hareketleri:
            raise StokValidationError(f"Transfer bulunamadı: {transfer_ref}")
        
        # İptal hareketleri oluştur
        iptal_ref = f"IPTAL_{transfer_ref}_{datetime.now().strftime('%H%M%S')}"
        
        for hareket in transfer_hareketleri:
            # Ters hareket oluştur
            iptal_hareket = StokHareketDTO(
                urun_id=hareket.urun_id,
                magaza_id=hareket.magaza_id,
                depo_id=hareket.depo_id,
                hareket_tipi=f"IPTAL_{hareket.hareket_tipi}",
                miktar=-hareket.miktar,  # Ters miktar
                aciklama=f"Transfer iptali - Orijinal Ref: {transfer_ref}",
                kullanici_id=kullanici_id,
                referans_tablo="stok_transfer_iptalleri",
                referans_id=None
            )
            
            # İptal hareketini kaydet
            self._hareket_repository.hareket_ekle(iptal_hareket)
            
            # Bakiyeyi güncelle
            bakiye = self._bakiye_repository.bakiye_getir(
                hareket.urun_id, hareket.magaza_id, hareket.depo_id
            )
            
            if bakiye:
                yeni_miktar = bakiye.miktar - hareket.miktar  # Ters işlem
                yeni_kullanilabilir = bakiye.kullanilabilir_miktar - hareket.miktar
                
                self._bakiye_repository.bakiye_guncelle(
                    bakiye.id,
                    yeni_miktar,
                    bakiye.rezerve_miktar,
                    yeni_kullanilabilir,
                    None,
                    datetime.utcnow()
                )
        
        return True
    
    def transfer_gecmisi(self, 
                        urun_id: Optional[int] = None,
                        magaza_id: Optional[int] = None,
                        baslangic_tarihi: Optional[datetime] = None,
                        bitis_tarihi: Optional[datetime] = None) -> List[Dict]:
        """
        Transfer geçmişini getirir
        
        Args:
            urun_id: Ürün ID filtresi (opsiyonel)
            magaza_id: Mağaza ID filtresi (opsiyonel)
            baslangic_tarihi: Başlangıç tarihi filtresi (opsiyonel)
            bitis_tarihi: Bitiş tarihi filtresi (opsiyonel)
            
        Returns:
            List[Dict]: Transfer geçmişi listesi
        """
        # Transfer hareketlerini getir
        from ..dto import StokHareketFiltreDTO
        
        filtre = StokHareketFiltreDTO(
            urun_id=urun_id,
            magaza_id=magaza_id,
            hareket_tipi="TRANSFER",  # TRANSFER ile başlayan tüm tipler
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi
        )
        
        hareketler = self._hareket_repository.hareket_listesi(filtre)
        
        # Transfer referanslarına göre grupla
        transfer_gruplari = {}
        
        for hareket in hareketler:
            if hareket.referans_tablo == "stok_transferleri":
                ref = hareket.aciklama.split("Ref: ")[1].split(" -")[0] if "Ref: " in hareket.aciklama else "UNKNOWN"
                
                if ref not in transfer_gruplari:
                    transfer_gruplari[ref] = {
                        'transfer_ref': ref,
                        'urun_id': hareket.urun_id,
                        'tarih': hareket.olusturma_tarihi,
                        'kullanici_id': hareket.kullanici_id,
                        'cikis': None,
                        'giris': None
                    }
                
                if hareket.hareket_tipi == "TRANSFER_CIKIS":
                    transfer_gruplari[ref]['cikis'] = {
                        'magaza_id': hareket.magaza_id,
                        'depo_id': hareket.depo_id,
                        'miktar': abs(hareket.miktar)
                    }
                elif hareket.hareket_tipi == "TRANSFER_GIRIS":
                    transfer_gruplari[ref]['giris'] = {
                        'magaza_id': hareket.magaza_id,
                        'depo_id': hareket.depo_id,
                        'miktar': hareket.miktar
                    }
        
        return list(transfer_gruplari.values())
    
    def _validate_transfer_parametreleri(self,
                                       urun_id: int,
                                       kaynak_magaza_id: int,
                                       hedef_magaza_id: int,
                                       miktar: Decimal) -> None:
        """
        Transfer parametrelerini doğrular
        
        Args:
            urun_id: Ürün ID
            kaynak_magaza_id: Kaynak mağaza ID
            hedef_magaza_id: Hedef mağaza ID
            miktar: Transfer miktarı
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if urun_id <= 0:
            raise StokValidationError("Geçerli ürün ID gereklidir")
        
        if kaynak_magaza_id <= 0:
            raise StokValidationError("Geçerli kaynak mağaza ID gereklidir")
        
        if hedef_magaza_id <= 0:
            raise StokValidationError("Geçerli hedef mağaza ID gereklidir")
        
        if kaynak_magaza_id == hedef_magaza_id:
            raise StokValidationError("Kaynak ve hedef mağaza aynı olamaz")
        
        if miktar <= 0:
            raise StokValidationError("Transfer miktarı pozitif olmalıdır")
        
        if miktar > Decimal('999999.9999'):
            raise StokValidationError("Transfer miktarı çok büyük")