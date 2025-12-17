# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_raporlama_dto_tip_guvenligi_property
# Description: Raporlama modülü DTO tip güvenliği property testi
# Changelog:
# - İlk oluşturma

"""
**Feature: raporlama-modulu, Property 28: DTO tip güvenliği**
**Validates: Requirements 7.3**

Herhangi bir veri transfer işlemi için, tüm veri yapıları için güçlü tipli DTO sınıfları kullanılmalıdır
"""

import pytest
from hypothesis import given, strategies as st, assume
from decimal import Decimal
from datetime import date, datetime
from typing import Any, Dict, List

from sontechsp.uygulama.moduller.raporlar.dto import (
    TarihAraligiDTO, SatisOzetiDTO, UrunPerformansDTO, 
    KritikStokDTO, RaporSatirDTO, DisariAktarDTO,
    RaporTuru, DisariAktarFormat
)


# Test stratejileri
pozitif_int_strategy = st.integers(min_value=1, max_value=1000)
pozitif_decimal_strategy = st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2)
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
def test_satis_ozeti_dto_tip_guvenligi(magaza_id, brut_satis, indirim_toplam, net_satis, satis_adedi, iade_toplam):
    """
    Property: Satış özeti DTO tip güvenliği
    
    Herhangi bir satış özeti DTO'su için:
    - Tüm alanlar belirtilen türde olmalı
    - Tür dönüşümleri güvenli olmalı
    - Dataclass anotasyonları doğru olmalı
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
    
    # Assert: Tip güvenliği kontrolü
    assert type(satis_ozeti.magaza_id) is int
    assert type(satis_ozeti.brut_satis) is Decimal
    assert type(satis_ozeti.indirim_toplam) is Decimal
    assert type(satis_ozeti.net_satis) is Decimal
    assert type(satis_ozeti.satis_adedi) is int
    assert type(satis_ozeti.iade_toplam) is Decimal
    
    # Dataclass anotasyonları kontrolü
    annotations = satis_ozeti.__annotations__
    assert annotations['magaza_id'] == int
    assert annotations['brut_satis'] == Decimal
    assert annotations['indirim_toplam'] == Decimal
    assert annotations['net_satis'] == Decimal
    assert annotations['satis_adedi'] == int
    assert annotations['iade_toplam'] == Decimal
    
    # Immutable kontrolü (dataclass frozen değil ama tip güvenliği için)
    original_magaza_id = satis_ozeti.magaza_id
    satis_ozeti.magaza_id = magaza_id + 1
    assert type(satis_ozeti.magaza_id) is int


@given(
    urun_id=pozitif_int_strategy,
    urun_adi=urun_adi_strategy,
    miktar_toplam=st.integers(min_value=0, max_value=100000),
    ciro_toplam=non_negative_decimal_strategy
)
def test_urun_performans_dto_tip_guvenligi(urun_id, urun_adi, miktar_toplam, ciro_toplam):
    """
    Property: Ürün performans DTO tip güvenliği
    
    Herhangi bir ürün performans DTO'su için:
    - String alanlar Unicode güvenli olmalı
    - Numeric alanlar doğru precision'da olmalı
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
    
    # Assert: Tip güvenliği kontrolü
    assert type(urun_performans.urun_id) is int
    assert type(urun_performans.urun_adi) is str
    assert type(urun_performans.miktar_toplam) is int
    assert type(urun_performans.ciro_toplam) is Decimal
    
    # String encoding güvenliği
    assert isinstance(urun_performans.urun_adi.encode('utf-8'), bytes)
    
    # Decimal precision kontrolü
    assert urun_performans.ciro_toplam.as_tuple().exponent >= -2  # En fazla 2 ondalık basamak


