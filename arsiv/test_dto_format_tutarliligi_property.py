# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_dto_format_tutarliligi_property
# Description: Yapılandırılmış veri formatı property-based testleri
# Changelog:
# - İlk versiyon: Özellik 7 - Yapılandırılmış Veri Formatı testleri

"""
Yapılandırılmış veri formatı property testleri

**Özellik: ui-smoke-test-altyapisi, Özellik 7: Yapılandırılmış Veri Formatı**
**Doğrular: Gereksinim 2.4**
"""

import unittest
from datetime import datetime
from typing import Any, Dict, List, Optional

from hypothesis import given, settings, strategies as st

from uygulama.arayuz.buton_eslestirme_kaydi import (
    kayit_ekle,
    kayitlari_listele,
    kayitlari_temizle,
)


class TestYapilandirilmisVeriFormati(unittest.TestCase):
    """
    **Özellik: ui-smoke-test-altyapisi, Özellik 7: Yapılandırılmış Veri Formatı**
    **Doğrular: Gereksinim 2.4**

    Herhangi bir eşleştirme sorgulandığında, sistem yapılandırılmış formatta veri sağlamalıdır
    """

    def setUp(self):
        """Her test öncesi kayıtları temizle"""
        kayitlari_temizle()

    def tearDown(self):
        """Her test sonrası kayıtları temizle"""
        kayitlari_temizle()

    @given(
        ekran_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        buton_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        handler_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        servis_metodu=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_yapilandirilmis_veri_formati(
        self, ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: Optional[str]
    ):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 7: Yapılandırılmış Veri Formatı**
        **Doğrular: Gereksinim 2.4**

        Herhangi bir eşleştirme sorgulandığında, sistem yapılandırılmış formatta veri sağlamalıdır
        """
        # Başlangıç kayıt sayısını al
        baslangic_sayisi = len(kayitlari_listele())

        # Kayıt ekle
        kayit_ekle(ekran_adi, buton_adi, handler_adi, servis_metodu)

        # Kayıtları sorgula
        kayitlar = kayitlari_listele()

        # Yapılandırılmış format kontrolü
        self.assertIsInstance(kayitlar, list, "Kayıtlar liste formatında olmalı")
        self.assertEqual(len(kayitlar), baslangic_sayisi + 1, "Kayıt sayısı bir artmalı")

        # Son eklenen kayıt bizim kayıdımız olmalı
        kayit = kayitlar[-1]

        # Sözlük formatı kontrolü
        self.assertIsInstance(kayit, dict, "Her kayıt sözlük formatında olmalı")

        # Gerekli alanların varlığı
        gerekli_alanlar = ["ekran_adi", "buton_adi", "handler_adi", "servis_metodu", "kayit_zamani", "cagrilma_sayisi"]
        for alan in gerekli_alanlar:
            self.assertIn(alan, kayit, f"Kayıt '{alan}' alanını içermeli")

        # Veri türü kontrolü
        self.assertIsInstance(kayit["ekran_adi"], str, "ekran_adi string olmalı")
        self.assertIsInstance(kayit["buton_adi"], str, "buton_adi string olmalı")
        self.assertIsInstance(kayit["handler_adi"], str, "handler_adi string olmalı")
        self.assertTrue(
            kayit["servis_metodu"] is None or isinstance(kayit["servis_metodu"], str),
            "servis_metodu None veya string olmalı",
        )
        self.assertIsInstance(kayit["kayit_zamani"], str, "kayit_zamani ISO format string olmalı")
        self.assertIsInstance(kayit["cagrilma_sayisi"], int, "cagrilma_sayisi integer olmalı")

        # Veri doğruluğu kontrolü
        self.assertEqual(kayit["ekran_adi"], ekran_adi, "ekran_adi değeri korunmalı")
        self.assertEqual(kayit["buton_adi"], buton_adi, "buton_adi değeri korunmalı")
        self.assertEqual(kayit["handler_adi"], handler_adi, "handler_adi değeri korunmalı")
        self.assertEqual(kayit["servis_metodu"], servis_metodu, "servis_metodu değeri korunmalı")
        self.assertEqual(kayit["cagrilma_sayisi"], 0, "Yeni kayıt çağrılma sayısı 0 olmalı")

        # ISO format zaman damgası kontrolü
        try:
            datetime.fromisoformat(kayit["kayit_zamani"])
        except ValueError:
            self.fail("kayit_zamani geçerli ISO format olmalı")

    @given(kayit_sayisi=st.integers(min_value=1, max_value=5))
    @settings(max_examples=20, deadline=5000)
    def test_property_coklu_kayit_yapilandirilmis_format(self, kayit_sayisi: int):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 7: Yapılandırılmış Veri Formatı**
        **Doğrular: Gereksinim 2.4**

        Çoklu kayıt durumunda da yapılandırılmış format korunmalıdır
        """
        # Başlangıç kayıt sayısını al
        baslangic_sayisi = len(kayitlari_listele())

        # Çoklu kayıt ekle
        for i in range(kayit_sayisi):
            kayit_ekle(f"ekran_{i}", f"buton_{i}", f"handler_{i}", f"servis_{i}")

        # Kayıtları sorgula
        kayitlar = kayitlari_listele()

        # Liste formatı kontrolü
        self.assertIsInstance(kayitlar, list, "Kayıtlar liste formatında olmalı")
        self.assertEqual(len(kayitlar), baslangic_sayisi + kayit_sayisi, "Kayıt sayısı doğru olmalı")

        # Son eklenen kayıtlar için format kontrolü
        son_kayitlar = kayitlar[-kayit_sayisi:]
        for i, kayit in enumerate(son_kayitlar):
            self.assertIsInstance(kayit, dict, f"Kayıt {i} sözlük formatında olmalı")

            # Gerekli alanların varlığı
            gerekli_alanlar = [
                "ekran_adi",
                "buton_adi",
                "handler_adi",
                "servis_metodu",
                "kayit_zamani",
                "cagrilma_sayisi",
            ]
            for alan in gerekli_alanlar:
                self.assertIn(alan, kayit, f"Kayıt {i} '{alan}' alanını içermeli")

    def test_bos_liste_yapilandirilmis_format(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 7: Yapılandırılmış Veri Formatı**
        **Doğrular: Gereksinim 2.4**

        Boş durumda da yapılandırılmış format döndürülmelidir
        """
        # Kayıtları sorgula (boş liste bekleniyor)
        kayitlar = kayitlari_listele()

        # Yapılandırılmış format kontrolü
        self.assertIsInstance(kayitlar, list, "Boş durumda da liste formatında olmalı")
        self.assertEqual(len(kayitlar), 0, "Boş liste döndürülmeli")


if __name__ == "__main__":
    unittest.main()
