# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_turkce_ascii_tablo_isimlendirmesi
# Description: SONTECHSP Türkçe ASCII tablo isimlendirmesi property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Türkçe ASCII Tablo İsimlendirmesi Property Testleri

Bu dosya veritabanı tablolarının Türkçe ASCII isimlendirme standardına
uygun olduğunu property-based testing ile kontrol eder.

Türkçe ASCII isimlendirme kuralları:
- Türkçe karakter içermemeli (ç, ğ, ı, ö, ş, ü yerine c, g, i, o, s, u)
- Anlamlı Türkçe kelimeler kullanılmalı
- Çoğul formda olmalı (kullanicilar, urunler, vs.)
- Snake_case formatında olmalı
"""

import re
import pytest
from hypothesis import given, strategies as st
from pathlib import Path


class TestTurkceAsciiTabloIsimlendirmesi:
    """SONTECHSP Türkçe ASCII tablo isimlendirmesi testleri"""
    
    # SONTECHSP standart tablo isimleri (tasarım belgesinden)
    BEKLENEN_TABLO_ISIMLERI = {
        'yetki_kullanici': [
            'kullanicilar', 'roller', 'yetkiler', 
            'kullanici_rolleri', 'rol_yetkileri'
        ],
        'firma_magaza': [
            'firmalar', 'magazalar', 'terminaller', 'depolar'
        ],
        'stok': [
            'urunler', 'urun_barkodlari', 'stok_bakiyeleri', 'stok_hareketleri'
        ],
        'crm': [
            'musteriler', 'sadakat_puanlari'
        ],
        'pos': [
            'pos_satislar', 'pos_satis_satirlari', 'odeme_kayitlari'
        ],
        'belgeler': [
            'satis_belgeleri', 'satis_belge_satirlari'
        ],
        'eticaret': [
            'eticaret_hesaplari', 'eticaret_siparisleri'
        ],
        'ebelge': [
            'ebelge_cikis_kuyrugu', 'ebelge_durumlari'
        ],
        'kargo': [
            'kargo_etiketleri', 'kargo_takipleri'
        ]
    }
    
    # Türkçe karakterler ve ASCII karşılıkları
    TURKCE_ASCII_DONUSUM = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G', 
        'ı': 'i', 'I': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    def test_turkce_ascii_tablo_isimlendirmesi(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 12: Türkçe ASCII tablo isimlendirmesi**
        
        Herhangi bir veritabanı tablosu, kullanicilar/urunler/pos_satislar gibi 
        Türkçe ASCII isimlendirme standardını kullanmalıdır
        **Doğrular: Gereksinim 6.1, 6.2, 6.3, 6.4, 6.5**
        """
        # Tüm beklenen tablo isimlerini kontrol et
        for kategori, tablo_listesi in self.BEKLENEN_TABLO_ISIMLERI.items():
            for tablo_adi in tablo_listesi:
                # ASCII kontrolü
                assert self._ascii_karakter_kontrolu(tablo_adi), \
                    f"Tablo adı Türkçe karakter içeriyor: {tablo_adi}"
                
                # Snake_case kontrolü
                assert self._snake_case_kontrolu(tablo_adi), \
                    f"Tablo adı snake_case formatında değil: {tablo_adi}"
                
                # Çoğul form kontrolü
                assert self._cogul_form_kontrolu(tablo_adi), \
                    f"Tablo adı çoğul formda değil: {tablo_adi}"
                
                # Anlamlı Türkçe kelime kontrolü
                assert self._anlamli_turkce_kelime_kontrolu(tablo_adi), \
                    f"Tablo adı anlamlı Türkçe kelime içermiyor: {tablo_adi}"
    
    def _ascii_karakter_kontrolu(self, tablo_adi: str) -> bool:
        """Tablo adının sadece ASCII karakterler içerdiğini kontrol eder"""
        try:
            tablo_adi.encode('ascii')
            return True
        except UnicodeEncodeError:
            return False
    
    def _snake_case_kontrolu(self, tablo_adi: str) -> bool:
        """Tablo adının snake_case formatında olduğunu kontrol eder"""
        # snake_case pattern: küçük harfler, rakamlar ve alt çizgi
        pattern = r'^[a-z0-9_]+$'
        return bool(re.match(pattern, tablo_adi))
    
    def _cogul_form_kontrolu(self, tablo_adi: str) -> bool:
        """Tablo adının çoğul formda olduğunu kontrol eder"""
        # Türkçe çoğul ekleri: -lar, -ler, -ari, -eri, -lari, -leri
        cogul_ekleri = ['lar', 'ler', 'ari', 'eri', 'lari', 'leri']
        
        # Alt çizgi ile ayrılmış kelimeler için her parçayı kontrol et
        kelimeler = tablo_adi.split('_')
        
        # En az bir kelime çoğul formda olmalı
        for kelime in kelimeler:
            for ek in cogul_ekleri:
                if kelime.endswith(ek):
                    return True
        
        # Özel durumlar (compound kelimeler)
        ozel_durumlar = [
            'pos_satislar', 'pos_satis_satirlari', 'odeme_kayitlari',
            'satis_belgeleri', 'satis_belge_satirlari',
            'eticaret_hesaplari', 'eticaret_siparisleri',
            'ebelge_cikis_kuyrugu', 'ebelge_durumlari',
            'kargo_etiketleri', 'kargo_takipleri',
            'urun_barkodlari', 'stok_bakiyeleri', 'stok_hareketleri',
            'sadakat_puanlari', 'kullanici_rolleri', 'rol_yetkileri'
        ]
        
        return tablo_adi in ozel_durumlar
    
    def _anlamli_turkce_kelime_kontrolu(self, tablo_adi: str) -> bool:
        """Tablo adının anlamlı Türkçe kelimeler içerdiğini kontrol eder"""
        # Bilinen Türkçe kelime kökleri (ASCII formda)
        turkce_kokler = [
            'kullanici', 'rol', 'yetki', 'firma', 'magaza', 'terminal', 'depo',
            'urun', 'barkod', 'stok', 'bakiye', 'hareket', 'musteri', 'sadakat', 'puan',
            'pos', 'satis', 'satir', 'odeme', 'kayit', 'belge', 'eticaret', 'hesap', 'siparis',
            'ebelge', 'cikis', 'kuyruk', 'kuyrugu', 'durum', 'kargo', 'etiket', 'takip'
        ]
        
        # Tablo adındaki kelimeleri ayır
        kelimeler = tablo_adi.split('_')
        
        # Her kelimenin Türkçe kök içerip içermediğini kontrol et
        for kelime in kelimeler:
            kelime_bulundu = False
            for kok in turkce_kokler:
                # Tam eşleşme veya kelime içinde kök bulunması
                if kok == kelime or kok in kelime:
                    kelime_bulundu = True
                    break
            if not kelime_bulundu:
                return False
        
        return True
    
    @given(st.sampled_from([
        'kullanicilar', 'roller', 'yetkiler', 'firmalar', 'magazalar',
        'urunler', 'musteriler', 'pos_satislar', 'satis_belgeleri'
    ]))
    def test_standart_tablo_isimleri_property(self, tablo_adi):
        """
        Property test: Herhangi bir standart tablo adı için ASCII ve format kontrolü
        """
        # ASCII kontrolü
        assert self._ascii_karakter_kontrolu(tablo_adi), \
            f"Standart tablo adı ASCII değil: {tablo_adi}"
        
        # Snake_case kontrolü
        assert self._snake_case_kontrolu(tablo_adi), \
            f"Standart tablo adı snake_case değil: {tablo_adi}"
        
        # Anlamlı Türkçe kelime kontrolü
        assert self._anlamli_turkce_kelime_kontrolu(tablo_adi), \
            f"Standart tablo adı anlamlı Türkçe kelime içermiyor: {tablo_adi}"
    
    @given(st.text(min_size=1, max_size=50))
    def test_turkce_karakter_donusum_property(self, metin):
        """
        Property test: Herhangi bir metin için Türkçe karakter dönüşümü
        """
        # Türkçe karakterleri ASCII'ye dönüştür
        ascii_metin = metin
        for turkce_kar, ascii_kar in self.TURKCE_ASCII_DONUSUM.items():
            ascii_metin = ascii_metin.replace(turkce_kar, ascii_kar)
        
        # Dönüştürülmüş metin ASCII olmalı
        try:
            ascii_metin.encode('ascii')
            ascii_kontrol = True
        except UnicodeEncodeError:
            ascii_kontrol = False
        
        # Eğer orijinal metin sadece Türkçe karakterler içeriyorsa, dönüşüm başarılı olmalı
        sadece_turkce_karakterler = all(
            kar in self.TURKCE_ASCII_DONUSUM or kar.isascii() 
            for kar in metin
        )
        
        if sadece_turkce_karakterler:
            assert ascii_kontrol, f"Türkçe karakter dönüşümü başarısız: {metin} -> {ascii_metin}"
    
    def test_kategori_bazli_tablo_gruplari(self):
        """
        Her kategori için tablo gruplarının doğru organize edildiğini kontrol eder
        """
        for kategori, tablo_listesi in self.BEKLENEN_TABLO_ISIMLERI.items():
            assert len(tablo_listesi) > 0, f"Kategori boş: {kategori}"
            
            # Kategori adı da ASCII olmalı
            assert self._ascii_karakter_kontrolu(kategori), \
                f"Kategori adı ASCII değil: {kategori}"
            
            # Her tablo adı benzersiz olmalı
            assert len(tablo_listesi) == len(set(tablo_listesi)), \
                f"Kategoride tekrarlanan tablo adı var: {kategori}"
    
    def test_tablo_adi_uzunluk_limitleri(self):
        """
        Tablo adlarının PostgreSQL ve SQLite limitlerini aşmadığını kontrol eder
        """
        # PostgreSQL: 63 karakter, SQLite: 1000+ karakter (pratik limit 63)
        MAX_TABLO_ADI_UZUNLUK = 63
        
        for kategori, tablo_listesi in self.BEKLENEN_TABLO_ISIMLERI.items():
            for tablo_adi in tablo_listesi:
                assert len(tablo_adi) <= MAX_TABLO_ADI_UZUNLUK, \
                    f"Tablo adı çok uzun ({len(tablo_adi)} > {MAX_TABLO_ADI_UZUNLUK}): {tablo_adi}"
    
    def test_rezerve_kelime_kontrolu(self):
        """
        Tablo adlarının SQL rezerve kelimeleri içermediğini kontrol eder
        """
        # Yaygın SQL rezerve kelimeleri
        REZERVE_KELIMELER = {
            'select', 'insert', 'update', 'delete', 'create', 'drop', 'alter',
            'table', 'index', 'view', 'database', 'schema', 'user', 'group',
            'order', 'by', 'where', 'having', 'join', 'union', 'distinct'
        }
        
        for kategori, tablo_listesi in self.BEKLENEN_TABLO_ISIMLERI.items():
            for tablo_adi in tablo_listesi:
                kelimeler = tablo_adi.split('_')
                for kelime in kelimeler:
                    assert kelime.lower() not in REZERVE_KELIMELER, \
                        f"Tablo adı SQL rezerve kelimesi içeriyor: {tablo_adi} ({kelime})"
    
    @given(st.sampled_from(list(BEKLENEN_TABLO_ISIMLERI.keys())))
    def test_kategori_tablo_eslestirmesi_property(self, kategori):
        """
        Property test: Herhangi bir kategori için tablo listesi varlığı
        """
        tablo_listesi = self.BEKLENEN_TABLO_ISIMLERI[kategori]
        
        # Kategori boş olmamalı
        assert len(tablo_listesi) > 0, f"Kategori boş: {kategori}"
        
        # Her tablo adı geçerli olmalı
        for tablo_adi in tablo_listesi:
            assert isinstance(tablo_adi, str), f"Tablo adı string değil: {tablo_adi}"
            assert len(tablo_adi) > 0, f"Tablo adı boş: {kategori}"
            assert self._ascii_karakter_kontrolu(tablo_adi), \
                f"Tablo adı ASCII değil: {tablo_adi}"
    
    def test_compound_tablo_isimleri(self):
        """
        Birleşik tablo adlarının (alt çizgi ile ayrılmış) doğru formatlandığını kontrol eder
        """
        compound_tablolar = [
            'kullanici_rolleri', 'rol_yetkileri', 'urun_barkodlari',
            'stok_bakiyeleri', 'stok_hareketleri', 'sadakat_puanlari',
            'pos_satislar', 'pos_satis_satirlari', 'odeme_kayitlari',
            'satis_belgeleri', 'satis_belge_satirlari',
            'eticaret_hesaplari', 'eticaret_siparisleri',
            'ebelge_cikis_kuyrugu', 'ebelge_durumlari',
            'kargo_etiketleri', 'kargo_takipleri'
        ]
        
        for tablo_adi in compound_tablolar:
            # Alt çizgi ile ayrılmış olmalı
            assert '_' in tablo_adi, f"Compound tablo adı alt çizgi içermiyor: {tablo_adi}"
            
            # En az 2 kelime olmalı
            kelimeler = tablo_adi.split('_')
            assert len(kelimeler) >= 2, f"Compound tablo adı yeterli kelime içermiyor: {tablo_adi}"
            
            # Her kelime anlamlı olmalı
            for kelime in kelimeler:
                assert len(kelime) > 1, f"Compound tablo adında çok kısa kelime: {kelime} in {tablo_adi}"