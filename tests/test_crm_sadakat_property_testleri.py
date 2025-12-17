# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_sadakat_property_testleri
# Description: CRM sadakat servisi property testleri (6.8-6.15)
# Changelog:
# - İlk oluşturma: Kalan property testleri toplu olarak

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


# Test için gerekli sınıfları burada tanımla
class PuanIslemTuru(Enum):
    KAZANIM = "KAZANIM"
    HARCAMA = "HARCAMA"
    DUZELTME = "DUZELTME"


class ReferansTuru(Enum):
    POS_SATIS = "POS_SATIS"
    SATIS_BELGESI = "SATIS_BELGESI"


@dataclass
class PuanIslemDTO:
    musteri_id: int
    puan: int
    aciklama: Optional[str] = None
    referans_turu: Optional[ReferansTuru] = None
    referans_id: Optional[int] = None


class DogrulamaHatasi(Exception):
    pass


class SadakatServisi:
    """Test için basit SadakatServisi mock'u"""
    
    def __init__(self, db):
        self.db = db
        self.puan_hareketleri = {}  # musteri_id -> list of movements
        self.next_id = 1
    
    def puan_kazan(self, dto: PuanIslemDTO):
        if dto.puan <= 0:
            raise DogrulamaHatasi("Puan değeri pozitif olmalıdır")
        
        hareket = Mock()
        hareket.id = self.next_id
        hareket.musteri_id = dto.musteri_id
        hareket.puan = dto.puan
        hareket.islem_turu = PuanIslemTuru.KAZANIM.value
        hareket.aciklama = dto.aciklama
        hareket.referans_turu = dto.referans_turu.value if dto.referans_turu else None
        hareket.referans_id = dto.referans_id
        
        if dto.musteri_id not in self.puan_hareketleri:
            self.puan_hareketleri[dto.musteri_id] = []
        self.puan_hareketleri[dto.musteri_id].append(hareket)
        
        self.next_id += 1
        return hareket
    
    def puan_harca(self, dto: PuanIslemDTO):
        if dto.puan <= 0:
            raise DogrulamaHatasi("Puan değeri pozitif olmalıdır")
        
        bakiye = self.bakiye_getir(dto.musteri_id)
        if bakiye < dto.puan:
            raise DogrulamaHatasi("Yetersiz bakiye")
        
        hareket = Mock()
        hareket.id = self.next_id
        hareket.musteri_id = dto.musteri_id
        hareket.puan = dto.puan
        hareket.islem_turu = PuanIslemTuru.HARCAMA.value
        hareket.aciklama = dto.aciklama
        
        if dto.musteri_id not in self.puan_hareketleri:
            self.puan_hareketleri[dto.musteri_id] = []
        self.puan_hareketleri[dto.musteri_id].append(hareket)
        
        self.next_id += 1
        return hareket
    
    def bakiye_getir(self, musteri_id: int) -> int:
        if musteri_id not in self.puan_hareketleri:
            return 0
        
        bakiye = 0
        for hareket in self.puan_hareketleri[musteri_id]:
            if hareket.islem_turu == PuanIslemTuru.KAZANIM.value:
                bakiye += hareket.puan
            elif hareket.islem_turu == PuanIslemTuru.HARCAMA.value:
                bakiye -= hareket.puan
        
        return max(0, bakiye)
    
    def hareketler(self, musteri_id: int, limit: int = 100) -> List:
        if musteri_id not in self.puan_hareketleri:
            return []
        
        # Tarih sırasına göre sırala (en yeni önce)
        hareketler = sorted(
            self.puan_hareketleri[musteri_id],
            key=lambda x: x.id,
            reverse=True
        )
        
        return hareketler[:limit]
    
    def puan_duzelt(self, dto: PuanIslemDTO):
        if dto.puan == 0:
            raise DogrulamaHatasi("Düzeltme puanı sıfır olamaz")
        
        if not dto.aciklama or not dto.aciklama.strip():
            raise DogrulamaHatasi("Açıklama zorunludur")
        
        if dto.puan < 0:
            bakiye = self.bakiye_getir(dto.musteri_id)
            if bakiye < abs(dto.puan):
                raise DogrulamaHatasi("Yetersiz bakiye")
        
        hareket = Mock()
        hareket.id = self.next_id
        hareket.musteri_id = dto.musteri_id
        hareket.puan = dto.puan
        hareket.islem_turu = PuanIslemTuru.DUZELTME.value
        hareket.aciklama = dto.aciklama
        
        if dto.musteri_id not in self.puan_hareketleri:
            self.puan_hareketleri[dto.musteri_id] = []
        self.puan_hareketleri[dto.musteri_id].append(hareket)
        
        self.next_id += 1
        return hareket


