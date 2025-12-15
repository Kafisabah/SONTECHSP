# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_yetki_property
# Description: Yetki kontrol property testleri
# Changelog:
# - 0.1.0: İlk sürüm, yetki kontrol property testleri oluşturuldu

"""
Yetki Kontrol Property Testleri

Bu modül yetki kontrol sisteminin doğruluk özelliklerini test eder.
"""

from typing import Dict, List

import pytest
from hypothesis import given, strategies as st, settings, assume

from sontechsp.uygulama.cekirdek.yetki import (
    YetkiKontrolcu, YetkiMatrisi, yetki_kontrolcu_al,
    izin_kontrol_et, yetki_gerekli
)


# Test stratejileri
rol_adi_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
    min_size=1,
    max_size=20
).filter(lambda x: x.replace('_', '').isalnum())

izin_adi_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
    min_size=1,
    max_size=30
).filter(lambda x: x.replace('_', '').isalnum())

gecerli_rol_strategy = st.sampled_from(["misafir", "kullanici", "operator", "mudur", "admin"])
gecerli_izin_strategy = st.sampled_from([
    "sistem_goruntule", "veri_oku", "veri_yaz", "veri_sil", 
    "rapor_goruntule", "rapor_olustur", "kullanici_yonet"
])


class YetkiTestYardimcisi:
    """Yetki testleri için yardımcı sınıf"""
    
    @staticmethod
    def test_yetki_matrisi_olustur() -> YetkiMatrisi:
        """Test için basit yetki matrisi oluşturur"""
        return YetkiMatrisi(
            roller={
                "test_rol1": ["test_izin1", "test_izin2"],
                "test_rol2": ["test_izin2", "test_izin3"],
                "test_admin": ["*"]
            },
            varsayilan_roller=["test_rol1"],
            admin_rolleri=["test_admin"],
            rol_hiyerarsisi={
                "test_admin": ["test_rol2", "test_rol1"],
                "test_rol2": ["test_rol1"]
            }
        )
    
    @staticmethod
    def rastgele_yetki_matrisi_olustur(roller: List[str], izinler: List[str]) -> YetkiMatrisi:
        """Rastgele yetki matrisi oluşturur"""
        import random
        
        rol_izin_map = {}
        for rol in roller:
            # Her role rastgele izinler ata
            rol_izin_sayisi = random.randint(1, len(izinler))
            rol_izinleri = random.sample(izinler, rol_izin_sayisi)
            rol_izin_map[rol] = rol_izinleri
        
        return YetkiMatrisi(
            roller=rol_izin_map,
            varsayilan_roller=[roller[0]] if roller else [],
            admin_rolleri=[roller[-1]] if roller else []
        )


# **Feature: cekirdek-altyapi, Property 7: Yetki kontrol tutarlılığı**
@settings(max_examples=100)
@given(
    rol=gecerli_rol_strategy,
    izin=gecerli_izin_strategy
)
def test_yetki_kontrol_tutarliligi(rol, izin):
    """
    Özellik 7: Yetki kontrol tutarlılığı
    Herhangi bir rol-izin kombinasyonu için, yetki kontrolü tutarlı sonuç vermelidir
    Doğrular: Gereksinim 4.1, 4.4
    """
    kontrolcu = YetkiKontrolcu()
    
    # Aynı rol-izin kombinasyonunu birden fazla kez kontrol et
    sonuc1 = kontrolcu.izin_var_mi(rol, izin)
    sonuc2 = kontrolcu.izin_var_mi(rol, izin)
    sonuc3 = kontrolcu.izin_var_mi(rol, izin)
    
    # Tutarlılık kontrolü
    assert sonuc1 == sonuc2 == sonuc3, (
        f"Yetki kontrolü tutarsız: {rol}-{izin} için {sonuc1} != {sonuc2} != {sonuc3}"
    )
    
    # Global fonksiyon ile de aynı sonuç alınmalı
    global_sonuc = izin_kontrol_et(rol, izin)
    assert sonuc1 == global_sonuc, (
        f"Global fonksiyon tutarsız: {sonuc1} != {global_sonuc}"
    )
    
    # Rol listesinde de aynı sonuç olmalı
    if sonuc1:
        rol_izinleri = kontrolcu.rol_izinlerini_listele(rol)
        assert izin in rol_izinleri, (
            f"İzin rol listesinde bulunamadı: {izin} not in {rol_izinleri}"
        )
    
    # İzin gerektiren roller listesinde de tutarlılık
    if sonuc1:
        izin_rolleri = kontrolcu.izin_gerektiren_rolleri_listele(izin)
        assert rol in izin_rolleri, (
            f"Rol izin listesinde bulunamadı: {rol} not in {izin_rolleri}"
        )


