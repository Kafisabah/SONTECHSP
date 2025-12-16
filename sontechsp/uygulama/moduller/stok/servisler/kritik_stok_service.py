# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.kritik_stok_service
# Description: SONTECHSP kritik stok servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Kritik Stok Servisi

Bu modül kritik stok yönetimi işlemlerini gerçekleştirir.
Kritik seviye kontrolü, uyarı oluşturma ve raporlama işlemlerini içerir.
"""

from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass

from ..dto import StokBakiyeDTO, UrunDTO
from ..depolar.arayuzler import IStokBakiyeRepository, IUrunRepository
from ..hatalar.stok_hatalari import StokValidationError


@dataclass
class KritikStokUyari:
    """Kritik stok uyarı bilgileri"""
    urun_id: int
    urun_kodu: str
    urun_adi: str
    magaza_id: int
    magaza_adi: str
    depo_id: Optional[int]
    depo_adi: Optional[str]
    mevcut_stok: Decimal
    kritik_seviye: Decimal
    eksik_miktar: Decimal
    uyari_seviyesi: str  # 'KRITIK', 'UYARI', 'ACIL'
    son_hareket_tarihi: Optional[datetime]


class KritikStokService:
    """Kritik stok servisi implementasyonu"""
    
    def __init__(self, 
                 bakiye_repository: IStokBakiyeRepository,
                 urun_repository: IUrunRepository):
        """
        Kritik stok servisi constructor
        
        Args:
            bakiye_repository: Stok bakiye repository
            urun_repository: Ürün repository
        """
        self._bakiye_repository = bakiye_repository
        self._urun_repository = urun_repository
        self._varsayilan_kritik_seviye = Decimal('10.0000')  # Varsayılan kritik seviye
    
    def kritik_stok_listesi(self, 
                           magaza_id: Optional[int] = None,
                           depo_id: Optional[int] = None,
                           sadece_kritik: bool = False) -> List[KritikStokUyari]:
        """
        Kritik stok listesini getirir
        
        Args:
            magaza_id: Mağaza ID filtresi (opsiyonel)
            depo_id: Depo ID filtresi (opsiyonel)
            sadece_kritik: Sadece kritik seviyenin altındaki stokları getir
            
        Returns:
            List[KritikStokUyari]: Kritik stok uyarıları listesi
        """
        # Tüm stok bakiyelerini getir
        bakiyeler = self._bakiye_repository.tum_bakiyeler_getir(magaza_id, depo_id)
        
        kritik_stoklar = []
        
        for bakiye in bakiyeler:
            # Ürün bilgilerini getir
            urun = self._urun_repository.id_ile_getir(bakiye.urun_id)
            if not urun:
                continue
            
            # Kritik seviyeyi belirle
            kritik_seviye = urun.minimum_stok or self._varsayilan_kritik_seviye
            
            # Kritik stok kontrolü
            if bakiye.kullanilabilir_miktar <= kritik_seviye:
                eksik_miktar = kritik_seviye - bakiye.kullanilabilir_miktar
                
                # Uyarı seviyesini belirle
                uyari_seviyesi = self._uyari_seviyesi_belirle(
                    bakiye.kullanilabilir_miktar, kritik_seviye
                )
                
                # Sadece kritik filtresi varsa ve bu kritik değilse atla
                if sadece_kritik and uyari_seviyesi != 'KRITIK':
                    continue
                
                uyari = KritikStokUyari(
                    urun_id=bakiye.urun_id,
                    urun_kodu=urun.urun_kodu,
                    urun_adi=urun.urun_adi,
                    magaza_id=bakiye.magaza_id,
                    magaza_adi=f"Mağaza {bakiye.magaza_id}",  # Gerçek mağaza adı alınabilir
                    depo_id=bakiye.depo_id,
                    depo_adi=f"Depo {bakiye.depo_id}" if bakiye.depo_id else None,
                    mevcut_stok=bakiye.kullanilabilir_miktar,
                    kritik_seviye=kritik_seviye,
                    eksik_miktar=eksik_miktar,
                    uyari_seviyesi=uyari_seviyesi,
                    son_hareket_tarihi=bakiye.son_hareket_tarihi
                )
                
                kritik_stoklar.append(uyari)
        
        # Uyarı seviyesine göre sırala (ACIL > KRITIK > UYARI)
        kritik_stoklar.sort(key=lambda x: (
            {'ACIL': 0, 'KRITIK': 1, 'UYARI': 2}[x.uyari_seviyesi],
            x.eksik_miktar
        ), reverse=True)
        
        return kritik_stoklar
    
    def uyari_olustur(self, 
                     magaza_id: Optional[int] = None,
                     email_gonder: bool = False,
                     sms_gonder: bool = False) -> Dict[str, int]:
        """
        Kritik stok uyarıları oluşturur
        
        Args:
            magaza_id: Mağaza ID filtresi (opsiyonel)
            email_gonder: Email uyarısı gönder
            sms_gonder: SMS uyarısı gönder
            
        Returns:
            Dict[str, int]: Uyarı istatistikleri
        """
        kritik_stoklar = self.kritik_stok_listesi(magaza_id, sadece_kritik=True)
        
        istatistikler = {
            'toplam_uyari': len(kritik_stoklar),
            'acil_uyari': 0,
            'kritik_uyari': 0,
            'uyari_uyari': 0,
            'email_gonderilen': 0,
            'sms_gonderilen': 0
        }
        
        for uyari in kritik_stoklar:
            # İstatistikleri güncelle
            if uyari.uyari_seviyesi == 'ACIL':
                istatistikler['acil_uyari'] += 1
            elif uyari.uyari_seviyesi == 'KRITIK':
                istatistikler['kritik_uyari'] += 1
            else:
                istatistikler['uyari_uyari'] += 1
            
            # Uyarı kaydet (veritabanına)
            self._uyari_kaydet(uyari)
            
            # Email/SMS gönderimi (burada sadece simüle ediyoruz)
            if email_gonder:
                self._email_uyari_gonder(uyari)
                istatistikler['email_gonderilen'] += 1
            
            if sms_gonder:
                self._sms_uyari_gonder(uyari)
                istatistikler['sms_gonderilen'] += 1
        
        return istatistikler
    
    def kritik_seviye_guncelle(self, 
                              urun_id: int, 
                              yeni_kritik_seviye: Decimal) -> bool:
        """
        Ürünün kritik seviyesini günceller
        
        Args:
            urun_id: Ürün ID
            yeni_kritik_seviye: Yeni kritik seviye
            
        Returns:
            bool: Güncelleme başarılı mı
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if urun_id <= 0:
            raise StokValidationError("Geçerli ürün ID gereklidir")
        
        if yeni_kritik_seviye < 0:
            raise StokValidationError("Kritik seviye negatif olamaz")
        
        # Ürünü getir
        urun = self._urun_repository.id_ile_getir(urun_id)
        if not urun:
            raise StokValidationError(f"Ürün bulunamadı: {urun_id}")
        
        # Kritik seviyeyi güncelle
        urun.minimum_stok = yeni_kritik_seviye
        
        return self._urun_repository.guncelle(urun_id, urun)
    
    def depo_bazinda_kritik_stok_raporu(self, 
                                       magaza_id: int) -> Dict[str, List[KritikStokUyari]]:
        """
        Depo bazında kritik stok raporu oluşturur
        
        Args:
            magaza_id: Mağaza ID
            
        Returns:
            Dict[str, List[KritikStokUyari]]: Depo adı -> Kritik stok listesi
        """
        if magaza_id <= 0:
            raise StokValidationError("Geçerli mağaza ID gereklidir")
        
        kritik_stoklar = self.kritik_stok_listesi(magaza_id=magaza_id)
        
        # Depo bazında grupla
        depo_gruplari = {}
        
        for uyari in kritik_stoklar:
            depo_adi = uyari.depo_adi or "Ana Depo"
            
            if depo_adi not in depo_gruplari:
                depo_gruplari[depo_adi] = []
            
            depo_gruplari[depo_adi].append(uyari)
        
        # Her depo için uyarı seviyesine göre sırala
        for depo_adi in depo_gruplari:
            depo_gruplari[depo_adi].sort(
                key=lambda x: {'ACIL': 0, 'KRITIK': 1, 'UYARI': 2}[x.uyari_seviyesi]
            )
        
        return depo_gruplari
    
    def _uyari_seviyesi_belirle(self, 
                               mevcut_stok: Decimal, 
                               kritik_seviye: Decimal) -> str:
        """
        Uyarı seviyesini belirler
        
        Args:
            mevcut_stok: Mevcut stok miktarı
            kritik_seviye: Kritik seviye
            
        Returns:
            str: Uyarı seviyesi ('ACIL', 'KRITIK', 'UYARI')
        """
        if mevcut_stok <= 0:
            return 'ACIL'
        elif mevcut_stok <= kritik_seviye * Decimal('0.5'):
            return 'KRITIK'
        else:
            return 'UYARI'
    
    def _uyari_kaydet(self, uyari: KritikStokUyari) -> None:
        """
        Uyarıyı veritabanına kaydeder
        
        Args:
            uyari: Kritik stok uyarısı
        """
        # Burada uyarı tablosuna kayıt yapılabilir
        # Şimdilik log olarak kaydediyoruz
        print(f"KRITIK STOK UYARI: {uyari.urun_kodu} - {uyari.uyari_seviyesi} - Eksik: {uyari.eksik_miktar}")
    
    def _email_uyari_gonder(self, uyari: KritikStokUyari) -> None:
        """
        Email uyarısı gönderir
        
        Args:
            uyari: Kritik stok uyarısı
        """
        # Email gönderimi simülasyonu
        print(f"EMAIL GÖNDERILDI: {uyari.urun_kodu} kritik seviyede")
    
    def _sms_uyari_gonder(self, uyari: KritikStokUyari) -> None:
        """
        SMS uyarısı gönderir
        
        Args:
            uyari: Kritik stok uyarısı
        """
        # SMS gönderimi simülasyonu
        print(f"SMS GÖNDERILDI: {uyari.urun_kodu} kritik seviyede")