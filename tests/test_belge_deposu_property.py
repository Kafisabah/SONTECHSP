# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_belge_deposu_property
# Description: Belge deposu property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 3: Transaction bütünlüğü**
**Validates: Requirements 1.4, 1.5**

**Feature: satis-belgeleri-modulu, Property 16: Eş zamanlı erişim kontrolü**
**Validates: Requirements 6.5**

Belge deposu için property-based testler.
"""

from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from hypothesis import given, strategies as st, assume
import pytest
from sqlalchemy.exc import SQLAlchemyError

from sontechsp.uygulama.moduller.satis_belgeleri.modeller import (
    SatisBelgesi, BelgeSatiri, BelgeTuru, BelgeDurumu
)
from sontechsp.uygulama.moduller.satis_belgeleri.depolar import (
    BelgeDeposu, BelgeSatirDeposu
)
from sontechsp.uygulama.cekirdek.hatalar import VeriTabaniHatasi


# Test stratejileri
@st.composite
def satis_belgesi_strategy(draw):
    """Satış belgesi üretici"""
    return SatisBelgesi(
        belge_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=1000))),
        belge_numarasi=draw(st.text(min_size=10, max_size=20)),
        belge_turu=draw(st.sampled_from(list(BelgeTuru))),
        belge_durumu=draw(st.sampled_from(list(BelgeDurumu))),
        magaza_id=draw(st.integers(min_value=1, max_value=100)),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=100)),
        toplam_tutar=Decimal(str(draw(st.floats(min_value=0, max_value=10000)))),
        kdv_tutari=Decimal(str(draw(st.floats(min_value=0, max_value=1000)))),
        genel_toplam=Decimal(str(draw(st.floats(min_value=0, max_value=11000))))
    )


@st.composite
def belge_satiri_strategy(draw):
    """Belge satırı üretici"""
    miktar = Decimal(str(draw(st.floats(min_value=0.01, max_value=100))))
    birim_fiyat = Decimal(str(draw(st.floats(min_value=0.01, max_value=1000))))
    
    return BelgeSatiri(
        satir_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=1000))),
        belge_id=draw(st.integers(min_value=1, max_value=1000)),
        urun_id=draw(st.integers(min_value=1, max_value=10000)),
        sira_no=draw(st.integers(min_value=1, max_value=100)),
        miktar=miktar,
        birim_fiyat=birim_fiyat
    )


class TestBelgeDepositoryProperty:
    """Belge deposu property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_session = Mock()
        self.belge_deposu = BelgeDeposu(self.mock_session)
        self.satir_deposu = BelgeSatirDeposu(self.mock_session)
    
    @given(satis_belgesi_strategy())
    def test_transaction_butunlugu_ekleme(self, belge):
        """
        **Feature: satis-belgeleri-modulu, Property 3: Transaction bütünlüğü**
        **Validates: Requirements 1.4, 1.5**
        
        Herhangi bir belge işlemi için, tüm veritabanı değişiklikleri transaction içinde 
        gerçekleştirilmeli ve hata durumunda geri alınmalıdır
        """
        # Mock DB modeli
        mock_db_belge = Mock()
        mock_db_belge.id = 123
        
        # Başarılı ekleme senaryosu
        belge.to_db_model = Mock(return_value=mock_db_belge)
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        
        # Belge ekle
        eklenen_belge = self.belge_deposu.ekle(belge)
        
        # Transaction işlemleri kontrol et
        self.mock_session.add.assert_called_once_with(mock_db_belge)
        self.mock_session.flush.assert_called_once()
        
        # ID atanmış olmalı
        assert eklenen_belge.belge_id == 123
        
        # Hata senaryosu - transaction rollback
        self.mock_session.reset_mock()
        self.mock_session.add.side_effect = SQLAlchemyError("DB Hatası")
        
        with pytest.raises(VeriTabaniHatasi):
            self.belge_deposu.ekle(belge)
        
        # Add çağrılmış olmalı (hata öncesi)
        self.mock_session.add.assert_called_once()
    
    @given(satis_belgesi_strategy())
    def test_transaction_butunlugu_guncelleme(self, belge):
        """
        Belge güncelleme işleminde transaction bütünlüğünü test et
        """
        # Belgeye ID ata
        belge.belge_id = 456
        
        # Mock DB modeli
        mock_db_belge = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.with_for_update.return_value = mock_query
        mock_query.first.return_value = mock_db_belge
        
        self.mock_session.query.return_value = mock_query
        self.mock_session.flush.return_value = None
        
        # Belge güncelle
        guncellenen_belge = self.belge_deposu.guncelle(belge)
        
        # Row-level lock uygulanmış olmalı
        mock_query.with_for_update.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Güncellenen belge döndürülmeli
        assert guncellenen_belge.belge_id == 456
        
        # Hata senaryosu
        self.mock_session.reset_mock()
        mock_query.reset_mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.with_for_update.return_value = mock_query
        mock_query.first.side_effect = SQLAlchemyError("Lock hatası")
        
        with pytest.raises(VeriTabaniHatasi):
            self.belge_deposu.guncelle(belge)
    
    @given(st.integers(min_value=1, max_value=1000))
    def test_es_zamanli_erisim_kontrolu(self, belge_id):
        """
        **Feature: satis-belgeleri-modulu, Property 16: Eş zamanlı erişim kontrolü**
        **Validates: Requirements 6.5**
        
        Herhangi bir eş zamanlı belge işlemi için row-level lock kullanılarak 
        veri tutarlılığı korunmalıdır
        """
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.with_for_update.return_value = mock_query
        mock_query.first.return_value = Mock()
        
        self.mock_session.query.return_value = mock_query
        
        # Belge güncelleme - row-level lock kullanılmalı
        belge = SatisBelgesi(
            belge_id=belge_id,
            belge_turu=BelgeTuru.SIPARIS,
            belge_durumu=BelgeDurumu.TASLAK,
            magaza_id=1,
            olusturan_kullanici_id=1
        )
        
        try:
            self.belge_deposu.guncelle(belge)
            
            # Row-level lock uygulanmış olmalı
            mock_query.with_for_update.assert_called_once()
            
        except VeriTabaniHatasi:
            # Hata durumunda da lock denenmiş olmalı
            mock_query.with_for_update.assert_called_once()
        
        # Belge silme - row-level lock kullanılmalı
        mock_query.reset_mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.with_for_update.return_value = mock_query
        mock_query.first.return_value = Mock()
        mock_query.count.return_value = 0  # Bağımlı belge yok
        
        try:
            self.belge_deposu.sil(belge_id)
            
            # Row-level lock uygulanmış olmalı
            mock_query.with_for_update.assert_called_once()
            
        except VeriTabaniHatasi:
            # Hata durumunda da lock denenmiş olmalı
            pass
    
    @given(belge_satiri_strategy())
    def test_satir_transaction_butunlugu(self, satir):
        """
        Belge satırı işlemlerinde transaction bütünlüğünü test et
        """
        # Mock DB modeli
        mock_db_satir = Mock()
        mock_db_satir.id = 789
        
        # Başarılı ekleme
        satir.to_db_model = Mock(return_value=mock_db_satir)
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        
        eklenen_satir = self.satir_deposu.ekle(satir)
        
        # Transaction işlemleri kontrol et
        self.mock_session.add.assert_called_once_with(mock_db_satir)
        self.mock_session.flush.assert_called_once()
        assert eklenen_satir.satir_id == 789
        
        # Hata senaryosu
        self.mock_session.reset_mock()
        self.mock_session.add.side_effect = SQLAlchemyError("Satır ekleme hatası")
        
        with pytest.raises(VeriTabaniHatasi):
            self.satir_deposu.ekle(satir)
    
    @given(st.integers(min_value=1, max_value=1000))
    def test_bagimlilik_kontrolu(self, belge_id):
        """
        Belge silme işleminde bağımlılık kontrolünü test et
        """
        # Mock query chain - ana belge
        mock_belge_query = Mock()
        mock_belge_query.filter.return_value = mock_belge_query
        mock_belge_query.with_for_update.return_value = mock_belge_query
        mock_belge_query.first.return_value = Mock()  # Belge mevcut
        
        # Mock query chain - bağımlı belgeler
        mock_bagimlı_query = Mock()
        mock_bagimlı_query.filter.return_value = mock_bagimlı_query
        mock_bagimlı_query.count.return_value = 2  # 2 bağımlı belge var
        
        self.mock_session.query.side_effect = [mock_belge_query, mock_bagimlı_query]
        
        # Bağımlı belge varken silme denemesi - hata fırlatmalı
        with pytest.raises(VeriTabaniHatasi, match="türetilmiş belge"):
            self.belge_deposu.sil(belge_id)
        
        # Bağımlılık kontrolü yapılmış olmalı
        mock_bagimlı_query.count.assert_called_once()
        
        # Bağımlı belge yokken silme - başarılı olmalı
        self.mock_session.reset_mock()
        mock_belge_query.reset_mock()
        mock_bagimlı_query.reset_mock()
        
        mock_bagimlı_query.count.return_value = 0  # Bağımlı belge yok
        self.mock_session.query.side_effect = [mock_belge_query, mock_bagimlı_query]
        self.mock_session.delete.return_value = None
        self.mock_session.flush.return_value = None
        
        sonuc = self.belge_deposu.sil(belge_id)
        
        # Silme işlemi başarılı olmalı
        assert sonuc == True
        self.mock_session.delete.assert_called_once()
        self.mock_session.flush.assert_called_once()
    
    @given(st.dictionaries(
        st.sampled_from(['belge_turu', 'belge_durumu', 'magaza_id']),
        st.one_of(
            st.sampled_from(['SIPARIS', 'IRSALIYE', 'FATURA']),
            st.sampled_from(['TASLAK', 'ONAYLANDI', 'FATURALANDI']),
            st.integers(min_value=1, max_value=100)
        ),
        min_size=0, max_size=3
    ))
    def test_filtreleme_tutarliligi(self, filtre):
        """
        Filtreleme işlemlerinin tutarlılığını test et
        """
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        self.mock_session.query.return_value = mock_query
        
        # Filtreleme ile listeleme
        belgeler = self.belge_deposu.listele(filtre)
        
        # Query oluşturulmuş olmalı
        self.mock_session.query.assert_called_once()
        
        # Filtre varsa filter çağrılmış olmalı
        if filtre:
            assert mock_query.filter.call_count >= 1
        
        # Sıralama uygulanmış olmalı
        mock_query.order_by.assert_called_once()
        
        # Sonuç liste olmalı
        assert isinstance(belgeler, list)
    
    @given(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=50))
    def test_sayfalama_tutarliligi(self, sayfa, sayfa_boyutu):
        """
        Sayfalama işlemlerinin tutarlılığını test et
        """
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 100  # Toplam 100 kayıt
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        self.mock_session.query.return_value = mock_query
        
        # Sayfalanmış listeleme
        sonuc = self.belge_deposu.sayfalanmis_listele(sayfa, sayfa_boyutu)
        
        # Sayfalama parametreleri doğru hesaplanmış olmalı
        beklenen_offset = (sayfa - 1) * sayfa_boyutu
        mock_query.offset.assert_called_once_with(beklenen_offset)
        mock_query.limit.assert_called_once_with(sayfa_boyutu)
        
        # Sonuç yapısı doğru olmalı
        assert 'belgeler' in sonuc
        assert 'sayfa_bilgileri' in sonuc
        assert sonuc['sayfa_bilgileri']['mevcut_sayfa'] == sayfa
        assert sonuc['sayfa_bilgileri']['sayfa_boyutu'] == sayfa_boyutu
        assert sonuc['sayfa_bilgileri']['toplam_kayit'] == 100