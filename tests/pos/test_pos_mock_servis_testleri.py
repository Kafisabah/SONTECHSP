# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_mock_servis_testleri
# Description: POS Mock servis testleri (Görev 16.1)
# Changelog:
# - İlk oluşturma - Mock servis implementasyonları ve testleri

"""
POS Mock Servis Testleri

Bu modül POS sisteminin servis katmanı için mock implementasyonları
ve bunların testlerini içerir. Gerçek servis davranışlarını simüle eder.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

# Proje kök dizinini path'e ekle
proje_kok = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, proje_kok)

from sontechsp.uygulama.moduller.pos.arayuzler import (
    ISepetService,
    IOdemeService,
    IStokService,
    IOfflineKuyrukService,
    OdemeTuru,
    IslemTuru,
    SepetDurum,
    KuyrukDurum,
)
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi, NetworkHatasi


class MockSepetService:
    """Mock Sepet Service implementasyonu"""

    def __init__(self):
        self._sepetler: Dict[int, Dict] = {}
        self._sepet_satirlari: Dict[int, List[Dict]] = {}
        self._sonraki_sepet_id = 1
        self._sonraki_satir_id = 1

    def yeni_sepet_olustur(self, terminal_id: int, kasiyer_id: int) -> int:
        """Yeni sepet oluşturur"""
        if terminal_id <= 0 or kasiyer_id <= 0:
            raise DogrulamaHatasi("gecersiz_parametre", "Geçersiz terminal veya kasiyer ID")

        sepet_id = self._sonraki_sepet_id
        self._sepetler[sepet_id] = {
            "id": sepet_id,
            "terminal_id": terminal_id,
            "kasiyer_id": kasiyer_id,
            "durum": SepetDurum.AKTIF.value,
            "toplam_tutar": Decimal("0.00"),
            "net_tutar": Decimal("0.00"),
            "olusturma_tarihi": datetime.now(),
        }
        self._sepet_satirlari[sepet_id] = []
        self._sonraki_sepet_id += 1
        return sepet_id

    def barkod_ekle(self, sepet_id: int, barkod: str) -> bool:
        """Barkod ile ürün ekler"""
        if sepet_id not in self._sepetler:
            raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")

        if not barkod or not barkod.strip():
            raise DogrulamaHatasi("barkod_bos", "Barkod boş olamaz")

        # Mock ürün bilgisi oluştur
        urun_id = hash(barkod) % 1000 + 1
        birim_fiyat = Decimal("10.50")

        # Sepet satırı ekle
        satir = {
            "id": self._sonraki_satir_id,
            "sepet_id": sepet_id,
            "urun_id": urun_id,
            "barkod": barkod,
            "urun_adi": f"Mock Ürün {barkod}",
            "adet": 1,
            "birim_fiyat": birim_fiyat,
            "toplam_fiyat": birim_fiyat,
        }

        self._sepet_satirlari[sepet_id].append(satir)
        self._sonraki_satir_id += 1

        # Sepet toplamını güncelle
        self._sepet_toplamini_guncelle(sepet_id)
        return True

    def urun_adedi_degistir(self, satir_id: int, yeni_adet: int) -> bool:
        """Ürün adedini değiştirir"""
        if yeni_adet <= 0:
            raise DogrulamaHatasi("adet_pozitif", "Adet pozitif olmalıdır")

        # Satırı bul
        for sepet_id, satirlar in self._sepet_satirlari.items():
            for satir in satirlar:
                if satir["id"] == satir_id:
                    satir["adet"] = yeni_adet
                    satir["toplam_fiyat"] = satir["birim_fiyat"] * yeni_adet
                    self._sepet_toplamini_guncelle(sepet_id)
                    return True

        raise SontechHatasi(f"Satır bulunamadı: {satir_id}")

    def satir_sil(self, satir_id: int) -> bool:
        """Sepet satırını siler"""
        for sepet_id, satirlar in self._sepet_satirlari.items():
            for i, satir in enumerate(satirlar):
                if satir["id"] == satir_id:
                    del satirlar[i]
                    self._sepet_toplamini_guncelle(sepet_id)
                    return True

        raise SontechHatasi(f"Satır bulunamadı: {satir_id}")

    def sepet_bilgisi_getir(self, sepet_id: int) -> Optional[Dict[str, Any]]:
        """Sepet bilgilerini getirir"""
        if sepet_id not in self._sepetler:
            return None

        sepet = self._sepetler[sepet_id].copy()
        sepet["satirlar"] = self._sepet_satirlari[sepet_id].copy()
        return sepet

    def sepet_bosalt(self, sepet_id: int) -> bool:
        """Sepeti boşaltır"""
        if sepet_id not in self._sepetler:
            raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")

        self._sepet_satirlari[sepet_id] = []
        self._sepet_toplamini_guncelle(sepet_id)
        return True

    def _sepet_toplamini_guncelle(self, sepet_id: int):
        """Sepet toplamını günceller"""
        if sepet_id not in self._sepetler:
            return

        toplam = Decimal("0.00")
        for satir in self._sepet_satirlari[sepet_id]:
            toplam += satir["toplam_fiyat"]

        self._sepetler[sepet_id]["toplam_tutar"] = toplam
        self._sepetler[sepet_id]["net_tutar"] = toplam


class MockOdemeService:
    """Mock Ödeme Service implementasyonu"""

    def __init__(self):
        self._satislar: Dict[int, Dict] = {}
        self._sonraki_satis_id = 1

    def tek_odeme_yap(self, sepet_id: int, odeme_turu: OdemeTuru, tutar: Decimal) -> bool:
        """Tek ödeme işlemi yapar"""
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")

        if tutar <= 0:
            raise DogrulamaHatasi("tutar_pozitif", "Ödeme tutarı pozitif olmalıdır")

        # Mock satış kaydı oluştur
        satis_id = self._sonraki_satis_id
        self._satislar[satis_id] = {
            "id": satis_id,
            "sepet_id": sepet_id,
            "odeme_turu": odeme_turu.value,
            "tutar": tutar,
            "tarih": datetime.now(),
            "fis_no": f"FIS{satis_id:06d}",
        }
        self._sonraki_satis_id += 1
        return True

    def parcali_odeme_yap(self, sepet_id: int, odemeler: List[Dict[str, Any]]) -> bool:
        """Parçalı ödeme işlemi yapar"""
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")

        if not odemeler:
            raise DogrulamaHatasi("odemeler_bos", "Ödeme listesi boş olamaz")

        toplam_odeme = Decimal("0.00")
        for odeme in odemeler:
            toplam_odeme += Decimal(str(odeme["tutar"]))

        # Mock satış kaydı oluştur
        satis_id = self._sonraki_satis_id
        self._satislar[satis_id] = {
            "id": satis_id,
            "sepet_id": sepet_id,
            "odemeler": odemeler,
            "toplam_tutar": toplam_odeme,
            "tarih": datetime.now(),
            "fis_no": f"FIS{satis_id:06d}",
        }
        self._sonraki_satis_id += 1
        return True

    def odeme_tutari_kontrol(self, sepet_id: int, odeme_tutari: Decimal) -> Dict[str, Any]:
        """Ödeme tutarını kontrol eder"""
        # Mock sepet tutarı (gerçek implementasyonda sepet servisinden alınır)
        mock_sepet_tutari = Decimal("50.00")

        if odeme_tutari == mock_sepet_tutari:
            return {"gecerli": True, "mesaj": "Ödeme tutarı doğru", "eksik_tutar": Decimal("0.00")}
        elif odeme_tutari < mock_sepet_tutari:
            eksik = mock_sepet_tutari - odeme_tutari
            return {"gecerli": False, "mesaj": f"Yetersiz ödeme. Eksik tutar: {eksik}", "eksik_tutar": eksik}
        else:
            fazla = odeme_tutari - mock_sepet_tutari
            return {"gecerli": False, "mesaj": f"Fazla ödeme. Fazla tutar: {fazla}", "eksik_tutar": Decimal("0.00")}


class MockStokService:
    """Mock Stok Service implementasyonu"""

    def __init__(self):
        self._urunler: Dict[str, Dict] = {
            "1234567890": {
                "urun_id": 1,
                "barkod": "1234567890",
                "urun_adi": "Test Ürün 1",
                "satis_fiyati": Decimal("10.50"),
                "stok_miktari": 100,
                "aktif": True,
            },
            "9876543210": {
                "urun_id": 2,
                "barkod": "9876543210",
                "urun_adi": "Test Ürün 2",
                "satis_fiyati": Decimal("25.75"),
                "stok_miktari": 50,
                "aktif": True,
            },
        }

    def urun_bilgisi_getir(self, barkod: str) -> Optional[Dict[str, Any]]:
        """Barkod ile ürün bilgisi getirir"""
        if not barkod:
            return None

        if barkod in self._urunler:
            return self._urunler[barkod].copy()

        # Bilinmeyen barkod için mock ürün oluştur
        return {
            "urun_id": hash(barkod) % 1000 + 1,
            "barkod": barkod,
            "urun_adi": f"Mock Ürün {barkod}",
            "satis_fiyati": Decimal("10.50"),
            "stok_miktari": 10,
            "aktif": True,
        }

    def stok_kontrol(self, urun_id: int, magaza_id: int, adet: int, depo_id: Optional[int] = None) -> bool:
        """Stok kontrolü yapar"""
        # Mock stok kontrolü - her zaman yeterli stok var
        return adet <= 100

    def stok_dusur(
        self,
        urun_id: int,
        magaza_id: int,
        adet: int,
        referans_no: str,
        aciklama: Optional[str] = None,
        depo_id: Optional[int] = None,
    ) -> bool:
        """Stok düşer"""
        # Mock stok düşümü - her zaman başarılı
        return True


class MockOfflineKuyrukService:
    """Mock Offline Kuyruk Service implementasyonu"""

    def __init__(self):
        self._kuyruk: List[Dict] = []
        self._sonraki_id = 1

    def islem_kuyruga_ekle(
        self, islem_turu: IslemTuru, veri: Dict[str, Any], terminal_id: int, kasiyer_id: int
    ) -> bool:
        """İşlemi offline kuyruğa ekler"""
        kayit = {
            "id": self._sonraki_id,
            "islem_turu": islem_turu.value,
            "veri": veri,
            "terminal_id": terminal_id,
            "kasiyer_id": kasiyer_id,
            "durum": KuyrukDurum.BEKLEMEDE.value,
            "olusturma_tarihi": datetime.now(),
        }

        self._kuyruk.append(kayit)
        self._sonraki_id += 1
        return True

    def kuyruk_senkronize_et(self) -> int:
        """Offline kuyruğu senkronize eder"""
        islenen_sayisi = 0

        for kayit in self._kuyruk:
            if kayit["durum"] == KuyrukDurum.BEKLEMEDE.value:
                # Mock senkronizasyon - her zaman başarılı
                kayit["durum"] = KuyrukDurum.TAMAMLANDI.value
                islenen_sayisi += 1

        return islenen_sayisi

    def kuyruk_istatistikleri_getir(self, terminal_id: int) -> Dict[str, Any]:
        """Kuyruk istatistiklerini getirir"""
        terminal_kayitlari = [k for k in self._kuyruk if k["terminal_id"] == terminal_id]

        durum_sayilari = {}
        for durum in KuyrukDurum:
            durum_sayilari[durum.value] = len([k for k in terminal_kayitlari if k["durum"] == durum.value])

        return {"toplam_kayit": len(terminal_kayitlari), "durum_sayilari": durum_sayilari, "network_durumu": True}


class TestMockSepetService:
    """Mock Sepet Service testleri"""

    def test_yeni_sepet_olusturma(self):
        """Yeni sepet oluşturma testi"""
        service = MockSepetService()

        sepet_id = service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)

        assert sepet_id == 1
        assert sepet_id in service._sepetler

        sepet = service._sepetler[sepet_id]
        assert sepet["terminal_id"] == 1
        assert sepet["kasiyer_id"] == 1
        assert sepet["durum"] == SepetDurum.AKTIF.value

    def test_barkod_ekleme(self):
        """Barkod ekleme testi"""
        service = MockSepetService()
        sepet_id = service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)

        basarili = service.barkod_ekle(sepet_id, "1234567890")

        assert basarili is True
        assert len(service._sepet_satirlari[sepet_id]) == 1

        satir = service._sepet_satirlari[sepet_id][0]
        assert satir["barkod"] == "1234567890"
        assert satir["adet"] == 1

    def test_adet_degistirme(self):
        """Adet değiştirme testi"""
        service = MockSepetService()
        sepet_id = service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        service.barkod_ekle(sepet_id, "1234567890")

        satir_id = service._sepet_satirlari[sepet_id][0]["id"]
        basarili = service.urun_adedi_degistir(satir_id, 3)

        assert basarili is True

        satir = service._sepet_satirlari[sepet_id][0]
        assert satir["adet"] == 3
        assert satir["toplam_fiyat"] == Decimal("31.50")  # 10.50 * 3

    def test_sepet_toplam_hesaplama(self):
        """Sepet toplam hesaplama testi"""
        service = MockSepetService()
        sepet_id = service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)

        # 3 ürün ekle
        service.barkod_ekle(sepet_id, "1111111111")
        service.barkod_ekle(sepet_id, "2222222222")
        service.barkod_ekle(sepet_id, "3333333333")

        sepet = service.sepet_bilgisi_getir(sepet_id)
        assert sepet["toplam_tutar"] == Decimal("31.50")  # 3 * 10.50

    def test_gecersiz_parametre_hatalari(self):
        """Geçersiz parametre hataları testi"""
        service = MockSepetService()

        # Geçersiz terminal ID
        with pytest.raises(DogrulamaHatasi):
            service.yeni_sepet_olustur(terminal_id=0, kasiyer_id=1)

        # Boş barkod
        sepet_id = service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        with pytest.raises(DogrulamaHatasi):
            service.barkod_ekle(sepet_id, "")


class TestMockOdemeService:
    """Mock Ödeme Service testleri"""

    def test_tek_odeme(self):
        """Tek ödeme testi"""
        service = MockOdemeService()

        basarili = service.tek_odeme_yap(sepet_id=1, odeme_turu=OdemeTuru.NAKIT, tutar=Decimal("50.00"))

        assert basarili is True
        assert len(service._satislar) == 1

        satis = service._satislar[1]
        assert satis["sepet_id"] == 1
        assert satis["odeme_turu"] == OdemeTuru.NAKIT.value
        assert satis["tutar"] == Decimal("50.00")

    def test_parcali_odeme(self):
        """Parçalı ödeme testi"""
        service = MockOdemeService()

        odemeler = [
            {"turu": OdemeTuru.NAKIT, "tutar": Decimal("30.00")},
            {"turu": OdemeTuru.KART, "tutar": Decimal("20.00")},
        ]

        basarili = service.parcali_odeme_yap(sepet_id=1, odemeler=odemeler)

        assert basarili is True
        assert len(service._satislar) == 1

        satis = service._satislar[1]
        assert satis["toplam_tutar"] == Decimal("50.00")
        assert len(satis["odemeler"]) == 2

    def test_odeme_tutari_kontrolu(self):
        """Ödeme tutarı kontrolü testi"""
        service = MockOdemeService()

        # Doğru tutar
        sonuc = service.odeme_tutari_kontrol(sepet_id=1, odeme_tutari=Decimal("50.00"))
        assert sonuc["gecerli"] is True

        # Eksik tutar
        sonuc = service.odeme_tutari_kontrol(sepet_id=1, odeme_tutari=Decimal("30.00"))
        assert sonuc["gecerli"] is False
        assert sonuc["eksik_tutar"] == Decimal("20.00")

        # Fazla tutar
        sonuc = service.odeme_tutari_kontrol(sepet_id=1, odeme_tutari=Decimal("70.00"))
        assert sonuc["gecerli"] is False


class TestMockStokService:
    """Mock Stok Service testleri"""

    def test_urun_bilgisi_getirme(self):
        """Ürün bilgisi getirme testi"""
        service = MockStokService()

        # Mevcut ürün
        urun = service.urun_bilgisi_getir("1234567890")
        assert urun is not None
        assert urun["barkod"] == "1234567890"
        assert urun["urun_adi"] == "Test Ürün 1"

        # Bilinmeyen ürün (mock oluşturulur)
        urun = service.urun_bilgisi_getir("9999999999")
        assert urun is not None
        assert urun["barkod"] == "9999999999"
        assert "Mock Ürün" in urun["urun_adi"]

    def test_stok_kontrolu(self):
        """Stok kontrolü testi"""
        service = MockStokService()

        # Yeterli stok
        yeterli = service.stok_kontrol(urun_id=1, magaza_id=1, adet=10)
        assert yeterli is True

        # Yetersiz stok
        yeterli = service.stok_kontrol(urun_id=1, magaza_id=1, adet=200)
        assert yeterli is False

    def test_stok_dusumu(self):
        """Stok düşümü testi"""
        service = MockStokService()

        basarili = service.stok_dusur(urun_id=1, magaza_id=1, adet=5, referans_no="TEST_REF_001")

        assert basarili is True


class TestMockOfflineKuyrukService:
    """Mock Offline Kuyruk Service testleri"""

    def test_kuyruga_ekleme(self):
        """Kuyruğa ekleme testi"""
        service = MockOfflineKuyrukService()

        veri = {"barkod": "1234567890", "adet": 1}
        basarili = service.islem_kuyruga_ekle(
            islem_turu=IslemTuru.SEPET_URUN_EKLEME, veri=veri, terminal_id=1, kasiyer_id=1
        )

        assert basarili is True
        assert len(service._kuyruk) == 1

        kayit = service._kuyruk[0]
        assert kayit["islem_turu"] == IslemTuru.SEPET_URUN_EKLEME.value
        assert kayit["veri"] == veri
        assert kayit["durum"] == KuyrukDurum.BEKLEMEDE.value

    def test_kuyruk_senkronizasyonu(self):
        """Kuyruk senkronizasyonu testi"""
        service = MockOfflineKuyrukService()

        # 3 kayıt ekle
        for i in range(3):
            service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri={"sepet_id": i + 1}, terminal_id=1, kasiyer_id=1
            )

        islenen_sayisi = service.kuyruk_senkronize_et()

        assert islenen_sayisi == 3

        # Tüm kayıtlar tamamlandı durumunda olmalı
        for kayit in service._kuyruk:
            assert kayit["durum"] == KuyrukDurum.TAMAMLANDI.value

    def test_kuyruk_istatistikleri(self):
        """Kuyruk istatistikleri testi"""
        service = MockOfflineKuyrukService()

        # 2 kayıt ekle
        service.islem_kuyruga_ekle(islem_turu=IslemTuru.SATIS, veri={"sepet_id": 1}, terminal_id=1, kasiyer_id=1)
        service.islem_kuyruga_ekle(islem_turu=IslemTuru.IADE, veri={"satis_id": 1}, terminal_id=1, kasiyer_id=1)

        istatistikler = service.kuyruk_istatistikleri_getir(terminal_id=1)

        assert istatistikler["toplam_kayit"] == 2
        assert istatistikler["durum_sayilari"][KuyrukDurum.BEKLEMEDE.value] == 2
        assert istatistikler["network_durumu"] is True


class TestMockServisEntegrasyonu:
    """Mock servis entegrasyon testleri"""

    def test_tam_akis_entegrasyonu(self):
        """Tam akış entegrasyon testi"""
        # Mock servisleri oluştur
        sepet_service = MockSepetService()
        odeme_service = MockOdemeService()
        stok_service = MockStokService()

        # 1. Sepet oluştur
        sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)

        # 2. Ürün ekle
        sepet_service.barkod_ekle(sepet_id, "1234567890")
        sepet_service.barkod_ekle(sepet_id, "9876543210")

        # 3. Sepet bilgisini kontrol et
        sepet = sepet_service.sepet_bilgisi_getir(sepet_id)
        assert len(sepet["satirlar"]) == 2
        assert sepet["toplam_tutar"] > Decimal("0")

        # 4. Ödeme yap
        basarili = odeme_service.tek_odeme_yap(
            sepet_id=sepet_id, odeme_turu=OdemeTuru.NAKIT, tutar=sepet["toplam_tutar"]
        )

        assert basarili is True

    def test_hata_senaryolari_entegrasyonu(self):
        """Hata senaryoları entegrasyon testi"""
        sepet_service = MockSepetService()

        # Geçersiz sepet ID ile işlem
        with pytest.raises(SontechHatasi):
            sepet_service.barkod_ekle(sepet_id=999, barkod="1234567890")

        # Geçersiz parametre ile sepet oluşturma
        with pytest.raises(DogrulamaHatasi):
            sepet_service.yeni_sepet_olustur(terminal_id=0, kasiyer_id=1)


if __name__ == "__main__":
    # Test çalıştırma
    pytest.main([__file__, "-v"])
