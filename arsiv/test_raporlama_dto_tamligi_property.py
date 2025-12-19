# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_raporlama_dto_tamligi_property
# Description: Raporlama modülü DTO tamlığı property testi
# Changelog:
# - İlk oluşturma

"""
**Feature: raporlama-modulu, Property 1: Satış özeti tamlığı**
**Validates: Requirements 1.1**

Herhangi bir geçerli mağaza ID'si ve tarih aralığı için, satış özeti tüm gerekli alanları 
(brüt satış, indirimler, net satış, satış sayısı, iadeler) null olmayan değerlerle içermelidir
"""

import pytest
from hypothesis import given, strategies as st, assume
from decimal import Decimal
from datetime import date, datetime, timedelta

from sontechsp.uygulama.moduller.raporlar.dto import (
    TarihAraligiDTO, SatisOzetiDTO, UrunPerformansDTO, 
    KritikStokDTO, RaporSatirDTO, DisariAktarDTO,
    RaporTuru, DisariAktarFormat
)


# Test stratejileri
pozitif_int_strategy = st.integers(min_value=1, max_value=1000)
pozitif_decimal_strategy = st.decimals(min_value=Decimal('0'), max_value=Decimal('999999.99'), places=2)
non_negative_decimal_strategy = st.decimals(min_value=Decimal('0'), max_value=Decimal('999999.99'), places=2)
tarih_strategy = st.dates(min_value=date(2024, 1, 1), max_value=date(2024, 12, 31))
urun_adi_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Zs')))


@given(
    magaza_id=pozitif_int_strategy,
    brut_satis=pozitif_decimal_strategy,
    indirim_toplam=non_negative_decimal_strategy,
    net_satis=pozitif_decimal_strategy,
    satis_adedi=st.integers(min_value=0, max_value=10000),
    iade_toplam=non_negative_decimal_strategy
)
def test_satis_ozeti_dto_tamligi(magaza_id, brut_satis, indirim_toplam, net_satis, satis_adedi, iade_toplam):
    """
    Property: Satış özeti DTO tamlığı
    
    Herhangi bir satış özeti DTO'su için:
    - Tüm gerekli alanlar null olmayan değerlerle dolu olmalı
    - Numeric alanlar uygun türde olmalı
    - Mağaza ID pozitif olmalı
    """
    # Act: SatisOzetiDTO oluştur
    satis_ozeti = SatisOzetiDTO(
        magaza_id=magaza_id,
        brut_satis=brut_satis,
        indirim_toplam=indirim_toplam,
        net_satis=net_satis,
        satis_adedi=satis_adedi,
        iade_toplam=iade_toplam
    )
    
    # Assert: Tüm alanlar dolu ve doğru türde
    assert satis_ozeti.magaza_id is not None
    assert satis_ozeti.brut_satis is not None
    assert satis_ozeti.indirim_toplam is not None
    assert satis_ozeti.net_satis is not None
    assert satis_ozeti.satis_adedi is not None
    assert satis_ozeti.iade_toplam is not None
    
    # Tür kontrolü
    assert isinstance(satis_ozeti.magaza_id, int)
    assert isinstance(satis_ozeti.brut_satis, Decimal)
    assert isinstance(satis_ozeti.indirim_toplam, Decimal)
    assert isinstance(satis_ozeti.net_satis, Decimal)
    assert isinstance(satis_ozeti.satis_adedi, int)
    assert isinstance(satis_ozeti.iade_toplam, Decimal)
    
    # Değer kontrolü
    assert satis_ozeti.magaza_id > 0
    assert satis_ozeti.brut_satis >= 0
    assert satis_ozeti.indirim_toplam >= 0
    assert satis_ozeti.net_satis >= 0
    assert satis_ozeti.satis_adedi >= 0
    assert satis_ozeti.iade_toplam >= 0