@settings(max_examples=100)
@given(
    roller=st.lists(rol_adi_strategy, min_size=1, max_size=5, unique=True),
    izinler=st.lists(izin_adi_strategy, min_size=1, max_size=10, unique=True)
)
def test_ozel_yetki_matrisi_tutarliligi(roller, izinler):
    """
    Özel yetki matrisi ile tutarlılık testi
    Herhangi bir özel yetki matrisi için, kontroller tutarlı olmalıdır
    """
    assume(len(roller) > 0 and len(izinler) > 0)
    
    # Özel yetki matrisi oluştur
    matris = YetkiTestYardimcisi.rastgele_yetki_matrisi_olustur(roller, izinler)
    
    kontrolcu = YetkiKontrolcu()
    kontrolcu.yetki_matrisi_yukle(matris)
    
    # Her rol-izin kombinasyonu için tutarlılık kontrol et
    for rol in roller:
        for izin in izinler:
            sonuc1 = kontrolcu.izin_var_mi(rol, izin)
            sonuc2 = kontrolcu.izin_var_mi(rol, izin)
            
            assert sonuc1 == sonuc2, (
                f"Özel matris tutarsız: {rol}-{izin} için {sonuc1} != {sonuc2}"
            )
            
            # Rol doğrulama
            assert kontrolcu.rol_dogrula(rol) == True, f"Geçerli rol doğrulanamadı: {rol}"
            
            # İzin doğrulama
            assert kontrolcu.izin_dogrula(izin) == True, f"Geçerli izin doğrulanamadı: {izin}"


def test_geçersiz_rol_izin_kontrolu():
    """Geçersiz rol ve izinler için False döndürme testi"""
    kontrolcu = YetkiKontrolcu()
    
    # Geçersiz rol
    assert kontrolcu.izin_var_mi("gecersiz_rol", "sistem_goruntule") == False
    assert kontrolcu.rol_dogrula("gecersiz_rol") == False
    
    # Geçersiz izin
    assert kontrolcu.izin_var_mi("kullanici", "gecersiz_izin") == False
    assert kontrolcu.izin_dogrula("gecersiz_izin") == False
    
    # Boş değerler
    assert kontrolcu.izin_var_mi("", "sistem_goruntule") == False
    assert kontrolcu.izin_var_mi("kullanici", "") == False
    assert kontrolcu.izin_var_mi(None, "sistem_goruntule") == False
    assert kontrolcu.izin_var_mi("kullanici", None) == False


def test_admin_rol_tum_izinlere_sahip():
    """Admin rolünün tüm izinlere sahip olduğunu test eder"""
    kontrolcu = YetkiKontrolcu()
    
    # Tüm mevcut izinler için admin kontrolü
    istatistikler = kontrolcu.yetki_istatistikleri()
    tum_izinler = istatistikler['izinler']
    
    for izin in tum_izinler:
        assert kontrolcu.izin_var_mi("admin", izin) == True, (
            f"Admin rolü {izin} iznine sahip değil"
        )


def test_rol_hiyerarsisi():
    """Rol hiyerarşisinin doğru çalıştığını test eder"""
    kontrolcu = YetkiKontrolcu()
    
    # Mudur rolü, operator izinlerine de sahip olmalı
    operator_izinleri = kontrolcu.rol_izinlerini_listele("operator")
    mudur_izinleri = kontrolcu.rol_izinlerini_listele("mudur")
    
    for izin in operator_izinleri:
        assert izin in mudur_izinleri, (
            f"Mudur rolü operator iznine sahip değil: {izin}"
        )
    
    # Admin en yüksek rol olmalı
    en_yuksek = kontrolcu.en_yuksek_rol_bul(["kullanici", "operator", "admin"])
    assert en_yuksek == "admin", f"En yüksek rol admin değil: {en_yuksek}"


