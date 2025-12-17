# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_raporlama_satis_durumu_filtreleme_property
# Description: Raporlama modülü satış durumu filtreleme property testi
# Changelog:
# - İlk oluşturma

"""
**Feature: raporlama-modulu, Property 2: Satış durumu filtreleme**
**Validates: Requirements 1.2**

Herhangi bir satış özeti hesaplamasında, yalnızca TAMAMLANDI durumundaki işlemler toplamaya dahil edilmelidir
"""

import pytest
from hypothesis import given, strategies as st, assume
from decimal import Decimal
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from sontechsp.uygulama.moduller.raporlar.dto import TarihAraligiDTO
from sontechsp.uygulama.moduller.raporlar.sabitler import SatisDurumu
from sontechsp.uygulama.moduller.raporlar.sorgular import satis_ozeti


# Test stratejileri
pozitif_int_strategy = st.integers(min_value=1, max_value=1000)
pozitif_decimal_strategy = st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2)
tarih_strategy = st.dates(min_value=date(2024, 1, 1), max_value=date(2024, 12, 31))
satis_durumu_strategy = st.sampled_from([
    SatisDurumu.BEKLEMEDE, SatisDurumu.TAMAMLANDI, 
    SatisDurumu.IPTAL, SatisDurumu.IADE
])


@given(
    magaza_id=pozitif_int_strategy,
    baslangic_tarihi=tarih_strategy,
    gun_farki=st.integers(min_value=0, max_value=30),
    tamamlandi_sayisi=st.integers(min_value=0, max_value=100),
    diger_durum_sayisi=st.integers(min_value=0, max_value=100)
)
def test_satis_durumu_filtreleme_property(magaza_id, baslangic_tarihi, gun_farki, tamamlandi_sayisi, diger_durum_sayisi):
    """
    Property: Satış durumu filtreleme
    
    Herhangi bir satış özeti sorgusu için:
    - Yalnızca TAMAMLANDI durumundaki satışlar dahil edilmeli
    - Diğer durumlar (BEKLEMEDE, IPTAL, IADE) filtrelenmeli
    - Sorgu parametrelerinde TAMAMLANDI durumu belirtilmeli
    """
    # Arrange: Tarih aralığı oluştur
    bitis_tarihi = baslangic_tarihi + timedelta(days=gun_farki)
    tarih_araligi = TarihAraligiDTO(
        baslangic_tarihi=baslangic_tarihi,
        bitis_tarihi=bitis_tarihi
    )
    
    # Mock session ve sorgu sonucu oluştur
    mock_session = Mock(spec=Session)
    mock_result = Mock()
    
    # TAMAMLANDI durumundaki satışlar için sonuç
    mock_result.brut_satis = Decimal('1000.00') * tamamlandi_sayisi
    mock_result.indirim_toplam = Decimal('50.00') * tamamlandi_sayisi
    mock_result.net_satis = Decimal('950.00') * tamamlandi_sayisi
    mock_result.satis_adedi = tamamlandi_sayisi
    mock_result.iade_toplam = Decimal('0.00')
    
    mock_session.execute.return_value.fetchone.return_value = mock_result
    
    # Act: Satış özeti sorgusunu çalıştır
    sonuc = satis_ozeti(mock_session, magaza_id, tarih_araligi)
    
    # Assert: Sorgu çağrısını kontrol et
    mock_session.execute.assert_called_once()
    call_args = mock_session.execute.call_args
    
    # SQL sorgusu ve parametreleri kontrol et
    sql_query = call_args[0][0]  # İlk argüman SQL sorgusu
    parameters = call_args[0][1]  # İkinci argüman parametreler
    
    # Sorgu parametrelerinde TAMAMLANDI durumu olmalı
    assert parameters['durum'] == SatisDurumu.TAMAMLANDI.value
    assert parameters['magaza_id'] == magaza_id
    assert parameters['baslangic'] == baslangic_tarihi
    assert parameters['bitis'] == bitis_tarihi
    
    # SQL sorgusunda durum filtresi olmalı
    assert "durum = :durum" in str(sql_query)
    
    # Sonuç kontrolü
    assert sonuc['brut_satis'] == Decimal('1000.00') * tamamlandi_sayisi
    assert sonuc['satis_adedi'] == tamamlandi_sayisi