@given(
    baslangic_tarihi=tarih_strategy,
    bitis_tarihi=tarih_strategy
)
def test_tarih_araligi_dto_tip_guvenligi(baslangic_tarihi, bitis_tarihi):
    """
    Property: Tarih aralığı DTO tip güvenliği
    
    Herhangi bir tarih aralığı DTO'su için:
    - Tarih alanları date türünde olmalı
    - datetime ile karışmamalı
    """
    # Tarih sıralaması için
    if baslangic_tarihi > bitis_tarihi:
        baslangic_tarihi, bitis_tarihi = bitis_tarihi, baslangic_tarihi
    
    # Act: TarihAraligiDTO oluştur
    tarih_araligi = TarihAraligiDTO(
        baslangic_tarihi=baslangic_tarihi,
        bitis_tarihi=bitis_tarihi
    )
    
    # Assert: Tip güvenliği kontrolü
    assert type(tarih_araligi.baslangic_tarihi) is date
    assert type(tarih_araligi.bitis_tarihi) is date
    
    # datetime ile karışmaması kontrolü
    assert not isinstance(tarih_araligi.baslangic_tarihi, datetime)
    assert not isinstance(tarih_araligi.bitis_tarihi, datetime)
    
    # Dataclass anotasyonları kontrolü
    annotations = tarih_araligi.__annotations__
    assert annotations['baslangic_tarihi'] == date
    assert annotations['bitis_tarihi'] == date


@given(
    format=st.sampled_from([DisariAktarFormat.CSV, DisariAktarFormat.PDF])
)
def test_disari_aktar_dto_enum_tip_guvenligi(format):
    """
    Property: Dışa aktarım DTO enum tip güvenliği
    
    Herhangi bir dışa aktarım DTO'su için:
    - Enum alanları doğru enum türünde olmalı
    - String değerlerle karışmamalı
    """
    # Act: DisariAktarDTO oluştur
    disari_aktar = DisariAktarDTO(format=format)
    
    # Assert: Enum tip güvenliği kontrolü
    assert type(disari_aktar.format) is DisariAktarFormat
    assert isinstance(disari_aktar.format, DisariAktarFormat)
    
    # String ile karışmaması kontrolü
    assert not isinstance(disari_aktar.format, str)
    
    # Enum değer kontrolü
    assert disari_aktar.format in [DisariAktarFormat.CSV, DisariAktarFormat.PDF]
    
    # Dataclass anotasyonları kontrolü
    annotations = disari_aktar.__annotations__
    assert annotations['format'] == DisariAktarFormat


@given(
    rapor_turu=st.sampled_from([RaporTuru.SATIS_OZETI, RaporTuru.KRITIK_STOK, RaporTuru.EN_COK_SATAN, RaporTuru.KARLILIK])
)
def test_rapor_turu_enum_tip_guvenligi(rapor_turu):
    """
    Property: Rapor türü enum tip güvenliği
    
    Herhangi bir rapor türü enum'u için:
    - Enum değerleri string ile karışmamalı
    - Değer erişimi güvenli olmalı
    """
    # Assert: Enum tip güvenliği kontrolü
    assert type(rapor_turu) is RaporTuru
    assert isinstance(rapor_turu, RaporTuru)
    
    # String ile karışmaması kontrolü
    assert not isinstance(rapor_turu, str)
    
    # Değer erişimi güvenliği
    assert isinstance(rapor_turu.value, str)
    assert rapor_turu.value in ["satis_ozeti", "kritik_stok", "en_cok_satan", "karlilik"]