def test_coklu_izin_kontrolu():
    """Çoklu izin kontrolü fonksiyonunu test eder"""
    kontrolcu = YetkiKontrolcu()
    
    test_izinleri = ["sistem_goruntule", "veri_oku", "veri_yaz"]
    sonuclar = kontrolcu.coklu_izin_var_mi("operator", test_izinleri)
    
    # Sonuçlar sözlüğü doğru formatta olmalı
    assert isinstance(sonuclar, dict)
    assert len(sonuclar) == len(test_izinleri)
    
    for izin in test_izinleri:
        assert izin in sonuclar
        # Tek tek kontrol ile aynı sonuç olmalı
        assert sonuclar[izin] == kontrolcu.izin_var_mi("operator", izin)


def test_yetki_decorator():
    """Yetki decorator'ının doğru çalıştığını test eder"""
    
    @yetki_gerekli("veri_yaz")
    def test_fonksiyon(rol, veri):
        return f"Veri kaydedildi: {veri}"
    
    # Yetkili rol ile çağrı
    sonuc = test_fonksiyon("operator", "test_veri")
    assert sonuc == "Veri kaydedildi: test_veri"
    
    # Yetkisiz rol ile çağrı
    from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi
    with pytest.raises(DogrulamaHatasi):
        test_fonksiyon("misafir", "test_veri")


def test_yetki_istatistikleri():
    """Yetki istatistiklerinin doğruluğunu test eder"""
    kontrolcu = YetkiKontrolcu()
    istatistikler = kontrolcu.yetki_istatistikleri()
    
    # Gerekli alanların varlığı
    gerekli_alanlar = [
        'toplam_rol_sayisi', 'toplam_izin_sayisi', 'admin_rol_sayisi',
        'varsayilan_rol_sayisi', 'cache_boyutu', 'hiyerarsi_var_mi',
        'roller', 'izinler'
    ]
    
    for alan in gerekli_alanlar:
        assert alan in istatistikler, f"İstatistikte eksik alan: {alan}"
    
    # Sayısal değerlerin pozitif olması
    assert istatistikler['toplam_rol_sayisi'] > 0
    assert istatistikler['toplam_izin_sayisi'] > 0
    
    # Listelerin sıralı olması
    assert istatistikler['roller'] == sorted(istatistikler['roller'])
    assert istatistikler['izinler'] == sorted(istatistikler['izinler'])


def test_cache_yonetimi():
    """Cache yönetiminin doğru çalıştığını test eder"""
    kontrolcu = YetkiKontrolcu()
    
    # İlk kontrol (cache doldurulur)
    sonuc1 = kontrolcu.izin_var_mi("kullanici", "veri_oku")
    
    # Cache temizle
    kontrolcu.cache_temizle()
    
    # Aynı kontrol (cache'den değil, yeniden hesaplanır)
    sonuc2 = kontrolcu.izin_var_mi("kullanici", "veri_oku")
    
    assert sonuc1 == sonuc2, "Cache temizleme sonrası tutarsızlık"
    
    # Cache yenile
    kontrolcu.cache_yenile()
    
    # Tekrar kontrol
    sonuc3 = kontrolcu.izin_var_mi("kullanici", "veri_oku")
    
    assert sonuc1 == sonuc3, "Cache yenileme sonrası tutarsızlık"


def test_global_yetki_kontrolcu():
    """Global yetki kontrolcü singleton'ını test eder"""
    kontrolcu1 = yetki_kontrolcu_al()
    kontrolcu2 = yetki_kontrolcu_al()
    
    assert kontrolcu1 is kontrolcu2, "Global yetki kontrolcü singleton değil"
    assert isinstance(kontrolcu1, YetkiKontrolcu)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])