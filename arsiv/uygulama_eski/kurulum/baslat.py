# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kurulum.baslat
# Description: Ana bootstrap koordinatörü
# Changelog:
# - Ana bootstrap koordinatörü oluşturuldu
# - Tüm kurulum adımlarını sırasıyla koordine eder

"""
Ana Bootstrap Koordinatörü

Bu modül, SONTECHSP uygulamasının ilk çalıştırılması için gerekli tüm
hazırlık işlemlerini koordine eder ve sırasıyla çalıştırır.

Kurulum Adımları:
1. Klasör yapısı oluşturma
2. Ayar dosyası oluşturma
3. Veritabanı bağlantı testi
4. Alembic migration'ları çalıştırma
5. Varsayılan admin kullanıcı oluşturma
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .sabitler import VARSAYILAN_ADMIN_KULLANICI, VARSAYILAN_ADMIN_SIFRE
from .klasorler import klasorleri_olustur, klasor_var_mi, eksik_klasorleri_listele
from .ayar_olusturucu import (
    varsayilan_ayarlar, 
    ayar_dosyasi_var_mi, 
    ayar_dosyasi_olustur,
    ayarlari_yukle
)
from .veritabani_kontrol import baglanti_test_et, gocleri_calistir
from .admin_olusturucu import admin_varsa_gec, admin_olustur
from . import (
    KurulumHatasi, 
    DogrulamaHatasi, 
    KlasorHatasi, 
    AyarHatasi,
    MigrationHatasi,
    KullaniciHatasi,
    logger
)

# SQLAlchemy import'ları
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import SQLAlchemyError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("SQLAlchemy bulunamadı, veritabanı işlemleri devre dışı")


def kurulum_durumunu_kontrol_et(proje_koku: Path) -> Dict[str, bool]:
    """
    Mevcut kurulum durumunu kontrol et
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        Dict[str, bool]: Kurulum adımlarının durum bilgileri
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        durum = {
            "klasorler_mevcut": klasor_var_mi(proje_koku),
            "ayar_dosyasi_mevcut": ayar_dosyasi_var_mi(proje_koku),
            "veritabani_baglantisi": False,
            "admin_kullanici_mevcut": False
        }
        
        # Ayar dosyası varsa veritabanı bağlantısını test et
        if durum["ayar_dosyasi_mevcut"]:
            try:
                ayarlar = ayarlari_yukle(proje_koku)
                baglanti_test_et(ayarlar["veritabani_url"])
                durum["veritabani_baglantisi"] = True
                
                # Admin kullanıcı kontrolü için session oluştur
                if SQLALCHEMY_AVAILABLE:
                    engine = create_engine(ayarlar["veritabani_url"])
                    Session = sessionmaker(bind=engine)
                    with Session() as session:
                        durum["admin_kullanici_mevcut"] = admin_varsa_gec(session)
                        
            except Exception as e:
                logger.debug(f"Durum kontrolü sırasında hata (normal): {e}")
        
        return durum
        
    except Exception as e:
        logger.error(f"Kurulum durumu kontrol hatası: {e}")
        return {
            "klasorler_mevcut": False,
            "ayar_dosyasi_mevcut": False,
            "veritabani_baglantisi": False,
            "admin_kullanici_mevcut": False
        }


def klasor_kurulumunu_yap(proje_koku: Path) -> None:
    """
    Klasör kurulumu adımını gerçekleştir
    
    Args:
        proje_koku: Proje kök dizini
        
    Raises:
        KlasorHatasi: Klasör kurulumu başarısızsa
    """
    try:
        logger.info("=== ADIM 1: Klasör Yapısı Oluşturma ===")
        
        # Mevcut durumu kontrol et
        if klasor_var_mi(proje_koku):
            logger.info("Tüm gerekli klasörler zaten mevcut")
            return
        
        # Eksik klasörleri listele
        eksik_klasorler = eksik_klasorleri_listele(proje_koku)
        if eksik_klasorler:
            logger.info(f"Eksik klasörler: {', '.join(eksik_klasorler)}")
        
        # Klasörleri oluştur
        klasorleri_olustur(proje_koku)
        
        # Doğrulama
        if not klasor_var_mi(proje_koku):
            raise KlasorHatasi("Klasör oluşturma doğrulaması başarısız")
        
        logger.info("✓ Klasör yapısı başarıyla oluşturuldu")
        
    except Exception as e:
        if isinstance(e, KlasorHatasi):
            raise
        raise KlasorHatasi(f"Klasör kurulumu hatası: {e}")


