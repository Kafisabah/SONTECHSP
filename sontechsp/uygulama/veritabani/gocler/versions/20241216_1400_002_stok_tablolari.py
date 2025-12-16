# Version: 0.1.0
# Last Update: 2024-12-16
# Module: veritabani.gocler.versions.stok_tablolari
# Description: SONTECHSP stok tabloları migration
# Changelog:
# - İlk oluşturma

"""Stok tabloları migration

Revision ID: 002
Revises: 001
Create Date: 2024-12-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade migration - stok tablolarını oluştur"""
    
    # Depolar tablosu (stok lokasyonları için)
    op.create_table('depolar',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), 
                 server_default=sa.text('now()'), nullable=False),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('magaza_id', sa.Integer(), nullable=False),
        sa.Column('depo_adi', sa.String(length=100), nullable=False),
        sa.Column('depo_kodu', sa.String(length=20), nullable=False),
        sa.Column('aciklama', sa.Text(), nullable=True),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['magaza_id'], ['magazalar.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Depo/stok lokasyonları tablosu'
    )
    
    # Ürünler tablosu
    op.create_table('urunler',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), 
                 server_default=sa.text('now()'), nullable=False),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('urun_kodu', sa.String(length=50), nullable=False),
        sa.Column('urun_adi', sa.String(length=200), nullable=False),
        sa.Column('aciklama', sa.Text(), nullable=True),
        sa.Column('kategori', sa.String(length=100), nullable=True),
        sa.Column('alt_kategori', sa.String(length=100), nullable=True),
        sa.Column('marka', sa.String(length=100), nullable=True),
        sa.Column('birim', sa.String(length=20), nullable=False, default='adet'),
        sa.Column('alis_fiyati', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('satis_fiyati', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('kdv_orani', sa.Numeric(precision=5, scale=2), nullable=False, 
                 default=sa.text('18.00')),
        sa.Column('stok_takip', sa.Boolean(), nullable=False, default=True),
        sa.Column('negatif_stok_izin', sa.Boolean(), nullable=False, default=False),
        sa.Column('minimum_stok', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('maksimum_stok', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('urun_kodu'),
        comment='Ürün ana bilgileri tablosu'
    )
    
    # Ürün barkodları tablosu
    op.create_table('urun_barkodlari',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), 
                 server_default=sa.text('now()'), nullable=False),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('urun_id', sa.Integer(), nullable=False),
        sa.Column('barkod', sa.String(length=50), nullable=False),
        sa.Column('barkod_tipi', sa.String(length=20), nullable=False, default='EAN13'),
        sa.Column('birim', sa.String(length=20), nullable=False),
        sa.Column('carpan', sa.Numeric(precision=15, scale=4), nullable=False, 
                 default=sa.text('1.0000')),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.Column('ana_barkod', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['urun_id'], ['urunler.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('barkod'),
        comment='Ürün barkod bilgileri tablosu'
    )
    
    # Stok bakiyeleri tablosu
    op.create_table('stok_bakiyeleri',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), 
                 server_default=sa.text('now()'), nullable=False),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('urun_id', sa.Integer(), nullable=False),
        sa.Column('magaza_id', sa.Integer(), nullable=False),
        sa.Column('depo_id', sa.Integer(), nullable=True),
        sa.Column('miktar', sa.Numeric(precision=15, scale=4), nullable=False, 
                 default=sa.text('0.0000')),
        sa.Column('rezerve_miktar', sa.Numeric(precision=15, scale=4), nullable=False, 
                 default=sa.text('0.0000')),
        sa.Column('kullanilabilir_miktar', sa.Numeric(precision=15, scale=4), 
                 nullable=False, default=sa.text('0.0000')),
        sa.Column('ortalama_maliyet', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('son_alis_fiyati', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('son_hareket_tarihi', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['urun_id'], ['urunler.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['magaza_id'], ['magazalar.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['depo_id'], ['depolar.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('urun_id', 'magaza_id', 'depo_id', name='uk_stok_bakiye'),
        comment='Stok bakiye tablosu'
    )
    
    # Stok hareketleri tablosu
    op.create_table('stok_hareketleri',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), 
                 server_default=sa.text('now()'), nullable=False),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('urun_id', sa.Integer(), nullable=False),
        sa.Column('magaza_id', sa.Integer(), nullable=False),
        sa.Column('depo_id', sa.Integer(), nullable=True),
        sa.Column('hareket_tipi', sa.String(length=50), nullable=False),
        sa.Column('miktar', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('birim_fiyat', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('toplam_tutar', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('referans_tablo', sa.String(length=50), nullable=True),
        sa.Column('referans_id', sa.Integer(), nullable=True),
        sa.Column('aciklama', sa.Text(), nullable=True),
        sa.Column('kullanici_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['urun_id'], ['urunler.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['magaza_id'], ['magazalar.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['depo_id'], ['depolar.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['kullanici_id'], ['kullanicilar.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Stok hareket tablosu'
    )
    
    # Index'leri oluştur
    op.create_index('ix_depolar_magaza_id', 'depolar', ['magaza_id'])
    op.create_index('ix_depolar_depo_kodu', 'depolar', ['depo_kodu'])
    op.create_index('ix_urunler_urun_kodu', 'urunler', ['urun_kodu'])
    op.create_index('ix_urunler_urun_adi', 'urunler', ['urun_adi'])
    op.create_index('ix_urunler_kategori', 'urunler', ['kategori'])
    op.create_index('ix_urunler_aktif', 'urunler', ['aktif'])
    op.create_index('ix_urun_barkodlari_urun_id', 'urun_barkodlari', ['urun_id'])
    op.create_index('ix_urun_barkodlari_barkod', 'urun_barkodlari', ['barkod'])
    op.create_index('ix_urun_barkodlari_aktif', 'urun_barkodlari', ['aktif'])
    op.create_index('ix_stok_bakiyeleri_urun_id', 'stok_bakiyeleri', ['urun_id'])
    op.create_index('ix_stok_bakiyeleri_magaza_id', 'stok_bakiyeleri', ['magaza_id'])
    op.create_index('ix_stok_bakiyeleri_depo_id', 'stok_bakiyeleri', ['depo_id'])
    op.create_index('ix_stok_hareketleri_urun_id', 'stok_hareketleri', ['urun_id'])
    op.create_index('ix_stok_hareketleri_magaza_id', 'stok_hareketleri', ['magaza_id'])
    op.create_index('ix_stok_hareketleri_hareket_tipi', 'stok_hareketleri', ['hareket_tipi'])
    op.create_index('ix_stok_hareketleri_olusturma_tarihi', 'stok_hareketleri', ['olusturma_tarihi'])


def downgrade() -> None:
    """Downgrade migration - stok tablolarını kaldır"""
    
    # Index'leri kaldır
    op.drop_index('ix_stok_hareketleri_olusturma_tarihi', table_name='stok_hareketleri')
    op.drop_index('ix_stok_hareketleri_hareket_tipi', table_name='stok_hareketleri')
    op.drop_index('ix_stok_hareketleri_magaza_id', table_name='stok_hareketleri')
    op.drop_index('ix_stok_hareketleri_urun_id', table_name='stok_hareketleri')
    op.drop_index('ix_stok_bakiyeleri_depo_id', table_name='stok_bakiyeleri')
    op.drop_index('ix_stok_bakiyeleri_magaza_id', table_name='stok_bakiyeleri')
    op.drop_index('ix_stok_bakiyeleri_urun_id', table_name='stok_bakiyeleri')
    op.drop_index('ix_urun_barkodlari_aktif', table_name='urun_barkodlari')
    op.drop_index('ix_urun_barkodlari_barkod', table_name='urun_barkodlari')
    op.drop_index('ix_urun_barkodlari_urun_id', table_name='urun_barkodlari')
    op.drop_index('ix_urunler_aktif', table_name='urunler')
    op.drop_index('ix_urunler_kategori', table_name='urunler')
    op.drop_index('ix_urunler_urun_adi', table_name='urunler')
    op.drop_index('ix_urunler_urun_kodu', table_name='urunler')
    op.drop_index('ix_depolar_depo_kodu', table_name='depolar')
    op.drop_index('ix_depolar_magaza_id', table_name='depolar')
    
    # Tabloları kaldır (foreign key sırasına dikkat et)
    op.drop_table('stok_hareketleri')
    op.drop_table('stok_bakiyeleri')
    op.drop_table('urun_barkodlari')
    op.drop_table('urunler')
    op.drop_table('depolar')