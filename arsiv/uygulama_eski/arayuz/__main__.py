# Version: 1.0.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.__main__
# Description: Modül giriş noktası - python -m uygulama.arayuz desteği
# Changelog:
# - İlk sürüm oluşturuldu

import sys
from .smoke_test_calistir import main

if __name__ == "__main__":
    sys.exit(main())
