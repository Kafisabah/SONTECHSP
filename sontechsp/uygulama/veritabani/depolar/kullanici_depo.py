# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.kullanici_depo
# Description: SONTECHSP kullanıcı repository sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Kullanıcı Repository Sınıfları

Bu modül kullanıcı, rol ve yetki yönetimi için repository sınıflarını içerir.
"""

from typing import Optional
from sqlalchemy.orm import Session

from .taban import TemelDepo
from ..modeller.kullanici_yetki import Kullanici, Rol, Yetki


class KullaniciDepo(TemelDepo[Kullanici]):
    """Kullanıcı repository sınıfı"""
    
    def __init__(self):
        super().__init__(Kullanici)
    
    def kullanici_adi_ile_getir(self, session: Session, kullanici_adi: str) -> Optional[Kullanici]:
        """Kullanıcı adı ile kullanıcı getir"""
        return session.query(self.model).filter(
            self.model.kullanici_adi == kullanici_adi
        ).first()


class RolDepo(TemelDepo[Rol]):
    """Rol repository sınıfı"""
    
    def __init__(self):
        super().__init__(Rol)


class YetkiDepo(TemelDepo[Yetki]):
    """Yetki repository sınıfı"""
    
    def __init__(self):
        super().__init__(Yetki)