# Version: 0.1.0
# Last Update: 2024-12-15
# Module: tests.test_veri_yukleme_property
# Description: SONTECHSP veri yükleme property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Veri Yükleme Property Testleri

Bu modül temel veri yükleme sistemi için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import pytest
import tempfile
import os
from hypothesis import given, strategies as st, settings
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.veritabani.baglanti import sqlite_session
from sontechsp.uygulama.veritabani.veri_yukleyici import VeriYukleyici
from sontechsp.uygulama.veritabani.modeller import (
    Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
    Firma, Magaza, Terminal
)


class TestTemelVeriTutarliligi:
    """Temel veri tutarlılığı property testleri"""
    
    @pytest.fixture
    def temp_db_engine(self):
        """Geçici SQLite veritabanı engine'i"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        yield engine
        
        engine.dispose()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def test_session_factory(self, temp_db_engine):
        """Test session factory"""
        def session_factory():
            return sqlite_session()
        
        # Tabloları oluştur
        Taban.metadata.create_all(temp_db_engine)
        
        return session_factory
    
    @pytest.fixture
    def veri_yukleyici(self, test_session_factory):
        """Test veri yükleyici"""
        return VeriYukleyici(test_session_factory)
    
    @given(st.integers(min_value=1, max_value=3))
    @settings(max_examples=5)
    def test_temel_veri_yukleme_tutarliligi(self, veri_yukleyici, yukleme_sayisi):
        """
        **Feature: veritabani-migration-tamamlama, Property 13: Temel Veri Tutarlılığı**
        
        For any basic data loading operation, loaded data should maintain referential integrity
        """
        # Birden fazla kez veri yükle
        sonuclar = []
        for i in range(yukleme_sayisi):
            sonuc = veri_yukleyici.temel_verileri_yukle()
            sonuclar.append(sonuc)
        
        # Tüm yüklemeler başarılı olmalı
        for sonuc in sonuclar:
            assert sonuc['success'] is True, "Veri yükleme başarılı olmalı"
            assert len(sonuc['errors']) == 0, "Veri yükleme hatası olmamalı"
        
        # Veri tutarlılığını kontrol et
        with veri_yukleyici.session_factory() as session:
            # Admin kullanıcı mevcut olmalı
            admin = session.query(Kullanici).filter_by(kullanici_adi='admin').first()
            assert admin is not None, "Admin kullanıcı yüklenmeli"
            
            # Sistem rolleri mevcut olmalı
            sistem_rolleri = session.query(Rol).filter_by(sistem_rolu=True).all()
            assert len(sistem_rolleri) > 0, "Sistem rolleri yüklenmeli"
            
            # Sistem yetkileri mevcut olmalı
            sistem_yetkileri = session.query(Yetki).filter_by(sistem_yetkisi=True).all()
            assert len(sistem_yetkileri) > 0, "Sistem yetkileri yüklenmeli"
            
            # Varsayılan firma mevcut olmalı
            firma = session.query(Firma).first()
            assert firma is not None, "Varsayılan firma yüklenmeli"
            
            # Varsayılan mağaza mevcut olmalı
            magaza = session.query(Magaza).first()
            assert magaza is not None, "Varsayılan mağaza yüklenmeli"
            
            # Foreign key ilişkileri doğru olmalı
            assert magaza.firma_id == firma.id, "Mağaza-firma ilişkisi doğru olmalı"
    
    def test_referans_butunlugu_korunumu(self, veri_yukleyici):
        """
        **Feature: veritabani-migration-tamamlama, Property 13: Temel Veri Tutarlılığı**
        
        For any loaded data, referential integrity should be preserved
        """
        # Temel verileri yükle
        sonuc = veri_yukleyici.temel_verileri_yukle()
        assert sonuc['success'] is True, "Veri yükleme başarılı olmalı"
        
        with veri_yukleyici.session_factory() as session:
            # Kullanıcı-rol ilişkilerini kontrol et
            kullanici_rolleri = session.query(KullaniciRol).all()
            for kr in kullanici_rolleri:
                # Kullanıcı mevcut olmalı
                kullanici = session.query(Kullanici).filter_by(id=kr.kullanici_id).first()
                assert kullanici is not None, f"Kullanıcı {kr.kullanici_id} mevcut olmalı"
                
                # Rol mevcut olmalı
                rol = session.query(Rol).filter_by(id=kr.rol_id).first()
                assert rol is not None, f"Rol {kr.rol_id} mevcut olmalı"
            
            # Rol-yetki ilişkilerini kontrol et
            rol_yetkileri = session.query(RolYetki).all()
            for ry in rol_yetkileri:
                # Rol mevcut olmalı
                rol = session.query(Rol).filter_by(id=ry.rol_id).first()
                assert rol is not None, f"Rol {ry.rol_id} mevcut olmalı"
                
                # Yetki mevcut olmalı
                yetki = session.query(Yetki).filter_by(id=ry.yetki_id).first()
                assert yetki is not None, f"Yetki {ry.yetki_id} mevcut olmalı"
            
            # Mağaza-firma ilişkilerini kontrol et
            magazalar = session.query(Magaza).all()
            for magaza in magazalar:
                # Firma mevcut olmalı
                firma = session.query(Firma).filter_by(id=magaza.firma_id).first()
                assert firma is not None, f"Firma {magaza.firma_id} mevcut olmalı"
            
            # Terminal-mağaza ilişkilerini kontrol et
            terminaller = session.query(Terminal).all()
            for terminal in terminaller:
                # Mağaza mevcut olmalı
                magaza = session.query(Magaza).filter_by(id=terminal.magaza_id).first()
                assert magaza is not None, f"Mağaza {terminal.magaza_id} mevcut olmalı"
    
    def test_veri_yukleme_idempotency(self, veri_yukleyici):
        """
        **Feature: veritabani-migration-tamamlama, Property 13: Temel Veri Tutarlılığı**
        
        For any data loading operation, multiple executions should be idempotent
        """
        # İlk veri yükleme
        sonuc1 = veri_yukleyici.temel_verileri_yukle()
        assert sonuc1['success'] is True, "İlk veri yükleme başarılı olmalı"
        
        # İkinci veri yükleme (idempotent olmalı)
        sonuc2 = veri_yukleyici.temel_verileri_yukle()
        assert sonuc2['success'] is True, "İkinci veri yükleme başarılı olmalı"
        
        with veri_yukleyici.session_factory() as session:
            # Veri sayıları aynı olmalı (duplicate oluşmamalı)
            kullanici_sayisi = session.query(Kullanici).count()
            rol_sayisi = session.query(Rol).count()
            yetki_sayisi = session.query(Yetki).count()
            firma_sayisi = session.query(Firma).count()
            magaza_sayisi = session.query(Magaza).count()
            
            # Temel veriler tek olmalı
            assert kullanici_sayisi >= 1, "En az bir kullanıcı olmalı"
            assert rol_sayisi >= 1, "En az bir rol olmalı"
            assert yetki_sayisi >= 1, "En az bir yetki olmalı"
            assert firma_sayisi >= 1, "En az bir firma olmalı"
            assert magaza_sayisi >= 1, "En az bir mağaza olmalı"
            
            # Admin kullanıcı tek olmalı
            admin_sayisi = session.query(Kullanici).filter_by(kullanici_adi='admin').count()
            assert admin_sayisi == 1, "Admin kullanıcı tek olmalı"
    
    @given(st.sampled_from(['admin', 'test_admin', 'system_admin']))
    @settings(max_examples=10)
    def test_admin_kullanici_olusturma(self, veri_yukleyici, admin_kullanici_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 13: Temel Veri Tutarlılığı**
        
        For any admin user creation, user should have proper attributes and roles
        """
        with veri_yukleyici.session_factory() as session:
            # Önce sistem rollerini oluştur
            veri_yukleyici.sistem_yetkilerini_olustur(session)
            roller = veri_yukleyici.sistem_rollerini_olustur(session)
            veri_yukleyici.rol_yetki_iliskilerini_kur(session, roller, [])
            
            # Admin kullanıcı oluştur (sadece 'admin' adıyla)
            if admin_kullanici_adi == 'admin':
                admin = veri_yukleyici.admin_kullanici_olustur(session)
                
                if admin:
                    # Admin özellikleri kontrol et
                    assert admin.kullanici_adi == 'admin', "Admin kullanıcı adı doğru olmalı"
                    assert admin.aktif is True, "Admin aktif olmalı"
                    assert admin.email is not None, "Admin email'i olmalı"
                    assert admin.sifre_hash is not None, "Admin şifre hash'i olmalı"
                    
                    # Admin'e rol ata
                    admin_rolleri = veri_yukleyici.admin_rollerini_ata(session, admin, roller)
                    
                    # Admin'in sistem yöneticisi rolü olmalı
                    sistem_yoneticisi_rol = session.query(Rol).filter_by(rol_adi='Sistem Yöneticisi').first()
                    if sistem_yoneticisi_rol:
                        admin_rol_atamasi = session.query(KullaniciRol).filter_by(
                            kullanici_id=admin.id, rol_id=sistem_yoneticisi_rol.id
                        ).first()
                        assert admin_rol_atamasi is not None, "Admin'e sistem yöneticisi rolü atanmalı"
                        assert admin_rol_atamasi.aktif is True, "Admin rol ataması aktif olmalı"


