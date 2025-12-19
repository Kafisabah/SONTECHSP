# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_altyapi.veri_uretici
# Description: Test veri üretici sınıfları
# Changelog:
# - İlk oluşturma

"""
Test Veri Üretici

Bu modül test için rastgele veri üretimi sağlar:
- TestVeriUretici: Genel test verisi üretimi
- Hypothesis stratejileri
- Gerçekçi test verisi üretimi

Görev 8: Test altyapısı ve mock servisleri oluştur
Requirements: Test veri üretimi
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

from hypothesis import strategies as st
from hypothesis.strategies import composite

from sontechsp.uygulama.moduller.pos.arayuzler import IslemTuru, KuyrukDurum
from sontechsp.uygulama.moduller.ebelge.dto import EBelgeTuru


class TestVeriUretici:
    """Test veri üretici sınıfı"""

    @staticmethod
    def rastgele_string(uzunluk: int = 10, sadece_harf: bool = False) -> str:
        """Rastgele string üret"""
        if sadece_harf:
            karakterler = string.ascii_letters
        else:
            karakterler = string.ascii_letters + string.digits

        return "".join(random.choices(karakterler, k=uzunluk))

    @staticmethod
    def rastgele_email() -> str:
        """Rastgele email adresi üret"""
        kullanici = TestVeriUretici.rastgele_string(8, sadece_harf=True).lower()
        domain = TestVeriUretici.rastgele_string(6, sadece_harf=True).lower()
        return f"{kullanici}@{domain}.com"

    @staticmethod
    def rastgele_telefon() -> str:
        """Rastgele telefon numarası üret"""
        return f"05{random.randint(10, 99)}{random.randint(1000000, 9999999)}"

    @staticmethod
    def rastgele_tc_no() -> str:
        """Rastgele TC kimlik no üret (format kontrolü için)"""
        # Gerçek TC algoritması değil, sadece format için
        return "".join([str(random.randint(0, 9)) for _ in range(11)])

    @staticmethod
    def rastgele_tarih(baslangic: Optional[datetime] = None, bitis: Optional[datetime] = None) -> datetime:
        """Rastgele tarih üret"""
        if not baslangic:
            baslangic = datetime.now() - timedelta(days=365)
        if not bitis:
            bitis = datetime.now()

        delta = bitis - baslangic
        rastgele_saniye = random.randint(0, int(delta.total_seconds()))
        return baslangic + timedelta(seconds=rastgele_saniye)

    @staticmethod
    def rastgele_fiyat(min_fiyat: float = 1.0, max_fiyat: float = 1000.0) -> Decimal:
        """Rastgele fiyat üret"""
        fiyat = random.uniform(min_fiyat, max_fiyat)
        return Decimal(str(round(fiyat, 2)))

    @staticmethod
    def musteri_verisi_uret() -> Dict[str, Any]:
        """Rastgele müşteri verisi üret"""
        return {
            "ad": TestVeriUretici.rastgele_string(8, sadece_harf=True).title(),
            "soyad": TestVeriUretici.rastgele_string(10, sadece_harf=True).title(),
            "email": TestVeriUretici.rastgele_email(),
            "telefon": TestVeriUretici.rastgele_telefon(),
            "tc_no": TestVeriUretici.rastgele_tc_no(),
            "dogum_tarihi": TestVeriUretici.rastgele_tarih(datetime(1950, 1, 1), datetime(2005, 12, 31)).date(),
            "aktif": random.choice([True, False]),
            "sadakat_puani": random.randint(0, 1000),
        }

    @staticmethod
    def urun_verisi_uret() -> Dict[str, Any]:
        """Rastgele ürün verisi üret"""
        return {
            "ad": f"Test Ürün {TestVeriUretici.rastgele_string(5)}",
            "barkod": TestVeriUretici.rastgele_string(13, sadece_harf=False),
            "fiyat": TestVeriUretici.rastgele_fiyat(10.0, 500.0),
            "stok_miktari": random.randint(0, 100),
            "kategori": random.choice(["Elektronik", "Giyim", "Gıda", "Ev", "Spor"]),
            "aktif": random.choice([True, True, True, False]),  # %75 aktif
        }

    @staticmethod
    def satis_verisi_uret(urun_sayisi: int = None) -> Dict[str, Any]:
        """Rastgele satış verisi üret"""
        if urun_sayisi is None:
            urun_sayisi = random.randint(1, 5)

        urunler = []
        toplam_tutar = Decimal("0.00")

        for _ in range(urun_sayisi):
            urun_fiyat = TestVeriUretici.rastgele_fiyat(5.0, 100.0)
            adet = random.randint(1, 3)
            satir_toplam = urun_fiyat * adet

            urunler.append(
                {
                    "id": random.randint(1, 1000),
                    "ad": f"Ürün {TestVeriUretici.rastgele_string(5)}",
                    "barkod": TestVeriUretici.rastgele_string(13),
                    "fiyat": urun_fiyat,
                    "adet": adet,
                    "toplam": satir_toplam,
                }
            )

            toplam_tutar += satir_toplam

        return {
            "fis_no": f"F{random.randint(100000, 999999)}",
            "musteri_id": random.randint(1, 1000),
            "kasiyer_id": random.randint(1, 10),
            "terminal_id": random.randint(1, 5),
            "toplam_tutar": toplam_tutar,
            "odeme_turu": random.choice(["NAKIT", "KREDI_KARTI", "HAVALE"]),
            "urunler": urunler,
            "tarih": TestVeriUretici.rastgele_tarih(),
        }

    @staticmethod
    def offline_kuyruk_verisi_uret() -> Dict[str, Any]:
        """Rastgele offline kuyruk verisi üret"""
        islem_turu = random.choice(list(IslemTuru))

        if islem_turu == IslemTuru.SATIS:
            veri = TestVeriUretici.satis_verisi_uret()
        elif islem_turu == IslemTuru.IADE:
            veri = {
                "iade_no": f"I{random.randint(100000, 999999)}",
                "orijinal_fis_no": f"F{random.randint(100000, 999999)}",
                "iade_tutari": TestVeriUretici.rastgele_fiyat(10.0, 200.0),
                "sebep": random.choice(["Müşteri talebi", "Hasarlı ürün", "Yanlış ürün"]),
            }
        else:
            veri = {
                "islem_id": random.randint(1, 10000),
                "aciklama": f"Test işlemi {TestVeriUretici.rastgele_string(10)}",
            }

        return {
            "islem_turu": islem_turu,
            "veri": veri,
            "terminal_id": random.randint(1, 5),
            "kasiyer_id": random.randint(1, 10),
            "durum": random.choice(list(KuyrukDurum)),
            "oncelik": random.randint(1, 5),
            "deneme_sayisi": random.randint(0, 3),
        }

    @staticmethod
    def ebelge_verisi_uret() -> Dict[str, Any]:
        """Rastgele e-belge verisi üret"""
        return {
            "belge_id": random.randint(1, 10000),
            "belge_turu": random.choice(list(EBelgeTuru)),
            "belge_no": f"B{random.randint(100000, 999999)}",
            "musteri_vkn": TestVeriUretici.rastgele_string(10, sadece_harf=False),
            "toplam_tutar": TestVeriUretici.rastgele_fiyat(100.0, 5000.0),
            "xml_icerik": f"<xml>Test XML {TestVeriUretici.rastgele_string(20)}</xml>",
            "olusturma_tarihi": TestVeriUretici.rastgele_tarih(),
        }


# Hypothesis stratejileri
@composite
def musteri_strategy(draw):
    """Hypothesis müşteri stratejisi"""
    return {
        "ad": draw(st.text(min_size=2, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll")))),
        "soyad": draw(st.text(min_size=2, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll")))),
        "email": draw(st.emails()),
        "telefon": draw(st.text(min_size=11, max_size=11, alphabet=st.characters(whitelist_categories=("Nd",)))),
        "aktif": draw(st.booleans()),
        "sadakat_puani": draw(st.integers(min_value=0, max_value=10000)),
    }


@composite
def urun_strategy(draw):
    """Hypothesis ürün stratejisi"""
    return {
        "ad": draw(st.text(min_size=3, max_size=100)),
        "barkod": draw(st.text(min_size=8, max_size=20, alphabet=st.characters(whitelist_categories=("Nd", "Lu")))),
        "fiyat": draw(st.decimals(min_value=0.01, max_value=9999.99, places=2)),
        "stok_miktari": draw(st.integers(min_value=0, max_value=1000)),
        "aktif": draw(st.booleans()),
    }


@composite
def satis_strategy(draw):
    """Hypothesis satış stratejisi"""
    urun_sayisi = draw(st.integers(min_value=1, max_value=10))
    urunler = draw(
        st.lists(
            st.fixed_dictionaries(
                {
                    "id": st.integers(min_value=1, max_value=10000),
                    "adet": st.integers(min_value=1, max_value=10),
                    "fiyat": st.decimals(min_value=0.01, max_value=999.99, places=2),
                }
            ),
            min_size=urun_sayisi,
            max_size=urun_sayisi,
        )
    )

    return {
        "fis_no": draw(st.text(min_size=5, max_size=20)),
        "musteri_id": draw(st.integers(min_value=1, max_value=10000)),
        "kasiyer_id": draw(st.integers(min_value=1, max_value=100)),
        "terminal_id": draw(st.integers(min_value=1, max_value=20)),
        "urunler": urunler,
        "odeme_turu": draw(st.sampled_from(["NAKIT", "KREDI_KARTI", "HAVALE", "CEKLE"])),
    }


@composite
def offline_kuyruk_strategy(draw):
    """Hypothesis offline kuyruk stratejisi"""
    islem_turu = draw(st.sampled_from(list(IslemTuru)))

    return {
        "islem_turu": islem_turu,
        "veri": draw(
            st.dictionaries(
                st.text(min_size=1, max_size=20),
                st.one_of(st.text(), st.integers(), st.decimals(places=2), st.booleans()),
            )
        ),
        "terminal_id": draw(st.integers(min_value=1, max_value=20)),
        "kasiyer_id": draw(st.integers(min_value=1, max_value=100)),
        "oncelik": draw(st.integers(min_value=1, max_value=10)),
    }


# Test veri setleri
class TestVeriSetleri:
    """Hazır test veri setleri"""

    @staticmethod
    def ornek_musteriler() -> List[Dict[str, Any]]:
        """Örnek müşteri verileri"""
        return [
            {
                "ad": "Ahmet",
                "soyad": "Yılmaz",
                "email": "ahmet.yilmaz@test.com",
                "telefon": "05551234567",
                "tc_no": "12345678901",
                "aktif": True,
                "sadakat_puani": 150,
            },
            {
                "ad": "Fatma",
                "soyad": "Kaya",
                "email": "fatma.kaya@test.com",
                "telefon": "05559876543",
                "tc_no": "98765432109",
                "aktif": True,
                "sadakat_puani": 300,
            },
            {
                "ad": "Mehmet",
                "soyad": "Demir",
                "email": "mehmet.demir@test.com",
                "telefon": "05555555555",
                "tc_no": "11111111111",
                "aktif": False,
                "sadakat_puani": 0,
            },
        ]

    @staticmethod
    def ornek_urunler() -> List[Dict[str, Any]]:
        """Örnek ürün verileri"""
        return [
            {
                "id": 1,
                "ad": "Test Laptop",
                "barkod": "1234567890123",
                "fiyat": Decimal("2500.00"),
                "stok_miktari": 10,
                "aktif": True,
            },
            {
                "id": 2,
                "ad": "Test Mouse",
                "barkod": "2345678901234",
                "fiyat": Decimal("50.00"),
                "stok_miktari": 100,
                "aktif": True,
            },
            {
                "id": 3,
                "ad": "Test Klavye",
                "barkod": "3456789012345",
                "fiyat": Decimal("150.00"),
                "stok_miktari": 0,  # Stoksuz ürün
                "aktif": True,
            },
            {
                "id": 4,
                "ad": "Eski Ürün",
                "barkod": "4567890123456",
                "fiyat": Decimal("100.00"),
                "stok_miktari": 5,
                "aktif": False,  # Pasif ürün
            },
        ]

    @staticmethod
    def kritik_test_senaryolari() -> List[Dict[str, Any]]:
        """Kritik test senaryoları"""
        return [
            {
                "senaryo": "Negatif stok eşiği",
                "urun_id": 1,
                "baslangic_stok": 5,
                "satis_miktari": 8,  # Negatif stok yaratacak
                "beklenen_sonuc": "hata_veya_uyari",
            },
            {
                "senaryo": "Eş zamanlı stok düşümü",
                "urun_id": 2,
                "baslangic_stok": 10,
                "paralel_islem_sayisi": 5,
                "her_islem_miktari": 3,  # Toplam 15 > 10
                "beklenen_sonuc": "sadece_10_dusurulmeli",
            },
            {
                "senaryo": "Network kesintisi sırasında satış",
                "network_durumu": False,
                "satis_verisi": TestVeriUretici.satis_verisi_uret(),
                "beklenen_sonuc": "offline_kuyruga_eklenmeli",
            },
        ]
