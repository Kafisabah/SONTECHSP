# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge.hatalar
# Description: E-belge modülü özel hata sınıfları
# Changelog:
# - İlk versiyon: Hata sınıfları oluşturuldu


class EBelgeHatasiBase(Exception):
    """E-belge modülü temel hata sınıfı"""
    pass


class EntegrasyonHatasi(EBelgeHatasiBase):
    """Entegrasyon işlemlerinde oluşan hatalar"""
    pass


class BaglantiHatasi(EBelgeHatasiBase):
    """Bağlantı ve network hatalarında oluşan hatalar"""
    pass


class DogrulamaHatasi(EBelgeHatasiBase):
    """Veri doğrulama hatalarında oluşan hatalar"""
    pass


class KonfigurasyonHatasi(EBelgeHatasiBase):
    """Konfigürasyon hatalarında oluşan hatalar"""
    pass


class JSONHatasi(EBelgeHatasiBase):
    """JSON işleme hatalarında oluşan hatalar"""
    pass