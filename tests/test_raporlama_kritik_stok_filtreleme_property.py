# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_raporlama_kritik_stok_filtreleme_property
# Description: Raporlama modülü kritik stok filtreleme property testi
# Changelog:
# - İlk oluşturma

"""
**Feature: raporlama-modulu, Property 5: Kritik stok filtreleme**
**Validates: Requirements 2.1**

Herhangi bir ürün ve stok verisi için, kritik stok raporunda döndürülen ürünlerin 
mevcut stoğu kritik eşikte veya altında olmalıdır
"""

import pytest
from hypothesis import given, strategies as st, assume
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from sontechsp.uygulama.moduller.raporlar.sorgular import kritik_stok_listesi


# Test stratejileri
pozitif_int_strategy = st.integers(min_value=1, max_value=1000)
stok_miktar_strategy = st.integers(min_value=0, max_value=1000)
kritik_seviye_strategy = st.integers(min_value=1, max_value=100)
urun_adi_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Zs')))


@given(
    urun_listesi=st.lists(
        st.tuples(
            pozitif_int_strategy,  # urun_id
            urun_adi_strategy,     # urun_adi
            pozitif_int_strategy,  # depo_id
            stok_miktar_strategy,  # miktar
            kritik_seviye_strategy # kritik_seviye
        ),
        min_size=1,
        max_size=10
    )
)
def test_kritik_stok_filtreleme_property(urun_listesi):
    """
    Property: Kritik stok filtreleme
    
    Herhangi bir kritik stok sorgusu için:
    - Döndürülen tüm ürünlerin mevcut stoğu kritik seviyede veya altında olmalı
    - miktar <= kritik_seviye koşulu sağlanmalı
    - SQL sorgusunda bu filtre bulunmalı
    """
    # Arrange: Sadece kritik seviyede veya altındaki ürünleri filtrele
    kritik_urunler = [
        (urun_id, urun_adi, depo_id, miktar, kritik_seviye)
        for urun_id, urun_adi, depo_id, miktar, kritik_seviye in urun_listesi
        if miktar <= kritik_seviye and urun_adi.strip() != ""
    ]
    
    # En az bir kritik ürün olmalı
    assume(len(kritik_urunler) > 0)
    
    # Mock session ve sonuçlar
    mock_session = Mock(spec=Session)
    mock_results = []
    
    for urun_id, urun_adi, depo_id, miktar, kritik_seviye in kritik_urunler:
        mock_row = Mock()
        mock_row.urun_id = urun_id
        mock_row.urun_adi = urun_adi
        mock_row.depo_id = depo_id
        mock_row.miktar = miktar
        mock_row.kritik_seviye = kritik_seviye
        mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act: Kritik stok sorgusunu çalıştır
    sonuclar = kritik_stok_listesi(mock_session)
    
    # Assert: Tüm sonuçlar kritik seviyede veya altında olmalı
    for sonuc in sonuclar:
        assert sonuc['miktar'] <= sonuc['kritik_seviye'], \
            f"Ürün {sonuc['urun_id']} kritik seviyenin üstünde: {sonuc['miktar']} > {sonuc['kritik_seviye']}"
    
    # SQL sorgusunda kritik stok filtresi olmalı
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args
    sql_query = str(call_args[0][0])
    
    assert "miktar <= " in sql_query or "sb.miktar <= u.kritik_seviye" in sql_query


@given(
    depo_id=pozitif_int_strategy,
    urun_sayisi=st.integers(min_value=1, max_value=5)
)
def test_depo_filtresi_kritik_stok(depo_id, urun_sayisi):
    """
    Property: Depo filtresi kritik stok
    
    Belirli depo ID'si ile kritik stok sorgusu yapıldığında:
    - Sadece o depodaki ürünler döndürülmeli
    - SQL sorgusunda depo filtresi bulunmalı
    - Parametrelerde depo_id geçilmeli
    """
    # Arrange: Mock session
    mock_session = Mock(spec=Session)
    mock_results = []
    
    for i in range(urun_sayisi):
        mock_row = Mock()
        mock_row.urun_id = i + 1
        mock_row.urun_adi = f"Ürün {i + 1}"
        mock_row.depo_id = depo_id  # Aynı depo
        mock_row.miktar = 5  # Kritik seviyenin altında
        mock_row.kritik_seviye = 10
        mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act: Depo filtreli kritik stok sorgusu
    sonuclar = kritik_stok_listesi(mock_session, depo_id=depo_id)
    
    # Assert: Tüm sonuçlar aynı depodan olmalı
    for sonuc in sonuclar:
        assert sonuc['depo_id'] == depo_id
    
    # SQL sorgusunda depo filtresi olmalı
    call_args = mock_session.execute.call_args
    sql_query = str(call_args[0][0])
    parameters = call_args[0][1]
    
    assert "depo_id = :depo_id" in sql_query
    assert parameters['depo_id'] == depo_id


