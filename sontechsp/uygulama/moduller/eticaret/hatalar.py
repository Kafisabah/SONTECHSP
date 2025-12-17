# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.hatalar
# Description: E-ticaret entegrasyonu için özel hata sınıfları
# Changelog:
# - İlk oluşturma
# - EntegrasyonHatasi hiyerarşisi eklendi

"""
E-ticaret entegrasyonu için özel hata sınıfları.
Tüm entegrasyon hataları standartlaştırılmış hiyerarşi kullanır.
"""


class EntegrasyonHatasi(Exception):
    """Entegrasyon hataları için temel istisna sınıfı"""
    
    def __init__(self, mesaj: str, detay: str = None, hata_kodu: str = None):
        self.mesaj = mesaj
        self.detay = detay
        self.hata_kodu = hata_kodu
        super().__init__(mesaj)
    
    def __str__(self):
        if self.detay:
            return f"{self.mesaj} - Detay: {self.detay}"
        return self.mesaj


class BaglantiHatasi(EntegrasyonHatasi):
    """Bağlantı ile ilgili hatalar"""
    pass


class VeriDogrulamaHatasi(EntegrasyonHatasi):
    """Veri doğrulama hataları"""
    pass


class PlatformHatasi(EntegrasyonHatasi):
    """Platform-spesifik hatalar"""
    
    def __init__(self, mesaj: str, platform: str, detay: str = None, hata_kodu: str = None):
        self.platform = platform
        super().__init__(mesaj, detay, hata_kodu)
    
    def __str__(self):
        base_msg = f"[{self.platform}] {self.mesaj}"
        if self.detay:
            return f"{base_msg} - Detay: {self.detay}"
        return base_msg


class JobHatasi(EntegrasyonHatasi):
    """İş kuyruğu ile ilgili hatalar"""
    
    def __init__(self, mesaj: str, job_id: int = None, job_turu: str = None, detay: str = None):
        self.job_id = job_id
        self.job_turu = job_turu
        super().__init__(mesaj, detay)
    
    def __str__(self):
        base_msg = self.mesaj
        if self.job_turu:
            base_msg = f"[{self.job_turu}] {base_msg}"
        if self.job_id:
            base_msg = f"Job#{self.job_id} {base_msg}"
        if self.detay:
            return f"{base_msg} - Detay: {self.detay}"
        return base_msg