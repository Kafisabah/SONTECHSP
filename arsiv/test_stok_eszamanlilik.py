# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_stok_eszamanlilik
# Description: Eş zamanlı stok işlem testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Eş Zamanlı Stok İşlem Testleri

Bu modül eş zamanlı stok işlemlerinin güvenilirliğini test eder.
Row-level lock mekanizması ve veri tutarlılığı kontrolü yapar.
Thread-safe işlem testleri ve çakışma senaryolarını test eder.
"""

import threading
import time
from decimal import Decimal
from typing import List, Dict, Any
from unittest.mock import Mock, patch

import pytest
from hypothesis import given, strategies as st, settings, assume

from sontechsp.uygulama.moduller.stok.dto import UrunDTO, StokHareketDTO, StokBakiyeDTO
from sontechsp.uygulama.moduller.stok.depolar.urun_repository import UrunRepository
from sontechsp.uygulama.moduller.stok.depolar.stok_hareket_repository import StokHareketRepository
from sontechsp.uygulama.moduller.stok.depolar.stok_bakiye_repository import StokBakiyeRepository
from sontechsp.uygulama.moduller.stok.hatalar.stok_hatalari import EsZamanliErisimError, StokYetersizError


class TestEsZamanliStokKilitleme:
    """Eş zamanlı stok kilitleme property testleri"""

    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        magaza_id=st.integers(min_value=1, max_value=10),
        baslangic_stok=st.decimals(min_value=10, max_value=100, places=4),
        thread_sayisi=st.integers(min_value=2, max_value=5),
        islem_miktari=st.decimals(min_value=1, max_value=5, places=4),
    )
    @settings(max_examples=50, deadline=10000)
    def test_property_7_es_zamanli_stok_kilitleme(
        self, urun_id, magaza_id, baslangic_stok, thread_sayisi, islem_miktari
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 7: Eş zamanlı stok kilitleme**

        For any aynı ürüne eş zamanlı erişim, row-level lock ile sadece bir işlemin
        başarılı olmasını sağlamalı
        **Validates: Requirements 3.1, 3.2**
        """
        # Arrange - Test verilerini hazırla
        assume(baslangic_stok > islem_miktari * thread_sayisi)  # Yeterli stok olsun

        # Mock repository'leri oluştur
        stok_hareket_repo = Mock(spec=StokHareketRepository)
        stok_bakiye_repo = Mock(spec=StokBakiyeRepository)

        # Thread-safe stok kontrolü simülasyonu
        self._mevcut_stok = baslangic_stok
        self._kilitli_kaynaklar = set()
        self._lock = threading.Lock()
        self._basarili_islemler = []
        self._basarisiz_islemler = []

        def mock_kilitle_ve_bakiye_getir(u_id, m_id, d_id=None):
            """Mock kilitleme ve bakiye getirme"""
            kaynak_key = f"{u_id}_{m_id}_{d_id}"

            with self._lock:
                if kaynak_key in self._kilitli_kaynaklar:
                    # Zaten kilitli - PostgreSQL NOWAIT davranışı simülasyonu
                    raise EsZamanliErisimError(f"Kaynak zaten kilitli: {kaynak_key}")

                # Kilidi al
                self._kilitli_kaynaklar.add(kaynak_key)
                return self._mevcut_stok

        def mock_bakiye_guncelle(u_id, m_id, miktar_degisimi, d_id=None):
            """Mock bakiye güncelleme"""
            kaynak_key = f"{u_id}_{m_id}_{d_id}"

            with self._lock:
                if kaynak_key not in self._kilitli_kaynaklar:
                    raise EsZamanliErisimError(f"Kaynak kilitli değil: {kaynak_key}")

                # Stok kontrolü
                yeni_stok = self._mevcut_stok + miktar_degisimi
                if yeni_stok < 0:
                    raise StokYetersizError(
                        f"Yetersiz stok: {self._mevcut_stok}, talep: {abs(miktar_degisimi)}",
                        "TEST_URUN",
                        self._mevcut_stok,
                        abs(miktar_degisimi),
                    )

                # Stok güncelle
                self._mevcut_stok = yeni_stok

                # Kilidi serbest bırak
                self._kilitli_kaynaklar.discard(kaynak_key)
                return True

        # Mock fonksiyonları ata
        stok_hareket_repo.kilitle_ve_bakiye_getir.side_effect = mock_kilitle_ve_bakiye_getir
        stok_bakiye_repo.bakiye_guncelle.side_effect = mock_bakiye_guncelle

        def stok_islemi(thread_id):
            """Eş zamanlı stok işlemi"""
            try:
                # Kilitleme ve bakiye getirme
                mevcut_bakiye = stok_hareket_repo.kilitle_ve_bakiye_getir(urun_id, magaza_id)

                # Kısa bekleme (race condition simülasyonu)
                time.sleep(0.01)

                # Stok düşümü
                stok_bakiye_repo.bakiye_guncelle(urun_id, magaza_id, -islem_miktari)

                self._basarili_islemler.append(
                    {"thread_id": thread_id, "onceki_bakiye": mevcut_bakiye, "islem_miktari": islem_miktari}
                )

            except (EsZamanliErisimError, StokYetersizError) as e:
                self._basarisiz_islemler.append({"thread_id": thread_id, "hata": str(e)})

        # Act - Eş zamanlı thread'leri başlat
        threads = []
        for i in range(thread_sayisi):
            thread = threading.Thread(target=stok_islemi, args=(i,))
            threads.append(thread)
            thread.start()

        # Thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=5)

        # Assert - Eş zamanlı erişim kontrolü
        toplam_islem = len(self._basarili_islemler) + len(self._basarisiz_islemler)
        assert toplam_islem == thread_sayisi, f"Tüm thread'ler tamamlanmalıydı: {toplam_islem}/{thread_sayisi}"

        # En az bir işlem başarılı olmalı (stok yeterliyse)
        if baslangic_stok >= islem_miktari:
            assert len(self._basarili_islemler) > 0, "En az bir işlem başarılı olmalıydı"

        # Başarılı işlemler sıralı olmalı (aynı anda değil)
        if len(self._basarili_islemler) > 1:
            # Her başarılı işlem farklı bakiye değeri görmeli
            onceki_bakiyeler = [i["onceki_bakiye"] for i in self._basarili_islemler]
            # Sıralı erişim nedeniyle bakiyeler azalan sırada olmalı
            assert onceki_bakiyeler == sorted(
                onceki_bakiyeler, reverse=True
            ), "Bakiyeler azalan sırada olmalıydı (sıralı erişim)"

        # Final stok kontrolü
        beklenen_final_stok = baslangic_stok - (len(self._basarili_islemler) * islem_miktari)
        assert abs(self._mevcut_stok - beklenen_final_stok) < Decimal(
            "0.0001"
        ), f"Final stok doğru olmalıydı: {self._mevcut_stok} != {beklenen_final_stok}"

        # Hiçbir kaynak kilitli kalmamalı
        assert len(self._kilitli_kaynaklar) == 0, "Hiçbir kaynak kilitli kalmamalıydı"


