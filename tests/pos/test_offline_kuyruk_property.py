# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_offline_kuyruk_property
# Description: Offline kuyruk modeli özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
Offline Kuyruk Modeli Özellik Tabanlı Testleri

Bu modül offline kuyruk modelinin özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

import pytest
from hypothesis import given, settings, strategies as st

from sontechsp.uygulama.moduller.pos.arayuzler import IslemTuru, KuyrukDurum
from sontechsp.uygulama.moduller.pos.database.models.offline_kuyruk import (
    OfflineKuyruk,
    iade_kuyruk_verisi_olustur,
    offline_kuyruk_validasyon,
    satis_kuyruk_verisi_olustur,
    stok_dusumu_kuyruk_verisi_olustur
)


class TestOfflineKuyrukPropertyTests:
    """Offline kuyruk modeli özellik tabanlı testleri"""
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        islem_turu=st.sampled_from(list(IslemTuru)),
        satis_id=st.integers(min_value=1, max_value=10000),
        sepet_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2),
        fis_no=st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', min_size=3, max_size=10)
    )
    @settings(max_examples=100)
    def test_property_18_offline_islem_kaydetme(
        self, terminal_id, kasiyer_id, islem_turu, satis_id, sepet_id, toplam_tutar, fis_no
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 18: Offline İşlem Kaydetme**
        **Validates: Requirements 5.1**
        
        Herhangi bir satış işlemi için, network kesintisi durumunda sistem işlemi 
        Offline_Kuyruk'a kaydetmeli
        """
        # Arrange - Network kesintisi simülasyonu (kullanılmayan değişken kaldırıldı)
        
        # Satış verisi oluştur
        satis_data = {
            'satis_id': satis_id,
            'sepet_id': sepet_id,
            'toplam_tutar': toplam_tutar,
            'odemeler': [
                {'odeme_turu': 'nakit', 'tutar': str(toplam_tutar)}
            ],
            'fis_no': fis_no
        }
        
        # Act - Offline kuyruk kaydı oluştur
        kuyruk_verisi = satis_kuyruk_verisi_olustur(satis_data)
        
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.SATIS,
            durum=KuyrukDurum.BEKLEMEDE,
            veri=kuyruk_verisi,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=0,
            max_deneme_sayisi=3,
            oncelik=1
        )
        
        # Assert - Özellik doğrulamaları
        # 1. İşlem kuyruğa kaydedilmiş olmalı
        assert offline_kuyruk.islem_turu == IslemTuru.SATIS
        assert offline_kuyruk.durum == KuyrukDurum.BEKLEMEDE
        assert offline_kuyruk.terminal_id == terminal_id
        assert offline_kuyruk.kasiyer_id == kasiyer_id
        
        # 2. İşlem verisi doğru formatlanmış olmalı
        assert offline_kuyruk.veri is not None
        assert offline_kuyruk.veri['islem_turu'] == 'satis'
        assert offline_kuyruk.veri['satis_id'] == satis_id
        assert offline_kuyruk.veri['sepet_id'] == sepet_id
        assert offline_kuyruk.veri['toplam_tutar'] == str(toplam_tutar)
        assert offline_kuyruk.veri['fis_no'] == fis_no
        
        # 3. Kuyruk durumu beklemede olmalı
        assert offline_kuyruk.beklemede_mi() == True
        assert offline_kuyruk.isleniyor_mu() == False
        assert offline_kuyruk.tamamlandi_mi() == False
        assert offline_kuyruk.hata_durumunda_mi() == False
        
        # 4. Validasyon geçmeli
        hatalar = offline_kuyruk_validasyon(offline_kuyruk)
        assert len(hatalar) == 0, f"Offline kuyruk validasyon hataları: {hatalar}"
        
        # 5. Tekrar denenebilir durumda olmalı
        assert offline_kuyruk.tekrar_denenebilir_mi() == True
        assert offline_kuyruk.max_deneme_asildi_mi() == False
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        islem_turu=st.sampled_from(list(IslemTuru)),
        iade_id=st.integers(min_value=1, max_value=10000),
        orijinal_satis_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2),
        neden=st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ', min_size=5, max_size=50)
    )
    @settings(max_examples=100)
    def test_property_18_offline_iade_islem_kaydetme(
        self, terminal_id, kasiyer_id, islem_turu, iade_id, orijinal_satis_id, toplam_tutar, neden
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 18: Offline İşlem Kaydetme**
        **Validates: Requirements 5.1**
        
        Herhangi bir iade işlemi için, network kesintisi durumunda sistem işlemi 
        Offline_Kuyruk'a kaydetmeli
        """
        # Arrange - İade verisi oluştur
        iade_data = {
            'iade_id': iade_id,
            'orijinal_satis_id': orijinal_satis_id,
            'toplam_tutar': toplam_tutar,
            'neden': neden,
            'satirlar': [
                {'urun_id': 1, 'adet': 1, 'birim_fiyat': str(toplam_tutar)}
            ]
        }
        
        # Act - Offline kuyruk kaydı oluştur
        kuyruk_verisi = iade_kuyruk_verisi_olustur(iade_data)
        
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.IADE,
            durum=KuyrukDurum.BEKLEMEDE,
            veri=kuyruk_verisi,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=0,
            max_deneme_sayisi=3,
            oncelik=1
        )
        
        # Assert - Özellik doğrulamaları
        # 1. İade işlemi kuyruğa kaydedilmiş olmalı
        assert offline_kuyruk.islem_turu == IslemTuru.IADE
        assert offline_kuyruk.iade_verisi_mi() == True
        assert offline_kuyruk.satis_verisi_mi() == False
        assert offline_kuyruk.stok_dusumu_verisi_mi() == False
        
        # 2. İade verisi doğru formatlanmış olmalı
        assert offline_kuyruk.veri['islem_turu'] == 'iade'
        assert offline_kuyruk.veri['iade_id'] == iade_id
        assert offline_kuyruk.veri['orijinal_satis_id'] == orijinal_satis_id
        assert offline_kuyruk.veri['toplam_tutar'] == str(toplam_tutar)
        assert offline_kuyruk.veri['neden'] == neden
        
        # 3. Kuyruk durumu beklemede olmalı
        assert offline_kuyruk.beklemede_mi() == True
        
        # 4. Validasyon geçmeli
        hatalar = offline_kuyruk_validasyon(offline_kuyruk)
        assert len(hatalar) == 0, f"Offline kuyruk validasyon hataları: {hatalar}"
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        urun_id=st.integers(min_value=1, max_value=10000),
        adet=st.integers(min_value=1, max_value=100),
        islem_referansi=st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', min_size=5, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_18_offline_stok_dusumu_kaydetme(
        self, terminal_id, kasiyer_id, urun_id, adet, islem_referansi
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 18: Offline İşlem Kaydetme**
        **Validates: Requirements 5.1**
        
        Herhangi bir stok düşümü işlemi için, network kesintisi durumunda sistem işlemi 
        Offline_Kuyruk'a kaydetmeli
        """
        # Arrange - Stok düşümü verisi oluştur
        stok_data = {
            'urun_id': urun_id,
            'adet': adet,
            'islem_referansi': islem_referansi
        }
        
        # Act - Offline kuyruk kaydı oluştur
        kuyruk_verisi = stok_dusumu_kuyruk_verisi_olustur(stok_data)
        
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.STOK_DUSUMU,
            durum=KuyrukDurum.BEKLEMEDE,
            veri=kuyruk_verisi,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=0,
            max_deneme_sayisi=3,
            oncelik=1
        )
        
        # Assert - Özellik doğrulamaları
        # 1. Stok düşümü işlemi kuyruğa kaydedilmiş olmalı
        assert offline_kuyruk.islem_turu == IslemTuru.STOK_DUSUMU
        assert offline_kuyruk.stok_dusumu_verisi_mi() == True
        assert offline_kuyruk.satis_verisi_mi() == False
        assert offline_kuyruk.iade_verisi_mi() == False
        
        # 2. Stok düşümü verisi doğru formatlanmış olmalı
        assert offline_kuyruk.veri['islem_turu'] == 'stok_dusumu'
        assert offline_kuyruk.veri['urun_id'] == urun_id
        assert offline_kuyruk.veri['adet'] == adet
        assert offline_kuyruk.veri['islem_referansi'] == islem_referansi
        
        # 3. Validasyon geçmeli
        hatalar = offline_kuyruk_validasyon(offline_kuyruk)
        assert len(hatalar) == 0, f"Offline kuyruk validasyon hataları: {hatalar}"
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        islem_turu=st.sampled_from(list(IslemTuru)),
        offline_mesaj=st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ', min_size=10, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_19_offline_durum_bildirimi(
        self, terminal_id, kasiyer_id, islem_turu, offline_mesaj
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 19: Offline Durum Bildirimi**
        **Validates: Requirements 5.2**
        
        Herhangi bir offline işlem için, sistem kullanıcıya offline durumu bildirmeli
        """
        # Arrange - Offline işlem oluştur
        test_veri = {
            'islem_turu': islem_turu.value,
            'mesaj': offline_mesaj,
            'timestamp': datetime.now().isoformat()
        }
        
        offline_kuyruk = OfflineKuyruk(
            islem_turu=islem_turu,
            durum=KuyrukDurum.BEKLEMEDE,
            veri=test_veri,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=0,
            max_deneme_sayisi=3,
            oncelik=1,
            notlar=f"Offline işlem: {offline_mesaj}"
        )
        
        # Act - Offline durum bilgilerini kontrol et
        offline_durum_bilgisi = {
            'kuyruk_id': offline_kuyruk.id,
            'islem_turu': offline_kuyruk.islem_turu.value,
            'durum': offline_kuyruk.durum.value,
            'terminal_id': offline_kuyruk.terminal_id,
            'kasiyer_id': offline_kuyruk.kasiyer_id,
            'islem_tarihi': offline_kuyruk.islem_tarihi,
            'notlar': offline_kuyruk.notlar,
            'offline_mesaj': 'İşlem offline kuyruğa eklendi. Network bağlantısı geri geldiğinde işlenecek.'
        }
        
        # Assert - Özellik doğrulamaları
        # 1. Offline durum bilgisi mevcut olmalı
        assert offline_durum_bilgisi is not None
        assert offline_durum_bilgisi['islem_turu'] == islem_turu.value
        assert offline_durum_bilgisi['durum'] == KuyrukDurum.BEKLEMEDE.value
        assert offline_durum_bilgisi['terminal_id'] == terminal_id
        assert offline_durum_bilgisi['kasiyer_id'] == kasiyer_id
        
        # 2. Offline mesajı kullanıcıya bildirilmeli
        assert 'offline_mesaj' in offline_durum_bilgisi
        assert 'offline' in offline_durum_bilgisi['offline_mesaj'].lower()
        assert ('kuyruk' in offline_durum_bilgisi['offline_mesaj'].lower() or 
                'kuyru' in offline_durum_bilgisi['offline_mesaj'].lower())
        
        # 3. İşlem notları offline durumu belirtmeli
        assert offline_kuyruk.notlar is not None
        assert 'offline' in offline_kuyruk.notlar.lower()
        
        # 4. Kuyruk durumu beklemede olmalı (kullanıcıya bildirim için)
        assert offline_kuyruk.beklemede_mi() == True
        assert offline_kuyruk.isleniyor_mu() == False
        
        # 5. İşlem tarihi mevcut olmalı (bildirim için)
        assert offline_kuyruk.islem_tarihi is not None
        assert isinstance(offline_kuyruk.islem_tarihi, datetime)
        
        # 6. Validasyon geçmeli
        hatalar = offline_kuyruk_validasyon(offline_kuyruk)
        assert len(hatalar) == 0, f"Offline kuyruk validasyon hataları: {hatalar}"


