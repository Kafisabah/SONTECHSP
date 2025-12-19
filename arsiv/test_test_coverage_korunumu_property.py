# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_test_coverage_korunumu_property
# Description: Property test - Test coverage korunumu
# Changelog:
# - İlk versiyon: Property 23 testi oluşturuldu

"""
Property Test: Test Coverage Korunumu

**Feature: kod-kalitesi-standardizasyon, Property 23: Test Coverage Korunumu**
**Validates: Requirements 6.5**

For any test güncelleme işlemi, test coverage değeri korunmalıdır.
"""

from hypothesis import given, strategies as st, settings
from uygulama.moduller.kod_kalitesi.test_entegrasyon import TestDogrulayici


@settings(max_examples=100)
@given(
    onceki_coverage=st.floats(min_value=0.0, max_value=100.0),
    yeni_coverage=st.floats(min_value=0.0, max_value=100.0),
    tolerans=st.floats(min_value=0.0, max_value=5.0)
)
def test_coverage_korunumu_property(
    onceki_coverage: float,
    yeni_coverage: float,
    tolerans: float
):
    """
    Property: Coverage korunumu kontrolü doğru çalışmalı.
    
    Test eder:
    1. Yeni coverage >= (önceki - tolerans) ise korunmuş sayılmalı
    2. Yeni coverage < (önceki - tolerans) ise korunmamış sayılmalı
    """
    dogrulayici = TestDogrulayici()
    
    # Property 1: Coverage korunumu kontrolü
    korundu = dogrulayici.coverage_korundu_mu(
        onceki_coverage,
        yeni_coverage,
        tolerans
    )
    
    # Beklenen sonuç
    beklenen = yeni_coverage >= (onceki_coverage - tolerans)
    
    # Property: Sonuç beklenenle eşleşmeli
    assert korundu == beklenen, \
        f"Coverage korunumu yanlış: {korundu} != {beklenen} " \
        f"(önceki={onceki_coverage}, yeni={yeni_coverage}, tolerans={tolerans})"


@settings(max_examples=100)
@given(coverage=st.floats(min_value=0.0, max_value=100.0))
def test_coverage_kaydetme_property(coverage: float):
    """
    Property: Coverage kaydedilip geri alınabilmeli.
    """
    dogrulayici = TestDogrulayici()
    
    # Property 1: Coverage kaydet
    dogrulayici.onceki_coverage_kaydet(coverage)
    
    # Property 2: Kaydedilen coverage geri alınabilmeli
    alinan = dogrulayici.onceki_coverage_al()
    
    assert alinan == coverage, \
        f"Coverage kaydedilip alınamadı: {alinan} != {coverage}"
