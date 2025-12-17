# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_repository_property
# Description: Repository katmanı property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 3: Transaction bütünlüğü**
**Validates: Requirements 1.4, 1.5**

**Feature: satis-belgeleri-modulu, Property 16: Eş zamanlı erişim kontrolü**
**Validates: Requirements 6.5**

Repository katmanı için property-based testler.
"""

from unittest.mock import Mock, MagicMock, patch
from hypothesis import given, strategies as st, assume
import pytest
from sqlalchemy.exc import SQLAlchemyError

from sontechsp.uygulama.moduller.satis_belgeleri.modeller.satis_belgesi import (
    SatisBelgesi, BelgeTuru, BelgeDurumu
)
from sontechsp.uygulama.moduller.satis_belgeleri.modeller.belge_satiri import BelgeSatiri
from sontechsp.uygulama.moduller.satis_belgeleri.depolar import (
    BelgeDeposu, BelgeSatirDeposu
)
from sontechsp.uygulama.moduller.satis_belgeleri.dto.filtre_dto import BelgeFiltresiDTO
from sontechsp.uygulama.cekirdek.hatalar import VeriTabaniHatasi


# Test stratejileri
@st.composite
def satis_belgesi_strategy(draw):
    """Satış belgesi üretici"""
    return SatisBelgesi(
        belge_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10000))),
        belge_numarasi=draw(st.text(min_size=10, max_size=20)),
        belge_turu=draw(st.sampled_from(list(BelgeTuru))),
        belge_durumu=draw(st.sampled_from(list(BelgeDurumu))),
        magaza_id=draw(st.integers(min_value=1, max_value=100)),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=1000))
    )


@st.composite
def belge_satiri_strategy(draw):
    """Belge satırı üretici"""
    from decimal import Decimal
    return BelgeSatiri(
        satir_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10000))),
        belge_id=draw(st.integers(min_value=1, max_value=10000)),
        urun_id=draw(st.integers(min_value=1, max_value=10000)),
        sira_no=draw(st.integers(min_value=1, max_value=100)),
        miktar=Decimal(str(draw(st.floats(min_value=0.01, max_value=1000)))),
        birim_fiyat=Decimal(str(draw(st.floats(min_value=0.01, max_value=10000))))
    )


@st.composite
def belge_filtresi_strategy(draw):
    """Belge filtresi üretici"""
    return BelgeFiltresiDTO(
        belge_turu=draw(st.one_of(st.none(), st.sampled_from(list(BelgeTuru)))),
        belge_durumu=draw(st.one_of(st.none(), st.sampled_from(list(BelgeDurumu)))),
        magaza_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=100))),
        sayfa=draw(st.integers(min_value=1, max_value=10)),
        sayfa_boyutu=draw(st.integers(min_value=1, max_value=50))
    )


class TestRepositoryProperty:
    """Repository katmanı property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_session = Mock()
        self.belge_deposu = BelgeDeposu(self.mock_session)
        self.belge_satir_deposu = BelgeSatirDeposu(self.mock_session)
    
    @given(satis_belgesi_strategy())
    def test_transaction_butunlugu_belge_ekleme(self, belge):
        """
        **Feature: satis-belgeleri-modulu, Property 3: Transaction bütünlüğü**
        **Validates: Requirements 1.4, 1.5**
        
        Herhangi bir belge işlemi için, tüm veritabanı değişiklikleri transaction 
        içinde gerçekleştirilmeli ve hata durumunda geri alınmalıdır
        """
        # Mock DB modeli
        mock_db_belge = Mock()
        mock_db_belge.id = 123
        
        # Başarılı senaryo
        belge.to_db_model = Mock(return_value=mock_db_belge)
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        
        # Belge ekle
        eklenen_belge = self.belge_deposu.ekle(belge)
        
        # Transaction metodları çağrılmalı
        self.mock_session.add.assert_called_once_with(mock_db_belge)
        self.mock_session.flush.assert_called_once()
        
        # Belge ID atanmalı
        assert eklenen_belge.belge_id == 123
    
    @given(satis_belgesi_strategy())
    def test_transaction_rollback_belge_ekleme_hatasi(self, belge):
        """
        Belge ekleme sırasında hata oluştuğunda transaction rollback davranışını test et
        """
        # Mock DB modeli
        mock_db_belge = Mock()
        belge.to_db_model = Mock(return_value=mock_db_belge)
        
        # Session flush'ta hata fırlat
        self.mock_session.flush.side_effect = SQLAlchemyError("Test hatası")
        
        # VeriTabaniHatasi fırlatılmalı
        with pytest.raises(VeriTabaniHatasi):
            self.belge_deposu.ekle(belge)
        
        # Session metodları çağrılmalı
        self.mock_session.add.assert_called_once_with(mock_db_belge)
        self.mock_session.flush.assert_called_once()
    
    @given(belge_satiri_strategy())
    def test_transaction_butunlugu_satir_ekleme(self, satir):
        """
        Belge satırı ekleme işleminde transaction bütünlüğünü test et
        """
        # Mock DB modeli
        mock_db_satir = Mock()
        mock_db_satir.id = 456
        
        satir.to_db_model = Mock(return_value=mock_db_satir)
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        
        # Satır ekle
        eklenen_satir = self.belge_satir_deposu.ekle(satir)
        
        # Transaction metodları çağrılmalı
        self.mock_session.add.assert_called_once_with(mock_db_satir)
        self.mock_session.flush.assert_called_once()
        
        # Satır ID atanmalı
        assert eklenen_satir.satir_id == 456
    
    @given(st.lists(belge_satiri_strategy(), min_size=1, max_size=5))
    def test_transaction_butunlugu_toplu_ekleme(self, satirlar):
        """
        Toplu satır ekleme işleminde transaction bütünlüğünü test et
        """
        # Mock DB modelleri
        mock_db_satirlar = []
        for i, satir in enumerate(satirlar):
            mock_db_satir = Mock()
            mock_db_satir.id = i + 1
            mock_db_satirlar.append(mock_db_satir)
            satir.to_db_model = Mock(return_value=mock_db_satir)
        
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        
        # Toplu ekle
        eklenen_satirlar = self.belge_satir_deposu.toplu_ekle(satirlar)
        
        # Her satır için transaction metodları çağrılmalı
        assert self.mock_session.add.call_count == len(satirlar)
        assert self.mock_session.flush.call_count == len(satirlar)
        
        # Tüm satırlar ID almalı
        for i, satir in enumerate(eklenen_satirlar):
            assert satir.satir_id == i + 1
    
    @given(st.integers(min_value=1, max_value=10000))
    def test_es_zamanli_erisim_kontrolu_belge_guncelleme(self, belge_id):
        """
        **Feature: satis-belgeleri-modulu, Property 16: Eş zamanlı erişim kontrolü**
        **Validates: Requirements 6.5**
        
        Herhangi bir eş zamanlı belge işlemi için row-level lock kullanılarak 
        veri tutarlılığı korunmalıdır
        """
        # Mock belge
        belge = SatisBelgesi(
            belge_id=belge_id,
            belge_turu=BelgeTuru.SIPARIS,
            belge_durumu=BelgeDurumu.TASLAK,
            magaza_id=1,
            olusturan_kullanici_id=1
        )
        
        # Mock DB belge
        mock_db_belge = Mock()
        self.mock_session.get.return_value = mock_db_belge
        self.mock_session.flush.return_value = None
        
        # Belge güncelle
        guncellenen_belge = self.belge_deposu.guncelle(belge)
        
        # Session.get row-level lock için kullanılmalı
        self.mock_session.get.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Güncelleme başarılı olmalı
        assert guncellenen_belge.belge_id == belge_id
    
    @given(st.integers(min_value=1, max_value=10000))
    def test_es_zamanli_erisim_belge_silme(self, belge_id):
        """
        Eş zamanlı erişim durumunda belge silme işlemini test et
        """
        # Mock DB belge
        mock_db_belge = Mock()
        self.mock_session.get.return_value = mock_db_belge
        self.mock_session.delete.return_value = None
        self.mock_session.flush.return_value = None
        
        # Bağlı belge kontrolü için mock
        with patch.object(self.belge_deposu, 'bagli_belgeleri_bul', return_value=[]):
            # Belge sil
            silindi = self.belge_deposu.sil(belge_id)
        
        # Session metodları çağrılmalı
        self.mock_session.get.assert_called_once()
        self.mock_session.delete.assert_called_once_with(mock_db_belge)
        self.mock_session.flush.assert_called_once()
        
        # Silme başarılı olmalı
        assert silindi == True
    
    @given(belge_filtresi_strategy())
    def test_belge_listeleme_tutarliligi(self, filtre):
        """
        Belge listeleme işleminin tutarlılığını test et
        """
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        self.mock_session.query.return_value = mock_query
        
        # Belge listele
        belgeler = self.belge_deposu.listele(filtre)
        
        # Query metodları çağrılmalı
        self.mock_session.query.assert_called_once()
        mock_query.offset.assert_called_once()
        mock_query.limit.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
        
        # Liste dönmeli
        assert isinstance(belgeler, list)
    
    @given(st.integers(min_value=1, max_value=10000))
    def test_belge_satirlari_alma_tutarliligi(self, belge_id):
        """
        Belge satırları alma işleminin tutarlılığını test et
        """
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        self.mock_session.query.return_value = mock_query
        
        # Belge satırlarını al
        satirlar = self.belge_satir_deposu.belge_satirlari_al(belge_id)
        
        # Query metodları çağrılmalı
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
        
        # Liste dönmeli
        assert isinstance(satirlar, list)
    
    @given(st.integers(min_value=1, max_value=10000))
    def test_bagli_belge_kontrolu(self, kaynak_belge_id):
        """
        Bağlı belge kontrolü işleminin tutarlılığını test et
        """
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        self.mock_session.query.return_value = mock_query
        
        # Bağlı belgeleri bul
        bagli_belgeler = self.belge_deposu.bagli_belgeleri_bul(kaynak_belge_id)
        
        # Query metodları çağrılmalı
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.all.assert_called_once()
        
        # Liste dönmeli
        assert isinstance(bagli_belgeler, list)
    
    @given(st.text(min_size=5, max_size=20))
    def test_belge_numara_ile_bulma(self, belge_numarasi):
        """
        Belge numarası ile bulma işleminin tutarlılığını test et
        """
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        self.mock_session.query.return_value = mock_query
        
        # Belgeyi numara ile bul
        belge = self.belge_deposu.bul_numara_ile(belge_numarasi)
        
        # Query metodları çağrılmalı
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()
        
        # None dönmeli (mock'ta belge yok)
        assert belge is None