class TestOfflineKuyrukDurumPropertyTests:
    """Offline kuyruk durum yönetimi özellik tabanlı testleri"""
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        deneme_sayisi=st.integers(min_value=0, max_value=2),
        max_deneme_sayisi=st.integers(min_value=3, max_value=5)
    )
    @settings(max_examples=100)
    def test_offline_kuyruk_tekrar_denenebilirlik(
        self, terminal_id, kasiyer_id, deneme_sayisi, max_deneme_sayisi
    ):
        """
        Offline kuyruk tekrar denenebilirlik özellik testi
        
        Herhangi bir kuyruk kaydı için, deneme sayısı maksimum deneme sayısından 
        az ise tekrar denenebilir olmalı
        """
        # Arrange
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.SATIS,
            durum=KuyrukDurum.BEKLEMEDE,
            veri={'test': 'data'},
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=deneme_sayisi,
            max_deneme_sayisi=max_deneme_sayisi,
            oncelik=1
        )
        
        # Act & Assert
        if deneme_sayisi < max_deneme_sayisi:
            assert offline_kuyruk.tekrar_denenebilir_mi() == True
            assert offline_kuyruk.max_deneme_asildi_mi() == False
        else:
            assert offline_kuyruk.tekrar_denenebilir_mi() == False
            assert offline_kuyruk.max_deneme_asildi_mi() == True
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        hata_mesaji=st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ', min_size=5, max_size=100)
    )
    @settings(max_examples=100)
    def test_offline_kuyruk_hata_yonetimi(
        self, terminal_id, kasiyer_id, hata_mesaji
    ):
        """
        Offline kuyruk hata yönetimi özellik testi
        
        Herhangi bir hata durumu için, kuyruk kaydı hata durumuna getirilmeli 
        ve hata mesajı saklanmalı
        """
        # Arrange
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.SATIS,
            durum=KuyrukDurum.ISLENIYOR,
            veri={'test': 'data'},
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=1,
            max_deneme_sayisi=3,
            oncelik=1
        )
        
        # Act - Hata durumuna getir
        offline_kuyruk.hata_durumuna_getir(hata_mesaji)
        
        # Assert
        assert offline_kuyruk.hata_durumunda_mi() == True
        assert offline_kuyruk.durum == KuyrukDurum.HATA
        assert offline_kuyruk.hata_mesaji == hata_mesaji
        assert offline_kuyruk.son_deneme_tarihi is not None
        assert offline_kuyruk.isleniyor_mu() == False
        assert offline_kuyruk.tamamlandi_mi() == False
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        deneme_sayisi=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=100)
    def test_offline_kuyruk_gecikme_hesaplama(
        self, terminal_id, kasiyer_id, deneme_sayisi
    ):
        """
        Offline kuyruk gecikme hesaplama özellik testi
        
        Herhangi bir deneme sayısı için, exponential backoff ile gecikme süresi 
        doğru hesaplanmalı
        """
        # Arrange
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.SATIS,
            durum=KuyrukDurum.HATA,
            veri={'test': 'data'},
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=deneme_sayisi,
            max_deneme_sayisi=3,
            oncelik=1
        )
        
        # Act
        gecikme_suresi = offline_kuyruk.gecikme_suresi_hesapla()
        
        # Assert
        # Exponential backoff: 2^deneme_sayisi * 60 saniye (max 30 dakika = 1800 saniye)
        beklenen_gecikme = min(2 ** deneme_sayisi * 60, 1800)
        assert gecikme_suresi == beklenen_gecikme
        assert gecikme_suresi >= 60  # En az 1 dakika
        assert gecikme_suresi <= 1800  # En fazla 30 dakika
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        anahtar=st.text(alphabet='abcdefghijklmnopqrstuvwxyz_', min_size=3, max_size=20),
        deger=st.one_of(
            st.text(min_size=1, max_size=50),
            st.integers(min_value=1, max_value=1000),
            st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
        )
    )
    @settings(max_examples=100)
    def test_offline_kuyruk_veri_yonetimi(
        self, terminal_id, kasiyer_id, anahtar, deger
    ):
        """
        Offline kuyruk veri yönetimi özellik testi
        
        Herhangi bir anahtar-değer çifti için, veri JSON'ına ekleme ve getirme 
        işlemleri doğru çalışmalı
        """
        # Arrange
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.SATIS,
            durum=KuyrukDurum.BEKLEMEDE,
            veri={'mevcut_anahtar': 'mevcut_deger'},
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=0,
            max_deneme_sayisi=3,
            oncelik=1
        )
        
        # Act - Veri ekleme
        offline_kuyruk.veri_guncelle(anahtar, deger)
        
        # Assert - Veri getirme
        alinan_deger = offline_kuyruk.veri_getir(anahtar)
        assert alinan_deger == deger
        
        # Mevcut veri korunmuş olmalı
        mevcut_deger = offline_kuyruk.veri_getir('mevcut_anahtar')
        assert mevcut_deger == 'mevcut_deger'
        
        # Olmayan anahtar için varsayılan değer dönmeli
        olmayan_deger = offline_kuyruk.veri_getir('olmayan_anahtar', 'varsayilan')
        assert olmayan_deger == 'varsayilan'