def ayar_kurulumunu_yap(proje_koku: Path, ozel_ayarlar: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Ayar dosyası kurulumu adımını gerçekleştir
    
    Args:
        proje_koku: Proje kök dizini
        ozel_ayarlar: Özel ayarlar (opsiyonel)
        
    Returns:
        Dict[str, Any]: Oluşturulan/yüklenen ayarlar
        
    Raises:
        AyarHatasi: Ayar kurulumu başarısızsa
    """
    try:
        logger.info("=== ADIM 2: Ayar Dosyası Oluşturma ===")
        
        # Mevcut durumu kontrol et
        if ayar_dosyasi_var_mi(proje_koku):
            logger.info("Ayar dosyası zaten mevcut, yükleniyor...")
            ayarlar = ayarlari_yukle(proje_koku)
            logger.info("✓ Mevcut ayar dosyası yüklendi")
            return ayarlar
        
        # Varsayılan ayarları al
        ayarlar = varsayilan_ayarlar()
        
        # Özel ayarları birleştir
        if ozel_ayarlar:
            ayarlar.update(ozel_ayarlar)
            logger.info(f"Özel ayarlar eklendi: {list(ozel_ayarlar.keys())}")
        
        # Ayar dosyasını oluştur
        ayar_dosyasi_olustur(proje_koku, ayarlar)
        
        # Doğrulama
        if not ayar_dosyasi_var_mi(proje_koku):
            raise AyarHatasi("Ayar dosyası oluşturma doğrulaması başarısız")
        
        logger.info("✓ Ayar dosyası başarıyla oluşturuldu")
        return ayarlar
        
    except Exception as e:
        if isinstance(e, AyarHatasi):
            raise
        raise AyarHatasi(f"Ayar kurulumu hatası: {e}")


def veritabani_kurulumunu_yap(ayarlar: Dict[str, Any]) -> None:
    """
    Veritabanı kurulumu adımını gerçekleştir
    
    Args:
        ayarlar: Uygulama ayarları
        
    Raises:
        DogrulamaHatasi: Veritabanı bağlantı testi başarısızsa
    """
    try:
        logger.info("=== ADIM 3: Veritabanı Bağlantı Testi ===")
        
        veritabani_url = ayarlar.get("veritabani_url")
        if not veritabani_url:
            raise DogrulamaHatasi("Ayarlarda veritabanı URL'i bulunamadı")
        
        # Bağlantıyı test et
        baglanti_test_et(veritabani_url)
        
        logger.info("✓ Veritabanı bağlantısı başarıyla test edildi")
        
    except Exception as e:
        if isinstance(e, DogrulamaHatasi):
            raise
        raise DogrulamaHatasi(f"Veritabanı kurulumu hatası: {e}")


def migration_kurulumunu_yap(proje_koku: Path) -> None:
    """
    Migration kurulumu adımını gerçekleştir
    
    Args:
        proje_koku: Proje kök dizini
        
    Raises:
        MigrationHatasi: Migration işlemi başarısızsa
    """
    try:
        logger.info("=== ADIM 4: Alembic Migration'ları Çalıştırma ===")
        
        # Migration'ları çalıştır
        gocleri_calistir(proje_koku)
        
        logger.info("✓ Migration'lar başarıyla tamamlandı")
        
    except Exception as e:
        if isinstance(e, MigrationHatasi):
            raise
        raise MigrationHatasi(f"Migration kurulumu hatası: {e}")


def admin_kurulumunu_yap(ayarlar: Dict[str, Any]) -> None:
    """
    Admin kullanıcı kurulumu adımını gerçekleştir
    
    Args:
        ayarlar: Uygulama ayarları
        
    Raises:
        KullaniciHatasi: Admin kullanıcı oluşturma başarısızsa
    """
    try:
        logger.info("=== ADIM 5: Varsayılan Admin Kullanıcı Oluşturma ===")
        
        if not SQLALCHEMY_AVAILABLE:
            raise KullaniciHatasi("SQLAlchemy bulunamadı")
        
        veritabani_url = ayarlar.get("veritabani_url")
        if not veritabani_url:
            raise KullaniciHatasi("Ayarlarda veritabanı URL'i bulunamadı")
        
        # Veritabanı session'ı oluştur
        engine = create_engine(veritabani_url)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Admin kullanıcısını oluştur (idempotent)
            admin_olustur(
                session, 
                VARSAYILAN_ADMIN_KULLANICI, 
                VARSAYILAN_ADMIN_SIFRE
            )
        
        logger.info("✓ Admin kullanıcı kurulumu tamamlandı")
        
    except Exception as e:
        if isinstance(e, KullaniciHatasi):
            raise
        raise KullaniciHatasi(f"Admin kurulumu hatası: {e}")


def ilk_calistirma_hazirla(proje_koku: Path, ozel_ayarlar: Optional[Dict[str, Any]] = None) -> None:
    """
    İlk çalıştırma için tüm hazırlık işlemlerini gerçekleştir
    
    Bu fonksiyon tüm kurulum adımlarını sırasıyla çalıştırır:
    1. Klasör yapısı oluşturma
    2. Ayar dosyası oluşturma  
    3. Veritabanı bağlantı testi
    4. Alembic migration'ları çalıştırma
    5. Varsayılan admin kullanıcı oluşturma
    
    Args:
        proje_koku: Proje kök dizini
        ozel_ayarlar: Özel ayarlar (opsiyonel)
        
    Raises:
        KurulumHatasi: Herhangi bir kurulum adımı başarısızsa
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        logger.info("=" * 60)
        logger.info("SONTECHSP İLK ÇALIŞTIRMA HAZIRLIĞI BAŞLADI")
        logger.info("=" * 60)
        
        # Mevcut durumu kontrol et ve raporla
        durum = kurulum_durumunu_kontrol_et(proje_koku)
        logger.info(f"Mevcut durum: {durum}")
        
        # ADIM 1: Klasör yapısı oluşturma
        klasor_kurulumunu_yap(proje_koku)
        
        # ADIM 2: Ayar dosyası oluşturma
        ayarlar = ayar_kurulumunu_yap(proje_koku, ozel_ayarlar)
        
        # ADIM 3: Veritabanı bağlantı testi
        veritabani_kurulumunu_yap(ayarlar)
        
        # ADIM 4: Migration'ları çalıştırma
        migration_kurulumunu_yap(proje_koku)
        
        # ADIM 5: Admin kullanıcı oluşturma
        admin_kurulumunu_yap(ayarlar)
        
        # Başarı mesajı
        logger.info("=" * 60)
        logger.info("✓ KURULUM TAMAM - SİSTEM KULLANIMA HAZIR")
        logger.info("=" * 60)
        logger.info(f"Proje dizini: {proje_koku.absolute()}")
        logger.info(f"Ayar dosyası: {proje_koku / 'config.json'}")
        logger.info(f"Admin kullanıcı: {VARSAYILAN_ADMIN_KULLANICI}")
        logger.info(f"Admin şifre: {VARSAYILAN_ADMIN_SIFRE}")
        logger.info("Güvenlik için admin şifresini değiştirmeyi unutmayın!")
        
    except (KlasorHatasi, AyarHatasi, DogrulamaHatasi, MigrationHatasi, KullaniciHatasi) as e:
        error_msg = f"Kurulum hatası - {type(e).__name__}: {e}"
        logger.error(error_msg)
        raise KurulumHatasi(error_msg)
    
    except Exception as e:
        error_msg = f"Beklenmeyen kurulum hatası: {e}"
        logger.error(error_msg)
        raise KurulumHatasi(error_msg)


def kurulum_durumu_raporu(proje_koku: Path) -> str:
    """
    Kurulum durumu raporu oluştur
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        str: Kurulum durum raporu
    """
    try:
        # Proje kök dizinini Path nesnesine çevir
        if isinstance(proje_koku, str):
            proje_koku = Path(proje_koku)
        
        durum = kurulum_durumunu_kontrol_et(proje_koku)
        
        rapor = []
        rapor.append("SONTECHSP KURULUM DURUM RAPORU")
        rapor.append("=" * 40)
        rapor.append(f"Proje dizini: {proje_koku.absolute()}")
        rapor.append("")
        
        # Klasörler
        if durum["klasorler_mevcut"]:
            rapor.append("✓ Klasör yapısı: TAMAM")
        else:
            eksik = eksik_klasorleri_listele(proje_koku)
            rapor.append(f"✗ Klasör yapısı: EKSİK ({', '.join(eksik)})")
        
        # Ayar dosyası
        if durum["ayar_dosyasi_mevcut"]:
            rapor.append("✓ Ayar dosyası: TAMAM")
        else:
            rapor.append("✗ Ayar dosyası: EKSİK")
        
        # Veritabanı
        if durum["veritabani_baglantisi"]:
            rapor.append("✓ Veritabanı bağlantısı: TAMAM")
        else:
            rapor.append("✗ Veritabanı bağlantısı: BAŞARISIZ")
        
        # Admin kullanıcı
        if durum["admin_kullanici_mevcut"]:
            rapor.append("✓ Admin kullanıcı: TAMAM")
        else:
            rapor.append("✗ Admin kullanıcı: EKSİK")
        
        # Genel durum
        rapor.append("")
        tamamlanan = sum(durum.values())
        toplam = len(durum)
        
        if tamamlanan == toplam:
            rapor.append("🎉 SİSTEM TAMAMEN HAZIR")
        else:
            rapor.append(f"⚠️  KURULUM GEREKLİ ({tamamlanan}/{toplam} adım tamamlandı)")
            rapor.append("Eksik adımları tamamlamak için ilk_calistirma_hazirla() çalıştırın")
        
        return "\n".join(rapor)
        
    except Exception as e:
        return f"Durum raporu oluşturma hatası: {e}"


def hizli_kurulum_kontrol(proje_koku: Path) -> bool:
    """
    Hızlı kurulum kontrolü - sistem hazır mı?
    
    Args:
        proje_koku: Proje kök dizini
        
    Returns:
        bool: Sistem tamamen hazırsa True
    """
    try:
        durum = kurulum_durumunu_kontrol_et(proje_koku)
        return all(durum.values())
    except Exception:
        return False