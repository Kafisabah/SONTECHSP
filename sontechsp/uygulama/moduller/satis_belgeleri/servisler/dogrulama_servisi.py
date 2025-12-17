# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.servisler.dogrulama_servisi
# Description: Veri doğrulama servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Veri Doğrulama Servisi

Bu servis belge ve satır bilgileri doğrulama işlemlerini sağlar:
- Belge doğrulama kuralları
- Satır doğrulama kuralları
- Toplam tutar hesaplama ve doğrulama
- KDV hesaplama fonksiyonları
"""

import logging
from decimal import Decimal
from typing import List, Dict, Any, Optional

from ....cekirdek.hatalar import IsKuraliHatasi, DogrulamaHatasi
from ..modeller import SatisBelgesi, BelgeSatiri, BelgeTuru, BelgeDurumu

logger = logging.getLogger(__name__)


class DogrulamaServisi:
    """
    Veri doğrulama servisi
    
    Bu servis belge ve satır verilerinin doğruluğunu kontrol eder.
    """
    
    # KDV oranları (varsayılan değerler)
    VARSAYILAN_KDV_ORANLARI = {
        'STANDART': Decimal('18.00'),
        'INDIRIMLI': Decimal('8.00'),
        'MUAF': Decimal('0.00')
    }
    
    def __init__(self):
        self._maksimum_satir_sayisi = 1000
        self._maksimum_tutar = Decimal('999999999.99')
        self._minimum_tutar = Decimal('0.00')
    
    def belge_dogrula(self, belge: SatisBelgesi) -> List[str]:
        """
        Belge doğrulaması yap
        
        Args:
            belge: Doğrulanacak belge
            
        Returns:
            Hata listesi (boş ise doğrulama başarılı)
        """
        hatalar = []
        
        try:
            # Temel alan doğrulamaları
            hatalar.extend(self._temel_alan_dogrulama(belge))
            
            # Belge türü özel doğrulamaları
            hatalar.extend(self._belge_turu_dogrulama(belge))
            
            # Satır doğrulamaları
            hatalar.extend(self._belge_satirlari_dogrulama(belge))
            
            # Tutar doğrulamaları
            hatalar.extend(self._tutar_dogrulama(belge))
            
            # İş kuralı doğrulamaları
            hatalar.extend(self._is_kurali_dogrulama(belge))
            
        except Exception as e:
            logger.error(f"Belge doğrulama hatası: {e}")
            hatalar.append(f"Doğrulama işlemi sırasında hata oluştu: {e}")
        
        return hatalar
    
    def satir_dogrula(self, satir: BelgeSatiri) -> List[str]:
        """
        Belge satırı doğrulaması yap
        
        Args:
            satir: Doğrulanacak satır
            
        Returns:
            Hata listesi (boş ise doğrulama başarılı)
        """
        hatalar = []
        
        try:
            # Temel alan doğrulamaları
            hatalar.extend(self._satir_temel_dogrulama(satir))
            
            # Tutar hesaplama doğrulamaları
            hatalar.extend(self._satir_tutar_dogrulama(satir))
            
            # KDV doğrulamaları
            hatalar.extend(self._satir_kdv_dogrulama(satir))
            
        except Exception as e:
            logger.error(f"Satır doğrulama hatası: {e}")
            hatalar.append(f"Satır doğrulama işlemi sırasında hata oluştu: {e}")
        
        return hatalar
    
    def toplam_tutarlari_hesapla(self, belge: SatisBelgesi) -> Dict[str, Decimal]:
        """
        Belge toplam tutarlarını hesapla
        
        Args:
            belge: Hesaplanacak belge
            
        Returns:
            Hesaplanan tutarlar
        """
        try:
            toplam_tutar = Decimal('0.00')
            kdv_tutari = Decimal('0.00')
            
            for satir in belge.satirlar:
                # Satır tutarlarını hesapla
                satir_tutarlari = self.satir_tutarlari_hesapla(satir)
                
                toplam_tutar += satir_tutarlari['satir_tutari']
                kdv_tutari += satir_tutarlari['kdv_tutari']
            
            genel_toplam = toplam_tutar + kdv_tutari
            
            return {
                'toplam_tutar': toplam_tutar,
                'kdv_tutari': kdv_tutari,
                'genel_toplam': genel_toplam
            }
            
        except Exception as e:
            logger.error(f"Toplam tutar hesaplama hatası: {e}")
            raise IsKuraliHatasi(f"Toplam tutarlar hesaplanamadı: {e}")
    
    def satir_tutarlari_hesapla(self, satir: BelgeSatiri) -> Dict[str, Decimal]:
        """
        Satır tutarlarını hesapla
        
        Args:
            satir: Hesaplanacak satır
            
        Returns:
            Hesaplanan tutarlar
        """
        try:
            # Satır tutarı = miktar * birim_fiyat
            satir_tutari = satir.miktar * satir.birim_fiyat
            
            # KDV tutarı = satır_tutarı * (kdv_oranı / 100)
            kdv_tutari = satir_tutari * (satir.kdv_orani / Decimal('100'))
            
            # Satır toplamı = satır_tutarı + kdv_tutarı
            satir_toplami = satir_tutari + kdv_tutari
            
            return {
                'satir_tutari': satir_tutari,
                'kdv_tutari': kdv_tutari,
                'satir_toplami': satir_toplami
            }
            
        except Exception as e:
            logger.error(f"Satır tutar hesaplama hatası: {e}")
            raise IsKuraliHatasi(f"Satır tutarları hesaplanamadı: {e}")
    
    def kdv_orani_dogrula(self, kdv_orani: Decimal) -> bool:
        """
        KDV oranının geçerli olup olmadığını kontrol et
        
        Args:
            kdv_orani: Kontrol edilecek KDV oranı
            
        Returns:
            Geçerli mi?
        """
        # KDV oranı 0-100 arasında olmalı
        if kdv_orani < Decimal('0') or kdv_orani > Decimal('100'):
            return False
        
        # Bilinen KDV oranları ile karşılaştır
        bilinen_oranlar = list(self.VARSAYILAN_KDV_ORANLARI.values())
        
        # Tam eşleşme veya makul aralıkta olmalı
        return kdv_orani in bilinen_oranlar or Decimal('0') <= kdv_orani <= Decimal('50')
    
    def tutar_tutarliligi_kontrol_et(self, belge: SatisBelgesi) -> List[str]:
        """
        Belge tutar tutarlılığını kontrol et
        
        Args:
            belge: Kontrol edilecek belge
            
        Returns:
            Tutarsızlık hataları
        """
        hatalar = []
        
        try:
            # Hesaplanan tutarları al
            hesaplanan = self.toplam_tutarlari_hesapla(belge)
            
            # Belgedeki tutarlar ile karşılaştır
            if belge.toplam_tutar != hesaplanan['toplam_tutar']:
                hatalar.append(
                    f"Toplam tutar tutarsızlığı: "
                    f"Belge={belge.toplam_tutar}, Hesaplanan={hesaplanan['toplam_tutar']}"
                )
            
            if belge.kdv_tutari != hesaplanan['kdv_tutari']:
                hatalar.append(
                    f"KDV tutarı tutarsızlığı: "
                    f"Belge={belge.kdv_tutari}, Hesaplanan={hesaplanan['kdv_tutari']}"
                )
            
            if belge.genel_toplam != hesaplanan['genel_toplam']:
                hatalar.append(
                    f"Genel toplam tutarsızlığı: "
                    f"Belge={belge.genel_toplam}, Hesaplanan={hesaplanan['genel_toplam']}"
                )
            
        except Exception as e:
            hatalar.append(f"Tutar tutarlılık kontrolü hatası: {e}")
        
        return hatalar
    
    def _temel_alan_dogrulama(self, belge: SatisBelgesi) -> List[str]:
        """Temel alan doğrulamaları"""
        hatalar = []
        
        if not belge.belge_numarasi or not belge.belge_numarasi.strip():
            hatalar.append("Belge numarası boş olamaz")
        
        if not belge.belge_turu:
            hatalar.append("Belge türü belirtilmelidir")
        
        if not belge.belge_durumu:
            hatalar.append("Belge durumu belirtilmelidir")
        
        if not belge.magaza_id or belge.magaza_id <= 0:
            hatalar.append("Geçerli bir mağaza ID belirtilmelidir")
        
        if not belge.olusturan_kullanici_id or belge.olusturan_kullanici_id <= 0:
            hatalar.append("Geçerli bir oluşturan kullanıcı ID belirtilmelidir")
        
        return hatalar
    
    def _belge_turu_dogrulama(self, belge: SatisBelgesi) -> List[str]:
        """Belge türü özel doğrulamaları"""
        hatalar = []
        
        if belge.belge_turu == BelgeTuru.FATURA:
            # Fatura için müşteri bilgisi zorunlu olabilir
            if not belge.musteri_id:
                hatalar.append("Fatura için müşteri bilgisi gereklidir")
        
        if belge.belge_turu == BelgeTuru.IRSALIYE:
            # İrsaliye için kaynak belge kontrolü
            if not belge.kaynak_belge_id:
                hatalar.append("İrsaliye için kaynak belge bilgisi gereklidir")
        
        return hatalar
    
    def _belge_satirlari_dogrulama(self, belge: SatisBelgesi) -> List[str]:
        """Belge satırları doğrulaması"""
        hatalar = []
        
        if not belge.satirlar:
            hatalar.append("En az bir belge satırı bulunmalıdır")
            return hatalar
        
        if len(belge.satirlar) > self._maksimum_satir_sayisi:
            hatalar.append(f"Maksimum {self._maksimum_satir_sayisi} satır eklenebilir")
        
        # Her satırı doğrula
        for i, satir in enumerate(belge.satirlar, 1):
            satir_hatalari = self.satir_dogrula(satir)
            for hata in satir_hatalari:
                hatalar.append(f"Satır {i}: {hata}")
        
        # Sıra numarası tekrarı kontrolü
        sira_numaralari = [satir.sira_no for satir in belge.satirlar if satir.sira_no]
        if len(sira_numaralari) != len(set(sira_numaralari)):
            hatalar.append("Satır sıra numaraları tekrar edemez")
        
        return hatalar
    
    def _tutar_dogrulama(self, belge: SatisBelgesi) -> List[str]:
        """Tutar doğrulamaları"""
        hatalar = []
        
        if belge.toplam_tutar < self._minimum_tutar:
            hatalar.append("Toplam tutar negatif olamaz")
        
        if belge.toplam_tutar > self._maksimum_tutar:
            hatalar.append(f"Toplam tutar {self._maksimum_tutar} değerini aşamaz")
        
        if belge.kdv_tutari < Decimal('0'):
            hatalar.append("KDV tutarı negatif olamaz")
        
        if belge.genel_toplam < self._minimum_tutar:
            hatalar.append("Genel toplam negatif olamaz")
        
        # Tutar tutarlılığı kontrolü
        hatalar.extend(self.tutar_tutarliligi_kontrol_et(belge))
        
        return hatalar
    
    def _is_kurali_dogrulama(self, belge: SatisBelgesi) -> List[str]:
        """İş kuralı doğrulamaları"""
        hatalar = []
        
        # İptal durumu kontrolü
        if belge.belge_durumu == BelgeDurumu.IPTAL:
            if not belge.iptal_nedeni or not belge.iptal_nedeni.strip():
                hatalar.append("İptal durumundaki belgeler için iptal nedeni gereklidir")
        
        # Kaynak belge kontrolü
        if belge.kaynak_belge_id and belge.kaynak_belge_id == belge.belge_id:
            hatalar.append("Belge kendisini kaynak belge olarak gösteremez")
        
        return hatalar
    
    def _satir_temel_dogrulama(self, satir: BelgeSatiri) -> List[str]:
        """Satır temel doğrulamaları"""
        hatalar = []
        
        if not satir.urun_id or satir.urun_id <= 0:
            hatalar.append("Geçerli bir ürün ID belirtilmelidir")
        
        if satir.miktar <= Decimal('0'):
            hatalar.append("Miktar sıfırdan büyük olmalıdır")
        
        if satir.birim_fiyat < Decimal('0'):
            hatalar.append("Birim fiyat negatif olamaz")
        
        if satir.sira_no and satir.sira_no <= 0:
            hatalar.append("Sıra numarası pozitif olmalıdır")
        
        return hatalar
    
    def _satir_tutar_dogrulama(self, satir: BelgeSatiri) -> List[str]:
        """Satır tutar doğrulamaları"""
        hatalar = []
        
        try:
            # Hesaplanan tutarları al
            hesaplanan = self.satir_tutarlari_hesapla(satir)
            
            # Satırdaki tutarlar ile karşılaştır
            if satir.satir_tutari != hesaplanan['satir_tutari']:
                hatalar.append(
                    f"Satır tutarı tutarsızlığı: "
                    f"Satır={satir.satir_tutari}, Hesaplanan={hesaplanan['satir_tutari']}"
                )
            
            if satir.kdv_tutari != hesaplanan['kdv_tutari']:
                hatalar.append(
                    f"Satır KDV tutarı tutarsızlığı: "
                    f"Satır={satir.kdv_tutari}, Hesaplanan={hesaplanan['kdv_tutari']}"
                )
            
            if satir.satir_toplami != hesaplanan['satir_toplami']:
                hatalar.append(
                    f"Satır toplamı tutarsızlığı: "
                    f"Satır={satir.satir_toplami}, Hesaplanan={hesaplanan['satir_toplami']}"
                )
            
        except Exception as e:
            hatalar.append(f"Satır tutar doğrulama hatası: {e}")
        
        return hatalar
    
    def _satir_kdv_dogrulama(self, satir: BelgeSatiri) -> List[str]:
        """Satır KDV doğrulamaları"""
        hatalar = []
        
        if not self.kdv_orani_dogrula(satir.kdv_orani):
            hatalar.append(f"Geçersiz KDV oranı: {satir.kdv_orani}")
        
        return hatalar