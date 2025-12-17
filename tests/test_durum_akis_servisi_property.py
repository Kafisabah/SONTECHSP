# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_durum_akis_servisi_property
# Description: Durum akış servisi property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 11: Durum geçiş kontrolü**
**Validates: Requirements 5.1, 5.3**

**Feature: satis-belgeleri-modulu, Property 12: Geçerli durum geçişi**
**Validates: Requirements 5.2**

**Feature: satis-belgeleri-modulu, Property 13: İptal durumu yönetimi**
**Validates: Requirements 5.4, 5.5**

Durum akış servisi için property-based testler.
"""

from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, assume
import pytest

from sontechsp.uygulama.moduller.satis_belgeleri.modeller import (
    BelgeDurumu, SatisBelgesi, BelgeTuru, BelgeDurumGecmisi
)
from sontechsp.uygulama.moduller.satis_belgeleri.servisler import DurumAkisServisi
from sontechsp.uygulama.moduller.satis_belgeleri.depolar.belge_durum_gecmisi_deposu import IBelgeDurumGecmisiDeposu
from sontechsp.uygulama.cekirdek.hatalar import IsKuraliHatasi


# Test stratejileri
@st.composite
def belge_durumu_strategy(draw):
    """Belge durumu üretici"""
    return draw(st.sampled_from(list(BelgeDurumu)))


@st.composite
def satis_belgesi_strategy(draw):
    """Satış belgesi üretici"""
    return SatisBelgesi(
        belge_id=draw(st.integers(min_value=1, max_value=10000)),
        belge_turu=draw(st.sampled_from(list(BelgeTuru))),
        belge_durumu=draw(belge_durumu_strategy()),
        magaza_id=draw(st.integers(min_value=1, max_value=100)),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=1000))
    )


@st.composite
def benzersiz_satis_belgesi_listesi_strategy(draw):
    """Benzersiz ID'li satış belgesi listesi üretici"""
    liste_boyutu = draw(st.integers(min_value=1, max_value=3))  # Daha küçük liste
    belgeler = []
    
    # Basit sıralı ID kullan
    base_id = draw(st.integers(min_value=1, max_value=1000))
    
    for i in range(liste_boyutu):
        belge = SatisBelgesi(
            belge_id=base_id + i,  # Sıralı ID
            belge_turu=draw(st.sampled_from(list(BelgeTuru))),
            belge_durumu=draw(belge_durumu_strategy()),
            magaza_id=draw(st.integers(min_value=1, max_value=10)),  # Daha küçük aralık
            olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=10))  # Daha küçük aralık
        )
        belgeler.append(belge)
    
    return belgeler


@st.composite
def kullanici_id_strategy(draw):
    """Kullanıcı ID üretici"""
    return draw(st.integers(min_value=1, max_value=1000))


@st.composite
def iptal_nedeni_strategy(draw):
    """İptal nedeni üretici"""
    return draw(st.text(min_size=5, max_size=100))


