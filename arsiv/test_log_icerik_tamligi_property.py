# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_log_icerik_tamligi_property
# Description: Log içerik tamlığı property-based testleri
# Changelog:
# - İlk versiyon: Log içerik tamlığı özellik testleri oluşturuldu versiyon: Log içerik tamlığı özellik testleri

import unittest
from datetime import datetime
from typing import Optional

from hypothesis import given, settings, strategies as st

from uygulama.arayuz.log_sistemi import (
    LogDurumu,
    LogSeviyesi,
    handler_loglama,
    stub_servis_loglama,
    log_kayitlarini_listele,
    log_kayitlarini_temizle,
    log_sayisi,
)


class TestLogIcerikTamligi(unittest.TestCase):
    """Log içerik tamlığı property-based testleri"""

    def setUp(self):
        """Her test öncesi log kayıtlarını temizle"""
        log_kayitlarini_temizle()

    def tearDown(self):
        """Her test sonrası log kayıtlarını temizle"""
        log_kayitlarini_temizle()

    def _temiz_baslangic_kontrol(self):
        """Test başlangıcında temiz durum sağla"""
        log_kayitlarini_temizle()
        # Emin olmak için tekrar kontrol et
        if log_sayisi() != 0:
            log_kayitlarini_temizle()

    @given(
        ekran_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        buton_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        handler_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        servis_metodu=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        durum=st.sampled_from([LogDurumu.BASARILI, LogDurumu.HATA, LogDurumu.STUB]),
        detay=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_handler_log_icerik_tamligi(
        self,
        ekran_adi: str,
        buton_adi: str,
        handler_adi: str,
        servis_metodu: Optional[str],
        durum: LogDurumu,
        detay: Optional[str],
    ):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 10: Log İçerik Tamlığı**

        Herhangi bir loglama gerçekleştiğinde, sistem ekran adı, buton adı ve handler
        bilgilerini içermelidir.

        **Doğrular: Gereksinim 3.3**
        """
        # Başlangıç durumu: log kayıtları boş
        self._temiz_baslangic_kontrol()
        baslangic_sayisi = log_sayisi()
        self.assertEqual(baslangic_sayisi, 0)

        # Handler loglama çağrısı
        handler_loglama(
            ekran_adi=ekran_adi,
            buton_adi=buton_adi,
            handler_adi=handler_adi,
            servis_metodu=servis_metodu,
            durum=durum,
            detay=detay,
        )

        # Log kayıtları kontrol et
        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), 1)

        log_kaydi = log_kayitlari[0]

        # Özellik 1: Ekran adı bilgisi zorunlu ve doğru olmalı
        self.assertIn("ekran_adi", log_kaydi)
        self.assertIsNotNone(log_kaydi["ekran_adi"])
        self.assertEqual(log_kaydi["ekran_adi"], ekran_adi)
        self.assertTrue(isinstance(log_kaydi["ekran_adi"], str))
        self.assertTrue(len(log_kaydi["ekran_adi"].strip()) > 0)

        # Özellik 2: Buton adı bilgisi zorunlu ve doğru olmalı
        self.assertIn("buton_adi", log_kaydi)
        self.assertIsNotNone(log_kaydi["buton_adi"])
        self.assertEqual(log_kaydi["buton_adi"], buton_adi)
        self.assertTrue(isinstance(log_kaydi["buton_adi"], str))
        self.assertTrue(len(log_kaydi["buton_adi"].strip()) > 0)

        # Özellik 3: Handler bilgisi zorunlu ve doğru olmalı
        self.assertIn("handler_adi", log_kaydi)
        self.assertIsNotNone(log_kaydi["handler_adi"])
        self.assertEqual(log_kaydi["handler_adi"], handler_adi)
        self.assertTrue(isinstance(log_kaydi["handler_adi"], str))
        self.assertTrue(len(log_kaydi["handler_adi"].strip()) > 0)

        # Özellik 4: Zaman damgası bilgisi zorunlu olmalı
        self.assertIn("zaman", log_kaydi)
        self.assertIsNotNone(log_kaydi["zaman"])
        self.assertTrue(isinstance(log_kaydi["zaman"], str))

        # Zaman damgası geçerli ISO formatında olmalı
        try:
            parsed_time = datetime.fromisoformat(log_kaydi["zaman"])
            self.assertIsInstance(parsed_time, datetime)
        except ValueError:
            self.fail(f"Zaman damgası geçersiz ISO formatında: {log_kaydi['zaman']}")

        # Özellik 5: Durum bilgisi zorunlu olmalı
        self.assertIn("durum", log_kaydi)
        self.assertIsNotNone(log_kaydi["durum"])
        self.assertEqual(log_kaydi["durum"], durum.value)
        self.assertTrue(isinstance(log_kaydi["durum"], str))

        # Özellik 6: Log seviyesi bilgisi zorunlu olmalı
        self.assertIn("log_seviyesi", log_kaydi)
        self.assertIsNotNone(log_kaydi["log_seviyesi"])
        self.assertTrue(isinstance(log_kaydi["log_seviyesi"], str))

        # Özellik 7: Servis metodu bilgisi (varsa) doğru olmalı
        self.assertIn("servis_metodu", log_kaydi)
        self.assertEqual(log_kaydi["servis_metodu"], servis_metodu)

        # Özellik 8: Detay bilgisi (varsa) doğru olmalı
        self.assertIn("detay", log_kaydi)
        self.assertEqual(log_kaydi["detay"], detay)

    @given(
        ekran_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        buton_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        handler_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        servis_metodu=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        detay=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_stub_servis_log_icerik_tamligi(
        self,
        ekran_adi: str,
        buton_adi: str,
        handler_adi: str,
        servis_metodu: str,
        detay: Optional[str],
    ):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 10: Log İçerik Tamlığı (Stub Servis)**

        Herhangi bir stub servis loglama gerçekleştiğinde, sistem ekran adı, buton adı
        ve handler bilgilerini içermelidir.

        **Doğrular: Gereksinim 3.3**
        """
        # Başlangıç durumu: log kayıtları boş
        self._temiz_baslangic_kontrol()
        baslangic_sayisi = log_sayisi()
        self.assertEqual(baslangic_sayisi, 0)

        # Stub servis loglama çağrısı
        stub_servis_loglama(
            ekran_adi=ekran_adi,
            buton_adi=buton_adi,
            handler_adi=handler_adi,
            servis_metodu=servis_metodu,
            detay=detay,
        )

        # Log kayıtları kontrol et
        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), 1)

        log_kaydi = log_kayitlari[0]

        # Özellik 1: Ekran adı bilgisi zorunlu ve doğru olmalı
        self.assertIn("ekran_adi", log_kaydi)
        self.assertIsNotNone(log_kaydi["ekran_adi"])
        self.assertEqual(log_kaydi["ekran_adi"], ekran_adi)
        self.assertTrue(isinstance(log_kaydi["ekran_adi"], str))
        self.assertTrue(len(log_kaydi["ekran_adi"].strip()) > 0)

        # Özellik 2: Buton adı bilgisi zorunlu ve doğru olmalı
        self.assertIn("buton_adi", log_kaydi)
        self.assertIsNotNone(log_kaydi["buton_adi"])
        self.assertEqual(log_kaydi["buton_adi"], buton_adi)
        self.assertTrue(isinstance(log_kaydi["buton_adi"], str))
        self.assertTrue(len(log_kaydi["buton_adi"].strip()) > 0)

        # Özellik 3: Handler bilgisi zorunlu ve doğru olmalı
        self.assertIn("handler_adi", log_kaydi)
        self.assertIsNotNone(log_kaydi["handler_adi"])
        self.assertEqual(log_kaydi["handler_adi"], handler_adi)
        self.assertTrue(isinstance(log_kaydi["handler_adi"], str))
        self.assertTrue(len(log_kaydi["handler_adi"].strip()) > 0)

        # Özellik 4: Servis metodu bilgisi zorunlu ve doğru olmalı (stub servis için)
        self.assertIn("servis_metodu", log_kaydi)
        self.assertIsNotNone(log_kaydi["servis_metodu"])
        self.assertEqual(log_kaydi["servis_metodu"], servis_metodu)
        self.assertTrue(isinstance(log_kaydi["servis_metodu"], str))
        self.assertTrue(len(log_kaydi["servis_metodu"].strip()) > 0)

        # Özellik 5: Durum bilgisi STUB olmalı
        self.assertIn("durum", log_kaydi)
        self.assertEqual(log_kaydi["durum"], LogDurumu.STUB.value)

        # Özellik 6: Detay bilgisi varsayılan olarak "stub çağrıldı" olmalı
        self.assertIn("detay", log_kaydi)
        if detay is None:
            self.assertEqual(log_kaydi["detay"], "stub çağrıldı")
        else:
            self.assertEqual(log_kaydi["detay"], detay)

        # Özellik 7: Zaman damgası bilgisi zorunlu olmalı
        self.assertIn("zaman", log_kaydi)
        self.assertIsNotNone(log_kaydi["zaman"])
        try:
            parsed_time = datetime.fromisoformat(log_kaydi["zaman"])
            self.assertIsInstance(parsed_time, datetime)
        except ValueError:
            self.fail(f"Zaman damgası geçersiz ISO formatında: {log_kaydi['zaman']}")

    @given(log_sayisi_hedef=st.integers(min_value=2, max_value=10))
    @settings(max_examples=50, deadline=10000)
    def test_property_coklu_log_icerik_tamligi(self, log_sayisi_hedef: int):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 10: Log İçerik Tamlığı (Çoklu)**

        Birden fazla loglama gerçekleştiğinde, her log kaydı ekran adı, buton adı
        ve handler bilgilerini içermelidir.

        **Doğrular: Gereksinim 3.3**
        """
        # Başlangıç durumu
        self._temiz_baslangic_kontrol()
        self.assertEqual(log_sayisi(), 0)

        # Çoklu loglama çağrıları (karışık handler ve stub servis)
        for i in range(log_sayisi_hedef):
            if i % 2 == 0:
                # Handler loglama
                handler_loglama(
                    ekran_adi=f"Ekran_{i}",
                    buton_adi=f"Buton_{i}",
                    handler_adi=f"handler_{i}",
                    servis_metodu=f"servis_{i}" if i % 3 == 0 else None,
                    durum=LogDurumu.BASARILI,
                )
            else:
                # Stub servis loglama
                stub_servis_loglama(
                    ekran_adi=f"Ekran_{i}",
                    buton_adi=f"Buton_{i}",
                    handler_adi=f"handler_{i}",
                    servis_metodu=f"stub_servis_{i}",
                )

        # Tüm log kayıtlarını kontrol et
        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), log_sayisi_hedef)

        # Her log kaydının zorunlu alanları içerdiğini kontrol et
        for i, log_kaydi in enumerate(log_kayitlari):
            # Zorunlu alanlar mevcut olmalı
            zorunlu_alanlar = ["ekran_adi", "buton_adi", "handler_adi", "zaman", "durum", "log_seviyesi"]
            for alan in zorunlu_alanlar:
                self.assertIn(alan, log_kaydi, f"Log kaydı {i}: '{alan}' alanı eksik")
                self.assertIsNotNone(log_kaydi[alan], f"Log kaydı {i}: '{alan}' alanı None")

            # String alanlar boş olmamalı
            string_alanlar = ["ekran_adi", "buton_adi", "handler_adi"]
            for alan in string_alanlar:
                self.assertTrue(isinstance(log_kaydi[alan], str), f"Log kaydı {i}: '{alan}' string değil")
                self.assertTrue(len(log_kaydi[alan].strip()) > 0, f"Log kaydı {i}: '{alan}' boş")

            # Zaman damgası geçerli olmalı
            try:
                datetime.fromisoformat(log_kaydi["zaman"])
            except ValueError:
                self.fail(f"Log kaydı {i}: Zaman damgası geçersiz - {log_kaydi['zaman']}")

    def test_property_log_icerik_immutability(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 10: Log İçerik Tamlığı (Değişmezlik)**

        Log kayıtları oluşturulduktan sonra içerikleri değişmemelidir.

        **Doğrular: Gereksinim 3.3**
        """
        # Başlangıç durumu
        self._temiz_baslangic_kontrol()

        # İlk log kaydı
        handler_loglama(
            ekran_adi="TestEkran",
            buton_adi="TestButon",
            handler_adi="test_handler",
            servis_metodu="test_servis",
            durum=LogDurumu.BASARILI,
        )

        # İlk durumu kaydet
        ilk_log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(ilk_log_kayitlari), 1)
        ilk_kayit = ilk_log_kayitlari[0].copy()

        # İkinci log kaydı ekle
        handler_loglama(
            ekran_adi="DigerEkran",
            buton_adi="DigerButon",
            handler_adi="diger_handler",
            durum=LogDurumu.HATA,
        )

        # İlk kaydın değişmediğini kontrol et
        guncel_log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(guncel_log_kayitlari), 2)

        # İlk kayıt hala aynı olmalı
        guncel_ilk_kayit = guncel_log_kayitlari[0]
        for alan, deger in ilk_kayit.items():
            self.assertEqual(guncel_ilk_kayit[alan], deger, f"İlk kaydın '{alan}' alanı değişti")


if __name__ == "__main__":
    unittest.main()