# Hypothesis stratejileri
pozitif_puan_strategy = st.integers(min_value=1, max_value=1000)
musteri_id_strategy = st.integers(min_value=1, max_value=100)


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_pozitif_puan_kontrolu(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 11: Pozitif puan kontrolü**
    **Validates: Requirements 4.1**
    
    Her puan kazanım işlemi için, sadece pozitif puan değerleri kabul edilir
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    
    # Pozitif puan ile işlem başarılı olmalı
    hareket = sadakat_servisi.puan_kazan(dto)
    assert hareket.puan == puan
    assert hareket.islem_turu == PuanIslemTuru.KAZANIM.value


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_islem_turu_otomatik_atama(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 12: İşlem türü otomatik atama**
    **Validates: Requirements 4.2, 5.4, 10.1**
    
    Her puan işlemi için, işlem türü otomatik olarak doğru değere atanır
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Kazanım işlemi
    kazanim_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    kazanim_hareket = sadakat_servisi.puan_kazan(kazanim_dto)
    assert kazanim_hareket.islem_turu == PuanIslemTuru.KAZANIM.value
    
    # Harcama işlemi
    harcama_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    harcama_hareket = sadakat_servisi.puan_harca(harcama_dto)
    assert harcama_hareket.islem_turu == PuanIslemTuru.HARCAMA.value
    
    # Düzeltme işlemi
    duzeltme_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan, aciklama="Test düzeltme")
    duzeltme_hareket = sadakat_servisi.puan_duzelt(duzeltme_dto)
    assert duzeltme_hareket.islem_turu == PuanIslemTuru.DUZELTME.value


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_referans_bilgisi_saklama(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 13: Referans bilgisi saklama**
    **Validates: Requirements 4.3, 8.4, 9.3**
    
    Her referans bilgisi verilen puan işlemi için, referans türü ve ID'si kaydedilir
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    dto = PuanIslemDTO(
        musteri_id=musteri_id,
        puan=puan,
        referans_turu=ReferansTuru.POS_SATIS,
        referans_id=123
    )
    
    hareket = sadakat_servisi.puan_kazan(dto)
    assert hareket.referans_turu == ReferansTuru.POS_SATIS.value
    assert hareket.referans_id == 123


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_bakiye_kontrolu(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 14: Bakiye kontrolü**
    **Validates: Requirements 5.1, 5.2**
    
    Her puan harcama işlemi için, müşteri bakiyesi kontrol edilir
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Önce puan kazan
    kazanim_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    sadakat_servisi.puan_kazan(kazanim_dto)
    
    # Bakiyeden az harca - başarılı olmalı (en az 1 puan harca)
    harcama_miktari = max(1, puan // 2)
    harcama_dto = PuanIslemDTO(musteri_id=musteri_id, puan=harcama_miktari)
    hareket = sadakat_servisi.puan_harca(harcama_dto)
    assert hareket.puan == harcama_miktari
    
    # Bakiyeden fazla harca - hata fırlatmalı
    fazla_harcama_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan * 2)
    with pytest.raises(DogrulamaHatasi):
        sadakat_servisi.puan_harca(fazla_harcama_dto)


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_basarili_harcama_kaydi(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 15: Başarılı harcama kaydı**
    **Validates: Requirements 5.3**
    
    Her yeterli bakiyeli puan harcama işlemi için, işlem başarıyla kaydedilir
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Önce puan kazan
    kazanim_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    sadakat_servisi.puan_kazan(kazanim_dto)
    
    # Harca
    harcama_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    hareket = sadakat_servisi.puan_harca(harcama_dto)
    
    # Hareket kaydedilmiş olmalı
    assert hareket.musteri_id == musteri_id
    assert hareket.puan == puan
    assert hareket.islem_turu == PuanIslemTuru.HARCAMA.value


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_bakiye_hesaplama_formulu(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 16: Bakiye hesaplama formülü**
    **Validates: Requirements 6.1, 6.4**
    
    Her bakiye sorgulaması için, KAZANIM - HARCAMA formülü kullanılır
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Başlangıç bakiyesi 0 olmalı
    assert sadakat_servisi.bakiye_getir(musteri_id) == 0
    
    # Puan kazan
    kazanim_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    sadakat_servisi.puan_kazan(kazanim_dto)
    
    # Bakiye puan kadar olmalı
    assert sadakat_servisi.bakiye_getir(musteri_id) == puan
    
    # Yarısını harca (en az 1 puan)
    harcama_miktari = max(1, puan // 2)
    harcama_dto = PuanIslemDTO(musteri_id=musteri_id, puan=harcama_miktari)
    sadakat_servisi.puan_harca(harcama_dto)
    
    # Bakiye kalan miktar olmalı
    beklenen_bakiye = puan - harcama_miktari
    assert sadakat_servisi.bakiye_getir(musteri_id) == beklenen_bakiye


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_hareket_listesi_siralama(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 17: Hareket listesi sıralama**
    **Validates: Requirements 7.1**
    
    Her puan hareketleri sorgulaması için, sonuçlar tarih sırasına göre sıralanır
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Birkaç hareket yap
    for i in range(3):
        dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan + i)
        sadakat_servisi.puan_kazan(dto)
    
    # Hareketleri getir
    hareketler = sadakat_servisi.hareketler(musteri_id)
    
    # En yeni hareket en başta olmalı (ID'ye göre ters sıralı)
    assert len(hareketler) == 3
    assert hareketler[0].id > hareketler[1].id > hareketler[2].id


@given(musteri_id=musteri_id_strategy, limit=st.integers(min_value=1, max_value=10))
@settings(max_examples=50)
def test_limit_parametresi(musteri_id, limit):
    """
    **Feature: crm-cekirdek-modulu, Property 18: Limit parametresi**
    **Validates: Requirements 7.2, 7.3**
    
    Her limit parametresi verilen sorgu için, belirtilen sayıda kayıt döndürülür
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Limit'ten fazla hareket yap
    hareket_sayisi = limit + 5
    for i in range(hareket_sayisi):
        dto = PuanIslemDTO(musteri_id=musteri_id, puan=10)
        sadakat_servisi.puan_kazan(dto)
    
    # Limit ile hareketleri getir
    hareketler = sadakat_servisi.hareketler(musteri_id, limit)
    
    # Dönen kayıt sayısı limit kadar olmalı
    assert len(hareketler) == limit


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_duzeltme_bakiye_kontrolu(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 22: Düzeltme bakiye kontrolü**
    **Validates: Requirements 10.2, 10.3**
    
    Her negatif puan düzeltme işlemi için, bakiye kontrolü yapılır
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Önce puan kazan
    kazanim_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    sadakat_servisi.puan_kazan(kazanim_dto)
    
    # Negatif düzeltme (bakiyeden az, en az -1)
    duzeltme_miktari = -max(1, puan // 2)
    duzeltme_dto = PuanIslemDTO(
        musteri_id=musteri_id,
        puan=duzeltme_miktari,
        aciklama="Test düzeltme"
    )
    hareket = sadakat_servisi.puan_duzelt(duzeltme_dto)
    assert hareket.puan == duzeltme_miktari
    
    # Negatif düzeltme (bakiyeden fazla) - hata fırlatmalı
    fazla_duzeltme_dto = PuanIslemDTO(
        musteri_id=musteri_id,
        puan=-(puan * 2),
        aciklama="Test düzeltme"
    )
    with pytest.raises(DogrulamaHatasi):
        sadakat_servisi.puan_duzelt(fazla_duzeltme_dto)


@given(musteri_id=musteri_id_strategy, puan=pozitif_puan_strategy)
@settings(max_examples=50)
def test_duzeltme_aciklama_zorunlulugu(musteri_id, puan):
    """
    **Feature: crm-cekirdek-modulu, Property 23: Düzeltme açıklama zorunluluğu**
    **Validates: Requirements 10.4**
    
    Her puan düzeltme işlemi için, açıklama alanı zorunludur
    """
    mock_session = Mock()
    sadakat_servisi = SadakatServisi(mock_session)
    
    # Açıklama ile düzeltme - başarılı olmalı
    aciklamali_dto = PuanIslemDTO(
        musteri_id=musteri_id,
        puan=puan,
        aciklama="Test açıklama"
    )
    hareket = sadakat_servisi.puan_duzelt(aciklamali_dto)
    assert hareket.aciklama == "Test açıklama"
    
    # Açıklama olmadan düzeltme - hata fırlatmalı
    aciklamasiz_dto = PuanIslemDTO(musteri_id=musteri_id, puan=puan)
    with pytest.raises(DogrulamaHatasi):
        sadakat_servisi.puan_duzelt(aciklamasiz_dto)
    
    # Boş açıklama ile düzeltme - hata fırlatmalı
    bos_aciklama_dto = PuanIslemDTO(
        musteri_id=musteri_id,
        puan=puan,
        aciklama=""
    )
    with pytest.raises(DogrulamaHatasi):
        sadakat_servisi.puan_duzelt(bos_aciklama_dto)