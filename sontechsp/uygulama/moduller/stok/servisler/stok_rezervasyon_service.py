# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.stok_rezervasyon_service
# Description: SONTECHSP stok rezervasyon servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Rezervasyon Servisi

Bu modül stok rezervasyon işlemlerini yöneten servis sınıfını içerir.
E-ticaret entegrasyonu için stok rezervasyon yönetimi sağlar.
"""

from typing import Optional, Dict, List
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass

from ..dto import StokBakiyeDTO
from ..depolar.arayuzler import IStokBakiyeRepository
from ..hatalar.stok_hatalari import StokValidationError, StokYetersizError


@dataclass
class StokRezervasyonu:
    """Stok rezervasyon bilgileri"""
    rezervasyon_id: str
    urun_id: int
    magaza_id: int
    depo_id: Optional[int]
    rezerve_miktar: Decimal
    rezervasyon_tarihi: datetime
    gecerlilik_tarihi: datetime
    durum: str  # 'AKTIF', 'KULLANILDI', 'IPTAL_EDILDI', 'SURESI_DOLDU'
    referans_tablo: Optional[str] = None
    referans_id: Optional[int] = None
    aciklama: Optional[str] = None


class StokRezervasyonService:
    """Stok rezervasyon servisi implementasyonu"""
    
    def __init__(self, bakiye_repository: IStokBakiyeRepository):
        """
        Stok rezervasyon servisi constructor
        
        Args:
            bakiye_repository: Stok bakiye repository
        """
        self._bakiye_repository = bakiye_repository
        self._aktif_rezervasyonlar: Dict[str, StokRezervasyonu] = {}
        self._varsayilan_gecerlilik_suresi = timedelta(hours=2)  # 2 saat
    
    def rezervasyon_yap(self,
                       urun_id: int,
                       magaza_id: int,
                       miktar: Decimal,
                       depo_id: Optional[int] = None,
                       gecerlilik_suresi: Optional[timedelta] = None,
                       referans_tablo: Optional[str] = None,
                       referans_id: Optional[int] = None,
                       aciklama: Optional[str] = None) -> str:
        """
        Stok rezervasyonu yapar (Ana koordinasyon fonksiyonu)
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            miktar: Rezerve edilecek miktar
            depo_id: Depo ID (opsiyonel)
            gecerlilik_suresi: Rezervasyon geçerlilik süresi
            referans_tablo: Referans tablo adı
            referans_id: Referans kayıt ID
            aciklama: Rezervasyon açıklaması
            
        Returns:
            str: Rezervasyon ID
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
            StokYetersizError: Yetersiz stok durumunda
        """
        # 1. Doğrulama
        self._rezervasyon_dogrula(urun_id, magaza_id, miktar, depo_id)
        
        # 2. Rezervasyon oluştur
        rezervasyon_id = self._rezervasyon_olustur(
            urun_id, magaza_id, miktar, depo_id, 
            gecerlilik_suresi, referans_tablo, referans_id, aciklama
        )
        
        # 3. Stok bakiyesinde rezervasyon yap
        self._stok_rezerve_et(urun_id, magaza_id, miktar, depo_id)
        
        return rezervasyon_id
    
    def _rezervasyon_dogrula(self, urun_id: int, magaza_id: int, 
                            miktar: Decimal, depo_id: Optional[int]) -> None:
        """
        Rezervasyon parametrelerini doğrular ve stok kontrolü yapar
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            miktar: Rezerve edilecek miktar
            depo_id: Depo ID
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
            StokYetersizError: Yetersiz stok durumunda
        """
        # Parametre validasyonu
        self._validate_rezervasyon_parametreleri(urun_id, magaza_id, miktar)
        
        # Mevcut kullanılabilir stok miktarını al
        kullanilabilir_miktar = self.kullanilabilir_stok_getir(urun_id, magaza_id, depo_id)
        
        if kullanilabilir_miktar <= 0:
            raise StokYetersizError(
                f"Stok bulunamadı",
                urun_kodu=f"ID:{urun_id}",
                kullanilabilir_stok=Decimal('0'),
                talep_edilen_miktar=miktar
            )
        
        # Kullanılabilir stok kontrolü
        if kullanilabilir_miktar < miktar:
            raise StokYetersizError(
                f"Yetersiz kullanılabilir stok. Mevcut: {kullanilabilir_miktar}, Talep: {miktar}",
                urun_kodu=f"ID:{urun_id}",
                kullanilabilir_stok=kullanilabilir_miktar,
                talep_edilen_miktar=miktar
            )
    
    def _rezervasyon_olustur(self, urun_id: int, magaza_id: int, miktar: Decimal,
                            depo_id: Optional[int], gecerlilik_suresi: Optional[timedelta],
                            referans_tablo: Optional[str], referans_id: Optional[int],
                            aciklama: Optional[str]) -> str:
        """
        Rezervasyon kaydını oluşturur
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            miktar: Rezerve edilecek miktar
            depo_id: Depo ID
            gecerlilik_suresi: Geçerlilik süresi
            referans_tablo: Referans tablo
            referans_id: Referans ID
            aciklama: Açıklama
            
        Returns:
            str: Rezervasyon ID
        """
        # Rezervasyon ID oluştur
        rezervasyon_id = f"RZV_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Geçerlilik süresini belirle
        gecerlilik_suresi = gecerlilik_suresi or self._varsayilan_gecerlilik_suresi
        gecerlilik_tarihi = datetime.utcnow() + gecerlilik_suresi
        
        # Rezervasyon oluştur
        rezervasyon = StokRezervasyonu(
            rezervasyon_id=rezervasyon_id,
            urun_id=urun_id,
            magaza_id=magaza_id,
            depo_id=depo_id,
            rezerve_miktar=miktar,
            rezervasyon_tarihi=datetime.utcnow(),
            gecerlilik_tarihi=gecerlilik_tarihi,
            durum='AKTIF',
            referans_tablo=referans_tablo,
            referans_id=referans_id,
            aciklama=aciklama
        )
        
        # Rezervasyonu kaydet
        self._aktif_rezervasyonlar[rezervasyon_id] = rezervasyon
        
        return rezervasyon_id
    
    def _stok_rezerve_et(self, urun_id: int, magaza_id: int, 
                        miktar: Decimal, depo_id: Optional[int]) -> None:
        """
        Stok bakiyesinde rezervasyon yapar
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            miktar: Rezerve edilecek miktar
            depo_id: Depo ID
        """
        self._bakiye_repository.rezervasyon_yap(
            urun_id, magaza_id, miktar, depo_id
        )
    
    def rezervasyon_iptal(self, rezervasyon_id: str) -> bool:
        """
        Rezervasyonu iptal eder
        
        Args:
            rezervasyon_id: Rezervasyon ID
            
        Returns:
            bool: İptal başarılı mı
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if rezervasyon_id not in self._aktif_rezervasyonlar:
            raise StokValidationError(f"Rezervasyon bulunamadı: {rezervasyon_id}")
        
        rezervasyon = self._aktif_rezervasyonlar[rezervasyon_id]
        
        if rezervasyon.durum != 'AKTIF':
            raise StokValidationError(f"Sadece aktif rezervasyonlar iptal edilebilir. Durum: {rezervasyon.durum}")
        
        # Stok bakiyesinde rezervasyonu iptal et
        self._bakiye_repository.rezervasyon_iptal(
            rezervasyon.urun_id,
            rezervasyon.magaza_id,
            rezervasyon.rezerve_miktar,
            rezervasyon.depo_id
        )
        
        # Rezervasyon durumunu güncelle
        rezervasyon.durum = 'IPTAL_EDILDI'
        
        return True
    
    def rezervasyon_kullan(self, rezervasyon_id: str, kullanilan_miktar: Optional[Decimal] = None) -> bool:
        """
        Rezervasyonu kullanır (stok düşümü yapar)
        
        Args:
            rezervasyon_id: Rezervasyon ID
            kullanilan_miktar: Kullanılan miktar (None ise tüm rezervasyon)
            
        Returns:
            bool: Kullanım başarılı mı
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if rezervasyon_id not in self._aktif_rezervasyonlar:
            raise StokValidationError(f"Rezervasyon bulunamadı: {rezervasyon_id}")
        
        rezervasyon = self._aktif_rezervasyonlar[rezervasyon_id]
        
        if rezervasyon.durum != 'AKTIF':
            raise StokValidationError(f"Sadece aktif rezervasyonlar kullanılabilir. Durum: {rezervasyon.durum}")
        
        # Kullanılan miktarı belirle
        kullanilan_miktar = kullanilan_miktar or rezervasyon.rezerve_miktar
        
        if kullanilan_miktar > rezervasyon.rezerve_miktar:
            raise StokValidationError(
                f"Kullanılan miktar rezerve miktardan büyük olamaz. "
                f"Rezerve: {rezervasyon.rezerve_miktar}, Kullanılan: {kullanilan_miktar}"
            )
        
        # Stok bakiyesini güncelle - önce rezervasyonu iptal et, sonra stok düşümü yap
        self._bakiye_repository.rezervasyon_iptal(
            rezervasyon.urun_id,
            rezervasyon.magaza_id,
            kullanilan_miktar,
            rezervasyon.depo_id
        )
        
        # Stok düşümü yap (negatif miktar ile güncelleme)
        self._bakiye_repository.bakiye_guncelle(
            rezervasyon.urun_id,
            rezervasyon.magaza_id,
            -kullanilan_miktar,
            rezervasyon.depo_id
        )
        
        # Rezervasyon durumunu güncelle
        if kullanilan_miktar == rezervasyon.rezerve_miktar:
            rezervasyon.durum = 'KULLANILDI'
        else:
            # Kısmi kullanım - rezerve miktarını azalt
            rezervasyon.rezerve_miktar -= kullanilan_miktar
        
        return True
    
    def kullanilabilir_stok_getir(self, 
                                 urun_id: int, 
                                 magaza_id: int, 
                                 depo_id: Optional[int] = None) -> Decimal:
        """
        Kullanılabilir stok miktarını getirir (toplam - rezerve)
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            Decimal: Kullanılabilir stok miktarı
        """
        bakiye = self._bakiye_repository.bakiye_getir(urun_id, magaza_id, depo_id)
        
        if not bakiye:
            return Decimal('0')
        
        return bakiye.kullanilabilir_miktar
    
    def rezervasyon_bilgisi_getir(self, rezervasyon_id: str) -> Optional[StokRezervasyonu]:
        """
        Rezervasyon bilgilerini getirir
        
        Args:
            rezervasyon_id: Rezervasyon ID
            
        Returns:
            Optional[StokRezervasyonu]: Rezervasyon bilgileri
        """
        return self._aktif_rezervasyonlar.get(rezervasyon_id)
    
    def aktif_rezervasyonlar_listesi(self, 
                                   urun_id: Optional[int] = None,
                                   magaza_id: Optional[int] = None) -> List[StokRezervasyonu]:
        """
        Aktif rezervasyonların listesini getirir
        
        Args:
            urun_id: Ürün ID filtresi (opsiyonel)
            magaza_id: Mağaza ID filtresi (opsiyonel)
            
        Returns:
            List[StokRezervasyonu]: Aktif rezervasyonlar listesi
        """
        rezervasyonlar = []
        
        for rezervasyon in self._aktif_rezervasyonlar.values():
            if rezervasyon.durum != 'AKTIF':
                continue
            
            if urun_id is not None and rezervasyon.urun_id != urun_id:
                continue
            
            if magaza_id is not None and rezervasyon.magaza_id != magaza_id:
                continue
            
            rezervasyonlar.append(rezervasyon)
        
        # Rezervasyon tarihine göre sırala (en yeni önce)
        rezervasyonlar.sort(key=lambda r: r.rezervasyon_tarihi, reverse=True)
        
        return rezervasyonlar
    
    def suresi_dolan_rezervasyonlari_temizle(self) -> int:
        """
        Süresi dolan rezervasyonları temizler
        
        Returns:
            int: Temizlenen rezervasyon sayısı
        """
        simdi = datetime.utcnow()
        temizlenen_sayisi = 0
        
        for rezervasyon_id, rezervasyon in list(self._aktif_rezervasyonlar.items()):
            if rezervasyon.durum == 'AKTIF' and rezervasyon.gecerlilik_tarihi < simdi:
                # Rezervasyonu iptal et
                try:
                    self.rezervasyon_iptal(rezervasyon_id)
                    rezervasyon.durum = 'SURESI_DOLDU'
                    temizlenen_sayisi += 1
                except Exception:
                    # Hata durumunda sadece durumu güncelle
                    rezervasyon.durum = 'SURESI_DOLDU'
                    temizlenen_sayisi += 1
        
        return temizlenen_sayisi
    
    def _validate_rezervasyon_parametreleri(self,
                                          urun_id: int,
                                          magaza_id: int,
                                          miktar: Decimal) -> None:
        """
        Rezervasyon parametrelerini doğrular
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            miktar: Rezerve edilecek miktar
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if urun_id <= 0:
            raise StokValidationError("Geçerli ürün ID gereklidir")
        
        if magaza_id <= 0:
            raise StokValidationError("Geçerli mağaza ID gereklidir")
        
        if miktar <= 0:
            raise StokValidationError("Rezerve edilecek miktar pozitif olmalıdır")
        
        if miktar > Decimal('999999.9999'):
            raise StokValidationError("Rezerve edilecek miktar çok büyük")