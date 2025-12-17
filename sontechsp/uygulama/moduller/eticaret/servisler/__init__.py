# Version: 0.2.0
# Last Update: 2024-12-17
# Module: eticaret.servisler
# Description: E-ticaret servis katmanı
# Changelog:
# - İlk oluşturma
# - EticaretServisi eklendi

"""
E-ticaret servis katmanı

Servis sınıfları:
- EticaretServisi: Ana e-ticaret iş mantığı
"""

from .eticaret_servisi import EticaretServisi

__all__ = ["EticaretServisi"]