@given(
    urun_id=pozitif_int_strategy,
    urun_adi=urun_adi_strategy,
    miktar_toplam=st.integers(min_value=0, max_value=100000),
    ciro_toplam=non_negative_decimal_strategy
)
def test_urun_performans_dto_tamligi(urun_id, urun_adi, miktar_toplam, ciro_toplam):
    """
    Property: Ürün performans DTO tamlığı
    
    Herhangi bir ürün performans DTO'su için:
    - Tüm gerekli alanlar null olmayan değerlerle dolu olmalı
    - Ürün adı boş olmamalı
    - Numeric değerler uygun türde olmalı
    """
    # Boş string kontrolü için
    assume(urun_adi.strip() != "")
    
    # Act: UrunPerformansDTO oluştur
    urun_performans = UrunPerformansDTO(
        urun_id=urun_id,
        urun_adi=urun_adi,
        miktar_toplam=miktar_toplam,
        ciro_toplam=ciro_toplam
    )
    
    # Assert: Tüm alanlar dolu ve doğru türde
    assert urun_performans.urun_id is not None
    assert urun_performans.urun_adi is not None
    assert urun_performans.miktar_toplam is not None
    assert urun_performans.ciro_toplam is not None
    
    # Tür kontrolü
    assert isinstance(urun_performans.urun_id, int)
    assert isinstance(urun_performans.urun_adi, str)
    assert isinstance(urun_performans.miktar_toplam, int)
    assert isinstance(urun_performans.ciro_toplam, Decimal)
    
    # Değer kontrolü
    assert urun_performans.urun_id > 0
    assert urun_performans.urun_adi.strip() != ""
    assert urun_performans.miktar_toplam >= 0
    assert urun_performans.ciro_toplam >= 0


@given(
    urun_id=pozitif_int_strategy,
    urun_adi=urun_adi_strategy,
    depo_id=pozitif_int_strategy,
    miktar=st.integers(min_value=0, max_value=1000),
    kritik_seviye=st.integers(min_value=1, max_value=100)
)
def test_kritik_stok_dto_tamligi(urun_id, urun_adi, depo_id, miktar, kritik_seviye):
    """
    Property: Kritik stok DTO tamlığı
    
    Herhangi bir kritik stok DTO'su için:
    - Tüm gerekli alanlar null olmayan değerlerle dolu olmalı
    - ID'ler pozitif olmalı
    - Ürün adı boş olmamalı
    """
    # Boş string kontrolü için
    assume(urun_adi.strip() != "")
    
    # Act: KritikStokDTO oluştur
    kritik_stok = KritikStokDTO(
        urun_id=urun_id,
        urun_adi=urun_adi,
        depo_id=depo_id,
        miktar=miktar,
        kritik_seviye=kritik_seviye
    )
    
    # Assert: Tüm alanlar dolu ve doğru türde
    assert kritik_stok.urun_id is not None
    assert kritik_stok.urun_adi is not None
    assert kritik_stok.depo_id is not None
    assert kritik_stok.miktar is not None
    assert kritik_stok.kritik_seviye is not None
    
    # Tür kontrolü
    assert isinstance(kritik_stok.urun_id, int)
    assert isinstance(kritik_stok.urun_adi, str)
    assert isinstance(kritik_stok.depo_id, int)
    assert isinstance(kritik_stok.miktar, int)
    assert isinstance(kritik_stok.kritik_seviye, int)
    
    # Değer kontrolü
    assert kritik_stok.urun_id > 0
    assert kritik_stok.urun_adi.strip() != ""
    assert kritik_stok.depo_id > 0
    assert kritik_stok.miktar >= 0
    assert kritik_stok.kritik_seviye > 0


@given(
    baslangic_tarihi=tarih_strategy,
    gun_farki=st.integers(min_value=0, max_value=365)
)
def test_tarih_araligi_dto_tamligi(baslangic_tarihi, gun_farki):
    """
    Property: Tarih aralığı DTO tamlığı
    
    Herhangi bir tarih aralığı DTO'su için:
    - Tüm tarih alanları null olmayan değerlerle dolu olmalı
    - Başlangıç tarihi bitiş tarihinden küçük veya eşit olmalı
    """
    # Act: TarihAraligiDTO oluştur
    bitis_tarihi = baslangic_tarihi + timedelta(days=gun_farki)
    
    tarih_araligi = TarihAraligiDTO(
        baslangic_tarihi=baslangic_tarihi,
        bitis_tarihi=bitis_tarihi
    )
    
    # Assert: Tüm alanlar dolu ve doğru türde
    assert tarih_araligi.baslangic_tarihi is not None
    assert tarih_araligi.bitis_tarihi is not None
    
    # Tür kontrolü
    assert isinstance(tarih_araligi.baslangic_tarihi, date)
    assert isinstance(tarih_araligi.bitis_tarihi, date)
    
    # Değer kontrolü
    assert tarih_araligi.baslangic_tarihi <= tarih_araligi.bitis_tarihi


