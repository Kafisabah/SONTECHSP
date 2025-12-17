# Version: 0.1.0
# Last Update: 2024-12-17
# Module: migration.ebelge_outbox
# Description: E-belge outbox pattern tabloları migration
# Changelog:
# - İlk versiyon: E-belge outbox tabloları oluşturuldu

"""E-belge outbox pattern tabloları

Revision ID: 005_ebelge_outbox
Revises: 004_eticaret_altyapi
Create Date: 2024-12-17 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_ebelge_outbox'
down_revision = '004_eticaret_altyapi'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """E-belge outbox tabloları oluştur"""
    
    # ebelge_cikis_kuyrugu tablosu
    op.create_table(
        'ebelge_cikis_kuyrugu',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kaynak_turu', sa.String(length=50), nullable=False),
        sa.Column('kaynak_id', sa.Integer(), nullable=False),
        sa.Column('belge_turu', sa.String(length=20), nullable=False),
        sa.Column('musteri_ad', sa.String(length=200), nullable=False),
        sa.Column('vergi_no', sa.String(length=20), nullable=False),
        sa.Column('toplam_tutar', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('para_birimi', sa.String(length=3), nullable=False, server_default='TRY'),
        sa.Column('belge_json', sa.Text(), nullable=False),
        sa.Column('durum', sa.String(length=20), nullable=False),
        sa.Column('mesaj', sa.Text(), nullable=True),
        sa.Column('dis_belge_no', sa.String(length=100), nullable=True),
        sa.Column('deneme_sayisi', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('aciklama', sa.Text(), nullable=True),
        sa.Column('olusturulma_zamani', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('guncellenme_zamani', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kaynak_turu', 'kaynak_id', 'belge_turu', name='uq_ebelge_kaynak')
    )
    
    # ebelge_cikis_kuyrugu indeksleri
    op.create_index('ix_ebelge_durum', 'ebelge_cikis_kuyrugu', ['durum'])
    op.create_index('ix_ebelge_durum_deneme', 'ebelge_cikis_kuyrugu', ['durum', 'deneme_sayisi'])
    op.create_index('ix_ebelge_olusturulma', 'ebelge_cikis_kuyrugu', ['olusturulma_zamani'])
    
    # ebelge_durumlari tablosu
    op.create_table(
        'ebelge_durumlari',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cikis_id', sa.Integer(), nullable=False),
        sa.Column('durum', sa.String(length=20), nullable=False),
        sa.Column('mesaj', sa.Text(), nullable=True),
        sa.Column('olusturulma_zamani', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['cikis_id'], ['ebelge_cikis_kuyrugu.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ebelge_durumlari indeksleri
    op.create_index('ix_ebelge_durum_cikis_id', 'ebelge_durumlari', ['cikis_id'])
    op.create_index('ix_ebelge_durum_olusturulma', 'ebelge_durumlari', ['olusturulma_zamani'])


def downgrade() -> None:
    """E-belge outbox tabloları kaldır"""
    
    # İndeksleri kaldır
    op.drop_index('ix_ebelge_durum_olusturulma', table_name='ebelge_durumlari')
    op.drop_index('ix_ebelge_durum_cikis_id', table_name='ebelge_durumlari')
    op.drop_index('ix_ebelge_olusturulma', table_name='ebelge_cikis_kuyrugu')
    op.drop_index('ix_ebelge_durum_deneme', table_name='ebelge_cikis_kuyrugu')
    op.drop_index('ix_ebelge_durum', table_name='ebelge_cikis_kuyrugu')
    
    # Tabloları kaldır
    op.drop_table('ebelge_durumlari')
    op.drop_table('ebelge_cikis_kuyrugu')