# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_stub_servis_loglama_property
# Description: Stub servis loglama property-based testleri
# Changelog:
# - İlk versiyon: Stub servis loglama özellik testleri

import unittest
from datetime import datetime
from typing import Optional

from hypothesis import given, settings, strategies as st

from uygulama.arayuz.log_sistemi import (
    LogDurumu,
    LogSeviyesi,
    stub_servis_loglama,
    log_kayitlarini_listele,
    log_kayitlarini_temizle,
    log_sayisi,
)


class TestStubServisLoglama(unittest.TestCase):
    """Stub servis loglama property-based testleri"""

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
        servis_metodu=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        detay=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_stub_servis_loglama(
        self, ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: str, detay: Optional[str]
    ):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 9: Stub Servis Loglama**

        Herhangi bir stub servis çağrıldığında, sistem "stub çağrıldı" mesajını loglamalıdır.

        **Doğrular: Gereksinim 3.2**
        """
        # Başlangıç durumu: log kayıtları boş
        self._temiz_baslangic_kontrol()
        baslangic_sayisi = log_sayisi()
        self.assertEqual(baslangic_sayisi, 0)

        # Stub servis loglama çağrısı
        stub_servis_loglama(
            ekran_adi=ekran_adi, buton_adi=buton_adi, handler_adi=handler_adi, servis_metodu=servis_metodu, detay=detay
        )

        # Log kayıtları kontrol et
        log_kayitlari = log_kayitlarini_listele()

        # Özellik 1: Tam olarak bir log kaydı eklenmeli
        self.assertEqual(len(log_kayitlari), 1)
        self.assertEqual(log_sayisi(), 1)

        # Özellik 2: Log kaydı tüm gerekli bilgileri içermeli
        log_kaydi = log_kayitlari[0]

        # Ekran, buton ve handler bilgileri korunmalı
        self.assertEqual(log_kaydi["ekran_adi"], ekran_adi)
        self.assertEqual(log_kaydi["buton_adi"], buton_adi)
        self.assertEqual(log_kaydi["handler_adi"], handler_adi)

        # Servis metodu bilgisi korunmalı
        self.assertEqual(log_kaydi["servis_metodu"], servis_metodu)

        # Özellik 3: Durum STUB olmalı
        self.assertEqual(log_kaydi["durum"], LogDurumu.STUB.value)

        # Özellik 4: Detay "stub çağrıldı" içermeli
        if detay is None:
            self.assertEqual(log_kaydi["detay"], "stub çağrıldı")
        else:
            self.assertEqual(log_kaydi["detay"], detay)

        # Özellik 5: Zaman damgası mevcut olmalı ve geçerli format olmalı
        self.assertIn("zaman", log_kaydi)
        self.assertIsNotNone(log_kaydi["zaman"])

        # ISO format kontrolü
        try:
            datetime.fromisoformat(log_kaydi["zaman"])
        except ValueError:
            self.fail(f"Zaman damgası geçersiz ISO formatında: {log_kaydi['zaman']}")

        # Özellik 6: Log seviyesi varsayılan olarak INFO olmalı
        self.assertEqual(log_kaydi["log_seviyesi"], LogSeviyesi.INFO.value)

    @given(stub_sayisi=st.integers(min_value=1, max_value=15))
    @settings(max_examples=50, deadline=10000)
    def test_property_coklu_stub_servis_loglama(self, stub_sayisi: int):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 9: Stub Servis Loglama (Çoklu)**

        Birden fazla stub servis çağrısı yapıldığında, her çağrı için ayrı log kaydı
        oluşturulmalıdır ve hepsi STUB durumunda olmalıdır.

        **Doğrular: Gereksinim 3.2**
        """
        # Başlangıç durumu
        self._temiz_baslangic_kontrol()
        self.assertEqual(log_sayisi(), 0)

        # Çoklu stub servis loglama çağrıları
        for i in range(stub_sayisi):
            stub_servis_loglama(
                ekran_adi=f"Ekran_{i}",
                buton_adi=f"Buton_{i}",
                handler_adi=f"handler_{i}",
                servis_metodu=f"stub_servis_{i}",
            )

        # Özellik: Her çağrı için ayrı log kaydı oluşturulmalı
        self.assertEqual(log_sayisi(), stub_sayisi)

        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), stub_sayisi)

        # Özellik: Tüm kayıtlar STUB durumunda olmalı
        for kayit in log_kayitlari:
            self.assertEqual(kayit["durum"], LogDurumu.STUB.value)
            self.assertIn("stub çağrıldı", kayit["detay"])

        # Her log kaydının benzersiz olduğunu kontrol et
        servis_metodlari = [kayit["servis_metodu"] for kayit in log_kayitlari]
        self.assertEqual(len(set(servis_metodlari)), stub_sayisi)

    def test_property_stub_servis_mesaj_icerigi(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 9: Stub Servis Loglama (Mesaj İçeriği)**

        Stub servis loglama çağrısında detay belirtilmezse, varsayılan olarak
        "stub çağrıldı" mesajı kullanılmalıdır.

        **Doğrular: Gereksinim 3.2**
        """
        # Başlangıç durumu
        self._temiz_baslangic_kontrol()
        self.assertEqual(log_sayisi(), 0)

        # Detay belirtmeden stub servis loglama
        stub_servis_loglama(
            ekran_adi="Test Ekranı",
            buton_adi="Test Butonu",
            handler_adi="test_handler",
            servis_metodu="test_stub_servis",
        )

        # Log kaydını kontrol et
        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), 1)

        log_kaydi = log_kayitlari[0]

        # Özellik: Varsayılan mesaj "stub çağrıldı" olmalı
        self.assertEqual(log_kaydi["detay"], "stub çağrıldı")
        self.assertEqual(log_kaydi["durum"], LogDurumu.STUB.value)

    def test_property_stub_servis_ozel_detay(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 9: Stub Servis Loglama (Özel Detay)**

        Stub servis loglama çağrısında özel detay belirtilirse, o detay kullanılmalıdır.

        **Doğrular: Gereksinim 3.2**
        """
        # Başlangıç durumu
        self._temiz_baslangic_kontrol()
        self.assertEqual(log_sayisi(), 0)

        ozel_detay = "Özel stub servis detayı - test amaçlı"

        # Özel detay ile stub servis loglama
        stub_servis_loglama(
            ekran_adi="Test Ekranı",
            buton_adi="Test Butonu",
            handler_adi="test_handler",
            servis_metodu="test_stub_servis",
            detay=ozel_detay,
        )

        # Log kaydını kontrol et
        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), 1)

        log_kaydi = log_kayitlari[0]

        # Özellik: Özel detay kullanılmalı
        self.assertEqual(log_kaydi["detay"], ozel_detay)
        self.assertEqual(log_kaydi["durum"], LogDurumu.STUB.value)


if __name__ == "__main__":
    unittest.main()
