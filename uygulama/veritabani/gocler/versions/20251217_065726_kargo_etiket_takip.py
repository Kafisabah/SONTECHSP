# Version: 0.1.0
# Last Update: 2024-12-17
# Module: veritabani.gocler.versions.kargo_etiket_takip
# Description: Kargo etiket ve takip tabloları migration'ı
# Changelog:
# - kargo_etiketleri tablosu oluşturuldu
# - kargo_takipleri tablosu oluşturuldu
# - Foreign key constraint'leri eklendi
# - Index'ler tanımlandı

"""Kargo etiket ve takip tabloları

Revision ID: 20251217_065726
Revises: 
Create Date: 2024-12-17 06:57:26.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '20251217_065726'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Kargo tabloları oluştur."""
    
    # kargo_etiketleri tablosunu oluştur
    op.create_table(
        'kargo_etiketleri',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        
        # Kaynak bilgileri
        sa.Column('kaynak_turu', sa.String(length=50), nullable=False,
                 comment='POS_SATIS veya SATIS_BELGESI'),
        sa.Column('kaynak_id', sa.Integer(), nullable=False,
                 comment='Kaynak belge ID'),
        
        # Taşıyıcı bilgileri
        sa.Column('tasiyici', sa.String(length=50), nullable=False,
                 comment='Taşıyıcı kodu'),
        sa.Column('servis_kodu', sa.String(length=50), nullable=True,
                 comment='Taşıyıcı servis kodu'),
        
        # Alıcı bilgileri
        sa.Column('alici_ad', sa.String(length=255), nullable=False,
                 comment='Alıcı adı'),
        sa.Column('alici_telefon', sa.String(length=20), nullable=False,
                 comment='Alıcı telefonu'),
        sa.Column('alici_adres', sa.Text(), nullable=False,
                 comment='Alıcı adresi'),
        sa.Column('alici_il', sa.String(length=100), nullable=False,
                 comment='Alıcı ili'),
        sa.Column('alici_ilce', sa.String(length=100), nullable=False,
                 comment='Alıcı ilçesi'),
        
        # Paket bilgileri
        sa.Column('paket_agirlik_kg', sa.DECIMAL(precision=10, scale=2), 
                 nullable=False, server_default='1.0',
                 comment='Paket ağırlığı (kg)'),
        
        # Durum bilgileri
        sa.Column('durum', sa.String(length=50), nullable=False,
                 comment='Etiket durumu'),
        sa.Column('mesaj', sa.Text(), nullable=True,
                 comment='Hata/bilgi mesajı'),
        sa.Column('takip_no', sa.String(length=100), nullable=True,
                 comment='Takip numarası'),
        
        # Retry bilgileri
        sa.Column('deneme_sayisi', sa.Integer(), nullable=False, 
                 server_default='0', comment='Retry sayısı'),
        
        # Zaman damgaları
        sa.Column('olusturulma_zamani', sa.TIMESTAMP(), nullable=False,
                 server_default=func.now(), comment='Oluşturulma zamanı'),
        sa.Column('guncellenme_zamani', sa.TIMESTAMP(), nullable=False,
                 server_default=func.now(), comment='Güncellenme zamanı'),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Unique constraint
        sa.UniqueConstraint('kaynak_turu', 'kaynak_id', 'tasiyici',
                           name='uk_kargo_etiketleri_kaynak_tasiyici'),
        
        comment='Kargo etiketleri tablosu'
    )
    
    # kargo_takipleri tablosunu oluştur
    op.create_table(
        'kargo_takipleri',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        
        # Foreign key
        sa.Column('etiket_id', sa.Integer(), nullable=False,
                 comment='Etiket referansı'),
        
        # Takip bilgileri
        sa.Column('takip_no', sa.String(length=100), nullable=False,
                 comment='Takip numarası'),
        sa.Column('durum', sa.String(length=50), nullable=False,
                 comment='Takip durumu'),
        sa.Column('aciklama', sa.Text(), nullable=True,
                 comment='Durum açıklaması'),
        sa.Column('zaman', sa.TIMESTAMP(), nullable=True,
                 comment='Durum zamanı'),
        
        # Zaman damgası
        sa.Column('olusturulma_zamani', sa.TIMESTAMP(), nullable=False,
                 server_default=func.now(), comment='Kayıt zamanı'),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign key constraint
        sa.ForeignKeyConstraint(['etiket_id'], ['kargo_etiketleri.id'],
                               name='fk_kargo_takipleri_etiket_id'),
        
        comment='Kargo takip kayıtları tablosu'
    )
    
    # kargo_etiketleri tablosu index'leri
    op.create_index('ix_kargo_etiketleri_kaynak', 'kargo_etiketleri',
                   ['kaynak_turu', 'kaynak_id'])
    op.create_index('ix_kargo_etiketleri_durum', 'kargo_etiketleri',
                   ['durum'])
    op.create_index('ix_kargo_etiketleri_takip_no', 'kargo_etiketleri',
                   ['takip_no'])
    op.create_index('ix_kargo_etiketleri_tasiyici', 'kargo_etiketleri',
                   ['tasiyici'])
    
    # kargo_takipleri tablosu index'leri
    op.create_index('ix_kargo_takipleri_etiket_id', 'kargo_takipleri',
                   ['etiket_id'])
    op.create_index('ix_kargo_takipleri_takip_no', 'kargo_takipleri',
                   ['takip_no'])
    op.create_index('ix_kargo_takipleri_durum', 'kargo_takipleri',
                   ['durum'])
    op.create_index('ix_kargo_takipleri_zaman', 'kargo_takipleri',
                   ['zaman'])


def downgrade():
    """Kargo tablolarını kaldır."""
    
    # Index'leri kaldır
    op.drop_index('ix_kargo_takipleri_zaman', table_name='kargo_takipleri')
    op.drop_index('ix_kargo_takipleri_durum', table_name='kargo_takipleri')
    op.drop_index('ix_kargo_takipleri_takip_no', table_name='kargo_takipleri')
    op.drop_index('ix_kargo_takipleri_etiket_id', table_name='kargo_takipleri')
    
    op.drop_index('ix_kargo_etiketleri_tasiyici', table_name='kargo_etiketleri')
    op.drop_index('ix_kargo_etiketleri_takip_no', table_name='kargo_etiketleri')
    op.drop_index('ix_kargo_etiketleri_durum', table_name='kargo_etiketleri')
    op.drop_index('ix_kargo_etiketleri_kaynak', table_name='kargo_etiketleri')
    
    # Tabloları kaldır
    op.drop_table('kargo_takipleri')
    op.drop_table('kargo_etiketleri')