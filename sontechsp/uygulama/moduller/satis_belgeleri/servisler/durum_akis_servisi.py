# Version: 0.1.0
# Last Update: 2024-12-17
# Module: satis_belgeleri.servisler.durum_akis_servisi
# Description: Belge durum akış yönetim servisi
# Changelog:
# - İlk oluşturma
# - Durum geçmişi kaydetme fonksiyonu eklendi

"""
SONTECHSP Belge Durum Akış Servisi

Bu servis belge durum geçişlerini yönetir:
- Durum geçiş kuralları
- Geçerli/geçersiz geçiş kontrolü
- Durum geçmiş takibi
- İptal işlemleri
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ....cekirdek.hatalar import IsKuraliHatasi, VeriTabaniHatasi
from ..depolar.belge_durum_gecmisi_deposu import IBelgeDurumGecmisiDeposu
from ..modeller.satis_belgesi import SatisBelgesi, BelgeDurumu

logger = logging.getLogger(__name__)


class DurumAkisServisi:
    """
    Belge durum akış yönetim servisi
    
    Bu servis belge durumları arasındaki geçişleri kontrol eder ve yönetir.
    """
    
    # Durum geçiş kuralları
    GECERLI_GECISLER: Dict[BelgeDurumu, List[BelgeDurumu]] = {
        BelgeDurumu.TASLAK: [BelgeDurumu.ONAYLANDI, BelgeDurumu.IPTAL],
        BelgeDurumu.ONAYLANDI: [BelgeDurumu.FATURALANDI, BelgeDurumu.IPTAL],
        BelgeDurumu.FATURALANDI: [BelgeDurumu.IPTAL],
        BelgeDurumu.IPTAL: []  # İptal durumundan çıkış yok
    }
    
    def __init__(self, gecmis_deposu: IBelgeDurumGecmisiDeposu):
        """Durum akış servisi başlatıcı
        
        Args:
            gecmis_deposu: Belge durum geçmişi deposu
        """
        self._durum_gecmisi_deposu = gecmis_deposu
    
    def durum_guncelle(
        self, 
        belge: SatisBelgesi, 
        yeni_durum: BelgeDurumu,
        degistiren_kullanici_id: int,
        aciklama: Optional[str] = None
    ) -> bool:
        """
        Belge durumunu güncelle
        
        Args:
            belge: Güncellenecek belge
            yeni_durum: Yeni durum
            degistiren_kullanici_id: Durumu değiştiren kullanıcı ID
            aciklama: Durum değişikliği açıklaması
            
        Returns:
            Güncelleme başarılı mı?
            
        Raises:
            IsKuraliHatasi: Geçersiz durum geçişi
            VeriTabaniHatasi: Veritabanı hatası
        """
        if not belge or not belge.belge_id:
            raise IsKuraliHatasi("Geçerli bir belge belirtilmelidir")
        
        if not degistiren_kullanici_id or degistiren_kullanici_id <= 0:
            raise IsKuraliHatasi("Geçerli bir kullanıcı ID belirtilmelidir")
        
        # Mevcut durum ile aynı ise işlem yapma
        if belge.belge_durumu == yeni_durum:
            logger.info(f"Belge {belge.belge_id} zaten {yeni_durum.value} durumunda")
            return True
        
        # Durum geçiş kontrolü
        if not self.durum_degistirilebilir_mi(belge.belge_durumu, yeni_durum):
            raise IsKuraliHatasi(
                f"Belge durumu {belge.belge_durumu.value} -> {yeni_durum.value} "
                f"geçişi geçerli değil"
            )
        
        try:
            # Eski durumu kaydet
            eski_durum = belge.belge_durumu
            
            # Belge durumunu güncelle
            belge.belge_durumu = yeni_durum
            belge.guncelleme_tarihi = datetime.now()
            
            # Durum geçmişini kaydet
            self._durum_gecmisi_kaydet(
                belge.belge_id,
                eski_durum,
                yeni_durum,
                degistiren_kullanici_id,
                aciklama
            )
            
            logger.info(
                f"Belge {belge.belge_id} durumu güncellendi: "
                f"{eski_durum.value} -> {yeni_durum.value}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Durum güncelleme hatası: {e}")
            raise VeriTabaniHatasi(f"Durum güncellenemedi: {e}")
    
    def durum_degistirilebilir_mi(
        self, 
        mevcut_durum: BelgeDurumu, 
        yeni_durum: BelgeDurumu
    ) -> bool:
        """
        Belirtilen durum geçişinin geçerli olup olmadığını kontrol et
        
        Args:
            mevcut_durum: Mevcut durum
            yeni_durum: Hedef durum
            
        Returns:
            Geçiş geçerli mi?
        """
        gecerli_gecisler = self.GECERLI_GECISLER.get(mevcut_durum, [])
        return yeni_durum in gecerli_gecisler
    
    def gecerli_gecisleri_al(self, mevcut_durum: BelgeDurumu) -> List[BelgeDurumu]:
        """
        Mevcut durumdan yapılabilecek geçerli geçişleri al
        
        Args:
            mevcut_durum: Mevcut durum
            
        Returns:
            Geçerli durum listesi
        """
        return self.GECERLI_GECISLER.get(mevcut_durum, []).copy()
    
    def belge_iptal_et(
        self, 
        belge: SatisBelgesi, 
        iptal_nedeni: str,
        degistiren_kullanici_id: int
    ) -> bool:
        """
        Belgeyi iptal et
        
        Args:
            belge: İptal edilecek belge
            iptal_nedeni: İptal nedeni
            degistiren_kullanici_id: İptal eden kullanıcı ID
            
        Returns:
            İptal başarılı mı?
            
        Raises:
            IsKuraliHatasi: İptal edilemez durum
        """
        if not iptal_nedeni or not iptal_nedeni.strip():
            raise IsKuraliHatasi("İptal nedeni belirtilmelidir")
        
        # İptal edilebilir mi kontrol et
        if not self.durum_degistirilebilir_mi(belge.belge_durumu, BelgeDurumu.IPTAL):
            raise IsKuraliHatasi(
                f"Belge {belge.belge_durumu.value} durumundan iptal edilemez"
            )
        
        try:
            # Belgeyi iptal et
            belge.iptal_nedeni = iptal_nedeni
            belge.iptal_tarihi = datetime.now()
            
            # Durum geçişini kaydet
            return self.durum_guncelle(
                belge, 
                BelgeDurumu.IPTAL, 
                degistiren_kullanici_id,
                f"İptal nedeni: {iptal_nedeni}"
            )
            
        except Exception as e:
            logger.error(f"Belge iptal hatası: {e}")
            raise VeriTabaniHatasi(f"Belge iptal edilemedi: {e}")
    
    def durum_gecmisi_al(self, belge_id: int) -> List[Dict]:
        """
        Belge durum değişiklik geçmişini al
        
        Args:
            belge_id: Belge ID
            
        Returns:
            Durum geçmiş listesi
        """
        try:
            gecmis_kayitlari = self._durum_gecmisi_deposu.belge_gecmisi_al(belge_id)
            
            gecmis_listesi = []
            for kayit in gecmis_kayitlari:
                gecmis_listesi.append({
                    'eski_durum': kayit.eski_durum,
                    'yeni_durum': kayit.yeni_durum,
                    'degistiren_kullanici_id': kayit.degistiren_kullanici_id,
                    'aciklama': kayit.aciklama,
                    'tarih': kayit.olusturma_tarihi
                })
            
            return gecmis_listesi
            
        except Exception as e:
            logger.error(f"Durum geçmişi alma hatası: {e}")
            return []
    
    def durum_istatistikleri_al(self, belge_id: int) -> Dict:
        """
        Belge durum istatistiklerini al
        
        Args:
            belge_id: Belge ID
            
        Returns:
            Durum istatistikleri
        """
        try:
            gecmis = self.durum_gecmisi_al(belge_id)
            
            if not gecmis:
                return {
                    'toplam_degisiklik': 0,
                    'ilk_durum': None,
                    'son_durum': None,
                    'degisiklik_sayisi_duruma_gore': {}
                }
            
            # İstatistikleri hesapla
            duruma_gore_sayim = {}
            for kayit in gecmis:
                yeni_durum = kayit['yeni_durum']
                duruma_gore_sayim[yeni_durum] = duruma_gore_sayim.get(yeni_durum, 0) + 1
            
            return {
                'toplam_degisiklik': len(gecmis),
                'ilk_durum': gecmis[0]['yeni_durum'] if gecmis else None,
                'son_durum': gecmis[-1]['yeni_durum'] if gecmis else None,
                'degisiklik_sayisi_duruma_gore': duruma_gore_sayim
            }
            
        except Exception as e:
            logger.error(f"Durum istatistikleri alma hatası: {e}")
            return {}
    
    def toplu_durum_guncelle(
        self, 
        belge_listesi: List[SatisBelgesi],
        yeni_durum: BelgeDurumu,
        degistiren_kullanici_id: int,
        aciklama: Optional[str] = None
    ) -> Dict[int, bool]:
        """
        Birden fazla belgenin durumunu toplu güncelle
        
        Args:
            belge_listesi: Güncellenecek belgeler
            yeni_durum: Yeni durum
            degistiren_kullanici_id: Durumu değiştiren kullanıcı ID
            aciklama: Durum değişikliği açıklaması
            
        Returns:
            Belge ID -> başarı durumu mapping
        """
        sonuclar = {}
        
        for belge in belge_listesi:
            try:
                basarili = self.durum_guncelle(
                    belge, yeni_durum, degistiren_kullanici_id, aciklama
                )
                sonuclar[belge.belge_id] = basarili
                
            except Exception as e:
                logger.error(f"Belge {belge.belge_id} durum güncelleme hatası: {e}")
                sonuclar[belge.belge_id] = False
        
        return sonuclar
    
    def _durum_gecmisi_kaydet(
        self,
        belge_id: int,
        eski_durum: Optional[BelgeDurumu],
        yeni_durum: BelgeDurumu,
        degistiren_kullanici_id: int,
        aciklama: Optional[str]
    ) -> None:
        """
        Durum değişikliğini geçmişe kaydet
        
        Args:
            belge_id: Belge ID
            eski_durum: Eski durum
            yeni_durum: Yeni durum
            degistiren_kullanici_id: Değiştiren kullanıcı ID
            aciklama: Açıklama
        """
        try:
            from ..modeller.belge_durum_gecmisi import BelgeDurumGecmisi
            
            gecmis_kaydi = BelgeDurumGecmisi(
                belge_id=belge_id,
                eski_durum=eski_durum.value if eski_durum else None,
                yeni_durum=yeni_durum.value,
                degistiren_kullanici_id=degistiren_kullanici_id,
                aciklama=aciklama
            )
            
            self._durum_gecmisi_deposu.ekle(gecmis_kaydi)
            
        except Exception as e:
            logger.error(f"Durum geçmişi kaydetme hatası: {e}")
            # Geçmiş kaydı başarısız olsa da ana işlemi durdurmayalım
            pass