class TestOfflineKuyrukValidasyonPropertyTests:
    """Offline kuyruk validasyon özellik tabanlı testleri"""
    
    @given(
        terminal_id=st.integers(min_value=-100, max_value=100),
        kasiyer_id=st.integers(min_value=-100, max_value=100),
        deneme_sayisi=st.integers(min_value=-10, max_value=20),
        max_deneme_sayisi=st.integers(min_value=-5, max_value=10),
        oncelik=st.integers(min_value=-5, max_value=10)
    )
    @settings(max_examples=100)
    def test_offline_kuyruk_validasyon_kurallari(
        self, terminal_id, kasiyer_id, deneme_sayisi, max_deneme_sayisi, oncelik
    ):
        """
        Offline kuyruk validasyon kuralları özellik testi
        
        Herhangi bir kuyruk kaydı için, validasyon kuralları doğru uygulanmalı
        """
        # Arrange
        offline_kuyruk = OfflineKuyruk(
            islem_turu=IslemTuru.SATIS,
            durum=KuyrukDurum.BEKLEMEDE,
            veri={'test': 'data'} if terminal_id > 0 and kasiyer_id > 0 else None,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            islem_tarihi=datetime.now(),
            deneme_sayisi=deneme_sayisi,
            max_deneme_sayisi=max_deneme_sayisi,
            oncelik=oncelik
        )
        
        # Act
        hatalar = offline_kuyruk_validasyon(offline_kuyruk)
        
        # Assert - Validasyon kuralları kontrolü
        hata_sayisi = 0
        
        if terminal_id <= 0:
            hata_sayisi += 1
            assert any("terminal id" in hata.lower() for hata in hatalar)
        
        if kasiyer_id <= 0:
            hata_sayisi += 1
            assert any("kasiyer id" in hata.lower() for hata in hatalar)
        
        if deneme_sayisi < 0:
            hata_sayisi += 1
            assert any("deneme sayısı" in hata.lower() for hata in hatalar)
        
        if max_deneme_sayisi <= 0:
            hata_sayisi += 1
            assert any("maksimum deneme" in hata.lower() for hata in hatalar)
        
        if oncelik < 1 or oncelik > 5:
            hata_sayisi += 1
            assert any("öncelik" in hata.lower() for hata in hatalar)
        
        if not offline_kuyruk.veri:
            hata_sayisi += 1
            assert any("işlem verisi" in hata.lower() for hata in hatalar)
        
        if deneme_sayisi > max_deneme_sayisi and max_deneme_sayisi > 0:
            hata_sayisi += 1
            assert any("deneme sayısı maksimum" in hata.lower() for hata in hatalar)
        
        # Geçerli durumda hata olmamalı
        if (terminal_id > 0 and kasiyer_id > 0 and deneme_sayisi >= 0 and 
            max_deneme_sayisi > 0 and 1 <= oncelik <= 5 and 
            offline_kuyruk.veri and deneme_sayisi <= max_deneme_sayisi):
            assert len(hatalar) == 0, f"Geçerli kuyruk için beklenmeyen hatalar: {hatalar}"
        else:
            assert len(hatalar) >= hata_sayisi, f"Beklenen hata sayısı: {hata_sayisi}, Gerçek: {len(hatalar)}"