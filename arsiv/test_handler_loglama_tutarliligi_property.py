# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_handler_loglama_tutarliligi_property
# Description: Handler loglama tutarlılığı property-based testleri
# Changelog:
# - İlk versiyon: Handler loglama tutarlılığı özellik testleri

import unittest
from datetime import datetime
from typing import Optional

from hypothesis import given, settings, strategies as st

from uygulama.arayuz.log_sistemi import (
    LogDurumu,
    LogSeviyesi,
    handler_loglama,
    log_kayitlarini_listele,
    log_kayitlarini_temizle,
    log_sayisi,
)


class TestHandlerLoglamaTutarliligi(unittest.TestCase):
    """Handler loglama tutarlılığı property-based testleri"""

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
    def test_property_handler_loglama_tutarliligi(
        self,
        ekran_adi: str,
        buton_adi: str,
        handler_adi: str,
        servis_metodu: Optional[str],
        durum: LogDurumu,
        detay: Optional[str],
    ):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 8: Handler Loglama Tutarlılığı**

        Herhangi bir buton handler'ı çalıştığında, sistem hangi butonun hangi handler'ı
        tetiklediğini loglamalıdır.

        **Doğrular: Gereksinim 3.1**
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

        # Durum bilgisi korunmalı
        self.assertEqual(log_kaydi["durum"], durum.value)

        # Detay bilgisi korunmalı
        self.assertEqual(log_kaydi["detay"], detay)

        # Özellik 3: Zaman damgası mevcut olmalı ve geçerli format olmalı
        self.assertIn("zaman", log_kaydi)
        self.assertIsNotNone(log_kaydi["zaman"])

        # ISO format kontrolü
        try:
            datetime.fromisoformat(log_kaydi["zaman"])
        except ValueError:
            self.fail(f"Zaman damgası geçersiz ISO formatında: {log_kaydi['zaman']}")

        # Özellik 4: Log seviyesi varsayılan olarak INFO olmalı
        self.assertEqual(log_kaydi["log_seviyesi"], LogSeviyesi.INFO.value)

    @given(log_sayisi_hedef=st.integers(min_value=1, max_value=20))
    @settings(max_examples=50, deadline=10000)
    def test_property_coklu_handler_loglama_tutarliligi(self, log_sayisi_hedef: int):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 8: Handler Loglama Tutarlılığı (Çoklu)**

        Birden fazla handler loglama çağrısı yapıldığında, her çağrı için ayrı log kaydı
        oluşturulmalıdır.

        **Doğrular: Gereksinim 3.1**
        """
        # Başlangıç durumu
        self._temiz_baslangic_kontrol()
        self.assertEqual(log_sayisi(), 0)

        # Çoklu handler loglama çağrıları
        for i in range(log_sayisi_hedef):
            handler_loglama(
                ekran_adi=f"Ekran_{i}",
                buton_adi=f"Buton_{i}",
                handler_adi=f"handler_{i}",
                servis_metodu=f"servis_metodu_{i}",
                durum=LogDurumu.BASARILI,
            )

        # Özellik: Her çağrı için ayrı log kaydı oluşturulmalı
        self.assertEqual(log_sayisi(), log_sayisi_hedef)

        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), log_sayisi_hedef)

        # Her log kaydının benzersiz olduğunu kontrol et
        ekran_adlari = [kayit["ekran_adi"] for kayit in log_kayitlari]
        self.assertEqual(len(set(ekran_adlari)), log_sayisi_hedef)

    def test_property_handler_loglama_thread_safety(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 8: Handler Loglama Tutarlılığı (Thread Safety)**

        Eş zamanlı handler loglama çağrıları thread-safe olmalıdır.

        **Doğrular: Gereksinim 3.1**
        """
        import threading
        import time

        # Başlangıç durumu
        self._temiz_baslangic_kontrol()
        self.assertEqual(log_sayisi(), 0)

        # Thread fonksiyonu
        def log_ekle(thread_id: int):
            for i in range(5):
                handler_loglama(
                    ekran_adi=f"Ekran_T{thread_id}_{i}",
                    buton_adi=f"Buton_T{thread_id}_{i}",
                    handler_adi=f"handler_T{thread_id}_{i}",
                    durum=LogDurumu.BASARILI,
                )
                time.sleep(0.001)  # Küçük gecikme

        # 3 thread oluştur ve çalıştır
        thread_sayisi = 3
        log_per_thread = 5
        beklenen_toplam = thread_sayisi * log_per_thread

        threads = []
        for i in range(thread_sayisi):
            thread = threading.Thread(target=log_ekle, args=(i,))
            threads.append(thread)

        # Tüm thread'leri başlat
        for thread in threads:
            thread.start()

        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join()

        # Özellik: Tüm log kayıtları thread-safe şekilde eklenmiş olmalı
        self.assertEqual(log_sayisi(), beklenen_toplam)

        log_kayitlari = log_kayitlarini_listele()
        self.assertEqual(len(log_kayitlari), beklenen_toplam)


if __name__ == "__main__":
    unittest.main()