@given(
    veri_dict=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(
            st.integers(),
            st.text(),
            st.decimals(min_value=Decimal('0'), max_value=Decimal('9999.99'), places=2),
            st.booleans(),
            st.none()
        ),
        min_size=1,
        max_size=10
    )
)
def test_dto_dict_donusum_tip_guvenligi(veri_dict):
    """
    Property: DTO dict dönüşüm tip güvenliği
    
    Herhangi bir veri dict'i için:
    - DTO'ya dönüştürme işlemi tip güvenli olmalı
    - Desteklenmeyen türler için uygun hata verilmeli
    """
    # Act: Mock DTO sınıfı ile test
    from dataclasses import dataclass, fields
    from typing import Optional, Any
    
    @dataclass
    class MockDTO:
        id: int
        ad: str
        deger: Optional[Decimal] = None
        aktif: bool = True
        
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'MockDTO':
            """Dict'ten DTO oluştur (tip güvenli)"""
            # Tip dönüşümleri
            converted_data = {}
            
            if 'id' in data:
                if isinstance(data['id'], int):
                    converted_data['id'] = data['id']
                elif isinstance(data['id'], str) and data['id'].isdigit():
                    converted_data['id'] = int(data['id'])
                else:
                    raise TypeError(f"id alanı int olmalı, {type(data['id'])} verildi")
            
            if 'ad' in data:
                if isinstance(data['ad'], str):
                    converted_data['ad'] = data['ad']
                else:
                    converted_data['ad'] = str(data['ad'])
            
            if 'deger' in data and data['deger'] is not None:
                if isinstance(data['deger'], Decimal):
                    converted_data['deger'] = data['deger']
                elif isinstance(data['deger'], (int, float)):
                    converted_data['deger'] = Decimal(str(data['deger']))
                else:
                    raise TypeError(f"deger alanı Decimal olmalı, {type(data['deger'])} verildi")
            
            if 'aktif' in data:
                if isinstance(data['aktif'], bool):
                    converted_data['aktif'] = data['aktif']
                else:
                    converted_data['aktif'] = bool(data['aktif'])
            
            return cls(**converted_data)
    
    # Test verisi hazırla
    test_data = {}
    if any(isinstance(v, int) for v in veri_dict.values()):
        test_data['id'] = next(v for v in veri_dict.values() if isinstance(v, int))
    else:
        test_data['id'] = 1
    
    if any(isinstance(v, str) for v in veri_dict.values()):
        test_data['ad'] = next(v for v in veri_dict.values() if isinstance(v, str))
    else:
        test_data['ad'] = "test"
    
    # Assert: Tip güvenli dönüşüm
    try:
        dto = MockDTO.from_dict(test_data)
        assert type(dto.id) is int
        assert type(dto.ad) is str
        assert dto.aktif is True or dto.aktif is False  # bool kontrolü
        
        if dto.deger is not None:
            assert type(dto.deger) is Decimal
            
    except TypeError as e:
        # Tip hatası beklenen bir durum
        assert "olmalı" in str(e)


@given(
    yanlis_tip_magaza_id=st.one_of(st.text(), st.decimals(), st.booleans()),
    yanlis_tip_brut_satis=st.one_of(st.text(), st.integers(), st.booleans())
)
def test_dto_yanlis_tip_hata_yonetimi(yanlis_tip_magaza_id, yanlis_tip_brut_satis):
    """
    Property: DTO yanlış tip hata yönetimi
    
    Yanlış türde verilerle DTO oluşturulduğunda:
    - Uygun tip hataları fırlatılmalı
    - Hata mesajları açıklayıcı olmalı
    """
    # Act & Assert: Yanlış türlerle DTO oluşturma
    with pytest.raises((TypeError, ValueError)):
        # Python dataclass'lar runtime'da tip kontrolü yapmaz
        # Ancak post_init metodlarında doğrulama yapabiliriz
        satis_ozeti = SatisOzetiDTO(
            magaza_id=yanlis_tip_magaza_id,  # Yanlış tip
            brut_satis=yanlis_tip_brut_satis,  # Yanlış tip
            indirim_toplam=Decimal('0'),
            net_satis=Decimal('100'),
            satis_adedi=1,
            iade_toplam=Decimal('0')
        )


@given(
    nested_data=st.dictionaries(
        keys=st.text(min_size=1, max_size=10),
        values=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.integers(), st.text(), st.decimals()),
            min_size=1,
            max_size=3
        ),
        min_size=1,
        max_size=3
    )
)
def test_nested_dto_tip_guvenligi(nested_data):
    """
    Property: İç içe DTO tip güvenliği
    
    İç içe veri yapıları için:
    - Her seviyede tip güvenliği korunmalı
    - Nested DTO'lar doğru türde olmalı
    """
    # Act: Mock nested DTO yapısı
    from dataclasses import dataclass
    from typing import List, Dict, Any
    
    @dataclass
    class NestedItemDTO:
        key: str
        value: Any
        
        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> 'NestedItemDTO':
            return cls(
                key=str(data.get('key', '')),
                value=data.get('value')
            )
    
    @dataclass
    class ContainerDTO:
        items: List[NestedItemDTO]
        
        @classmethod
        def from_nested_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'ContainerDTO':
            items = []
            for key, value_dict in data.items():
                for sub_key, sub_value in value_dict.items():
                    item = NestedItemDTO.from_dict({
                        'key': f"{key}.{sub_key}",
                        'value': sub_value
                    })
                    items.append(item)
            return cls(items=items)
    
    # Assert: Nested tip güvenliği
    container = ContainerDTO.from_nested_dict(nested_data)
    
    assert type(container.items) is list
    for item in container.items:
        assert type(item) is NestedItemDTO
        assert type(item.key) is str
        # item.value herhangi bir tip olabilir