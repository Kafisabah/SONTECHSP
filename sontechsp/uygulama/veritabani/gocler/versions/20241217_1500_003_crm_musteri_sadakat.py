# Version: 0.1.0
# Last Update: 2024-12-17
# Module: veritabani.gocler.versions.crm_musteri_sadakat
# Description: CRM müşteri ve sadakat puanları tabloları migration
# Changelog:
# - CRM çekirdek modülü tabloları oluşturuldu

"""CRM müşteri ve sadakat puanları tabloları

Revision ID: 003
Revises: 002
Create Date: 2024-12-17 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade migration - CRM tablolarını oluştur"""
    
    # Müşteriler tablosu
    op.create_table('musteriler',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz müşteri kimliği'),
        sa.Column('olusturulma_zamani', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncellenme_zamani', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('ad', sa.String(length=100), nullable=False, comment='Müşteri adı'),
        sa.Column('soyad', sa.String(length=100), nullable=False, comment='Müşteri soyadı'),
        sa.Column('telefon', sa.String(length=20), nullable=True, comment='Telefon numarası'),
        sa.Column('eposta', sa.String(length=255), nullable=True, comment='E-posta adresi'),
        sa.Column('vergi_no', sa.String(length=20), nullable=True, comment='Vergi numarası'),
        sa.Column('adres', sa.Text(), nullable=True, comment='Müşteri adresi'),
        sa.Column('aktif_mi', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Müşteri aktif durumu'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telefon', name='uq_musteriler_telefon'),
        sa.UniqueConstraint('eposta', name='uq_musteriler_eposta'),
        comment='Müşteri bilgileri tablosu'
    )
    
    # Sadakat puanları tablosu
    op.create_table('sadakat_puanlari',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz puan işlem kimliği'),
        sa.Column('olusturulma_zamani', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='İşlem tarihi'),
        sa.Column('musteri_id', sa.Integer(), nullable=False, comment='Müşteri kimliği'),
        sa.Column('islem_turu', sa.String(length=20), nullable=False, comment='İşlem türü (KAZANIM, HARCAMA, DUZELTME)'),
        sa.Column('puan', sa.Integer(), nullable=False, comment='Puan miktarı'),
        sa.Column('aciklama', sa.Text(), nullable=True, comment='İşlem açıklaması'),
        sa.Column('referans_turu', sa.String(length=50), nullable=True, comment='Referans türü (POS_SATIS, SATIS_BELGESI)'),
        sa.Column('referans_id', sa.Integer(), nullable=True, comment='Referans kayıt kimliği'),
        sa.ForeignKeyConstraint(['musteri_id'], ['musteriler.id'], ondelete='CASCADE', name='fk_sadakat_puanlari_musteri_id'),
        sa.PrimaryKeyConstraint('id'),
        comment='Müşteri sadakat puanları işlem tablosu'
    )
    
    # İndeksler oluştur
    op.create_index('idx_musteriler_telefon', 'musteriler', ['telefon'])
    op.create_index('idx_musteriler_eposta', 'musteriler', ['eposta'])
    op.create_index('idx_musteriler_ad_soyad', 'musteriler', ['ad', 'soyad'])
    op.create_index('idx_musteriler_aktif_mi', 'musteriler', ['aktif_mi'])
    
    op.create_index('idx_sadakat_musteri_id', 'sadakat_puanlari', ['musteri_id'])
    op.create_index('idx_sadakat_referans', 'sadakat_puanlari', ['referans_turu', 'referans_id'])
    op.create_index('idx_sadakat_islem_turu', 'sadakat_puanlari', ['islem_turu'])
    op.create_index('idx_sadakat_olusturulma_zamani', 'sadakat_puanlari', ['olusturulma_zamani'])
    
    # Check constraint'ler ekle
    op.create_check_constraint(
        'ck_sadakat_puanlari_islem_turu',
        'sadakat_puanlari',
        "islem_turu IN ('KAZANIM', 'HARCAMA', 'DUZELTME')"
    )
    
    op.create_check_constraint(
        'ck_sadakat_puanlari_referans_turu',
        'sadakat_puanlari',
        "referans_turu IS NULL OR referans_turu IN ('POS_SATIS', 'SATIS_BELGESI')"
    )
    
    # E-posta format kontrolü için check constraint
    op.create_check_constraint(
        'ck_musteriler_eposta_format',
        'musteriler',
        "eposta IS NULL OR eposta ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
    )$'"
    )


def downgrade() -> None:
    """Downgrade migration - CRM tablolarını kaldır"""
    
    # Check constraint'leri kaldır
    op.drop_constraint('ck_musteriler_eposta_format', 'musteriler', type_='check')
    op.drop_constraint('ck_sadakat_puanlari_referans_turu', 'sadakat_puanlari', type_='check')
    op.drop_constraint('ck_sadakat_puanlari_islem_turu', 'sadakat_puanlari', type_='check')
    
    # İndeksleri kaldır
    op.drop_index('idx_sadakat_olusturulma_zamani', table_name='sadakat_puanlari')
    op.drop_index('idx_sadakat_islem_turu', table_name='sadakat_puanlari')
    op.drop_index('idx_sadakat_referans', table_name='sadakat_puanlari')
    op.drop_index('idx_sadakat_musteri_id', table_name='sadakat_puanlari')
    
    op.drop_index('idx_musteriler_aktif_mi', table_name='musteriler')
    op.drop_index('idx_musteriler_ad_soyad', table_name='musteriler')
    op.drop_index('idx_musteriler_eposta', table_name='musteriler')
    op.drop_index('idx_musteriler_telefon', table_name='musteriler')
    
    # Tabloları kaldır (foreign key sırasına dikkat et)
    op.drop_table('sadakat_puanlari')
    op.drop_table('musteriler')