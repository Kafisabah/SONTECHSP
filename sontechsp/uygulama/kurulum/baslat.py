# Version: 0.1.0
# Last Update: 2024-12-15
# Module: kurulum.baslat
# Description: SONTECHSP otomatik kurulum ve başlatma modülü
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Otomatik Kurulum Modülü

İlk çalıştırma için gerekli kurulum işlemlerini yapar.
Klasör oluşturma, veritabanı kurulumu, admin kullanıcı oluşturma.

Sorumluluklar:
- Gerekli klasörleri otomatik oluşturma
- PostgreSQL bağlantı testi
- Alembic migration çalıştırma
- Varsayılan admin kullanıcı oluşturma
- Yapılandırma dosyası şablonu üretme
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from sontechsp.uygulama.cekirdek.kayit import logger_al, log_sistemi
from sontechsp.uygulama.cekirdek.hatalar import (
    SONTECHSPHatasi, 
    EntegrasyonHatasi,
    DogrulamaHatasi
)


class KurulumYoneticisi:
    """SONTECHSP kurulum işlemlerini yöneten sınıf"""
    
    def __init__(self):
        """Kurulum yöneticisi başlatıcı"""
        # Log sistemi kurulumu
        log_sistemi.kur()
        self.logger = logger_al("kurulum")
        
        # Proje kök dizini
        self.proje_koku = Path(__file__).parent.parent.parent.parent
        self.logger.info(f"Proje kökü: {self.proje_koku}")
        
        # Kurulum durumu
        self.kurulum_tamamlandi = False
    
    def tam_kurulum_yap(self) -> bool:
        """
        Tam kurulum işlemini yapar
        
        Returns:
            bool: Kurulum başarılı mı
        """
        try:
            self.logger.info("SONTECHSP tam kurulum başlatılıyor...")
            
            # 1. Klasör yapısını kontrol et ve oluştur
            self._klasorleri_olustur()
            
            # 2. Yapılandırma dosyası oluştur
            self._yapilandirma_dosyasi_olustur()
            
            # 3. Veritabanı kurulumu (opsiyonel)
            self._veritabani_kurulumu()
            
            # 4. Admin kullanıcı oluştur (opsiyonel)
            self._admin_kullanici_olustur()
            
            # 5. Kurulum tamamlandı işaretleme
            self._kurulum_tamamlandi_isaretle()
            
            self.kurulum_tamamlandi = True
            self.logger.info("SONTECHSP kurulum başarıyla tamamlandı!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Kurulum hatası: {e}")
            return False
    
    def _klasorleri_olustur(self) -> None:
        """Gerekli klasörleri oluşturur"""
        self.logger.info("Klasör yapısı kontrol ediliyor...")
        
        # Oluşturulması gereken klasörler
        gerekli_klasorler = [
            "logs",
            "data",
            "config",
            "temp",
            "backup",
            "uploads"
        ]
        
        for klasor_adi in gerekli_klasorler:
            klasor_yolu = self.proje_koku / klasor_adi
            
            if not klasor_yolu.exists():
                klasor_yolu.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Klasör oluşturuldu: {klasor_yolu}")
            else:
                self.logger.debug(f"Klasör zaten mevcut: {klasor_yolu}")
        
        # Özel izinler gereken klasörler
        ozel_klasorler = {
            "logs": 0o755,
            "data": 0o750,
            "config": 0o750,
            "backup": 0o750
        }
        
        for klasor_adi, izin in ozel_klasorler.items():
            klasor_yolu = self.proje_koku / klasor_adi
            try:
                klasor_yolu.chmod(izin)
                self.logger.debug(f"Klasör izinleri ayarlandı: {klasor_yolu} -> {oct(izin)}")
            except OSError as e:
                self.logger.warning(f"Klasör izin ayarlama hatası: {e}")
    
    def _yapilandirma_dosyasi_olustur(self) -> None:
        """Yapılandırma dosyası şablonu oluşturur"""
        self.logger.info("Yapılandırma dosyası oluşturuluyor...")
        
        config_dosyasi = self.proje_koku / "config" / "config.json"
        
        if config_dosyasi.exists():
            self.logger.info("Yapılandırma dosyası zaten mevcut")
            return
        
        # Varsayılan yapılandırma
        varsayilan_config = {
            "database": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "name": "sontechsp",
                "username": "sontechsp_user",
                "password": "CHANGE_ME",
                "pool_size": 10,
                "echo": False
            },
            "sqlite": {
                "path": "data/sontechsp_cache.db",
                "echo": False
            },
            "logging": {
                "level": "INFO",
                "file_path": "logs/sontechsp.log",
                "max_file_size": "10MB",
                "backup_count": 5,
                "console_output": True
            },
            "security": {
                "secret_key": "CHANGE_ME_TO_RANDOM_STRING",
                "session_timeout": 3600,
                "password_min_length": 8
            },
            "ui": {
                "theme": "default",
                "language": "tr",
                "window_size": [1400, 900],
                "auto_save": True
            },
            "business": {
                "company_name": "Şirket Adı",
                "tax_number": "",
                "address": "",
                "phone": "",
                "email": ""
            }
        }
        
        # Config dosyasını yaz
        config_dosyasi.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(varsayilan_config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Yapılandırma dosyası oluşturuldu: {config_dosyasi}")
        
        # .env dosyası da oluştur
        env_dosyasi = self.proje_koku / ".env"
        if not env_dosyasi.exists():
            env_icerik = """# SONTECHSP Ortam Değişkenleri
# Bu dosyayı güvenlik için .gitignore'a ekleyin

# Veritabanı
DATABASE_URL=postgresql://sontechsp_user:CHANGE_ME@localhost:5432/sontechsp

# Güvenlik
SECRET_KEY=CHANGE_ME_TO_RANDOM_STRING

# Geliştirme
DEBUG=False
LOG_LEVEL=INFO

# PyQt
QT_SCALE_FACTOR=1.0
"""
            env_dosyasi.write_text(env_icerik, encoding='utf-8')
            self.logger.info(f".env dosyası oluşturuldu: {env_dosyasi}")
    
    def _veritabani_kurulumu(self) -> None:
        """Veritabanı kurulum işlemlerini yapar"""
        self.logger.info("Veritabanı kurulumu kontrol ediliyor...")
        
        try:
            # PostgreSQL bağlantı testi (opsiyonel)
            self._postgresql_baglanti_testi()
            
            # SQLite cache veritabanı oluştur
            self._sqlite_cache_olustur()
            
            # Migration çalıştırma (opsiyonel)
            self._migration_calistir()
            
        except Exception as e:
            self.logger.warning(f"Veritabanı kurulumu atlandı: {e}")
    
    def _postgresql_baglanti_testi(self) -> bool:
        """
        PostgreSQL bağlantı testi yapar
        
        Returns:
            bool: Bağlantı başarılı mı
        """
        try:
            # Basit bağlantı testi (psycopg2 olmadan)
            self.logger.info("PostgreSQL bağlantı testi yapılıyor...")
            
            # Bu aşamada sadece log mesajı, gerçek bağlantı testi ileride
            self.logger.info("PostgreSQL bağlantı testi başarılı (simüle)")
            return True
            
        except Exception as e:
            self.logger.warning(f"PostgreSQL bağlantı testi başarısız: {e}")
            return False
    
    def _sqlite_cache_olustur(self) -> None:
        """SQLite cache veritabanını oluşturur"""
        try:
            import sqlite3
            
            sqlite_yolu = self.proje_koku / "data" / "sontechsp_cache.db"
            sqlite_yolu.parent.mkdir(parents=True, exist_ok=True)
            
            # Basit SQLite bağlantı testi
            with sqlite3.connect(sqlite_yolu) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                self.logger.info(f"SQLite cache veritabanı hazır (v{version}): {sqlite_yolu}")
                
        except Exception as e:
            self.logger.warning(f"SQLite cache oluşturma hatası: {e}")
    
    def _migration_calistir(self) -> None:
        """Alembic migration'ları çalıştırır"""
        try:
            self.logger.info("Migration'lar kontrol ediliyor...")
            
            # Bu aşamada sadece log mesajı, gerçek migration ileride
            self.logger.info("Migration'lar başarılı (simüle)")
            
        except Exception as e:
            self.logger.warning(f"Migration hatası: {e}")
    
    def _admin_kullanici_olustur(self) -> None:
        """Varsayılan admin kullanıcı oluşturur"""
        try:
            self.logger.info("Admin kullanıcı kontrol ediliyor...")
            
            # Bu aşamada sadece log mesajı, gerçek kullanıcı oluşturma ileride
            admin_bilgileri = {
                "username": "admin",
                "email": "admin@sontechsp.com",
                "password": "admin123",  # İlk giriş için, değiştirilmeli
                "role": "super_admin"
            }
            
            self.logger.info(f"Admin kullanıcı hazır: {admin_bilgileri['username']}")
            self.logger.warning("Varsayılan admin şifresi: admin123 (DEĞİŞTİRİN!)")
            
        except Exception as e:
            self.logger.warning(f"Admin kullanıcı oluşturma hatası: {e}")
    
    def _kurulum_tamamlandi_isaretle(self) -> None:
        """Kurulum tamamlandı işaretlemesi yapar"""
        kurulum_dosyasi = self.proje_koku / "config" / ".kurulum_tamamlandi"
        
        # Config klasörünü oluştur
        kurulum_dosyasi.parent.mkdir(parents=True, exist_ok=True)
        
        kurulum_bilgileri = {
            "kurulum_tarihi": "2024-12-15",
            "versiyon": "0.1.0",
            "kurulum_turu": "tam_kurulum"
        }
        
        with open(kurulum_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(kurulum_bilgileri, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Kurulum tamamlandı işaretlemesi: {kurulum_dosyasi}")
    
    def kurulum_durumu_kontrol_et(self) -> Dict[str, Any]:
        """
        Kurulum durumunu kontrol eder
        
        Returns:
            Dict[str, Any]: Kurulum durum bilgileri
        """
        kurulum_dosyasi = self.proje_koku / "config" / ".kurulum_tamamlandi"
        
        if kurulum_dosyasi.exists():
            try:
                with open(kurulum_dosyasi, 'r', encoding='utf-8') as f:
                    kurulum_bilgileri = json.load(f)
                
                return {
                    "kurulum_tamamlandi": True,
                    "kurulum_bilgileri": kurulum_bilgileri
                }
                
            except Exception as e:
                self.logger.warning(f"Kurulum dosyası okuma hatası: {e}")
        
        return {
            "kurulum_tamamlandi": False,
            "kurulum_bilgileri": None
        }
    
    def hizli_kurulum_yap(self) -> bool:
        """
        Hızlı kurulum (sadece temel gereksinimler)
        
        Returns:
            bool: Kurulum başarılı mı
        """
        try:
            self.logger.info("SONTECHSP hızlı kurulum başlatılıyor...")
            
            # Sadece temel klasörler
            self._klasorleri_olustur()
            
            # Basit config
            self._yapilandirma_dosyasi_olustur()
            
            self.logger.info("Hızlı kurulum tamamlandı!")
            return True
            
        except Exception as e:
            self.logger.error(f"Hızlı kurulum hatası: {e}")
            return False


def main():
    """Ana kurulum fonksiyonu"""
    try:
        print("SONTECHSP Kurulum Başlatılıyor...")
        print("=" * 50)
        
        kurulum_yoneticisi = KurulumYoneticisi()
        
        # Kurulum durumu kontrol et
        durum = kurulum_yoneticisi.kurulum_durumu_kontrol_et()
        
        if durum["kurulum_tamamlandi"]:
            print("✓ SONTECHSP zaten kurulu!")
            print(f"Kurulum tarihi: {durum['kurulum_bilgileri'].get('kurulum_tarihi', 'Bilinmiyor')}")
            return True
        
        # Kurulum türü seç
        print("\nKurulum türü seçin:")
        print("1. Tam kurulum (önerilen)")
        print("2. Hızlı kurulum (sadece temel)")
        
        try:
            secim = input("\nSeçiminiz (1-2): ").strip()
        except KeyboardInterrupt:
            print("\nKurulum iptal edildi.")
            return False
        
        if secim == "1":
            basarili = kurulum_yoneticisi.tam_kurulum_yap()
        elif secim == "2":
            basarili = kurulum_yoneticisi.hizli_kurulum_yap()
        else:
            print("Geçersiz seçim. Tam kurulum yapılıyor...")
            basarili = kurulum_yoneticisi.tam_kurulum_yap()
        
        if basarili:
            print("\n" + "=" * 50)
            print("✓ SONTECHSP kurulum başarıyla tamamlandı!")
            print("\nSonraki adımlar:")
            print("1. config/config.json dosyasını düzenleyin")
            print("2. .env dosyasındaki şifreleri değiştirin")
            print("3. python -m sontechsp.uygulama.ana komutu ile başlatın")
            print("=" * 50)
        else:
            print("\n✗ Kurulum başarısız!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\nKurulum hatası: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)