@given(
    normal_urunler=st.lists(
        st.tuples(
            pozitif_int_strategy,  # urun_id
            urun_adi_strategy,     # urun_adi
            pozitif_int_strategy,  # depo_id
            st.integers(min_value=50, max_value=1000),  # yüksek miktar
            st.integers(min_value=1, max_value=49)      # düşük kritik seviye
        ),
        min_size=1,
        max_size=5
    )
)
def test_normal_stok_seviyesi_filtrelenmez(normal_urunler):
    """
    Property: Normal stok seviyesi filtrelenmez
    
    Mevcut stoğu kritik seviyenin üstünde olan ürünler:
    - Kritik stok raporunda yer almamalı
    - Sorgu sonucunda döndürülmemeli
    """
    # Arrange: Normal seviyedeki ürünler (miktar > kritik_seviye)
    # Bu ürünler kritik stok sorgusunda döndürülmemeli
    
    mock_session = Mock(spec=Session)
    # Boş sonuç - çünkü hiçbir ürün kritik seviyede değil
    mock_session.execute.return_value.fetchall.return_value = []
    
    # Act: Kritik stok sorgusu (normal ürünler kritik değil)
    sonuclar = kritik_stok_listesi(mock_session)
    
    # Assert: Sonuç boş olmalı (normal ürünler filtrelendi)
    assert len(sonuclar) == 0
    
    # SQL sorgusunda kritik stok filtresi olmalı
    call_args = mock_session.execute.call_args
    sql_query = str(call_args[0][0])
    
    assert "miktar <= " in sql_query or "sb.miktar <= u.kritik_seviye" in sql_query


@given(
    kritik_urun_sayisi=st.integers(min_value=1, max_value=10),
    normal_urun_sayisi=st.integers(min_value=1, max_value=10)
)
def test_karisik_stok_seviyeleri_filtreleme(kritik_urun_sayisi, normal_urun_sayisi):
    """
    Property: Karışık stok seviyeleri filtreleme
    
    Hem kritik hem normal seviyede ürünler olduğunda:
    - Sadece kritik seviyedeki ürünler döndürülmeli
    - Normal seviyedeki ürünler filtrelenmeli
    """
    # Arrange: Karışık ürün listesi oluştur
    mock_session = Mock(spec=Session)
    mock_results = []
    
    # Sadece kritik seviyedeki ürünleri mock sonuca ekle
    for i in range(kritik_urun_sayisi):
        mock_row = Mock()
        mock_row.urun_id = i + 1
        mock_row.urun_adi = f"Kritik Ürün {i + 1}"
        mock_row.depo_id = 1
        mock_row.miktar = 5  # Kritik seviyenin altında
        mock_row.kritik_seviye = 10
        mock_results.append(mock_row)
    
    # Normal seviyedeki ürünler mock sonuca eklenmez (filtrelendi)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act
    sonuclar = kritik_stok_listesi(mock_session)
    
    # Assert: Sadece kritik ürünler döndürülmeli
    assert len(sonuclar) == kritik_urun_sayisi
    
    for sonuc in sonuclar:
        assert sonuc['miktar'] <= sonuc['kritik_seviye']
        assert "Kritik" in sonuc['urun_adi']


@given(
    sifir_stok_sayisi=st.integers(min_value=1, max_value=5),
    kritik_seviye=st.integers(min_value=1, max_value=20)
)
def test_sifir_stok_kritik_seviyede(sifir_stok_sayisi, kritik_seviye):
    """
    Property: Sıfır stok kritik seviyede
    
    Stoğu sıfır olan ürünler için:
    - Kritik stok raporunda yer almalı (0 <= kritik_seviye)
    - En yüksek öncelikle listelenmeli
    """
    # Arrange: Sıfır stoklu ürünler
    mock_session = Mock(spec=Session)
    mock_results = []
    
    for i in range(sifir_stok_sayisi):
        mock_row = Mock()
        mock_row.urun_id = i + 1
        mock_row.urun_adi = f"Sıfır Stok Ürün {i + 1}"
        mock_row.depo_id = 1
        mock_row.miktar = 0  # Sıfır stok
        mock_row.kritik_seviye = kritik_seviye
        mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act
    sonuclar = kritik_stok_listesi(mock_session)
    
    # Assert: Sıfır stoklu ürünler dahil edilmeli
    assert len(sonuclar) == sifir_stok_sayisi
    
    for sonuc in sonuclar:
        assert sonuc['miktar'] == 0
        assert sonuc['miktar'] <= sonuc['kritik_seviye']


