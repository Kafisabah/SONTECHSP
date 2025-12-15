# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.firma_magaza
# Description: SONTECHSP firma ve mağaza modelleri import
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Firma ve Mağaza Modelleri Import

Bu modül firma ve mağaza modellerini import eder.
Geriye uyumluluk için mevcut.
"""

from .firma import Firma
from .magaza import Magaza, Terminal, Depo

__all__ = ['Firma', 'Magaza', 'Terminal', 'Depo']