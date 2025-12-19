# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_buton_eslestirme_veri_butunlugu_property
# Description: Buton eşleştirme veri bütünlüğü property-based testleri
# Changelog:
# - İlk oluşturma

"""
UI Smoke Test Altyapısı - Buton Eşleştirme Veri Bütünlüğü Property-Based Testleri

Bu modül buton eşleştirme kayıt sisteminin veri bütünlüğü özelliklerini test eder.
"""

from hypothesis import given, strategies as st, settings, assume
import pytest
from datetime import datetime
from typing import Optional

from uygulama.arayuz.buton_eslestirme_kaydi import (
    ButonEslestirme,
    ButonEslestirmeKayitSistemi,
    kayit_ekle,
    kayitlari_listele,
    kayitlari_temizle,
)


class TestButonEslestirmeVeriButunlugu:
    """Buton eşleştirme veri bütünlüğü property-based testleri"""

    def setup_method(self):
        """Her test öncesi kayıtları temizle"""
        kayitlari_temizle()

    @given(
        ekran_adi=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32, max_codepoint=126),
        ).filter(lambda x: x.strip()),
        buton_adi=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32, max_codepoint=126),
        ).filter(lambda x: x.strip()),
        handler_adi=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126),
        ).filter(lambda x: x.strip()),
        servis_metodu=st.one_of(
            st.none(),
            st.text(
                min_size=1,
                max_size=50,
                alphabet=st.characters(
                    whitelist_categories=("Lu", "Ll", "Nd", "Pc"), min_codepoint=32, max_codepoint=126
                ),
            ).filter(lambda x: x.strip()),
        ),
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_buton_eslestirme_veri_butunlugu(
        self, ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: Optional[str]
    ):
        """
        **Feature: ui-smoke-test-altyapisi, Property 4: Buton Eşleştirme Veri Bütünlüğü**

        Herhangi bir buton eşleştirmesi kaydedildiğinde, sistem ekran adı, buton adı,
        handler adı ve servis metodunu saklamalıdır
        **Validates: Requirements 2.1**
        """
        # Arrange - Başlangıç durumu
        baslangic_kayit_sayisi = len(kayitlari_listele())

        # Act - Buton eşleştirmesi kaydet
        kayit_ekle(ekran_adi=ekran_adi, buton_adi=buton_adi, handler_adi=handler_adi, servis_metodu=servis_metodu)

        # Assert - Veri bütünlüğü kontrolleri
        kayitlar = kayitlari_listele()

        # Kayıt sayısı artmış olmalı
        assert len(kayitlar) == baslangic_kayit_sayisi + 1

        # Son eklenen kayıt doğru verileri içermeli
        son_kayit = kayitlar[-1]

        # Zorunlu alanlar doğru kaydedilmiş olmalı
        assert son_kayit["ekran_adi"] == ekran_adi
        assert son_kayit["buton_adi"] == buton_adi
        assert son_kayit["handler_adi"] == handler_adi

        # Servis metodu doğru kaydedilmiş olmalı (None olabilir)
        assert son_kayit["servis_metodu"] == servis_metodu

        # Otomatik alanlar mevcut olmalı
        assert "kayit_zamani" in son_kayit
        assert son_kayit["kayit_zamani"] is not None
        assert "cagrilma_sayisi" in son_kayit
        assert son_kayit["cagrilma_sayisi"] == 0

        # Zaman damgası geçerli format olmalı
        try:
            datetime.fromisoformat(son_kayit["kayit_zamani"])
        except ValueError:
            pytest.fail("Kayıt zamanı geçersiz ISO format")

    @given(
        kayit_sayisi=st.integers(min_value=1, max_value=20),
        ekran_adi=st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32, max_codepoint=126),
        ).filter(lambda x: x.strip()),
    )
    @settings(max_examples=50, deadline=10000)
    def test_property_coklu_kayit_veri_butunlugu(self, kayit_sayisi: int, ekran_adi: str):
        """
        **Feature: ui-smoke-test-altyapisi, Property 4: Buton Eşleştirme Veri Bütünlüğü**

        Herhangi bir sayıda buton eşleştirmesi kaydedildiğinde, sistem tüm kayıtların
        veri bütünlüğünü korumalıdır
        **Validates: Requirements 2.1**
        """
        # Arrange - Başlangıç durumu
        baslangic_kayit_sayisi = len(kayitlari_listele())

        # Act - Birden fazla kayıt ekle
        for i in range(kayit_sayisi):
            kayit_ekle(
                ekran_adi=ekran_adi,
                buton_adi=f"buton_{i}",
                handler_adi=f"handler_{i}",
                servis_metodu=f"servis_{i}" if i % 2 == 0 else None,
            )

        # Assert - Tüm kayıtların veri bütünlüğü
        kayitlar = kayitlari_listele()

        # Toplam kayıt sayısı doğru olmalı
        assert len(kayitlar) == baslangic_kayit_sayisi + kayit_sayisi

        # Son eklenen kayıtları kontrol et
        son_kayitlar = kayitlar[-kayit_sayisi:]

        for i, kayit in enumerate(son_kayitlar):
            # Her kayıt gerekli alanları içermeli
            assert kayit["ekran_adi"] == ekran_adi
            assert kayit["buton_adi"] == f"buton_{i}"
            assert kayit["handler_adi"] == f"handler_{i}"

            # Servis metodu koşullu olarak doğru olmalı
            beklenen_servis = f"servis_{i}" if i % 2 == 0 else None
            assert kayit["servis_metodu"] == beklenen_servis

            # Otomatik alanlar mevcut olmalı
            assert "kayit_zamani" in kayit
            assert kayit["kayit_zamani"] is not None
            assert "cagrilma_sayisi" in kayit
            assert kayit["cagrilma_sayisi"] == 0

    @given(sistem_sayisi=st.integers(min_value=2, max_value=5))
    @settings(max_examples=20, deadline=10000)
    def test_property_thread_safety_veri_butunlugu(self, sistem_sayisi: int):
        """
        **Feature: ui-smoke-test-altyapisi, Property 4: Buton Eşleştirme Veri Bütünlüğü**

        Herhangi bir thread-safe kayıt sistemi kullanıldığında, veri bütünlüğü korunmalıdır
        **Validates: Requirements 2.1**
        """
        import threading
        import time

        # Arrange - Birden fazla kayıt sistemi oluştur
        sistemler = [ButonEslestirmeKayitSistemi() for _ in range(sistem_sayisi)]

        def kayit_ekle_thread(sistem, thread_id):
            """Thread içinde kayıt ekleme fonksiyonu"""
            for i in range(5):
                sistem.kayit_ekle(
                    ekran_adi=f"ekran_t{thread_id}",
                    buton_adi=f"buton_t{thread_id}_{i}",
                    handler_adi=f"handler_t{thread_id}_{i}",
                    servis_metodu=f"servis_t{thread_id}_{i}",
                )
                time.sleep(0.001)  # Kısa bekleme

        # Act - Paralel kayıt ekleme
        threads = []
        for i, sistem in enumerate(sistemler):
            thread = threading.Thread(target=kayit_ekle_thread, args=(sistem, i))
            threads.append(thread)
            thread.start()

        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join()

        # Assert - Her sistemde veri bütünlüğü korunmuş olmalı
        for i, sistem in enumerate(sistemler):
            kayitlar = sistem.kayitlari_listele()

            # Her sistemde 5 kayıt olmalı
            assert len(kayitlar) == 5

            # Her kayıt doğru thread ID'sine sahip olmalı
            for kayit in kayitlar:
                assert kayit["ekran_adi"] == f"ekran_t{i}"
                assert kayit["buton_adi"].startswith(f"buton_t{i}_")
                assert kayit["handler_adi"].startswith(f"handler_t{i}_")
                assert kayit["servis_metodu"].startswith(f"servis_t{i}_")

                # Otomatik alanlar mevcut olmalı
                assert "kayit_zamani" in kayit
                assert kayit["kayit_zamani"] is not None
                assert "cagrilma_sayisi" in kayit
                assert kayit["cagrilma_sayisi"] == 0
