# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_oturum_property
# Description: SONTECHSP oturum yönetimi property-based testleri
# Changelog:
# - 0.1.0: İlk versiyon - Oturum property testleri

"""
SONTECHSP Oturum Yönetimi Property-Based Testleri

Bu modül oturum yönetimi için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak çeşitli senaryolar test edilir.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from typing import List

from sontechsp.uygulama.cekirdek.oturum import (
    OturumBilgisi, OturumYoneticisi, oturum_yoneticisi_al
)


class TestOturumPropertyTestleri:
    """Oturum yönetimi property-based testleri"""
    
    def setup_method(self):
        """Her test öncesi temizlik"""
        # Yeni oturum yöneticisi instance oluştur
        global _oturum_yoneticisi
        import sontechsp.uygulama.cekirdek.oturum as oturum_modulu
        oturum_modulu._oturum_yoneticisi = None
    
    @given(
        kullanici_id=st.integers(min_value=1, max_value=999999),
        kullanici_adi=st.text(min_size=1, max_size=50),
        firma_id=st.integers(min_value=1, max_value=9999),
        magaza_id=st.integers(min_value=1, max_value=9999),
        terminal_id=st.one_of(st.none(), st.integers(min_value=1, max_value=99)),
        roller=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10)
    )
    @settings(max_examples=100)
    def test_oturum_bilgi_butunlugu_property(self, kullanici_id: int, 
                                           kullanici_adi: str, firma_id: int,
                                           magaza_id: int, terminal_id: int,
                                           roller: List[str]):
        """
        **Çekirdek Altyapı, Özellik 8: Oturum bilgi bütünlüğü**
        **Doğrular: Gereksinim 5.1**
        
        Herhangi bir oturum açma işlemi için, gerekli tüm bilgiler 
        (kullanıcı, firma, mağaza) tutulmalıdır
        """
        yonetici = oturum_yoneticisi_al()
        
        # Oturum başlat
        oturum = yonetici.oturum_baslat(
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            firma_id=firma_id,
            magaza_id=magaza_id,
            terminal_id=terminal_id,
            roller=roller
        )
        
        # Özellik: Gerekli tüm bilgiler tutulmalı
        assert oturum.kullanici_id == kullanici_id
        assert oturum.kullanici_adi == kullanici_adi
        assert oturum.firma_id == firma_id
        assert oturum.magaza_id == magaza_id
        assert oturum.terminal_id == terminal_id
        assert oturum.roller == roller
        
        # Otomatik oluşturulan bilgiler de mevcut olmalı
        assert oturum.oturum_baslangic is not None
        assert isinstance(oturum.oturum_baslangic, datetime)
        assert oturum.son_aktivite is not None
        assert isinstance(oturum.son_aktivite, datetime)
        assert isinstance(oturum.ek_bilgiler, dict)
        
        # Aktif oturum da aynı bilgileri içermeli
        aktif = yonetici.aktif_oturum_al()
        assert aktif is not None
        assert aktif.kullanici_id == kullanici_id
        assert aktif.kullanici_adi == kullanici_adi
        assert aktif.firma_id == firma_id
        assert aktif.magaza_id == magaza_id
    
    @given(
        kullanici_id=st.integers(min_value=1, max_value=999999),
        kullanici_adi=st.text(min_size=1, max_size=50),
        firma_id=st.integers(min_value=1, max_value=9999),
        magaza_id=st.integers(min_value=1, max_value=9999),
        yeni_firma_id=st.integers(min_value=1, max_value=9999),
        yeni_magaza_id=st.integers(min_value=1, max_value=9999),
        yeni_terminal_id=st.one_of(st.none(), st.integers(min_value=1, max_value=99))
    )
    @settings(max_examples=100)
    def test_oturum_baglan_guncelleme_property(self, kullanici_id: int,
                                             kullanici_adi: str, firma_id: int,
                                             magaza_id: int, yeni_firma_id: int,
                                             yeni_magaza_id: int, yeni_terminal_id: int):
        """
        **Çekirdek Altyapı, Özellik 9: Oturum bağlam güncelleme**
        **Doğrular: Gereksinim 5.2**
        
        Herhangi bir bağlam değişikliği için, oturum bilgisi güncellenmelidir
        """
        yonetici = oturum_yoneticisi_al()
        
        # İlk oturum başlat
        oturum = yonetici.oturum_baslat(
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            firma_id=firma_id,
            magaza_id=magaza_id
        )
        
        ilk_aktivite = oturum.son_aktivite
        
        # Bağlamı güncelle
        guncelleme_basarili = yonetici.baglan_guncelle(
            firma_id=yeni_firma_id,
            magaza_id=yeni_magaza_id,
            terminal_id=yeni_terminal_id
        )
        
        # Özellik: Bağlam değişikliği başarılı olmalı
        assert guncelleme_basarili is True
        
        # Güncellenmiş değerler doğru olmalı
        aktif = yonetici.aktif_oturum_al()
        assert aktif.firma_id == yeni_firma_id
        assert aktif.magaza_id == yeni_magaza_id
        assert aktif.terminal_id == yeni_terminal_id
        
        # Son aktivite güncellenmiş olmalı
        assert aktif.son_aktivite >= ilk_aktivite
        
        # Değişmeyen bilgiler korunmalı
        assert aktif.kullanici_id == kullanici_id
        assert aktif.kullanici_adi == kullanici_adi
    
    @given(
        kullanici_id=st.integers(min_value=1, max_value=999999),
        kullanici_adi=st.text(min_size=1, max_size=50),
        firma_id=st.integers(min_value=1, max_value=9999),
        magaza_id=st.integers(min_value=1, max_value=9999)
    )
    @settings(max_examples=100)
    def test_oturum_temizlik_garantisi_property(self, kullanici_id: int,
                                               kullanici_adi: str, firma_id: int,
                                               magaza_id: int):
        """
        **Çekirdek Altyapı, Özellik 10: Oturum temizlik garantisi**
        **Doğrular: Gereksinim 5.3**
        
        Herhangi bir oturum sonlandırma için, tüm bilgiler temizlenmelidir
        """
        yonetici = oturum_yoneticisi_al()
        
        # Oturum başlat
        yonetici.oturum_baslat(
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            firma_id=firma_id,
            magaza_id=magaza_id
        )
        
        # Oturum aktif olduğunu doğrula
        assert yonetici.oturum_aktif_mi() is True
        assert yonetici.aktif_oturum_al() is not None
        
        # Oturumu sonlandır
        sonlandirma_basarili = yonetici.oturum_sonlandir()
        
        # Özellik: Sonlandırma başarılı olmalı
        assert sonlandirma_basarili is True
        
        # Tüm bilgiler temizlenmiş olmalı
        assert yonetici.oturum_aktif_mi() is False
        assert yonetici.aktif_oturum_al() is None
        
        # Bağlam bilgisi alınamaz olmalı
        assert yonetici.baglan_bilgisi_al('kullanici_id') is None
        assert yonetici.baglan_bilgisi_al('firma_id') is None
    
    @given(
        kullanici_id=st.integers(min_value=1, max_value=999999),
        kullanici_adi=st.text(min_size=1, max_size=50),
        firma_id=st.integers(min_value=1, max_value=9999),
        magaza_id=st.integers(min_value=1, max_value=9999),
        terminal_listesi=st.lists(st.integers(min_value=1, max_value=99), 
                                min_size=1, max_size=10, unique=True)
    )
    @settings(max_examples=100)
    def test_coklu_terminal_destegi_property(self, kullanici_id: int,
                                           kullanici_adi: str, firma_id: int,
                                           magaza_id: int, terminal_listesi: List[int]):
        """
        **Çekirdek Altyapı, Özellik 11: Çoklu terminal desteği**
        **Doğrular: Gereksinim 5.4**
        
        Herhangi bir terminal kombinasyonu için, terminal bilgisi doğru şekilde tutulmalıdır
        """
        yonetici = oturum_yoneticisi_al()
        
        # Oturum başlat
        yonetici.oturum_baslat(
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            firma_id=firma_id,
            magaza_id=magaza_id
        )
        
        # Çoklu terminal desteği ayarla
        destek_basarili = yonetici.coklu_terminal_destegi(terminal_listesi)
        
        # Özellik: Çoklu terminal desteği başarılı olmalı
        assert destek_basarili is True
        
        # Terminal listesi doğru şekilde tutulmalı
        desteklenen = yonetici.baglan_bilgisi_al('desteklenen_terminaller')
        assert desteklenen == terminal_listesi
        
        # Listeden bir terminal seç ve aktif yap
        if terminal_listesi:
            secilen_terminal = terminal_listesi[0]
            degisim_basarili = yonetici.terminal_degistir(secilen_terminal)
            
            assert degisim_basarili is True
            aktif = yonetici.aktif_oturum_al()
            assert aktif.terminal_id == secilen_terminal
    
    @given(
        kullanici_id=st.integers(min_value=1, max_value=999999),
        kullanici_adi=st.text(min_size=1, max_size=50),
        firma_id=st.integers(min_value=1, max_value=9999),
        magaza_id=st.integers(min_value=1, max_value=9999),
        ek_anahtar=st.text(min_size=1, max_size=20),
        ek_deger=st.one_of(st.text(), st.integers(), st.booleans())
    )
    @settings(max_examples=100)
    def test_oturum_veri_korunumu_property(self, kullanici_id: int,
                                         kullanici_adi: str, firma_id: int,
                                         magaza_id: int, ek_anahtar: str,
                                         ek_deger):
        """
        **Çekirdek Altyapı, Özellik 12: Oturum veri korunumu**
        **Doğrular: Gereksinim 5.5**
        
        Herhangi bir aktif oturum için, bağlam bilgileri korunmalıdır
        """
        yonetici = oturum_yoneticisi_al()
        
        # Oturum başlat
        oturum = yonetici.oturum_baslat(
            kullanici_id=kullanici_id,
            kullanici_adi=kullanici_adi,
            firma_id=firma_id,
            magaza_id=magaza_id
        )
        
        # Ek bilgi ekle
        ek_bilgi_basarili = yonetici.baglan_bilgisi_ayarla(ek_anahtar, ek_deger)
        assert ek_bilgi_basarili is True
        
        # Özellik: Oturum aktif olduğu sürece tüm bilgiler korunmalı
        
        # Temel bilgiler korunmalı
        assert yonetici.baglan_bilgisi_al('kullanici_id') == kullanici_id
        assert yonetici.baglan_bilgisi_al('kullanici_adi') == kullanici_adi
        assert yonetici.baglan_bilgisi_al('firma_id') == firma_id
        assert yonetici.baglan_bilgisi_al('magaza_id') == magaza_id
        
        # Ek bilgi korunmalı
        assert yonetici.baglan_bilgisi_al(ek_anahtar) == ek_deger
        
        # Oturum süresi hesaplanabilmeli
        oturum_suresi = yonetici.oturum_suresi_al()
        assert oturum_suresi is not None
        assert oturum_suresi >= 0
        
        # Son aktivite süresi hesaplanabilmeli
        aktivite_suresi = yonetici.son_aktivite_suresi_al()
        assert aktivite_suresi is not None
        assert aktivite_suresi >= 0
        
        # Oturum hala aktif olmalı
        assert yonetici.oturum_aktif_mi() is True
        aktif = yonetici.aktif_oturum_al()
        assert aktif is not None
        assert aktif.kullanici_id == kullanici_id