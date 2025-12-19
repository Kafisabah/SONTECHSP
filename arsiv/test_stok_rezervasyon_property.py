# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_stok_rezervasyon_property
# Description: SONTECHSP stok rezervasyon yönetimi property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Rezervasyon Yönetimi Property Testleri

**Feature: gelismis-stok-yonetimi, Property 19: Stok rezervasyon yönetimi**
**Validates: Requirements 9.3, 9.4, 9.5**

Bu modül stok rezervasyon yönetimi için property-based testleri içerir.
Rezervasyon yapma, iptal etme ve kullanılabilir stok hesaplama işlemlerini test eder.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from decimal import Decimal
import decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from sontechsp.uygulama.moduller.stok.servisler.stok_rezervasyon_service import StokRezervasyonService
from sontechsp.uygulama.moduller.stok.dto.stok_bakiye_dto import StokBakiyeDTO
from sontechsp.uygulama.moduller.stok.hatalar.stok_hatalari import StokValidationError, StokYetersizError


class TestStokRezervasyonProperty:
    """Stok rezervasyon yönetimi property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_bakiye_repo = Mock()
        self.service = StokRezervasyonService(self.mock_bakiye_repo)
        # Her test için mock'ları sıfırla
        self.mock_bakiye_repo.reset_mock()
    
    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        magaza_id=st.integers(min_value=1, max_value=100),
        mevcut_stok=st.decimals(min_value=Decimal('10'), max_value=Decimal('1000'), places=4),
        rezerve_miktar=st.decimals(min_value=Decimal('1'), max_value=Decimal('50'), places=4)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_rezervasyon_yapma_tutarliligi(self, urun_id, magaza_id, mevcut_stok, rezerve_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 19: Stok rezervasyon yönetimi**
        **Validates: Requirements 9.3, 9.4, 9.5**
        
        Property: Rezervasyon yapma tutarlılığı
        For any geçerli rezervasyon talebi, sistem rezervasyonu doğru yapmalı ve 
        kullanılabilir stok miktarını doğru hesaplamalı
        """
        # Arrange - Yeterli stok olduğunu varsay
        assume(mevcut_stok >= rezerve_miktar)
        
        # Mock bakiye repository davranışı
        bakiye_dto = StokBakiyeDTO(
            id=1,
            urun_id=urun_id,
            magaza_id=magaza_id,
            depo_id=None,
            miktar=mevcut_stok,
            rezerve_miktar=Decimal('0'),
            kullanilabilir_miktar=mevcut_stok
        )
        
        self.mock_bakiye_repo.bakiye_getir.return_value = bakiye_dto
        self.mock_bakiye_repo.rezervasyon_yap.return_value = True
        
        # Act - Rezervasyon yap
        rezervasyon_id = self.service.rezervasyon_yap(
            urun_id=urun_id,
            magaza_id=magaza_id,
            miktar=rezerve_miktar
        )
        
        # Assert - Rezervasyon ID oluşturulmalı
        assert rezervasyon_id is not None
        assert isinstance(rezervasyon_id, str)
        assert rezervasyon_id.startswith('RZV_')
        
        # Rezervasyon repository'de kaydedilmeli
        self.mock_bakiye_repo.rezervasyon_yap.assert_called_with(
            urun_id, magaza_id, rezerve_miktar, None
        )
        
        # Rezervasyon bilgisi alınabilmeli
        rezervasyon_bilgisi = self.service.rezervasyon_bilgisi_getir(rezervasyon_id)
        assert rezervasyon_bilgisi is not None
        assert rezervasyon_bilgisi.urun_id == urun_id
        assert rezervasyon_bilgisi.magaza_id == magaza_id
        assert rezervasyon_bilgisi.rezerve_miktar == rezerve_miktar
        assert rezervasyon_bilgisi.durum == 'AKTIF'
    
    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        magaza_id=st.integers(min_value=1, max_value=100),
        mevcut_stok=st.decimals(min_value=Decimal('1'), max_value=Decimal('100'), places=4),
        talep_edilen_miktar=st.decimals(min_value=Decimal('101'), max_value=Decimal('1000'), places=4)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_yetersiz_stok_kontrolu(self, urun_id, magaza_id, mevcut_stok, talep_edilen_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 19: Stok rezervasyon yönetimi**
        **Validates: Requirements 9.3, 9.4, 9.5**
        
        Property: Yetersiz stok kontrolü
        For any yetersiz stok durumu, sistem rezervasyon talebini reddetmeli ve 
        uygun hata mesajı döndürmeli
        """
        # Arrange - Yetersiz stok durumu
        assume(mevcut_stok < talep_edilen_miktar)
        
        bakiye_dto = StokBakiyeDTO(
            id=1,
            urun_id=urun_id,
            magaza_id=magaza_id,
            depo_id=None,
            miktar=mevcut_stok,
            rezerve_miktar=Decimal('0'),
            kullanilabilir_miktar=mevcut_stok
        )
        
        self.mock_bakiye_repo.bakiye_getir.return_value = bakiye_dto
        
        # Act & Assert - Yetersiz stok hatası alınmalı
        with pytest.raises(StokYetersizError) as exc_info:
            self.service.rezervasyon_yap(
                urun_id=urun_id,
                magaza_id=magaza_id,
                miktar=talep_edilen_miktar
            )
        
        # Hata mesajında doğru bilgiler olmalı
        assert exc_info.value.kullanilabilir_stok == mevcut_stok
        assert exc_info.value.talep_edilen_miktar == talep_edilen_miktar
        
        # Repository'de rezervasyon yapılmamalı
        self.mock_bakiye_repo.rezervasyon_yap.assert_not_called()
    
    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        magaza_id=st.integers(min_value=1, max_value=100),
        rezerve_miktar=st.decimals(min_value=Decimal('1'), max_value=Decimal('100'), places=4)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_rezervasyon_iptal_tutarliligi(self, urun_id, magaza_id, rezerve_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 19: Stok rezervasyon yönetimi**
        **Validates: Requirements 9.3, 9.4, 9.5**
        
        Property: Rezervasyon iptal tutarlılığı
        For any aktif rezervasyon, iptal işlemi başarılı olmalı ve 
        rezerve miktar serbest bırakılmalı
        """
        # Arrange - Önce rezervasyon yap
        bakiye_dto = StokBakiyeDTO(
            id=1,
            urun_id=urun_id,
            magaza_id=magaza_id,
            depo_id=None,
            miktar=rezerve_miktar * 2,  # Yeterli stok
            rezerve_miktar=Decimal('0'),
            kullanilabilir_miktar=rezerve_miktar * 2
        )
        
        self.mock_bakiye_repo.bakiye_getir.return_value = bakiye_dto
        self.mock_bakiye_repo.rezervasyon_yap.return_value = True
        self.mock_bakiye_repo.rezervasyon_iptal.return_value = True
        
        # Rezervasyon yap
        rezervasyon_id = self.service.rezervasyon_yap(
            urun_id=urun_id,
            magaza_id=magaza_id,
            miktar=rezerve_miktar
        )
        
        # Act - Rezervasyonu iptal et
        iptal_sonucu = self.service.rezervasyon_iptal(rezervasyon_id)
        
        # Assert - İptal başarılı olmalı
        assert iptal_sonucu is True
        
        # Repository'de iptal çağrılmalı
        self.mock_bakiye_repo.rezervasyon_iptal.assert_called_with(
            urun_id, magaza_id, rezerve_miktar, None
        )
        
        # Rezervasyon durumu güncellenmiş olmalı
        rezervasyon_bilgisi = self.service.rezervasyon_bilgisi_getir(rezervasyon_id)
        assert rezervasyon_bilgisi.durum == 'IPTAL_EDILDI'
    
    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        magaza_id=st.integers(min_value=1, max_value=100),
        toplam_stok=st.decimals(min_value=Decimal('100'), max_value=Decimal('1000'), places=4),
        rezerve_miktar=st.decimals(min_value=Decimal('10'), max_value=Decimal('50'), places=4)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_kullanilabilir_stok_hesaplama(self, urun_id, magaza_id, toplam_stok, rezerve_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 19: Stok rezervasyon yönetimi**
        **Validates: Requirements 9.3, 9.4, 9.5**
        
        Property: Kullanılabilir stok hesaplama
        For any stok durumu, kullanılabilir stok miktarı (toplam - rezerve) 
        olarak doğru hesaplanmalı
        """
        # Arrange
        assume(toplam_stok >= rezerve_miktar)
        beklenen_kullanilabilir = toplam_stok - rezerve_miktar
        
        bakiye_dto = StokBakiyeDTO(
            id=1,
            urun_id=urun_id,
            magaza_id=magaza_id,
            depo_id=None,
            miktar=toplam_stok,
            rezerve_miktar=rezerve_miktar,
            kullanilabilir_miktar=beklenen_kullanilabilir
        )
        
        self.mock_bakiye_repo.bakiye_getir.return_value = bakiye_dto
        
        # Act - Kullanılabilir stok miktarını al
        kullanilabilir_stok = self.service.kullanilabilir_stok_getir(
            urun_id=urun_id,
            magaza_id=magaza_id
        )
        
        # Assert - Doğru hesaplama yapılmalı
        assert kullanilabilir_stok == beklenen_kullanilabilir
        assert kullanilabilir_stok == (toplam_stok - rezerve_miktar)
        assert kullanilabilir_stok >= 0  # Negatif olamaz
    
    @given(
        gecersiz_urun_id=st.integers(max_value=0),
        gecersiz_magaza_id=st.integers(max_value=0),
        gecersiz_miktar=st.decimals(max_value=Decimal('0'), places=4)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_gecersiz_parametre_kontrolu(self, gecersiz_urun_id, gecersiz_magaza_id, gecersiz_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 19: Stok rezervasyon yönetimi**
        **Validates: Requirements 9.3, 9.4, 9.5**
        
        Property: Geçersiz parametre kontrolü
        For any geçersiz parametre, sistem uygun validasyon hatası döndürmeli
        """
        # Test geçersiz ürün ID
        if gecersiz_urun_id <= 0:
            with pytest.raises(StokValidationError):
                self.service.rezervasyon_yap(
                    urun_id=gecersiz_urun_id,
                    magaza_id=1,
                    miktar=Decimal('10')
                )
        
        # Test geçersiz mağaza ID
        if gecersiz_magaza_id <= 0:
            with pytest.raises(StokValidationError):
                self.service.rezervasyon_yap(
                    urun_id=1,
                    magaza_id=gecersiz_magaza_id,
                    miktar=Decimal('10')
                )
        
        # Test geçersiz miktar - NaN kontrolü ekle
        try:
            if gecersiz_miktar <= 0:
                with pytest.raises(StokValidationError):
                    self.service.rezervasyon_yap(
                        urun_id=1,
                        magaza_id=1,
                        miktar=gecersiz_miktar
                    )
        except (decimal.InvalidOperation, TypeError):
            # NaN veya geçersiz decimal değerleri için
            with pytest.raises((StokValidationError, decimal.InvalidOperation, TypeError)):
                self.service.rezervasyon_yap(
                    urun_id=1,
                    magaza_id=1,
                    miktar=gecersiz_miktar
                )
    
    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        magaza_id=st.integers(min_value=1, max_value=100),
        rezerve_miktar=st.decimals(min_value=Decimal('10'), max_value=Decimal('100'), places=4),
        kullanilan_miktar=st.decimals(min_value=Decimal('1'), max_value=Decimal('50'), places=4)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_rezervasyon_kullanma_tutarliligi(self, urun_id, magaza_id, rezerve_miktar, kullanilan_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 19: Stok rezervasyon yönetimi**
        **Validates: Requirements 9.3, 9.4, 9.5**
        
        Property: Rezervasyon kullanma tutarlılığı
        For any rezervasyon kullanım işlemi, kullanılan miktar rezerve miktardan 
        fazla olmamalı ve stok düşümü doğru yapılmalı
        """
        # Arrange - Kullanılan miktar rezerve miktardan fazla olmasın
        assume(kullanilan_miktar <= rezerve_miktar)
        
        # Önce rezervasyon yap
        bakiye_dto = StokBakiyeDTO(
            id=1,
            urun_id=urun_id,
            magaza_id=magaza_id,
            depo_id=None,
            miktar=rezerve_miktar * 2,
            rezerve_miktar=Decimal('0'),
            kullanilabilir_miktar=rezerve_miktar * 2
        )
        
        self.mock_bakiye_repo.bakiye_getir.return_value = bakiye_dto
        self.mock_bakiye_repo.rezervasyon_yap.return_value = True
        self.mock_bakiye_repo.rezervasyon_iptal.return_value = True
        self.mock_bakiye_repo.bakiye_guncelle.return_value = True
        
        rezervasyon_id = self.service.rezervasyon_yap(
            urun_id=urun_id,
            magaza_id=magaza_id,
            miktar=rezerve_miktar
        )
        
        # Act - Rezervasyonu kullan
        kullanim_sonucu = self.service.rezervasyon_kullan(rezervasyon_id, kullanilan_miktar)
        
        # Assert - Kullanım başarılı olmalı
        assert kullanim_sonucu is True
        
        # Repository'de rezervasyon iptali ve stok düşümü çağrılmalı
        self.mock_bakiye_repo.rezervasyon_iptal.assert_called_with(
            urun_id, magaza_id, kullanilan_miktar, None
        )
        self.mock_bakiye_repo.bakiye_guncelle.assert_called_with(
            urun_id, magaza_id, -kullanilan_miktar, None
        )
        
        # Rezervasyon durumu güncellenmiş olmalı
        rezervasyon_bilgisi = self.service.rezervasyon_bilgisi_getir(rezervasyon_id)
        if kullanilan_miktar == rezerve_miktar:
            assert rezervasyon_bilgisi.durum == 'KULLANILDI'
        else:
            assert rezervasyon_bilgisi.durum == 'AKTIF'
            assert rezervasyon_bilgisi.rezerve_miktar == (rezerve_miktar - kullanilan_miktar)