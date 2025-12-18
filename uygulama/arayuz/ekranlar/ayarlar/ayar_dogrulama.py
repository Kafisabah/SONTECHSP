# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ayarlar.ayar_dogrulama
# Description: Ayarlar ekranı doğrulama fonksiyonları
# Changelog:
# - İlk sürüm oluşturuldu

import re
from typing import Dict, List, Tuple, Any, Optional


class AyarDogrulama:
    """Ayarlar ekranı doğrulama sınıfı"""
    
    def __init__(self):
        self.hatalar = []
    
    def tum_ayarlari_dogrula(self, ayar_verileri: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Tüm ayarları doğrula"""
        self.hatalar.clear()
        
        # Şirket bilgileri doğrulama
        if 'sirket_adi' in ayar_verileri:
            self.sirket_adi_dogrula(ayar_verileri['sirket_adi'])
        
        if 'vergi_no' in ayar_verileri:
            self.vergi_no_dogrula(ayar_verileri['vergi_no'])
        
        if 'adres' in ayar_verileri:
            self.adres_dogrula(ayar_verileri['adres'])
        
        # Veritabanı ayarları doğrulama
        if 'db_host' in ayar_verileri:
            self.db_host_dogrula(ayar_verileri['db_host'])
        
        if 'db_port' in ayar_verileri:
            self.db_port_dogrula(ayar_verileri['db_port'])
        
        if 'db_name' in ayar_verileri:
            self.db_name_dogrula(ayar_verileri['db_name'])
        
        if 'db_user' in ayar_verileri:
            self.db_user_dogrula(ayar_verileri['db_user'])
        
        if 'db_password' in ayar_verileri:
            self.db_password_dogrula(ayar_verileri['db_password'])
        
        # Performans ayarları doğrulama
        if 'baglanti_havuzu' in ayar_verileri:
            self.baglanti_havuzu_dogrula(ayar_verileri['baglanti_havuzu'])
        
        if 'sorgu_timeout' in ayar_verileri:
            self.sorgu_timeout_dogrula(ayar_verileri['sorgu_timeout'])
        
        # Güvenlik ayarları doğrulama
        if 'sifre_uzunlugu' in ayar_verileri:
            self.sifre_uzunlugu_dogrula(ayar_verileri['sifre_uzunlugu'])
        
        if 'oturum_suresi' in ayar_verileri:
            self.oturum_suresi_dogrula(ayar_verileri['oturum_suresi'])
        
        # Stok ayarları doğrulama
        if 'kritik_stok_seviye' in ayar_verileri:
            self.kritik_stok_seviye_dogrula(ayar_verileri['kritik_stok_seviye'])
        
        # E-ticaret ayarları doğrulama
        if 'siparis_cekme_araligi' in ayar_verileri:
            self.siparis_cekme_araligi_dogrula(ayar_verileri['siparis_cekme_araligi'])
        
        # E-belge ayarları doğrulama
        if 'gonderim_araligi' in ayar_verileri:
            self.gonderim_araligi_dogrula(ayar_verileri['gonderim_araligi'])
        
        if 'hata_tekrar_deneme' in ayar_verileri:
            self.hata_tekrar_deneme_dogrula(ayar_verileri['hata_tekrar_deneme'])
        
        # Kargo ayarları doğrulama
        if 'durum_sorgula_araligi' in ayar_verileri:
            self.durum_sorgula_araligi_dogrula(ayar_verileri['durum_sorgula_araligi'])
        
        # Sistem ayarları doğrulama
        if 'log_dosya_boyutu' in ayar_verileri:
            self.log_dosya_boyutu_dogrula(ayar_verileri['log_dosya_boyutu'])
        
        # Yedekleme ayarları doğrulama
        if 'yedek_sayisi' in ayar_verileri:
            self.yedek_sayisi_dogrula(ayar_verileri['yedek_sayisi'])
        
        return len(self.hatalar) == 0, self.hatalar.copy()
    
    def sirket_adi_dogrula(self, sirket_adi: str) -> bool:
        """Şirket adı doğrulama"""
        if not sirket_adi or not sirket_adi.strip():
            self.hatalar.append("Şirket adı boş olamaz")
            return False
        
        if len(sirket_adi.strip()) < 2:
            self.hatalar.append("Şirket adı en az 2 karakter olmalıdır")
            return False
        
        if len(sirket_adi.strip()) > 100:
            self.hatalar.append("Şirket adı en fazla 100 karakter olabilir")
            return False
        
        return True
    
    def vergi_no_dogrula(self, vergi_no: str) -> bool:
        """Vergi numarası doğrulama"""
        if not vergi_no or not vergi_no.strip():
            self.hatalar.append("Vergi numarası boş olamaz")
            return False
        
        # Sadece rakam kontrolü
        if not re.match(r'^\d+$', vergi_no.strip()):
            self.hatalar.append("Vergi numarası sadece rakam içermelidir")
            return False
        
        # Türkiye vergi numarası 10 haneli olmalı
        if len(vergi_no.strip()) != 10:
            self.hatalar.append("Vergi numarası 10 haneli olmalıdır")
            return False
        
        return True
    
    def adres_dogrula(self, adres: str) -> bool:
        """Adres doğrulama"""
        if not adres or not adres.strip():
            self.hatalar.append("Adres boş olamaz")
            return False
        
        if len(adres.strip()) < 10:
            self.hatalar.append("Adres en az 10 karakter olmalıdır")
            return False
        
        if len(adres.strip()) > 500:
            self.hatalar.append("Adres en fazla 500 karakter olabilir")
            return False
        
        return True
    
    def db_host_dogrula(self, host: str) -> bool:
        """Veritabanı host doğrulama"""
        if not host or not host.strip():
            self.hatalar.append("Veritabanı host adresi boş olamaz")
            return False
        
        # IP adresi veya domain name kontrolü
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        if host.strip() != "localhost" and not re.match(ip_pattern, host.strip()) and not re.match(domain_pattern, host.strip()):
            self.hatalar.append("Geçersiz host adresi formatı")
            return False
        
        return True
    
    def db_port_dogrula(self, port: int) -> bool:
        """Veritabanı port doğrulama"""
        if port < 1 or port > 65535:
            self.hatalar.append("Port numarası 1-65535 arasında olmalıdır")
            return False
        
        return True
    
    def db_name_dogrula(self, db_name: str) -> bool:
        """Veritabanı adı doğrulama"""
        if not db_name or not db_name.strip():
            self.hatalar.append("Veritabanı adı boş olamaz")
            return False
        
        # PostgreSQL veritabanı adı kuralları
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', db_name.strip()):
            self.hatalar.append("Veritabanı adı harf veya alt çizgi ile başlamalı, sadece harf, rakam ve alt çizgi içermelidir")
            return False
        
        if len(db_name.strip()) > 63:
            self.hatalar.append("Veritabanı adı en fazla 63 karakter olabilir")
            return False
        
        return True
    
    def db_user_dogrula(self, user: str) -> bool:
        """Veritabanı kullanıcı adı doğrulama"""
        if not user or not user.strip():
            self.hatalar.append("Veritabanı kullanıcı adı boş olamaz")
            return False
        
        if len(user.strip()) < 3:
            self.hatalar.append("Kullanıcı adı en az 3 karakter olmalıdır")
            return False
        
        if len(user.strip()) > 63:
            self.hatalar.append("Kullanıcı adı en fazla 63 karakter olabilir")
            return False
        
        return True
    
    def db_password_dogrula(self, password: str) -> bool:
        """Veritabanı şifre doğrulama"""
        if not password:
            self.hatalar.append("Veritabanı şifresi boş olamaz")
            return False
        
        if len(password) < 6:
            self.hatalar.append("Veritabanı şifresi en az 6 karakter olmalıdır")
            return False
        
        return True
    
    def baglanti_havuzu_dogrula(self, havuz_boyutu: int) -> bool:
        """Bağlantı havuzu boyutu doğrulama"""
        if havuz_boyutu < 5:
            self.hatalar.append("Bağlantı havuzu boyutu en az 5 olmalıdır")
            return False
        
        if havuz_boyutu > 100:
            self.hatalar.append("Bağlantı havuzu boyutu en fazla 100 olabilir")
            return False
        
        return True
    
    def sorgu_timeout_dogrula(self, timeout: int) -> bool:
        """Sorgu timeout doğrulama"""
        if timeout < 5:
            self.hatalar.append("Sorgu timeout en az 5 saniye olmalıdır")
            return False
        
        if timeout > 300:
            self.hatalar.append("Sorgu timeout en fazla 300 saniye olabilir")
            return False
        
        return True
    
    def sifre_uzunlugu_dogrula(self, uzunluk: int) -> bool:
        """Şifre uzunluğu doğrulama"""
        if uzunluk < 4:
            self.hatalar.append("Minimum şifre uzunluğu en az 4 karakter olmalıdır")
            return False
        
        if uzunluk > 20:
            self.hatalar.append("Minimum şifre uzunluğu en fazla 20 karakter olabilir")
            return False
        
        return True
    
    def oturum_suresi_dogrula(self, sure: int) -> bool:
        """Oturum süresi doğrulama"""
        if sure < 30:
            self.hatalar.append("Oturum süresi en az 30 dakika olmalıdır")
            return False
        
        if sure > 1440:  # 24 saat
            self.hatalar.append("Oturum süresi en fazla 1440 dakika (24 saat) olabilir")
            return False
        
        return True
    
    def kritik_stok_seviye_dogrula(self, seviye: int) -> bool:
        """Kritik stok seviyesi doğrulama"""
        if seviye < 0:
            self.hatalar.append("Kritik stok seviyesi negatif olamaz")
            return False
        
        if seviye > 1000:
            self.hatalar.append("Kritik stok seviyesi en fazla 1000 olabilir")
            return False
        
        return True
    
    def siparis_cekme_araligi_dogrula(self, aralik: int) -> bool:
        """Sipariş çekme aralığı doğrulama"""
        if aralik < 5:
            self.hatalar.append("Sipariş çekme aralığı en az 5 dakika olmalıdır")
            return False
        
        if aralik > 1440:  # 24 saat
            self.hatalar.append("Sipariş çekme aralığı en fazla 1440 dakika olabilir")
            return False
        
        return True
    
    def gonderim_araligi_dogrula(self, aralik: int) -> bool:
        """E-belge gönderim aralığı doğrulama"""
        if aralik < 1:
            self.hatalar.append("E-belge gönderim aralığı en az 1 dakika olmalıdır")
            return False
        
        if aralik > 60:
            self.hatalar.append("E-belge gönderim aralığı en fazla 60 dakika olabilir")
            return False
        
        return True
    
    def hata_tekrar_deneme_dogrula(self, deneme: int) -> bool:
        """Hata tekrar deneme sayısı doğrulama"""
        if deneme < 1:
            self.hatalar.append("Hata tekrar deneme sayısı en az 1 olmalıdır")
            return False
        
        if deneme > 10:
            self.hatalar.append("Hata tekrar deneme sayısı en fazla 10 olabilir")
            return False
        
        return True
    
    def durum_sorgula_araligi_dogrula(self, aralik: int) -> bool:
        """Kargo durum sorgulama aralığı doğrulama"""
        if aralik < 30:
            self.hatalar.append("Durum sorgulama aralığı en az 30 dakika olmalıdır")
            return False
        
        if aralik > 1440:  # 24 saat
            self.hatalar.append("Durum sorgulama aralığı en fazla 1440 dakika olabilir")
            return False
        
        return True
    
    def log_dosya_boyutu_dogrula(self, boyut: int) -> bool:
        """Log dosya boyutu doğrulama"""
        if boyut < 1:
            self.hatalar.append("Log dosya boyutu en az 1 MB olmalıdır")
            return False
        
        if boyut > 100:
            self.hatalar.append("Log dosya boyutu en fazla 100 MB olabilir")
            return False
        
        return True
    
    def yedek_sayisi_dogrula(self, sayi: int) -> bool:
        """Yedek sayısı doğrulama"""
        if sayi < 1:
            self.hatalar.append("Saklanacak yedek sayısı en az 1 olmalıdır")
            return False
        
        if sayi > 30:
            self.hatalar.append("Saklanacak yedek sayısı en fazla 30 olabilir")
            return False
        
        return True
    
    def email_dogrula(self, email: str) -> bool:
        """E-posta adresi doğrulama"""
        if not email or not email.strip():
            return True  # E-posta opsiyonel olabilir
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email.strip()):
            self.hatalar.append("Geçersiz e-posta adresi formatı")
            return False
        
        return True
    
    def telefon_dogrula(self, telefon: str) -> bool:
        """Telefon numarası doğrulama"""
        if not telefon or not telefon.strip():
            return True  # Telefon opsiyonel olabilir
        
        # Türkiye telefon numarası formatı
        telefon_temiz = re.sub(r'[^\d]', '', telefon)
        
        if len(telefon_temiz) == 11 and telefon_temiz.startswith('0'):
            return True
        elif len(telefon_temiz) == 10 and not telefon_temiz.startswith('0'):
            return True
        else:
            self.hatalar.append("Geçersiz telefon numarası formatı (0XXX XXX XX XX)")
            return False
    
    def url_dogrula(self, url: str) -> bool:
        """URL doğrulama"""
        if not url or not url.strip():
            return True  # URL opsiyonel olabilir
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url.strip()):
            self.hatalar.append("Geçersiz URL formatı")
            return False
        
        return True
    
    def pozitif_sayi_dogrula(self, sayi: Any, alan_adi: str, min_deger: int = 0, max_deger: int = None) -> bool:
        """Pozitif sayı doğrulama"""
        try:
            sayi_int = int(sayi)
        except (ValueError, TypeError):
            self.hatalar.append(f"{alan_adi} geçerli bir sayı olmalıdır")
            return False
        
        if sayi_int < min_deger:
            self.hatalar.append(f"{alan_adi} en az {min_deger} olmalıdır")
            return False
        
        if max_deger is not None and sayi_int > max_deger:
            self.hatalar.append(f"{alan_adi} en fazla {max_deger} olabilir")
            return False
        
        return True
    
    def metin_uzunlugu_dogrula(self, metin: str, alan_adi: str, min_uzunluk: int = 0, max_uzunluk: int = None) -> bool:
        """Metin uzunluğu doğrulama"""
        if not metin:
            metin = ""
        
        if len(metin.strip()) < min_uzunluk:
            self.hatalar.append(f"{alan_adi} en az {min_uzunluk} karakter olmalıdır")
            return False
        
        if max_uzunluk is not None and len(metin.strip()) > max_uzunluk:
            self.hatalar.append(f"{alan_adi} en fazla {max_uzunluk} karakter olabilir")
            return False
        
        return True
    
    def zorunlu_alan_dogrula(self, deger: Any, alan_adi: str) -> bool:
        """Zorunlu alan doğrulama"""
        if deger is None or (isinstance(deger, str) and not deger.strip()):
            self.hatalar.append(f"{alan_adi} zorunlu bir alandır")
            return False
        
        return True