@given(
    magaza_id=pozitif_int_strategy,
    tarih_araligi_gun=st.integers(min_value=1, max_value=30),
    beklemede_tutar=pozitif_decimal_strategy,
    tamamlandi_tutar=pozitif_decimal_strategy,
    iptal_tutar=pozitif_decimal_strategy
)
def test_sadece_tamamlandi_durumu_dahil_edilir(magaza_id, tarih_araligi_gun, beklemede_tutar, tamamlandi_tutar, iptal_tutar):
    """
    Property: Sadece TAMAMLANDI durumu dahil edilir
    
    Farklı durumlarda satışlar olduğunda:
    - Yalnızca TAMAMLANDI durumundaki tutarlar toplamda yer almalı
    - BEKLEMEDE, IPTAL durumları hariç tutulmalı
    """
    # Arrange: Tarih aralığı
    baslangic = date(2024, 1, 1)
    bitis = baslangic + timedelta(days=tarih_araligi_gun)
    tarih_araligi = TarihAraligiDTO(baslangic_tarihi=baslangic, bitis_tarihi=bitis)
    
    # Mock session
    mock_session = Mock(spec=Session)
    
    # Sadece TAMAMLANDI durumundaki satışları döndüren mock sonuç
    mock_result = Mock()
    mock_result.brut_satis = tamamlandi_tutar
    mock_result.indirim_toplam = Decimal('0')
    mock_result.net_satis = tamamlandi_tutar
    mock_result.satis_adedi = 1
    mock_result.iade_toplam = Decimal('0')
    
    mock_session.execute.return_value.fetchone.return_value = mock_result
    
    # Act: Sorguyu çalıştır
    sonuc = satis_ozeti(mock_session, magaza_id, tarih_araligi)
    
    # Assert: Sorgu parametrelerini kontrol et
    call_args = mock_session.execute.call_args
    parameters = call_args[0][1]
    
    # Yalnızca TAMAMLANDI durumu sorgulanmalı
    assert parameters['durum'] == SatisDurumu.TAMAMLANDI.value
    
    # Sonuç yalnızca TAMAMLANDI tutarını içermeli
    assert sonuc['brut_satis'] == tamamlandi_tutar
    assert sonuc['net_satis'] == tamamlandi_tutar
    
    # BEKLEMEDE ve IPTAL tutarları dahil edilmemeli (mock'ta sadece TAMAMLANDI var)
    # Bu, sorgu filtresinin doğru çalıştığını gösterir


@given(
    magaza_id=pozitif_int_strategy,
    baslangic_tarihi=tarih_strategy,
    bitis_tarihi=tarih_strategy
)
def test_durum_filtresi_sql_sorgusunda_mevcut(magaza_id, baslangic_tarihi, bitis_tarihi):
    """
    Property: Durum filtresi SQL sorgusunda mevcut
    
    Herhangi bir satış özeti sorgusu için:
    - SQL sorgusunda durum filtresi bulunmalı
    - WHERE koşulunda durum = :durum olmalı
    - Parametre olarak TAMAMLANDI değeri geçilmeli
    """
    # Tarih sıralaması
    if baslangic_tarihi > bitis_tarihi:
        baslangic_tarihi, bitis_tarihi = bitis_tarihi, baslangic_tarihi
    
    # Arrange
    tarih_araligi = TarihAraligiDTO(
        baslangic_tarihi=baslangic_tarihi,
        bitis_tarihi=bitis_tarihi
    )
    
    mock_session = Mock(spec=Session)
    mock_result = Mock()
    mock_result.brut_satis = Decimal('100')
    mock_result.indirim_toplam = Decimal('10')
    mock_result.net_satis = Decimal('90')
    mock_result.satis_adedi = 1
    mock_result.iade_toplam = Decimal('0')
    
    mock_session.execute.return_value.fetchone.return_value = mock_result
    
    # Act
    satis_ozeti(mock_session, magaza_id, tarih_araligi)
    
    # Assert: SQL sorgusu kontrolü
    call_args = mock_session.execute.call_args
    sql_query = str(call_args[0][0])
    parameters = call_args[0][1]
    
    # SQL sorgusunda durum filtresi olmalı
    assert "durum = :durum" in sql_query
    assert "WHERE" in sql_query or "where" in sql_query
    
    # Parametrelerde TAMAMLANDI durumu olmalı
    assert 'durum' in parameters
    assert parameters['durum'] == SatisDurumu.TAMAMLANDI.value


