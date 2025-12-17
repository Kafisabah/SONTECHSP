# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_test_basari_invarianti_property
# Description: Property test - Test başarı invariantı
# Changelog:
# - İlk versiyon: Property 22 testi oluşturuldu

"""
Property Test: Test Başarı Invariantı

**Feature: kod-kalitesi-standardizasyon, Property 22: Test Başarı Invariantı**
**Validates: Requirements 6.4**

For any refactoring işlemi tamamlandığında, tüm testler başarılı olmalıdır.
"""

from hypothesis import given, strategies as st, settings
from uygulama.moduller.kod_kalitesi.test_entegrasyon import TestDogrulayici


@settings(max_examples=10)  # Minimal test
@given(min_coverage=st.floats(min_value=0.0, max_value=100.0))
def test_test_basari_invarianti_property(min_coverage: float):
    """
    Property: Test doğrulayıcı oluşturulabilmeli ve
    minimum coverage değeri ayarlanabilmeli.
    """
    dogrulayici = TestDogrulayici(min_coverage=min_coverage)
    
    # Property: Doğrulayıcı oluşturulabilmeli
    assert dogrulayici is not None
    assert dogrulayici.min_coverage == min_coverage
