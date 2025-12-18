# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.servisler.odeme_service
# Description: POS Ödeme Service implementasyonu
# Changelog:
# - İlk oluşturma

"""
POS Ödeme Service Implementasyonu

Bu modül ödeme işlemleri iş kurallarını içerir.
Tek ve parçalı ödeme işlemleri, ödeme doğrulama ve stok düşümü sağlar.
"""

from decimal import Decimal
import decimal
from typing import Optional, Dict, Any, List
import logging

from sontechsp.uygulama.moduller.pos.arayuzler import (
    IOdemeService, ISepetRepository, ISatisRepository, IStokService,
    SepetDurum, SatisDurum, OdemeTuru
)
from sontechsp.uygulama.moduller.pos.repositories.sepet_repository import SepetRepository
from sontechsp.uygulama.moduller.pos.repositories.satis_repository import SatisRepository
from sontechsp.uygulama.moduller.pos.monitoring import islem_izle, get_pos_monitoring
from sontechsp.uygulama.cekirdek.hatalar import (
    DogrulamaHatasi, SontechHatasi, EntegrasyonHatasi
)


class OdemeHatasi(SontechHatasi):
    """Ödeme işlem hataları"""
    
    def __init__(self, mesaj: str, sepet_id: int = None, tutar: Decimal = None):
        ek_bilgi = {}
        if sepet_id:
            ek_bilgi['sepet_id'] = sepet_id
        if tutar:
            ek_bilgi['tutar'] = float(tutar)
        
        super().__init__(
            mesaj=f"Ödeme hatası: {mesaj}",
            hata_kodu="ODEME_HATA",
            ek_bilgi=ek_bilgi
        )