@given(
    magaza_id=pozitif_int_strategy,
    tarih_araligi_gun=st.integers(min_value=1, max_value=7)
)
def test_bos_sonuc_durumu_filtreleme(magaza_id, tarih_araligi_gun):
    """
    Property: Boş sonuç durumu filtreleme
    
    TAMAMLANDI durumunda satış olmadığında:
    - Sorgu yine de TAMAMLANDI durumu ile filtrelenmeli
    - Boş sonuç için sıfır değerler döndürülmeli
    - Diğer durumlar sorgulanmamalı
    """
    # Arrange
    baslangic = date(2024, 6, 1)
    bitis = baslangic + timedelta(days=tarih_araligi_gun)
    tarih_araligi = TarihAraligiDTO(baslangic_tarihi=baslangic, bitis_tarihi=bitis)
    
    mock_session = Mock(spec=Session)
    # Boş sonuç (TAMAMLANDI durumunda satış yok)
    mock_session.execute.return_value.fetchone.return_value = None
    
    # Act
    sonuc = satis_ozeti(mock_session, magaza_id, tarih_araligi)
    
    # Assert: Sorgu parametreleri kontrolü
    call_args = mock_session.execute.call_args
    parameters = call_args[0][1]
    
    # Yine de TAMAMLANDI durumu sorgulanmalı
    assert parameters['durum'] == SatisDurumu.TAMAMLANDI.value
    
    # Boş sonuç için sıfır değerler
    assert sonuc['brut_satis'] == Decimal('0')
    assert sonuc['satis_adedi'] == 0


@given(
    magaza_id=pozitif_int_strategy,
    yanlis_durum=st.sampled_from([SatisDurumu.BEKLEMEDE, SatisDurumu.IPTAL, SatisDurumu.IADE])
)
def test_yanlis_durum_kullanilmaz(magaza_id, yanlis_durum):
    """
    Property: Yanlış durum kullanılmaz
    
    Satış özeti sorgusunda:
    - BEKLEMEDE, IPTAL, IADE durumları kullanılmamalı
    - Sadece TAMAMLANDI durumu geçerli olmalı
    """
    # Arrange
    tarih_araligi = TarihAraligiDTO(
        baslangic_tarihi=date(2024, 1, 1),
        bitis_tarihi=date(2024, 1, 31)
    )
    
    mock_session = Mock(spec=Session)
    mock_result = Mock()
    mock_result.brut_satis = Decimal('100')
    mock_result.indirim_toplam = Decimal('0')
    mock_result.net_satis = Decimal('100')
    mock_result.satis_adedi = 1
    mock_result.iade_toplam = Decimal('0')
    
    mock_session.execute.return_value.fetchone.return_value = mock_result
    
    # Act
    satis_ozeti(mock_session, magaza_id, tarih_araligi)
    
    # Assert: Yanlış durum kullanılmamalı
    call_args = mock_session.execute.call_args
    parameters = call_args[0][1]
    
    # TAMAMLANDI dışındaki durumlar kullanılmamalı
    assert parameters['durum'] != yanlis_durum.value
    assert parameters['durum'] == SatisDurumu.TAMAMLANDI.value


@given(
    magaza_listesi=st.lists(pozitif_int_strategy, min_size=1, max_size=5),
    tarih_araligi_gun=st.integers(min_value=1, max_value=10)
)
def test_coklu_magaza_durum_filtreleme_tutarliligi(magaza_listesi, tarih_araligi_gun):
    """
    Property: Çoklu mağaza durum filtreleme tutarlılığı
    
    Farklı mağazalar için sorgu yapıldığında:
    - Her mağaza için aynı durum filtresi uygulanmalı
    - TAMAMLANDI durumu tutarlı şekilde kullanılmalı
    """
    # Arrange
    baslangic = date(2024, 3, 1)
    bitis = baslangic + timedelta(days=tarih_araligi_gun)
    tarih_araligi = TarihAraligiDTO(baslangic_tarihi=baslangic, bitis_tarihi=bitis)
    
    # Her mağaza için sorgu çalıştır
    for magaza_id in magaza_listesi:
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        mock_result.brut_satis = Decimal('500')
        mock_result.indirim_toplam = Decimal('25')
        mock_result.net_satis = Decimal('475')
        mock_result.satis_adedi = 2
        mock_result.iade_toplam = Decimal('0')
        
        mock_session.execute.return_value.fetchone.return_value = mock_result
        
        # Act
        satis_ozeti(mock_session, magaza_id, tarih_araligi)
        
        # Assert: Her mağaza için aynı durum filtresi
        call_args = mock_session.execute.call_args
        parameters = call_args[0][1]
        
        assert parameters['durum'] == SatisDurumu.TAMAMLANDI.value
        assert parameters['magaza_id'] == magaza_id