class TestVeriYuklemeUnitTestleri:
    """Veri yükleme unit testleri"""
    
    @pytest.fixture
    def temp_db_engine(self):
        """Geçici SQLite veritabanı engine'i"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        yield engine
        
        engine.dispose()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def test_session_factory(self, temp_db_engine):
        """Test session factory"""
        def session_factory():
            return sqlite_session()
        
        # Tabloları oluştur
        Taban.metadata.create_all(temp_db_engine)
        
        return session_factory
    
    @pytest.fixture
    def veri_yukleyici(self, test_session_factory):
        """Test veri yükleyici"""
        return VeriYukleyici(test_session_factory)
    
    def test_admin_kullanici_olusturma(self, veri_yukleyici):
        """
        Admin kullanıcı oluşturma testini yaz
        
        Validates: Requirements 6.1
        """
        with veri_yukleyici.session_factory() as session:
            admin = veri_yukleyici.admin_kullanici_olustur(session)
            
            assert admin is not None, "Admin kullanıcı oluşturulmalı"
            assert admin.kullanici_adi == 'admin', "Admin kullanıcı adı doğru olmalı"
            assert admin.aktif is True, "Admin aktif olmalı"
    
    def test_sistem_rolleri_olusturma(self, veri_yukleyici):
        """
        Sistem rolleri oluşturma testini yaz
        
        Validates: Requirements 6.2
        """
        with veri_yukleyici.session_factory() as session:
            roller = veri_yukleyici.sistem_rollerini_olustur(session)
            
            assert len(roller) > 0, "Sistem rolleri oluşturulmalı"
            
            rol_adlari = [rol.rol_adi for rol in roller]
            expected_roller = ['Sistem Yöneticisi', 'Mağaza Müdürü', 'Kasiyer', 'Stok Sorumlusu']
            
            for expected_rol in expected_roller:
                assert expected_rol in rol_adlari, f"'{expected_rol}' rolü oluşturulmalı"
    
    def test_sistem_yetkileri_olusturma(self, veri_yukleyici):
        """
        Sistem yetkileri oluşturma testini yaz
        
        Validates: Requirements 6.3
        """
        with veri_yukleyici.session_factory() as session:
            yetkiler = veri_yukleyici.sistem_yetkilerini_olustur(session)
            
            assert len(yetkiler) > 0, "Sistem yetkileri oluşturulmalı"
            
            yetki_kodlari = [yetki.yetki_kodu for yetki in yetkiler]
            expected_yetkiler = ['kullanici.olustur', 'pos.satis', 'stok.listele', 'sistem.yonetim']
            
            for expected_yetki in expected_yetkiler:
                assert expected_yetki in yetki_kodlari, f"'{expected_yetki}' yetkisi oluşturulmalı"
    
    def test_varsayilan_firma_magaza_olusturma(self, veri_yukleyici):
        """
        Varsayılan firma/mağaza oluşturma testini yaz
        
        Validates: Requirements 6.4
        """
        with veri_yukleyici.session_factory() as session:
            firma, magaza = veri_yukleyici.varsayilan_firma_magaza_olustur(session)
            
            assert firma is not None, "Varsayılan firma oluşturulmalı"
            assert magaza is not None, "Varsayılan mağaza oluşturulmalı"
            assert magaza.firma_id == firma.id, "Mağaza-firma ilişkisi doğru olmalı"
            assert firma.firma_adi == 'SONTECHSP Demo Firma', "Firma adı doğru olmalı"
            assert magaza.magaza_adi == 'Ana Mağaza', "Mağaza adı doğru olmalı"