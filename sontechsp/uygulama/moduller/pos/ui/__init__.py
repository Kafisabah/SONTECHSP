# Version: 0.1.0
# Last Update: 2024-12-18
# Module: pos.ui
# Description: POS UI katmanı - PyQt6 arayüz bileşenleri
# Changelog:
# - İlk oluşturma
# - POS ana ekran ve altyapı eklendi

"""
POS UI Katmanı

Bu modül POS sisteminin kullanıcı arayüzü bileşenlerini içerir.
Sadece Service katmanını çağırır, doğrudan Repository veya Database erişimi yasaktır.
"""

from .pos_ana_ekran import POSAnaEkran
from .bilesenler import POSBilesenArayuzu
from .handlers import POSSinyalleri, KlavyeKisayolYoneticisi

__all__ = [
    "POSAnaEkran",
    "POSBilesenArayuzu",
    "POSSinyalleri",
    "KlavyeKisayolYoneticisi",
]