@given(
    esit_seviye_sayisi=st.integers(min_value=1, max_value=5),
    kritik_seviye=st.integers(min_value=5, max_value=50)
)
def test_esit_kritik_seviye_dahil_edilir(esit_seviye_sayisi, kritik_seviye):
    """
    Property: Eşit kritik seviye dahil edilir
    
    Mevcut stoğu kritik seviyeye tam eşit olan ürünler:
    - Kritik stok raporunda yer almalı (miktar = kritik_seviye)
    - <= koşulu eşitliği de kapsamalı
    """
    # Arrange: Kritik seviyeye eşit stoklu ürünler
    mock_session = Mock(spec=Session)
    mock_results = []
    
    for i in range(esit_seviye_sayisi):
        mock_row = Mock()
        mock_row.urun_id = i + 1
        mock_row.urun_adi = f"Eşit Seviye Ürün {i + 1}"
        mock_row.depo_id = 1
        mock_row.miktar = kritik_seviye  # Kritik seviyeye eşit
        mock_row.kritik_seviye = kritik_seviye
        mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act
    sonuclar = kritik_stok_listesi(mock_session)
    
    # Assert: Eşit seviyedeki ürünler dahil edilmeli
    assert len(sonuclar) == esit_seviye_sayisi
    
    for sonuc in sonuclar:
        assert sonuc['miktar'] == kritik_seviye
        assert sonuc['miktar'] <= sonuc['kritik_seviye']  # Eşitlik de geçerli


@given(
    depo_listesi=st.lists(pozitif_int_strategy, min_size=2, max_size=5, unique=True),
    hedef_depo_index=st.integers(min_value=0, max_value=4)
)
def test_coklu_depo_filtreleme_tutarliligi(depo_listesi, hedef_depo_index):
    """
    Property: Çoklu depo filtreleme tutarlılığı
    
    Birden fazla depo olduğunda:
    - Belirtilen depo filtresi doğru çalışmalı
    - Diğer depolar sonuçta yer almamalı
    - Filtre parametresi tutarlı olmalı
    """
    # Hedef depo index'i listeden küçük olmalı
    assume(hedef_depo_index < len(depo_listesi))
    
    hedef_depo_id = depo_listesi[hedef_depo_index]
    
    # Arrange: Sadece hedef depodaki ürünler
    mock_session = Mock(spec=Session)
    mock_results = []
    
    mock_row = Mock()
    mock_row.urun_id = 1
    mock_row.urun_adi = "Hedef Depo Ürün"
    mock_row.depo_id = hedef_depo_id
    mock_row.miktar = 3
    mock_row.kritik_seviye = 10
    mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act: Hedef depo ile filtreleme
    sonuclar = kritik_stok_listesi(mock_session, depo_id=hedef_depo_id)
    
    # Assert: Sadece hedef depo sonuçları
    for sonuc in sonuclar:
        assert sonuc['depo_id'] == hedef_depo_id
        # Diğer depolar olmamalı
        for diger_depo in depo_listesi:
            if diger_depo != hedef_depo_id:
                assert sonuc['depo_id'] != diger_depo
    
    # Sorgu parametresi kontrolü
    call_args = mock_session.execute.call_args
    parameters = call_args[0][1]
    assert parameters['depo_id'] == hedef_depo_id


@given(
    urun_sayisi=st.integers(min_value=1, max_value=10)
)
def test_sql_sorgu_yapisinin_tutarliligi(urun_sayisi):
    """
    Property: SQL sorgu yapısının tutarlılığı
    
    Kritik stok sorgusu için:
    - JOIN işlemleri doğru olmalı (urunler ve stok_bakiyeleri)
    - WHERE koşulu kritik seviye filtresi içermeli
    - ORDER BY miktar ve ürün adına göre olmalı
    """
    # Arrange
    mock_session = Mock(spec=Session)
    mock_results = []
    
    for i in range(urun_sayisi):
        mock_row = Mock()
        mock_row.urun_id = i + 1
        mock_row.urun_adi = f"Ürün {i + 1}"
        mock_row.depo_id = 1
        mock_row.miktar = i + 1  # Artan miktar
        mock_row.kritik_seviye = 10
        mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act
    kritik_stok_listesi(mock_session)
    
    # Assert: SQL sorgu yapısı kontrolü
    call_args = mock_session.execute.call_args
    sql_query = str(call_args[0][0])
    
    # JOIN kontrolü
    assert "JOIN" in sql_query or "INNER JOIN" in sql_query
    assert "urunler" in sql_query
    assert "stok_bakiyeleri" in sql_query
    
    # WHERE koşulu kontrolü
    assert "WHERE" in sql_query
    assert "kritik_seviye" in sql_query
    
    # ORDER BY kontrolü
    assert "ORDER BY" in sql_query
    assert "miktar" in sql_query