# Version: 0.1.0
# Last Update: 2024-12-19
# Module: dialoglar
# Description: POS dialog'ları modülü
# Changelog:
# - İlk oluşturma

"""
POS Dialog'ları - POS ekranları için dialog bileşenleri
"""

from .parcali_odeme_dialog import ParcaliOdemeDialog
from .indirim_dialog import IndirimDialog
from .musteri_sec_dialog import MusteriSecDialog

__all__ = ["ParcaliOdemeDialog", "IndirimDialog", "MusteriSecDialog"]

__version__ = "0.1.0"
