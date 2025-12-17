# Version: 0.2.0
# Last Update: 2024-12-17
# Module: eticaret.depolar
# Description: E-ticaret depolar modülü
# Changelog:
# - İlk oluşturma
# - EticaretDeposu ve JobDeposu eklendi

"""
E-ticaret depolar modülü

Repository sınıfları:
- EticaretDeposu: Mağaza hesapları ve siparişler
- JobDeposu: Asenkron iş kuyruğu yönetimi
"""

from .eticaret_deposu import EticaretDeposu
from .job_deposu import JobDeposu

__all__ = ["EticaretDeposu", "JobDeposu"]