class TestDurumAkisServisiProperty:
    """Durum akış servisi property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_gecmis_deposu = Mock(spec=IBelgeDurumGecmisiDeposu)
        self.durum_akis_servisi = DurumAkisServisi(self.mock_gecmis_deposu)
    
    @given(belge_durumu_strategy(), belge_durumu_strategy())
    def test_durum_gecis_kontrolu(self, mevcut_durum, hedef_durum):
        """
        **Feature: satis-belgeleri-modulu, Property 11: Durum geçiş kontrolü**
        **Validates: Requirements 5.1, 5.3**
        
        Herhangi bir durum güncelleme işlemi için geçiş kuralları kontrol edilmeli 
        ve geçersiz geçişler reddedilmelidir
        """
        # Geçerli geçişler tanımı
        gecerli_gecisler = {
            BelgeDurumu.TASLAK: [BelgeDurumu.ONAYLANDI, BelgeDurumu.IPTAL],
            BelgeDurumu.ONAYLANDI: [BelgeDurumu.FATURALANDI, BelgeDurumu.IPTAL],
            BelgeDurumu.FATURALANDI: [BelgeDurumu.IPTAL],
            BelgeDurumu.IPTAL: []
        }
        
        # Durum geçiş kontrolü
        gecis_gecerli = self.durum_akis_servisi.durum_degistirilebilir_mi(
            mevcut_durum, hedef_durum
        )
        
        # Beklenen sonuç
        beklenen_gecerli = hedef_durum in gecerli_gecisler.get(mevcut_durum, [])
        
        # Kontrol
        assert gecis_gecerli == beklenen_gecerli
        
        # Geçerli geçişler listesi kontrolü
        gecerli_liste = self.durum_akis_servisi.gecerli_gecisleri_al(mevcut_durum)
        beklenen_liste = gecerli_gecisler.get(mevcut_durum, [])
        
        assert set(gecerli_liste) == set(beklenen_liste)
    
    @given(satis_belgesi_strategy(), belge_durumu_strategy(), kullanici_id_strategy())
    def test_gecerli_durum_gecisi(self, belge, yeni_durum, kullanici_id):
        """
        **Feature: satis-belgeleri-modulu, Property 12: Geçerli durum geçişi**
        **Validates: Requirements 5.2**
        
        Herhangi bir geçerli durum geçişi için belge durumu güncellenmeli 
        ve zaman damgası eklenmelidir
        """
        # Mock depo davranışı
        self.mock_gecmis_deposu.ekle.return_value = Mock()
        
        # Geçerli geçiş mi kontrol et
        gecis_gecerli = self.durum_akis_servisi.durum_degistirilebilir_mi(
            belge.belge_durumu, yeni_durum
        )
        
        if gecis_gecerli and belge.belge_durumu != yeni_durum:
            # Eski durumu kaydet
            eski_durum = belge.belge_durumu
            
            # Durum güncelle
            basarili = self.durum_akis_servisi.durum_guncelle(
                belge, yeni_durum, kullanici_id, "Test güncelleme"
            )
            
            # Güncelleme başarılı olmalı
            assert basarili == True
            
            # Belge durumu güncellenmiş olmalı
            assert belge.belge_durumu == yeni_durum
            
            # Geçmiş deposuna kayıt eklenmiş olmalı
            assert self.mock_gecmis_deposu.ekle.called
            
        elif not gecis_gecerli and belge.belge_durumu != yeni_durum:
            # Geçersiz geçiş için hata fırlatılmalı
            with pytest.raises(IsKuraliHatasi):
                self.durum_akis_servisi.durum_guncelle(
                    belge, yeni_durum, kullanici_id, "Test güncelleme"
                )
    
    @given(satis_belgesi_strategy(), iptal_nedeni_strategy(), kullanici_id_strategy())
    def test_iptal_durumu_yonetimi(self, belge, iptal_nedeni, kullanici_id):
        """
        **Feature: satis-belgeleri-modulu, Property 13: İptal durumu yönetimi**
        **Validates: Requirements 5.4, 5.5**
        
        Herhangi bir belge iptal edildiğinde iptal nedeni kaydedilmeli 
        ve sonraki durum geçişleri reddedilmelidir
        """
        # Mock depo davranışı
        self.mock_gecmis_deposu.ekle.return_value = Mock()
        
        # İptal edilebilir durum mu kontrol et
        iptal_edilebilir = self.durum_akis_servisi.durum_degistirilebilir_mi(
            belge.belge_durumu, BelgeDurumu.IPTAL
        )
        
        if iptal_edilebilir:
            # Belgeyi iptal et
            basarili = self.durum_akis_servisi.belge_iptal_et(
                belge, iptal_nedeni, kullanici_id
            )
            
            # İptal başarılı olmalı
            assert basarili == True
            
            # Belge durumu IPTAL olmalı
            assert belge.belge_durumu == BelgeDurumu.IPTAL
            
            # İptal bilgileri kaydedilmiş olmalı
            assert belge.iptal_nedeni == iptal_nedeni
            assert belge.iptal_tarihi is not None
            
            # İptal durumundan başka duruma geçiş yapılamamalı
            for hedef_durum in [BelgeDurumu.TASLAK, BelgeDurumu.ONAYLANDI, BelgeDurumu.FATURALANDI]:
                gecis_gecerli = self.durum_akis_servisi.durum_degistirilebilir_mi(
                    BelgeDurumu.IPTAL, hedef_durum
                )
                assert gecis_gecerli == False
        
        else:
            # İptal edilemez durum için hata fırlatılmalı
            with pytest.raises(IsKuraliHatasi):
                self.durum_akis_servisi.belge_iptal_et(
                    belge, iptal_nedeni, kullanici_id
                )
    
    @given(benzersiz_satis_belgesi_listesi_strategy(), 
           belge_durumu_strategy(), kullanici_id_strategy())
    def test_toplu_durum_guncelleme(self, belge_listesi, yeni_durum, kullanici_id):
        """
        Toplu durum güncelleme işleminin tutarlılığını test et
        """
        # Mock depo davranışı
        self.mock_gecmis_deposu.ekle.return_value = Mock()
        
        # Toplu güncelleme yap
        sonuclar = self.durum_akis_servisi.toplu_durum_guncelle(
            belge_listesi, yeni_durum, kullanici_id, "Toplu güncelleme"
        )
        
        # Her belge için sonuç olmalı
        assert len(sonuclar) == len(belge_listesi)
        
        # Sonuçları kontrol et
        for belge in belge_listesi:
            assert belge.belge_id in sonuclar
            
            # Geçerli geçiş ise başarılı olmalı
            gecis_gecerli = self.durum_akis_servisi.durum_degistirilebilir_mi(
                belge.belge_durumu, yeni_durum
            )
            
            if gecis_gecerli and belge.belge_durumu != yeni_durum:
                assert sonuclar[belge.belge_id] == True
                assert belge.belge_durumu == yeni_durum
            elif belge.belge_durumu == yeni_durum:
                assert sonuclar[belge.belge_id] == True
            else:
                assert sonuclar[belge.belge_id] == False
    
    @given(st.integers(min_value=1, max_value=10000))
    def test_durum_gecmisi_alma(self, belge_id):
        """
        Durum geçmişi alma işleminin tutarlılığını test et
        """
        # Mock geçmiş kayıtları
        mock_gecmis_kayitlari = [
            Mock(
                eski_durum=BelgeDurumu.TASLAK.value,
                yeni_durum=BelgeDurumu.ONAYLANDI.value,
                degistiren_kullanici_id=1,
                aciklama="Test geçiş",
                olusturma_tarihi=Mock()
            ),
            Mock(
                eski_durum=BelgeDurumu.ONAYLANDI.value,
                yeni_durum=BelgeDurumu.FATURALANDI.value,
                degistiren_kullanici_id=2,
                aciklama="Faturalama",
                olusturma_tarihi=Mock()
            )
        ]
        
        self.mock_gecmis_deposu.belge_gecmisi_al.return_value = mock_gecmis_kayitlari
        
        # Geçmişi al
        gecmis = self.durum_akis_servisi.durum_gecmisi_al(belge_id)
        
        # Doğru sayıda kayıt dönmeli
        assert len(gecmis) == len(mock_gecmis_kayitlari)
        
        # Her kayıt doğru formatta olmalı
        for i, kayit in enumerate(gecmis):
            assert 'eski_durum' in kayit
            assert 'yeni_durum' in kayit
            assert 'degistiren_kullanici_id' in kayit
            assert 'aciklama' in kayit
            assert 'tarih' in kayit
        
        # Depo metodu çağrılmalı
        self.mock_gecmis_deposu.belge_gecmisi_al.assert_called_with(belge_id)
    
    @given(st.integers(min_value=1, max_value=10000))
    def test_durum_istatistikleri(self, belge_id):
        """
        Durum istatistikleri hesaplama tutarlılığını test et
        """
        # Mock geçmiş kayıtları
        mock_gecmis_kayitlari = [
            Mock(
                eski_durum=None,
                yeni_durum=BelgeDurumu.TASLAK.value,
                degistiren_kullanici_id=1,
                aciklama="İlk oluşturma",
                olusturma_tarihi=Mock()
            ),
            Mock(
                eski_durum=BelgeDurumu.TASLAK.value,
                yeni_durum=BelgeDurumu.ONAYLANDI.value,
                degistiren_kullanici_id=1,
                aciklama="Onaylama",
                olusturma_tarihi=Mock()
            )
        ]
        
        self.mock_gecmis_deposu.belge_gecmisi_al.return_value = mock_gecmis_kayitlari
        
        # İstatistikleri al
        istatistikler = self.durum_akis_servisi.durum_istatistikleri_al(belge_id)
        
        # Gerekli alanlar mevcut olmalı
        assert 'toplam_degisiklik' in istatistikler
        assert 'ilk_durum' in istatistikler
        assert 'son_durum' in istatistikler
        assert 'degisiklik_sayisi_duruma_gore' in istatistikler
        
        # Değerler doğru olmalı
        assert istatistikler['toplam_degisiklik'] == len(mock_gecmis_kayitlari)
        assert istatistikler['ilk_durum'] == BelgeDurumu.TASLAK.value
        assert istatistikler['son_durum'] == BelgeDurumu.ONAYLANDI.value