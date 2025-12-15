# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.veri_yukleyici
# Description: SONTECHSP temel veri yükleme sistemi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Temel Veri Yükleme Sistemi

Bu modül sistem ilk kurulumunda gerekli temel verileri yükler.
Admin kullanıcı, sistem rolleri, yetkiler ve varsayılan firma/mağaza oluşturur.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..cekirdek.hatalar import VeriYuklemeHatasi
from .baglanti import postgresql_session, sqlite_session
from .modeller import (
    Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
    Firma, Magaza, Terminal
)

logger = logging.getLogger(__name__)


class VeriYukleyici:
    """SONTECHSP temel veri yükleme sınıfı"""
    
    def __init__(self, session_factory=None):
        """Veri yükleyici başlatma"""
        self.session_factory = session_factory or postgresql_session
    
    def temel_verileri_yukle(self) -> Dict[str, Any]:
        """
        Tüm temel verileri yükle
        
        Returns:
            Dict: Yükleme sonuç bilgileri
        """
        try:
            sonuc = {
                'success': True,
                'loaded_data': {},
                'errors': [],
                'load_time': datetime.now().isoformat()
            }
            
            with self.session_factory() as session:
                # Sistem yetkilerini oluştur
                yetkiler = self.sistem_yetkilerini_olustur(session)
                sonuc['loaded_data']['yetkiler'] = len(yetkiler)
                
                # Sistem rollerini oluştur
                roller = self.sistem_rollerini_olustur(session)
                sonuc['loaded_data']['roller'] = len(roller)
                
                # Rol-yetki ilişkilerini kur
                rol_yetkileri = self.rol_yetki_iliskilerini_kur(session, roller, yetkiler)
                sonuc['loaded_data']['rol_yetkileri'] = len(rol_yetkileri)
                
                # Admin kullanıcı oluştur
                admin_kullanici = self.admin_kullanici_olustur(session)
                sonuc['loaded_data']['admin_kullanici'] = 1 if admin_kullanici else 0
                
                # Admin'e roller ata
                if admin_kullanici:
                    admin_rolleri = self.admin_rollerini_ata(session, admin_kullanici, roller)
                    sonuc['loaded_data']['admin_rolleri'] = len(admin_rolleri)
                
                # Varsayılan firma ve mağaza oluştur
                firma, magaza = self.varsayilan_firma_magaza_olustur(session)
                sonuc['loaded_data']['firma'] = 1 if firma else 0
                sonuc['loaded_data']['magaza'] = 1 if magaza else 0
                
                # Varsayılan terminal oluştur
                if magaza:
                    terminal = self.varsayilan_terminal_olustur(session, magaza)
                    sonuc['loaded_data']['terminal'] = 1 if terminal else 0
            
            logger.info(f"Temel veriler başarıyla yüklendi: {sonuc['loaded_data']}")
            return sonuc
            
        except Exception as e:
            logger.error(f"Temel veri yükleme hatası: {e}")
            raise VeriYuklemeHatasi(f"Temel veriler yüklenemedi: {e}")
    
    def sistem_yetkilerini_olustur(self, session: Session) -> List[Yetki]:
        """Sistem yetkilerini oluştur"""
        try:
            yetkiler_data = [
                # Kullanıcı yönetimi yetkileri
                {'yetki_kodu': 'kullanici.olustur', 'yetki_adi': 'Kullanıcı Oluştur', 'kategori': 'kullanici_yonetimi'},
                {'yetki_kodu': 'kullanici.duzenle', 'yetki_adi': 'Kullanıcı Düzenle', 'kategori': 'kullanici_yonetimi'},
                {'yetki_kodu': 'kullanici.sil', 'yetki_adi': 'Kullanıcı Sil', 'kategori': 'kullanici_yonetimi'},
                {'yetki_kodu': 'kullanici.listele', 'yetki_adi': 'Kullanıcı Listele', 'kategori': 'kullanici_yonetimi'},
                
                # Rol yönetimi yetkileri
                {'yetki_kodu': 'rol.olustur', 'yetki_adi': 'Rol Oluştur', 'kategori': 'rol_yonetimi'},
                {'yetki_kodu': 'rol.duzenle', 'yetki_adi': 'Rol Düzenle', 'kategori': 'rol_yonetimi'},
                {'yetki_kodu': 'rol.sil', 'yetki_adi': 'Rol Sil', 'kategori': 'rol_yonetimi'},
                {'yetki_kodu': 'rol.listele', 'yetki_adi': 'Rol Listele', 'kategori': 'rol_yonetimi'},
                
                # POS yetkileri
                {'yetki_kodu': 'pos.satis', 'yetki_adi': 'POS Satış', 'kategori': 'pos'},
                {'yetki_kodu': 'pos.iade', 'yetki_adi': 'POS İade', 'kategori': 'pos'},
                {'yetki_kodu': 'pos.rapor', 'yetki_adi': 'POS Rapor', 'kategori': 'pos'},
                
                # Stok yetkileri
                {'yetki_kodu': 'stok.listele', 'yetki_adi': 'Stok Listele', 'kategori': 'stok'},
                {'yetki_kodu': 'stok.duzenle', 'yetki_adi': 'Stok Düzenle', 'kategori': 'stok'},
                {'yetki_kodu': 'stok.sayim', 'yetki_adi': 'Stok Sayım', 'kategori': 'stok'},
                
                # Sistem yönetimi yetkileri
                {'yetki_kodu': 'sistem.yonetim', 'yetki_adi': 'Sistem Yönetimi', 'kategori': 'sistem'},
                {'yetki_kodu': 'sistem.ayarlar', 'yetki_adi': 'Sistem Ayarları', 'kategori': 'sistem'},
            ]
            
            yetkiler = []
            for yetki_data in yetkiler_data:
                # Mevcut yetki var mı kontrol et
                mevcut_yetki = session.query(Yetki).filter_by(yetki_kodu=yetki_data['yetki_kodu']).first()
                if not mevcut_yetki:
                    yetki = Yetki(
                        yetki_kodu=yetki_data['yetki_kodu'],
                        yetki_adi=yetki_data['yetki_adi'],
                        kategori=yetki_data['kategori'],
                        sistem_yetkisi=True,
                        aktif=True
                    )
                    session.add(yetki)
                    yetkiler.append(yetki)
            
            session.commit()
            logger.info(f"{len(yetkiler)} sistem yetkisi oluşturuldu")
            return yetkiler
            
        except Exception as e:
            session.rollback()
            logger.error(f"Sistem yetkileri oluşturma hatası: {e}")
            raise VeriYuklemeHatasi(f"Sistem yetkileri oluşturulamadı: {e}")
    
    def sistem_rollerini_olustur(self, session: Session) -> List[Rol]:
        """Sistem rollerini oluştur"""
        try:
            roller_data = [
                {'rol_adi': 'Sistem Yöneticisi', 'aciklama': 'Tüm sistem yetkilerine sahip süper kullanıcı'},
                {'rol_adi': 'Mağaza Müdürü', 'aciklama': 'Mağaza yönetimi ve raporlama yetkileri'},
                {'rol_adi': 'Kasiyer', 'aciklama': 'POS satış ve temel işlem yetkileri'},
                {'rol_adi': 'Stok Sorumlusu', 'aciklama': 'Stok yönetimi ve sayım yetkileri'},
            ]
            
            roller = []
            for rol_data in roller_data:
                # Mevcut rol var mı kontrol et
                mevcut_rol = session.query(Rol).filter_by(rol_adi=rol_data['rol_adi']).first()
                if not mevcut_rol:
                    rol = Rol(
                        rol_adi=rol_data['rol_adi'],
                        aciklama=rol_data['aciklama'],
                        sistem_rolu=True,
                        aktif=True
                    )
                    session.add(rol)
                    roller.append(rol)
            
            session.commit()
            logger.info(f"{len(roller)} sistem rolü oluşturuldu")
            return roller
            
        except Exception as e:
            session.rollback()
            logger.error(f"Sistem rolleri oluşturma hatası: {e}")
            raise VeriYuklemeHatasi(f"Sistem rolleri oluşturulamadı: {e}")
    
    def rol_yetki_iliskilerini_kur(self, session: Session, roller: List[Rol], yetkiler: List[Yetki]) -> List[RolYetki]:
        """Rol-yetki ilişkilerini kur"""
        try:
            # Tüm rolleri ve yetkileri al (mevcut olanlar dahil)
            tum_roller = session.query(Rol).filter_by(sistem_rolu=True).all()
            tum_yetkiler = session.query(Yetki).filter_by(sistem_yetkisi=True).all()
            
            rol_yetki_iliskileri = []
            
            for rol in tum_roller:
                if rol.rol_adi == 'Sistem Yöneticisi':
                    # Sistem yöneticisine tüm yetkiler
                    for yetki in tum_yetkiler:
                        mevcut_iliski = session.query(RolYetki).filter_by(
                            rol_id=rol.id, yetki_id=yetki.id
                        ).first()
                        if not mevcut_iliski:
                            rol_yetki = RolYetki(rol_id=rol.id, yetki_id=yetki.id, aktif=True)
                            session.add(rol_yetki)
                            rol_yetki_iliskileri.append(rol_yetki)
                
                elif rol.rol_adi == 'Mağaza Müdürü':
                    # Mağaza müdürüne POS ve stok yetkileri
                    yetki_kodlari = ['pos.satis', 'pos.iade', 'pos.rapor', 'stok.listele', 'stok.duzenle']
                    for yetki in tum_yetkiler:
                        if yetki.yetki_kodu in yetki_kodlari:
                            mevcut_iliski = session.query(RolYetki).filter_by(
                                rol_id=rol.id, yetki_id=yetki.id
                            ).first()
                            if not mevcut_iliski:
                                rol_yetki = RolYetki(rol_id=rol.id, yetki_id=yetki.id, aktif=True)
                                session.add(rol_yetki)
                                rol_yetki_iliskileri.append(rol_yetki)
                
                elif rol.rol_adi == 'Kasiyer':
                    # Kasiyere sadece POS satış yetkileri
                    yetki_kodlari = ['pos.satis', 'pos.iade']
                    for yetki in tum_yetkiler:
                        if yetki.yetki_kodu in yetki_kodlari:
                            mevcut_iliski = session.query(RolYetki).filter_by(
                                rol_id=rol.id, yetki_id=yetki.id
                            ).first()
                            if not mevcut_iliski:
                                rol_yetki = RolYetki(rol_id=rol.id, yetki_id=yetki.id, aktif=True)
                                session.add(rol_yetki)
                                rol_yetki_iliskileri.append(rol_yetki)
                
                elif rol.rol_adi == 'Stok Sorumlusu':
                    # Stok sorumlusuna stok yetkileri
                    yetki_kodlari = ['stok.listele', 'stok.duzenle', 'stok.sayim']
                    for yetki in tum_yetkiler:
                        if yetki.yetki_kodu in yetki_kodlari:
                            mevcut_iliski = session.query(RolYetki).filter_by(
                                rol_id=rol.id, yetki_id=yetki.id
                            ).first()
                            if not mevcut_iliski:
                                rol_yetki = RolYetki(rol_id=rol.id, yetki_id=yetki.id, aktif=True)
                                session.add(rol_yetki)
                                rol_yetki_iliskileri.append(rol_yetki)
            
            session.commit()
            logger.info(f"{len(rol_yetki_iliskileri)} rol-yetki ilişkisi kuruldu")
            return rol_yetki_iliskileri
            
        except Exception as e:
            session.rollback()
            logger.error(f"Rol-yetki ilişkileri kurma hatası: {e}")
            raise VeriYuklemeHatasi(f"Rol-yetki ilişkileri kurulamadı: {e}")
    
    def admin_kullanici_olustur(self, session: Session) -> Optional[Kullanici]:
        """Admin kullanıcı oluştur"""
        try:
            # Mevcut admin var mı kontrol et
            mevcut_admin = session.query(Kullanici).filter_by(kullanici_adi='admin').first()
            if mevcut_admin:
                logger.info("Admin kullanıcı zaten mevcut")
                return mevcut_admin
            
            # Admin kullanıcı oluştur
            admin = Kullanici(
                kullanici_adi='admin',
                email='admin@sontechsp.com',
                sifre_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZp/k/K',  # admin123
                ad='Sistem',
                soyad='Yöneticisi',
                aktif=True
            )
            
            session.add(admin)
            session.commit()
            
            logger.info("Admin kullanıcı oluşturuldu")
            return admin
            
        except IntegrityError as e:
            session.rollback()
            logger.warning(f"Admin kullanıcı zaten mevcut: {e}")
            return session.query(Kullanici).filter_by(kullanici_adi='admin').first()
        except Exception as e:
            session.rollback()
            logger.error(f"Admin kullanıcı oluşturma hatası: {e}")
            raise VeriYuklemeHatasi(f"Admin kullanıcı oluşturulamadı: {e}")
    
    def admin_rollerini_ata(self, session: Session, admin: Kullanici, roller: List[Rol]) -> List[KullaniciRol]:
        """Admin'e rolleri ata"""
        try:
            # Sistem yöneticisi rolünü bul
            sistem_yoneticisi = session.query(Rol).filter_by(rol_adi='Sistem Yöneticisi').first()
            if not sistem_yoneticisi:
                raise VeriYuklemeHatasi("Sistem Yöneticisi rolü bulunamadı")
            
            # Mevcut rol ataması var mı kontrol et
            mevcut_atama = session.query(KullaniciRol).filter_by(
                kullanici_id=admin.id, rol_id=sistem_yoneticisi.id
            ).first()
            
            if mevcut_atama:
                logger.info("Admin rol ataması zaten mevcut")
                return [mevcut_atama]
            
            # Rol ataması yap
            kullanici_rol = KullaniciRol(
                kullanici_id=admin.id,
                rol_id=sistem_yoneticisi.id,
                aktif=True
            )
            
            session.add(kullanici_rol)
            session.commit()
            
            logger.info("Admin'e Sistem Yöneticisi rolü atandı")
            return [kullanici_rol]
            
        except Exception as e:
            session.rollback()
            logger.error(f"Admin rol atama hatası: {e}")
            raise VeriYuklemeHatasi(f"Admin'e rol atanamadı: {e}")
    
    def varsayilan_firma_magaza_olustur(self, session: Session) -> tuple[Optional[Firma], Optional[Magaza]]:
        """Varsayılan firma ve mağaza oluştur"""
        try:
            # Mevcut firma var mı kontrol et
            mevcut_firma = session.query(Firma).filter_by(firma_adi='SONTECHSP Demo Firma').first()
            if mevcut_firma:
                logger.info("Varsayılan firma zaten mevcut")
                # Mevcut mağaza var mı kontrol et
                mevcut_magaza = session.query(Magaza).filter_by(
                    firma_id=mevcut_firma.id, magaza_adi='Ana Mağaza'
                ).first()
                return mevcut_firma, mevcut_magaza
            
            # Firma oluştur
            firma = Firma(
                firma_adi='SONTECHSP Demo Firma',
                ticaret_unvani='SONTECHSP Teknoloji A.Ş.',
                vergi_dairesi='Kadıköy',
                vergi_no='1234567890',
                adres='İstanbul, Türkiye',
                telefon='+90 216 123 45 67',
                email='info@sontechsp.com',
                website='https://www.sontechsp.com',
                aktif=True
            )
            
            session.add(firma)
            session.flush()  # ID'yi al
            
            # Ana mağaza oluştur
            magaza = Magaza(
                firma_id=firma.id,
                magaza_adi='Ana Mağaza',
                magaza_kodu='ANA001',
                adres='İstanbul Merkez',
                sehir='İstanbul',
                ilce='Kadıköy',
                posta_kodu='34710',
                telefon='+90 216 123 45 67',
                email='ana@sontechsp.com',
                alan_m2=100.0,
                personel_sayisi=5,
                aktif=True
            )
            
            session.add(magaza)
            session.commit()
            
            logger.info("Varsayılan firma ve mağaza oluşturuldu")
            return firma, magaza
            
        except Exception as e:
            session.rollback()
            logger.error(f"Varsayılan firma/mağaza oluşturma hatası: {e}")
            raise VeriYuklemeHatasi(f"Varsayılan firma/mağaza oluşturulamadı: {e}")
    
    def varsayilan_terminal_olustur(self, session: Session, magaza: Magaza) -> Optional[Terminal]:
        """Varsayılan terminal oluştur"""
        try:
            # Mevcut terminal var mı kontrol et
            mevcut_terminal = session.query(Terminal).filter_by(
                magaza_id=magaza.id, terminal_kodu='T001'
            ).first()
            if mevcut_terminal:
                logger.info("Varsayılan terminal zaten mevcut")
                return mevcut_terminal
            
            # Terminal oluştur
            terminal = Terminal(
                magaza_id=magaza.id,
                terminal_adi='Ana Kasa',
                terminal_kodu='T001',
                ip_adresi='192.168.1.100',
                isletim_sistemi='Windows 11',
                yazici_modeli='Epson TM-T20',
                barkod_okuyucu=True,
                aktif=True,
                online=True
            )
            
            session.add(terminal)
            session.commit()
            
            logger.info("Varsayılan terminal oluşturuldu")
            return terminal
            
        except Exception as e:
            session.rollback()
            logger.error(f"Varsayılan terminal oluşturma hatası: {e}")
            raise VeriYuklemeHatasi(f"Varsayılan terminal oluşturulamadı: {e}")


# Global veri yükleyici instance
veri_yukleyici = VeriYukleyici()

# Kısayol fonksiyonlar
def temel_verileri_yukle() -> Dict[str, Any]:
    """Temel veri yükleme kısayolu"""
    return veri_yukleyici.temel_verileri_yukle()