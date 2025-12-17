"""E-ticaret entegrasyon altyapısı

Revision ID: 004_eticaret_altyapi
Revises: 003_crm_musteri_sadakat
Create Date: 2024-12-17 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_eticaret_altyapi'
down_revision = '003_crm_musteri_sadakat'
branch_labels = None
depends_on = None


def upgrade():
    """E-ticaret entegrasyon tablolarını oluştur"""
    
    # eticaret_hesaplari tablosu
    op.create_table(
        'eticaret_hesaplari',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False, comment='Platform türü (TRENDYOL, SHOPIFY vb.)'),
        sa.Column('magaza_adi', sa.String(length=200), nullable=False, comment='Mağaza adı'),
        sa.Column('aktif_mi', sa.Boolean(), nullable=False, comment='Hesap aktif mi'),
        sa.Column('kimlik_json', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='Şifrelenmiş kimlik bilgileri'),
        sa.Column('ayar_json', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Platform ayarları'),
        sa.Column('olusturma_zamani', sa.DateTime(), nullable=False),
        sa.Column('guncelleme_zamani', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        comment='E-ticaret mağaza hesapları'
    )
    
    # eticaret_hesaplari indeksleri
    op.create_index('idx_eticaret_hesaplari_platform', 'eticaret_hesaplari', ['platform'])
    op.create_index('idx_eticaret_hesaplari_aktif', 'eticaret_hesaplari', ['aktif_mi'])
    
    # eticaret_siparisleri tablosu
    op.create_table(
        'eticaret_siparisleri',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('magaza_hesabi_id', sa.Integer(), nullable=False, comment='Mağaza hesabı referansı'),
        sa.Column('platform', sa.String(length=50), nullable=False, comment='Platform türü'),
        sa.Column('dis_siparis_no', sa.String(length=100), nullable=False, comment='Platform sipariş numarası'),
        sa.Column('siparis_zamani', sa.DateTime(), nullable=False, comment='Sipariş tarihi'),
        sa.Column('musteri_ad_soyad', sa.String(length=200), nullable=True, comment='Müşteri adı soyadı'),
        sa.Column('toplam_tutar', sa.Numeric(precision=15, scale=2), nullable=True, comment='Toplam tutar'),
        sa.Column('para_birimi', sa.String(length=3), nullable=False, comment='Para birimi'),
        sa.Column('durum', sa.String(length=20), nullable=False, comment='Sipariş durumu'),
        sa.Column('kargo_tasiyici', sa.String(length=100), nullable=True, comment='Kargo taşıyıcı'),
        sa.Column('takip_no', sa.String(length=100), nullable=True, comment='Kargo takip numarası'),
        sa.Column('ham_veri_json', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='Platform ham verisi'),
        sa.Column('olusturma_zamani', sa.DateTime(), nullable=False),
        sa.Column('guncelleme_zamani', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['magaza_hesabi_id'], ['eticaret_hesaplari.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('magaza_hesabi_id', 'dis_siparis_no', name='uk_siparis_unique'),
        comment='E-ticaret siparişleri'
    )
    
    # eticaret_siparisleri indeksleri
    op.create_index('idx_eticaret_siparisleri_platform', 'eticaret_siparisleri', ['platform'])
    op.create_index('idx_eticaret_siparisleri_durum', 'eticaret_siparisleri', ['durum'])
    op.create_index('idx_eticaret_siparisleri_siparis_zamani', 'eticaret_siparisleri', ['siparis_zamani'])
    
    # eticaret_is_kuyrugu tablosu
    op.create_table(
        'eticaret_is_kuyrugu',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('magaza_hesabi_id', sa.Integer(), nullable=False, comment='Mağaza hesabı referansı'),
        sa.Column('tur', sa.String(length=50), nullable=False, comment='İş türü (SIPARIS_CEK, STOK_GONDER vb.)'),
        sa.Column('payload_json', postgresql.JSON(astext_type=sa.Text()), nullable=False, comment='İş verisi'),
        sa.Column('durum', sa.String(length=20), nullable=False, comment='İş durumu'),
        sa.Column('hata_mesaji', sa.Text(), nullable=True, comment='Hata mesajı'),
        sa.Column('deneme_sayisi', sa.Integer(), nullable=False, comment='Deneme sayısı'),
        sa.Column('sonraki_deneme', sa.DateTime(), nullable=True, comment='Sonraki deneme zamanı'),
        sa.Column('olusturma_zamani', sa.DateTime(), nullable=False),
        sa.Column('guncelleme_zamani', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['magaza_hesabi_id'], ['eticaret_hesaplari.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='E-ticaret iş kuyruğu'
    )
    
    # eticaret_is_kuyrugu indeksleri
    op.create_index('idx_eticaret_is_kuyrugu_durum', 'eticaret_is_kuyrugu', ['durum'])
    op.create_index('idx_eticaret_is_kuyrugu_tur', 'eticaret_is_kuyrugu', ['tur'])
    op.create_index('idx_eticaret_is_kuyrugu_sonraki_deneme', 'eticaret_is_kuyrugu', ['sonraki_deneme'])
    
    # Varsayılan değerler
    op.execute("ALTER TABLE eticaret_hesaplari ALTER COLUMN aktif_mi SET DEFAULT true")
    op.execute("ALTER TABLE eticaret_siparisleri ALTER COLUMN para_birimi SET DEFAULT 'TRY'")
    op.execute("ALTER TABLE eticaret_is_kuyrugu ALTER COLUMN durum SET DEFAULT 'BEKLIYOR'")
    op.execute("ALTER TABLE eticaret_is_kuyrugu ALTER COLUMN deneme_sayisi SET DEFAULT 0")


def downgrade():
    """E-ticaret entegrasyon tablolarını kaldır"""
    
    # İndeksleri kaldır
    op.drop_index('idx_eticaret_is_kuyrugu_sonraki_deneme', table_name='eticaret_is_kuyrugu')
    op.drop_index('idx_eticaret_is_kuyrugu_tur', table_name='eticaret_is_kuyrugu')
    op.drop_index('idx_eticaret_is_kuyrugu_durum', table_name='eticaret_is_kuyrugu')
    
    op.drop_index('idx_eticaret_siparisleri_siparis_zamani', table_name='eticaret_siparisleri')
    op.drop_index('idx_eticaret_siparisleri_durum', table_name='eticaret_siparisleri')
    op.drop_index('idx_eticaret_siparisleri_platform', table_name='eticaret_siparisleri')
    
    op.drop_index('idx_eticaret_hesaplari_aktif', table_name='eticaret_hesaplari')
    op.drop_index('idx_eticaret_hesaplari_platform', table_name='eticaret_hesaplari')
    
    # Tabloları kaldır (foreign key sırası önemli)
    op.drop_table('eticaret_is_kuyrugu')
    op.drop_table('eticaret_siparisleri')
    op.drop_table('eticaret_hesaplari')