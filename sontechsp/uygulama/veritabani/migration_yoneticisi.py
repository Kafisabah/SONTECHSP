# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.migration_yoneticisi
# Description: SONTECHSP migration yönetim fonksiyonları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Migration Yöneticisi

Bu modül Alembic migration yönetimi için fonksiyonları içerir.
Migration durum sorgulama, geçmiş listeleme ve çakışma kontrolü sağlar.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine

from ..cekirdek.hatalar import MigrationHatasi
from .baglanti import veritabani_baglanti

logger = logging.getLogger(__name__)


class MigrationYoneticisi:
    """SONTECHSP migration yönetim sınıfı"""
    
    def __init__(self, engine: Optional[Engine] = None):
        """Migration yöneticisi başlatma"""
        self.engine = engine or veritabani_baglanti.postgresql_engine_al()
        self.config = self._alembic_config_olustur()
        self.script_dir = ScriptDirectory.from_config(self.config)
    
    def _alembic_config_olustur(self) -> Config:
        """Alembic yapılandırması oluştur"""
        try:
            # Alembic config dosyasının yolunu bul
            current_dir = os.path.dirname(__file__)
            alembic_ini_path = os.path.join(current_dir, '..', '..', '..', 'alembic.ini')
            alembic_ini_path = os.path.abspath(alembic_ini_path)
            
            if not os.path.exists(alembic_ini_path):
                raise MigrationHatasi(f"Alembic config dosyası bulunamadı: {alembic_ini_path}")
            
            # Config oluştur
            config = Config(alembic_ini_path)
            config.set_main_option("sqlalchemy.url", str(self.engine.url))
            
            return config
            
        except Exception as e:
            logger.error(f"Alembic config oluşturma hatası: {e}")
            raise MigrationHatasi(f"Alembic yapılandırması oluşturulamadı: {e}")
    
    def migration_durumu(self) -> Dict[str, Any]:
        """
        Migration durum sorgulama fonksiyonu
        
        Returns:
            Dict: Migration durum bilgileri
        """
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                
                # Script directory'den head revision'ı al
                head_rev = self.script_dir.get_current_head()
                
                # Pending migration'ları bul
                pending_revisions = []
                if current_rev != head_rev:
                    # Mevcut revision'dan head'e kadar olan migration'ları bul
                    for rev in self.script_dir.walk_revisions(head_rev, current_rev):
                        if rev.revision != current_rev:
                            pending_revisions.append({
                                'revision': rev.revision,
                                'description': rev.doc,
                                'down_revision': rev.down_revision
                            })
                
                durum = {
                    'current_revision': current_rev,
                    'head_revision': head_rev,
                    'is_up_to_date': current_rev == head_rev,
                    'pending_migrations': pending_revisions,
                    'pending_count': len(pending_revisions),
                    'query_time': datetime.now().isoformat()
                }
                
                logger.info(f"Migration durumu sorgulandı: {current_rev} -> {head_rev}")
                return durum
                
        except Exception as e:
            logger.error(f"Migration durum sorgulama hatası: {e}")
            raise MigrationHatasi(f"Migration durumu sorgulanamadı: {e}")
    
    def migration_gecmisi(self) -> List[Dict[str, Any]]:
        """
        Migration geçmiş listeleme fonksiyonu
        
        Returns:
            List[Dict]: Uygulanan migration'ların listesi
        """
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                
                gecmis = []
                
                # Mevcut revision'dan başlayarak geçmişe doğru git
                if current_rev:
                    for rev in self.script_dir.walk_revisions("base", current_rev):
                        migration_info = {
                            'revision': rev.revision,
                            'description': rev.doc or 'Açıklama yok',
                            'down_revision': rev.down_revision,
                            'branch_labels': rev.branch_labels,
                            'depends_on': rev.depends_on,
                            'is_applied': True  # Bu revision uygulanmış
                        }
                        gecmis.append(migration_info)
                
                # Kronolojik sırada sırala (en eski önce)
                gecmis.reverse()
                
                logger.info(f"Migration geçmişi listelendi: {len(gecmis)} migration")
                return gecmis
                
        except Exception as e:
            logger.error(f"Migration geçmiş listeleme hatası: {e}")
            raise MigrationHatasi(f"Migration geçmişi listelenemedi: {e}")
    
    def migration_cakisma_kontrolu(self) -> Dict[str, Any]:
        """
        Migration çakışma kontrolü
        
        Returns:
            Dict: Çakışma durumu bilgileri
        """
        try:
            # Head revision'ları kontrol et
            heads = self.script_dir.get_heads()
            
            cakisma_durumu = {
                'has_conflict': len(heads) > 1,
                'head_count': len(heads),
                'heads': heads,
                'conflict_message': None,
                'check_time': datetime.now().isoformat()
            }
            
            if len(heads) > 1:
                cakisma_durumu['conflict_message'] = (
                    f"Birden fazla head revision bulundu: {', '.join(heads)}. "
                    "Migration çakışması var, merge gerekli."
                )
                logger.warning(f"Migration çakışması tespit edildi: {heads}")
            else:
                logger.info("Migration çakışması yok")
            
            return cakisma_durumu
            
        except Exception as e:
            logger.error(f"Migration çakışma kontrolü hatası: {e}")
            raise MigrationHatasi(f"Migration çakışma kontrolü yapılamadı: {e}")
    
    def migration_calistir(self, hedef_versiyon: str = "head") -> Dict[str, Any]:
        """
        Migration çalıştırma fonksiyonu
        
        Args:
            hedef_versiyon: Hedef migration versiyonu (default: "head")
            
        Returns:
            Dict: Migration sonuç bilgileri
        """
        try:
            # Önce durum kontrol et
            onceki_durum = self.migration_durumu()
            
            # Migration'ı çalıştır
            command.upgrade(self.config, hedef_versiyon)
            
            # Sonraki durumu kontrol et
            sonraki_durum = self.migration_durumu()
            
            sonuc = {
                'success': True,
                'previous_revision': onceki_durum['current_revision'],
                'current_revision': sonraki_durum['current_revision'],
                'target_revision': hedef_versiyon,
                'applied_migrations': onceki_durum['pending_count'],
                'execution_time': datetime.now().isoformat()
            }
            
            logger.info(f"Migration başarıyla çalıştırıldı: {onceki_durum['current_revision']} -> {sonraki_durum['current_revision']}")
            return sonuc
            
        except Exception as e:
            logger.error(f"Migration çalıştırma hatası: {e}")
            raise MigrationHatasi(f"Migration çalıştırılamadı: {e}")
    
    def migration_geri_al(self, hedef_versiyon: str) -> Dict[str, Any]:
        """
        Migration geri alma fonksiyonu
        
        Args:
            hedef_versiyon: Geri alınacak hedef versiyon
            
        Returns:
            Dict: Geri alma sonuç bilgileri
        """
        try:
            # Önce durum kontrol et
            onceki_durum = self.migration_durumu()
            
            # Migration'ı geri al
            command.downgrade(self.config, hedef_versiyon)
            
            # Sonraki durumu kontrol et
            sonraki_durum = self.migration_durumu()
            
            sonuc = {
                'success': True,
                'previous_revision': onceki_durum['current_revision'],
                'current_revision': sonraki_durum['current_revision'],
                'target_revision': hedef_versiyon,
                'execution_time': datetime.now().isoformat()
            }
            
            logger.info(f"Migration başarıyla geri alındı: {onceki_durum['current_revision']} -> {sonraki_durum['current_revision']}")
            return sonuc
            
        except Exception as e:
            logger.error(f"Migration geri alma hatası: {e}")
            raise MigrationHatasi(f"Migration geri alınamadı: {e}")


# Global migration yöneticisi instance
migration_yoneticisi = MigrationYoneticisi()

# Kısayol fonksiyonlar
def migration_durumu() -> Dict[str, Any]:
    """Migration durum sorgulama kısayolu"""
    return migration_yoneticisi.migration_durumu()

def migration_gecmisi() -> List[Dict[str, Any]]:
    """Migration geçmiş listeleme kısayolu"""
    return migration_yoneticisi.migration_gecmisi()

def migration_cakisma_kontrolu() -> Dict[str, Any]:
    """Migration çakışma kontrolü kısayolu"""
    return migration_yoneticisi.migration_cakisma_kontrolu()

def migration_calistir(hedef_versiyon: str = "head") -> Dict[str, Any]:
    """Migration çalıştırma kısayolu"""
    return migration_yoneticisi.migration_calistir(hedef_versiyon)

def migration_geri_al(hedef_versiyon: str) -> Dict[str, Any]:
    """Migration geri alma kısayolu"""
    return migration_yoneticisi.migration_geri_al(hedef_versiyon)