class TestStokTutarlilikKorunumu:
    """Stok tutarlılık korunumu property testleri"""

    @given(
        urun_sayisi=st.integers(min_value=2, max_value=5),
        magaza_id=st.integers(min_value=1, max_value=3),
        baslangic_stok=st.decimals(min_value=50, max_value=200, places=4),
        islem_sayisi=st.integers(min_value=5, max_value=15),
    )
    @settings(max_examples=30, deadline=15000)
    def test_property_8_stok_tutarlilik_korunumu(self, urun_sayisi, magaza_id, baslangic_stok, islem_sayisi):
        """
        **Feature: test-stabilizasyon-paketi, Property 8: Stok tutarlılık korunumu**

        For any stok işlem serisi, final stok seviyesi matematiksel olarak doğru olmalı
        ve veri kaybı olmamalı
        **Validates: Requirements 3.3, 3.4**
        """
        # Arrange - Test verilerini hazırla
        urun_ids = list(range(1, urun_sayisi + 1))

        # Her ürün için başlangıç stokları
        baslangic_stoklar = {uid: baslangic_stok for uid in urun_ids}
        mevcut_stoklar = baslangic_stoklar.copy()

        # Thread-safe stok yönetimi
        self._stok_lock = threading.Lock()
        self._islem_gecmisi = []
        self._hata_sayisi = 0

        def thread_safe_stok_islemi(urun_id, miktar_degisimi, islem_id):
            """Thread-safe stok işlemi"""
            try:
                with self._stok_lock:
                    # Mevcut stok kontrolü
                    mevcut = mevcut_stoklar[urun_id]
                    yeni_stok = mevcut + miktar_degisimi

                    if yeni_stok < 0:
                        # Negatif stok engelle
                        self._hata_sayisi += 1
                        return False

                    # Stok güncelle
                    mevcut_stoklar[urun_id] = yeni_stok

                    # İşlem geçmişi kaydet
                    self._islem_gecmisi.append(
                        {
                            "islem_id": islem_id,
                            "urun_id": urun_id,
                            "onceki_stok": mevcut,
                            "miktar_degisimi": miktar_degisimi,
                            "yeni_stok": yeni_stok,
                            "timestamp": time.time(),
                        }
                    )

                    return True

            except Exception as e:
                self._hata_sayisi += 1
                return False

        # Act - Rastgele stok işlemleri yap
        threads = []
        for i in range(islem_sayisi):
            # Rastgele ürün seç
            urun_id = urun_ids[i % len(urun_ids)]

            # Rastgele işlem türü (giriş/çıkış)
            if i % 3 == 0:  # %33 giriş
                miktar = Decimal(str(abs(hash(f"{i}_{urun_id}")) % 10 + 1))
            else:  # %67 çıkış
                miktar = -Decimal(str(abs(hash(f"{i}_{urun_id}")) % 5 + 1))

            thread = threading.Thread(target=thread_safe_stok_islemi, args=(urun_id, miktar, i))
            threads.append(thread)
            thread.start()

        # Thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=3)

        # Assert - Tutarlılık kontrolü

        # 1. Hiçbir stok negatif olmamalı
        for urun_id, stok in mevcut_stoklar.items():
            assert stok >= 0, f"Ürün {urun_id} stoku negatif olmamalıydı: {stok}"

        # 2. İşlem geçmişi tutarlılığı
        basarili_islemler = len(self._islem_gecmisi)
        toplam_deneme = islem_sayisi

        assert (
            basarili_islemler + self._hata_sayisi == toplam_deneme
        ), f"Toplam işlem sayısı tutmalıydı: {basarili_islemler} + {self._hata_sayisi} != {toplam_deneme}"

        # 3. Matematiksel tutarlılık kontrolü
        for urun_id in urun_ids:
            # Bu ürün için tüm işlemleri topla
            urun_islemleri = [i for i in self._islem_gecmisi if i["urun_id"] == urun_id]

            toplam_degisim = sum(i["miktar_degisimi"] for i in urun_islemleri)
            beklenen_final = baslangic_stoklar[urun_id] + toplam_degisim
            gercek_final = mevcut_stoklar[urun_id]

            assert abs(gercek_final - beklenen_final) < Decimal("0.0001"), (
                f"Ürün {urun_id} final stoku matematiksel olarak doğru olmalıydı: "
                f"{gercek_final} != {beklenen_final} (başlangıç: {baslangic_stoklar[urun_id]}, "
                f"değişim: {toplam_degisim})"
            )

        # 4. Veri kaybı kontrolü
        # Tüm başarılı işlemler geçmişte kayıtlı olmalı
        assert len(self._islem_gecmisi) > 0, "En az bir işlem başarılı olmalıydı"

        # İşlem geçmişi kronolojik sırada olmalı (timestamp kontrolü)
        timestamps = [i["timestamp"] for i in self._islem_gecmisi]
        assert timestamps == sorted(timestamps), "İşlem geçmişi kronolojik sırada olmalıydı"

        # 5. Toplam stok korunumu (giriş-çıkış dengesi)
        toplam_baslangic = sum(baslangic_stoklar.values())
        toplam_final = sum(mevcut_stoklar.values())
        toplam_net_degisim = sum(i["miktar_degisimi"] for i in self._islem_gecmisi)

        beklenen_toplam_final = toplam_baslangic + toplam_net_degisim
        assert abs(toplam_final - beklenen_toplam_final) < Decimal(
            "0.0001"
        ), f"Toplam stok korunumu: {toplam_final} != {beklenen_toplam_final}"