@given(
    id=pozitif_int_strategy,
    ad=urun_adi_strategy,
    deger1=st.one_of(st.none(), pozitif_decimal_strategy, pozitif_int_strategy),
    deger2=st.one_of(st.none(), pozitif_decimal_strategy, pozitif_int_strategy),
    deger3=st.one_of(st.none(), pozitif_decimal_strategy, pozitif_int_strategy),
    aciklama=st.one_of(st.none(), st.text(min_size=0, max_size=200))
)
def test_rapor_satir_dto_tamligi(id, ad, deger1, deger2, deger3, aciklama):
    """
    Property: Rapor satır DTO tamlığı
    
    Herhangi bir rapor satır DTO'su için:
    - Zorunlu alanlar (id, ad) null olmayan değerlerle dolu olmalı
    - Opsiyonel alanlar None olabilir
    """
    # Boş string kontrolü için
    assume(ad.strip() != "")
    
    # Act: RaporSatirDTO oluştur
    rapor_satir = RaporSatirDTO(
        id=id,
        ad=ad,
        deger1=deger1,
        deger2=deger2,
        deger3=deger3,
        aciklama=aciklama
    )
    
    # Assert: Zorunlu alanlar dolu
    assert rapor_satir.id is not None
    assert rapor_satir.ad is not None
    
    # Tür kontrolü
    assert isinstance(rapor_satir.id, int)
    assert isinstance(rapor_satir.ad, str)
    
    # Değer kontrolü
    assert rapor_satir.id > 0
    assert rapor_satir.ad.strip() != ""


@given(
    format=st.sampled_from([DisariAktarFormat.CSV, DisariAktarFormat.PDF]),
    dosya_adi=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
    klasor_yolu=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    baslik=st.one_of(st.none(), st.text(min_size=1, max_size=100))
)
def test_disari_aktar_dto_tamligi(format, dosya_adi, klasor_yolu, baslik):
    """
    Property: Dışa aktarım DTO tamlığı
    
    Herhangi bir dışa aktarım DTO'su için:
    - Format alanı null olmayan değerle dolu olmalı
    - Opsiyonel alanlar None olabilir
    - Dosya adı boş string olamaz (None olabilir)
    """
    # Boş string kontrolü için
    if dosya_adi is not None:
        assume(dosya_adi.strip() != "")
    
    # Act: DisariAktarDTO oluştur
    disari_aktar = DisariAktarDTO(
        format=format,
        dosya_adi=dosya_adi,
        klasor_yolu=klasor_yolu,
        baslik=baslik
    )
    
    # Assert: Zorunlu alanlar dolu
    assert disari_aktar.format is not None
    
    # Tür kontrolü
    assert isinstance(disari_aktar.format, DisariAktarFormat)
    
    # Değer kontrolü
    if disari_aktar.dosya_adi is not None:
        assert isinstance(disari_aktar.dosya_adi, str)
        assert disari_aktar.dosya_adi.strip() != ""


@given(
    magaza_id=st.integers(min_value=-1000, max_value=0),
    brut_satis=pozitif_decimal_strategy,
    indirim_toplam=non_negative_decimal_strategy,
    net_satis=pozitif_decimal_strategy,
    satis_adedi=st.integers(min_value=-100, max_value=-1),
    iade_toplam=non_negative_decimal_strategy
)
def test_satis_ozeti_dto_dogrulama_hatalari(magaza_id, brut_satis, indirim_toplam, net_satis, satis_adedi, iade_toplam):
    """
    Property: Satış özeti DTO doğrulama hataları
    
    Geçersiz değerlerle DTO oluşturulduğunda uygun hatalar fırlatılmalı
    """
    # Act & Assert: Geçersiz değerlerle DTO oluşturma
    with pytest.raises(ValueError):
        SatisOzetiDTO(
            magaza_id=magaza_id,  # Negatif veya sıfır
            brut_satis=brut_satis,
            indirim_toplam=indirim_toplam,
            net_satis=net_satis,
            satis_adedi=satis_adedi,  # Negatif
            iade_toplam=iade_toplam
        )


@given(
    baslangic_tarihi=tarih_strategy,
    gun_farki=st.integers(min_value=1, max_value=365)
)
def test_tarih_araligi_dto_dogrulama_hatalari(baslangic_tarihi, gun_farki):
    """
    Property: Tarih aralığı DTO doğrulama hataları
    
    Başlangıç tarihi bitiş tarihinden büyük olduğunda hata fırlatılmalı
    """
    # Act & Assert: Geçersiz tarih aralığı ile DTO oluşturma
    bitis_tarihi = baslangic_tarihi - timedelta(days=gun_farki)  # Başlangıçtan önce
    
    with pytest.raises(ValueError):
        TarihAraligiDTO(
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi
        )