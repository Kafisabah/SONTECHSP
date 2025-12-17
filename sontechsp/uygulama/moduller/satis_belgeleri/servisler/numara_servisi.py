# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.servisler.numara_servisi
# Description: Belge numarası üretim servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Belge Numarası Üretim Servisi

Bu servis belge numarası üretimi ve yönetimini sağlar:
- Benzersiz numara üretimi
- Mağaza bazlı sayaç yönetimi
- Ay değişiminde sıfırlama
- Çakışma durumunda retry mekanizması
"""

import logging
from datetime import datetime
from typing import Optional

from ....cekirdek.hatalar import IsKuraliHatasi, VeriTabaniHatasi
from ..modeller import BelgeTuru, NumaraSayaci
from ..depolar.numara_sayac_deposu import INumaraSayacDeposu

logger = logging.getLogger(__name__)


class NumaraServisi:
    """
    Belge numarası üretim servisi
    
    Bu servis belge numaralarının benzersiz ve sıralı olmasını garanti eder.
    Format: MGZ-YYYY-MM-NNNN
    """
    
    def __init__(self, numara_sayac_deposu: INumaraSayacDeposu):
        self._numara_sayac_deposu = numara_sayac_deposu
        self._max_retry = 3
    
    def numara_uret(
        self, 
        magaza_id: int, 
        magaza_kodu: str, 
        belge_turu: BelgeTuru
    ) -> str:
        """
        Yeni belge numarası üret
        
        Args:
            magaza_id: Mağaza ID
            magaza_kodu: Mağaza kodu (3 karakter)
            belge_turu: Belge türü
            
        Returns:
            Üretilen belge numarası
            
        Raises:
            IsKuraliHatasi: Geçersiz parametreler
            VeriTabaniHatasi: Numara üretimi başarısız
        """
        if not magaza_id or magaza_id <= 0:
            raise IsKuraliHatasi("Geçerli bir mağaza ID belirtilmelidir")
        
        if not magaza_kodu or len(magaza_kodu) != 3:
            raise IsKuraliHatasi("Mağaza kodu 3 karakter olmalıdır")
        
        if not belge_turu:
            raise IsKuraliHatasi("Belge türü belirtilmelidir")
        
        # Mevcut tarih bilgileri
        simdi = datetime.now()
        yil = simdi.year
        ay = simdi.month
        
        # Retry mekanizması ile numara üret
        for deneme in range(self._max_retry):
            try:
                # Sayacı al veya oluştur
                sayac = self._sayac_al_veya_olustur(magaza_id, belge_turu, yil, ay)
                
                # Sonraki numarayı al
                yeni_numara = sayac.sonraki_numara()
                
                # Sayacı güncelle
                self._numara_sayac_deposu.guncelle(sayac)
                
                # Formatlanmış numarayı döndür
                belge_numarasi = sayac.numara_formatla(magaza_kodu, yeni_numara)
                
                logger.info(
                    f"Belge numarası üretildi: {belge_numarasi} "
                    f"(Mağaza: {magaza_id}, Tür: {belge_turu.value}, Deneme: {deneme + 1})"
                )
                
                return belge_numarasi
                
            except Exception as e:
                logger.warning(
                    f"Numara üretimi başarısız (Deneme {deneme + 1}/{self._max_retry}): {e}"
                )
                
                if deneme == self._max_retry - 1:
                    raise VeriTabaniHatasi(f"Numara üretimi başarısız: {e}")
                
                # Kısa bekleme
                import time
                time.sleep(0.1)
        
        raise VeriTabaniHatasi("Numara üretimi maksimum deneme sayısını aştı")
    
    def numara_rezerve_et(
        self, 
        magaza_id: int, 
        magaza_kodu: str, 
        belge_turu: BelgeTuru
    ) -> str:
        """
        Belge numarası rezerve et (henüz kullanılmayacak)
        
        Bu metod gelecekte kullanım için numara rezerve eder.
        Şu an için numara_uret ile aynı işlevi görür.
        """
        return self.numara_uret(magaza_id, magaza_kodu, belge_turu)
    
    def ay_degisimi_kontrol_et(self, magaza_id: int, belge_turu: BelgeTuru) -> bool:
        """
        Ay değişimi kontrolü yap ve gerekirse sayacı sıfırla
        
        Args:
            magaza_id: Mağaza ID
            belge_turu: Belge türü
            
        Returns:
            Sayaç sıfırlandı mı?
        """
        simdi = datetime.now()
        yil = simdi.year
        ay = simdi.month
        
        try:
            # Mevcut sayacı bul
            mevcut_sayac = self._numara_sayac_deposu.bul_magaza_tur_yil_ay(
                magaza_id, belge_turu, yil, ay
            )
            
            # Eğer bu ay için sayaç yoksa, önceki aydan sıfırla
            if not mevcut_sayac:
                # Önceki ay sayacını bul
                onceki_sayac = self._numara_sayac_deposu.bul_son_sayac(
                    magaza_id, belge_turu
                )
                
                if onceki_sayac and (onceki_sayac.yil != yil or onceki_sayac.ay != ay):
                    logger.info(
                        f"Ay değişimi tespit edildi. Sayaç sıfırlanacak: "
                        f"Mağaza {magaza_id}, Tür {belge_turu.value}, "
                        f"Önceki: {onceki_sayac.yil}-{onceki_sayac.ay}, "
                        f"Yeni: {yil}-{ay}"
                    )
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ay değişimi kontrolü başarısız: {e}")
            return False
    
    def _sayac_al_veya_olustur(
        self, 
        magaza_id: int, 
        belge_turu: BelgeTuru, 
        yil: int, 
        ay: int
    ) -> NumaraSayaci:
        """
        Sayacı al, yoksa oluştur
        
        Args:
            magaza_id: Mağaza ID
            belge_turu: Belge türü
            yil: Yıl
            ay: Ay
            
        Returns:
            NumaraSayaci instance
        """
        # Mevcut sayacı bul
        sayac = self._numara_sayac_deposu.bul_magaza_tur_yil_ay(
            magaza_id, belge_turu, yil, ay
        )
        
        if sayac:
            return sayac
        
        # Yeni sayaç oluştur
        yeni_sayac = NumaraSayaci(
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=yil,
            ay=ay,
            son_numara=0
        )
        
        # Doğrulama
        hatalar = yeni_sayac.dogrula()
        if hatalar:
            raise IsKuraliHatasi(f"Sayaç doğrulama hatası: {', '.join(hatalar)}")
        
        # Veritabanına kaydet
        kaydedilen_sayac = self._numara_sayac_deposu.ekle(yeni_sayac)
        
        logger.info(
            f"Yeni sayaç oluşturuldu: Mağaza {magaza_id}, "
            f"Tür {belge_turu.value}, {yil}-{ay:02d}"
        )
        
        return kaydedilen_sayac
    
    def sayac_durumu_al(
        self, 
        magaza_id: int, 
        belge_turu: BelgeTuru
    ) -> Optional[NumaraSayaci]:
        """
        Mağaza ve belge türü için mevcut sayaç durumunu al
        
        Args:
            magaza_id: Mağaza ID
            belge_turu: Belge türü
            
        Returns:
            Mevcut sayaç veya None
        """
        try:
            return self._numara_sayac_deposu.bul_son_sayac(magaza_id, belge_turu)
        except Exception as e:
            logger.error(f"Sayaç durumu alınamadı: {e}")
            return None
    
    def sayac_sifirla(
        self, 
        magaza_id: int, 
        belge_turu: BelgeTuru, 
        yil: int, 
        ay: int
    ) -> bool:
        """
        Belirtilen sayacı sıfırla
        
        Args:
            magaza_id: Mağaza ID
            belge_turu: Belge türü
            yil: Yıl
            ay: Ay
            
        Returns:
            Sıfırlama başarılı mı?
        """
        try:
            sayac = self._numara_sayac_deposu.bul_magaza_tur_yil_ay(
                magaza_id, belge_turu, yil, ay
            )
            
            if sayac:
                sayac.sifirla()
                self._numara_sayac_deposu.guncelle(sayac)
                
                logger.info(
                    f"Sayaç sıfırlandı: Mağaza {magaza_id}, "
                    f"Tür {belge_turu.value}, {yil}-{ay:02d}"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Sayaç sıfırlama başarısız: {e}")
            return False