class OdemeService(IOdemeService):
    """
    Ödeme service implementasyonu
    
    Ödeme işlemleri iş kurallarını uygular:
    - Tek ve parçalı ödeme işlemleri
    - Ödeme doğrulama
    - Stok düşümü entegrasyonu
    - Satış tamamlama
    """
    
    def __init__(self, 
                 sepet_repository: Optional[ISepetRepository] = None,
                 satis_repository: Optional[ISatisRepository] = None,
                 stok_service: Optional[IStokService] = None):
        """
        Service'i başlatır
        
        Args:
            sepet_repository: Sepet repository (opsiyonel, default SepetRepository)
            satis_repository: Satış repository (opsiyonel, default SatisRepository)
            stok_service: Stok service (opsiyonel, mock için)
        """
        self._sepet_repository = sepet_repository or SepetRepository()
        self._satis_repository = satis_repository or SatisRepository()
        self._stok_service = stok_service  # Mock için opsiyonel
        self._logger = logging.getLogger(__name__)
    
    @islem_izle("odeme_tek_odeme")
    def tek_odeme_yap(self, sepet_id: int, odeme_turu: OdemeTuru, tutar: Decimal) -> bool:
        """
        Tek ödeme işlemi yapar
        
        Args:
            sepet_id: Sepet kimliği
            odeme_turu: Ödeme türü
            tutar: Ödeme tutarı
            
        Returns:
            Ödeme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            OdemeHatasi: Ödeme işlem hatası
        """
        self._logger.info(f"Tek ödeme başlatılıyor - Sepet: {sepet_id}, Tür: {odeme_turu.value}, Tutar: {tutar}")
        
        # Parametre validasyonu
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")
        
        # NaN ve geçersiz değer kontrolü
        try:
            if tutar.is_nan() or tutar.is_infinite():
                raise DogrulamaHatasi("tutar_gecersiz", "Ödeme tutarı geçersiz")
        except (AttributeError, decimal.InvalidOperation):
            # Decimal olmayan veya geçersiz değerler için
            raise DogrulamaHatasi("tutar_gecersiz", "Ödeme tutarı geçersiz")
        
        if tutar <= 0:
            raise DogrulamaHatasi("tutar_pozitif", "Ödeme tutarı pozitif olmalıdır")
        
        # Sepet bilgisini al ve kontrol et
        sepet = self._sepet_repository.sepet_getir(sepet_id)
        if not sepet:
            raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")
        
        if sepet['durum'] != SepetDurum.AKTIF.value:
            raise DogrulamaHatasi("sepet_aktif_degil", "Sepet aktif durumda değil")
        
        sepet_toplam = Decimal(str(sepet['toplam_tutar']))
        net_tutar = Decimal(str(sepet.get('net_tutar', sepet['toplam_tutar'])))
        
        # Ödeme tutarı kontrolü
        if tutar != net_tutar:
            raise OdemeHatasi(
                f"Ödeme tutarı sepet toplamına eşit değil. Beklenen: {net_tutar}, Verilen: {tutar}",
                sepet_id, tutar
            )
        
        try:
            # Satış kaydı oluştur
            satis_id = self._satis_repository.satis_olustur(
                sepet_id=sepet_id,
                terminal_id=sepet['terminal_id'],
                kasiyer_id=sepet['kasiyer_id'],
                toplam_tutar=sepet_toplam
            )
            
            # Ödeme kaydı ekle
            odeme_id = self._satis_repository.satis_odeme_ekle(
                satis_id=satis_id,
                odeme_turu=odeme_turu,
                tutar=tutar
            )
            
            # Stok düşümü yap (stok servisi varsa)
            if self._stok_service:
                self._stok_dusumu_yap(sepet)
            
            # Fiş numarası oluştur
            fis_no = self._fis_numarasi_olustur(satis_id)
            
            # Satışı tamamla
            self._satis_repository.satis_tamamla(satis_id, fis_no)
            
            # Sepet durumunu güncelle
            self._sepet_repository.sepet_durum_guncelle(sepet_id, SepetDurum.TAMAMLANDI)
            
            self._logger.info(f"Tek ödeme tamamlandı - Satış ID: {satis_id}, Fiş No: {fis_no}")
            return True
            
        except Exception as e:
            self._logger.error(f"Tek ödeme hatası: {str(e)}")
            raise
    
    @islem_izle("odeme_parcali_odeme")
    def parcali_odeme_yap(self, sepet_id: int, odemeler: List[Dict[str, Any]]) -> bool:
        """
        Parçalı ödeme işlemi yapar (Ana koordinasyon fonksiyonu)
        
        Args:
            sepet_id: Sepet kimliği
            odemeler: Ödeme listesi [{'turu': OdemeTuru, 'tutar': Decimal, 'referans': str}]
            
        Returns:
            Ödeme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            OdemeHatasi: Ödeme işlem hatası
        """
        self._logger.info(f"Parçalı ödeme başlatılıyor - Sepet: {sepet_id}, Ödeme sayısı: {len(odemeler)}")
        
        # 1. Doğrulama
        sepet = self._parcali_odeme_dogrula(sepet_id, odemeler)
        
        # 2. Ödeme tutarları kontrolü
        self._odeme_tutarlari_kontrol(odemeler, sepet)
        
        # 3. Satış işlemi
        satis_id = self._satis_islemi_yap(sepet, odemeler)
        
        # 4. İşlemi tamamla
        fis_no = self._odeme_tamamla(sepet_id, satis_id, sepet)
        
        self._logger.info(f"Parçalı ödeme tamamlandı - Satış ID: {satis_id}, Fiş No: {fis_no}")
        return True
    
    def _parcali_odeme_dogrula(self, sepet_id: int, odemeler: List[Dict[str, Any]]) -> Dict:
        """
        Parçalı ödeme parametrelerini doğrular
        
        Args:
            sepet_id: Sepet kimliği
            odemeler: Ödeme listesi
            
        Returns:
            Dict: Sepet bilgisi
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
        """
        # Parametre validasyonu
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")
        
        if not odemeler or len(odemeler) == 0:
            raise DogrulamaHatasi("odemeler_bos", "Ödeme listesi boş olamaz")
        
        # Sepet bilgisini al ve kontrol et
        sepet = self._sepet_repository.sepet_getir(sepet_id)
        if not sepet:
            raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")
        
        if sepet['durum'] != SepetDurum.AKTIF.value:
            raise DogrulamaHatasi("sepet_aktif_degil", "Sepet aktif durumda değil")
        
        return sepet
    
    def _odeme_tutarlari_kontrol(self, odemeler: List[Dict[str, Any]], sepet: Dict) -> None:
        """
        Ödeme tutarlarını kontrol eder
        
        Args:
            odemeler: Ödeme listesi
            sepet: Sepet bilgisi
            
        Raises:
            DogrulamaHatasi: Geçersiz ödeme tutarları
            OdemeHatasi: Toplam ödeme uyumsuzluğu
        """
        net_tutar = Decimal(str(sepet.get('net_tutar', sepet['toplam_tutar'])))
        toplam_odeme = Decimal('0.00')
        
        for odeme in odemeler:
            if 'turu' not in odeme or 'tutar' not in odeme:
                raise DogrulamaHatasi("odeme_eksik_alan", "Ödeme türü ve tutarı zorunludur")
            
            odeme_tutari = Decimal(str(odeme['tutar']))
            if odeme_tutari <= 0:
                raise DogrulamaHatasi("odeme_tutar_pozitif", "Ödeme tutarı pozitif olmalıdır")
            
            toplam_odeme += odeme_tutari
        
        # Toplam ödeme kontrolü
        if toplam_odeme != net_tutar:
            raise OdemeHatasi(
                f"Toplam ödeme sepet toplamına eşit değil. Beklenen: {net_tutar}, Verilen: {toplam_odeme}",
                sepet['id'], toplam_odeme
            )
    
    def _satis_islemi_yap(self, sepet: Dict, odemeler: List[Dict[str, Any]]) -> int:
        """
        Satış işlemini gerçekleştirir
        
        Args:
            sepet: Sepet bilgisi
            odemeler: Ödeme listesi
            
        Returns:
            int: Satış ID
            
        Raises:
            Exception: Satış işlemi hatası
        """
        try:
            sepet_toplam = Decimal(str(sepet['toplam_tutar']))
            
            # Satış kaydı oluştur
            satis_id = self._satis_repository.satis_olustur(
                sepet_id=sepet['id'],
                terminal_id=sepet['terminal_id'],
                kasiyer_id=sepet['kasiyer_id'],
                toplam_tutar=sepet_toplam
            )
            
            # Her ödeme için kayıt ekle
            for odeme in odemeler:
                odeme_turu = odeme['turu']
                if isinstance(odeme_turu, str):
                    odeme_turu = OdemeTuru(odeme_turu)
                
                self._satis_repository.satis_odeme_ekle(
                    satis_id=satis_id,
                    odeme_turu=odeme_turu,
                    tutar=Decimal(str(odeme['tutar'])),
                    referans_no=odeme.get('referans')
                )
            
            return satis_id
            
        except Exception as e:
            self._logger.error(f"Satış işlemi hatası: {str(e)}")
            raise
    
    def _odeme_tamamla(self, sepet_id: int, satis_id: int, sepet: Dict) -> str:
        """
        Ödeme işlemini tamamlar
        
        Args:
            sepet_id: Sepet ID
            satis_id: Satış ID
            sepet: Sepet bilgisi
            
        Returns:
            str: Fiş numarası
            
        Raises:
            Exception: Tamamlama işlemi hatası
        """
        try:
            # Stok düşümü yap (stok servisi varsa)
            if self._stok_service:
                self._stok_dusumu_yap(sepet)
            
            # Fiş numarası oluştur
            fis_no = self._fis_numarasi_olustur(satis_id)
            
            # Satışı tamamla
            self._satis_repository.satis_tamamla(satis_id, fis_no)
            
            # Sepet durumunu güncelle
            self._sepet_repository.sepet_durum_guncelle(sepet_id, SepetDurum.TAMAMLANDI)
            
            return fis_no
            
        except Exception as e:
            self._logger.error(f"Ödeme tamamlama hatası: {str(e)}")
            raise
    
    def odeme_tutari_kontrol(self, sepet_id: int, odeme_tutari: Decimal) -> Dict[str, Any]:
        """
        Ödeme tutarını kontrol eder
        
        Args:
            sepet_id: Sepet kimliği
            odeme_tutari: Kontrol edilecek ödeme tutarı
            
        Returns:
            Kontrol sonucu {'gecerli': bool, 'mesaj': str, 'eksik_tutar': Decimal}
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")
        
        # NaN ve geçersiz değer kontrolü
        try:
            if odeme_tutari.is_nan() or odeme_tutari.is_infinite():
                raise DogrulamaHatasi("odeme_tutar_gecersiz", "Ödeme tutarı geçersiz")
        except (AttributeError, decimal.InvalidOperation):
            # Decimal olmayan veya geçersiz değerler için
            raise DogrulamaHatasi("odeme_tutar_gecersiz", "Ödeme tutarı geçersiz")
        
        if odeme_tutari < 0:
            raise DogrulamaHatasi("odeme_tutar_negatif", "Ödeme tutarı negatif olamaz")
        
        # Sepet bilgisini al
        sepet = self._sepet_repository.sepet_getir(sepet_id)
        if not sepet:
            raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")
        
        net_tutar = Decimal(str(sepet.get('net_tutar', sepet['toplam_tutar'])))
        
        if odeme_tutari == net_tutar:
            return {
                'gecerli': True,
                'mesaj': 'Ödeme tutarı doğru',
                'eksik_tutar': Decimal('0.00')
            }
        elif odeme_tutari < net_tutar:
            eksik = net_tutar - odeme_tutari
            return {
                'gecerli': False,
                'mesaj': f'Yetersiz ödeme. Eksik tutar: {eksik}',
                'eksik_tutar': eksik
            }
        else:
            fazla = odeme_tutari - net_tutar
            return {
                'gecerli': False,
                'mesaj': f'Fazla ödeme. Fazla tutar: {fazla}',
                'eksik_tutar': Decimal('0.00')
            }
    
    def sepet_odeme_bilgisi_getir(self, sepet_id: int) -> Dict[str, Any]:
        """
        Sepet için ödeme bilgilerini getirir
        
        Args:
            sepet_id: Sepet kimliği
            
        Returns:
            Ödeme bilgileri
            
        Raises:
            DogrulamaHatasi: Geçersiz sepet ID
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")
        
        sepet = self._sepet_repository.sepet_getir(sepet_id)
        if not sepet:
            raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")
        
        toplam_tutar = Decimal(str(sepet['toplam_tutar']))
        indirim_tutari = Decimal(str(sepet.get('indirim_tutari', 0)))
        net_tutar = toplam_tutar - indirim_tutari
        
        return {
            'sepet_id': sepet_id,
            'toplam_tutar': float(toplam_tutar),
            'indirim_tutari': float(indirim_tutari),
            'net_tutar': float(net_tutar),
            'satir_sayisi': len(sepet.get('satirlar', [])),
            'durum': sepet['durum']
        }
    
    def _stok_dusumu_yap(self, sepet: Dict[str, Any]) -> None:
        """
        Sepetteki ürünler için stok düşümü yapar (private method)
        
        Args:
            sepet: Sepet bilgileri
        """
        if not self._stok_service:
            return
        
        try:
            for satir in sepet.get('satirlar', []):
                urun_id = satir['urun_id']
                adet = satir['adet']
                
                # Stok düşümü yap
                if not self._stok_service.stok_dusur(urun_id, adet):
                    self._logger.warning(f"Stok düşümü başarısız - Ürün: {urun_id}, Adet: {adet}")
                
        except Exception as e:
            self._logger.error(f"Stok düşümü hatası: {str(e)}")
            raise EntegrasyonHatasi("stok_servisi", f"Stok düşümü hatası: {str(e)}")
    
    def _fis_numarasi_olustur(self, satis_id: int) -> str:
        """
        Fiş numarası oluşturur (private method)
        
        Args:
            satis_id: Satış kimliği
            
        Returns:
            Fiş numarası
        """
        from datetime import datetime
        
        # Basit fiş numarası formatı: YYYYMMDD-HHMMSS-SATISID
        simdi = datetime.now()
        tarih_str = simdi.strftime("%Y%m%d")
        saat_str = simdi.strftime("%H%M%S")
        
        return f"{tarih_str}-{saat_str}-{satis_id:06d}"