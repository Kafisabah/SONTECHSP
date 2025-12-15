# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.gocler.versions.ilk_migration
# Description: SONTECHSP ilk migration - temel tablolar
# Changelog:
# - İlk oluşturma

"""İlk migration - temel sistem tabloları

Revision ID: 001
Revises: 
Create Date: 2024-12-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade migration - temel tabloları oluştur"""
    
    # Firmalar tablosu
    op.create_table('firmalar',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('firma_adi', sa.String(length=200), nullable=False, comment='Firma adı'),
        sa.Column('ticaret_unvani', sa.String(length=200), nullable=True, comment='Ticaret unvanı'),
        sa.Column('vergi_dairesi', sa.String(length=100), nullable=True, comment='Vergi dairesi'),
        sa.Column('vergi_no', sa.String(length=20), nullable=True, comment='Vergi numarası'),
        sa.Column('tc_kimlik_no', sa.String(length=11), nullable=True, comment='TC kimlik numarası (şahıs firması için)'),
        sa.Column('adres', sa.Text(), nullable=True, comment='Firma adresi'),
        sa.Column('telefon', sa.String(length=20), nullable=True, comment='Telefon numarası'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='E-posta adresi'),
        sa.Column('website', sa.String(length=255), nullable=True, comment='Web sitesi'),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True, comment='Firma aktif mi'),
        sa.PrimaryKeyConstraint('id'),
        comment='Ana firma bilgileri tablosu'
    )
    
    # Mağazalar tablosu
    op.create_table('magazalar',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('firma_id', sa.Integer(), nullable=False),
        sa.Column('magaza_adi', sa.String(length=200), nullable=False),
        sa.Column('magaza_kodu', sa.String(length=20), nullable=False),
        sa.Column('adres', sa.Text(), nullable=True),
        sa.Column('sehir', sa.String(length=100), nullable=True),
        sa.Column('ilce', sa.String(length=100), nullable=True),
        sa.Column('posta_kodu', sa.String(length=10), nullable=True),
        sa.Column('telefon', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('alan_m2', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('personel_sayisi', sa.Integer(), nullable=True),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['firma_id'], ['firmalar.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Mağaza/şube bilgileri tablosu'
    )
    
    # Terminaller tablosu
    op.create_table('terminaller',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('magaza_id', sa.Integer(), nullable=False),
        sa.Column('terminal_adi', sa.String(length=100), nullable=False),
        sa.Column('terminal_kodu', sa.String(length=20), nullable=False),
        sa.Column('ip_adresi', sa.String(length=15), nullable=True),
        sa.Column('mac_adresi', sa.String(length=17), nullable=True),
        sa.Column('isletim_sistemi', sa.String(length=100), nullable=True),
        sa.Column('yazici_modeli', sa.String(length=100), nullable=True),
        sa.Column('barkod_okuyucu', sa.Boolean(), nullable=False, default=True),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.Column('online', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['magaza_id'], ['magazalar.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='POS terminal bilgileri tablosu'
    )
    
    # Kullanıcılar tablosu
    op.create_table('kullanicilar',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('kullanici_adi', sa.String(length=50), nullable=False, comment='Benzersiz kullanıcı adı'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='E-posta adresi'),
        sa.Column('sifre_hash', sa.String(length=255), nullable=False, comment='Şifrelenmiş parola'),
        sa.Column('ad', sa.String(length=100), nullable=False, comment='Kullanıcı adı'),
        sa.Column('soyad', sa.String(length=100), nullable=False, comment='Kullanıcı soyadı'),
        sa.Column('telefon', sa.String(length=20), nullable=True, comment='Telefon numarası'),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True, comment='Kullanıcı aktif mi'),
        sa.Column('son_giris_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son giriş tarihi'),
        sa.Column('sifre_degisim_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son şifre değişim tarihi'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kullanici_adi'),
        sa.UniqueConstraint('email'),
        comment='Sistem kullanıcıları tablosu'
    )
    
    # Roller tablosu
    op.create_table('roller',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('rol_adi', sa.String(length=50), nullable=False),
        sa.Column('aciklama', sa.Text(), nullable=True),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.Column('sistem_rolu', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rol_adi'),
        comment='Kullanıcı rolleri tablosu'
    )
    
    # Yetkiler tablosu
    op.create_table('yetkiler',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('yetki_kodu', sa.String(length=100), nullable=False),
        sa.Column('yetki_adi', sa.String(length=100), nullable=False),
        sa.Column('aciklama', sa.Text(), nullable=True),
        sa.Column('kategori', sa.String(length=50), nullable=False),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.Column('sistem_yetkisi', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('yetki_kodu'),
        comment='Sistem yetkileri tablosu'
    )
    
    # Kullanıcı-Rol ilişki tablosu
    op.create_table('kullanici_rolleri',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('kullanici_id', sa.Integer(), nullable=False),
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('atayan_kullanici_id', sa.Integer(), nullable=True),
        sa.Column('atama_tarihi', sa.DateTime(timezone=True), nullable=False, default=sa.text('now()')),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['kullanici_id'], ['kullanicilar.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rol_id'], ['roller.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['atayan_kullanici_id'], ['kullanicilar.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='Kullanıcı-rol ilişki tablosu'
    )
    
    # Rol-Yetki ilişki tablosu
    op.create_table('rol_yetkileri',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Benzersiz kayıt kimliği'),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Kayıt oluşturma tarihi'),
        sa.Column('guncelleme_tarihi', sa.DateTime(timezone=True), nullable=True, comment='Son güncelleme tarihi'),
        sa.Column('rol_id', sa.Integer(), nullable=False),
        sa.Column('yetki_id', sa.Integer(), nullable=False),
        sa.Column('atayan_kullanici_id', sa.Integer(), nullable=True),
        sa.Column('atama_tarihi', sa.DateTime(timezone=True), nullable=False, default=sa.text('now()')),
        sa.Column('aktif', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['rol_id'], ['roller.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['yetki_id'], ['yetkiler.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['atayan_kullanici_id'], ['kullanicilar.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='Rol-yetki ilişki tablosu'
    )
    
    # Index'ler oluştur
    op.create_index('ix_firmalar_firma_adi', 'firmalar', ['firma_adi'])
    op.create_index('ix_magazalar_firma_id', 'magazalar', ['firma_id'])
    op.create_index('ix_magazalar_magaza_kodu', 'magazalar', ['magaza_kodu'])
    op.create_index('ix_terminaller_magaza_id', 'terminaller', ['magaza_id'])
    op.create_index('ix_terminaller_terminal_kodu', 'terminaller', ['terminal_kodu'])
    op.create_index('ix_kullanicilar_kullanici_adi', 'kullanicilar', ['kullanici_adi'])
    op.create_index('ix_kullanicilar_email', 'kullanicilar', ['email'])
    op.create_index('ix_roller_rol_adi', 'roller', ['rol_adi'])
    op.create_index('ix_yetkiler_yetki_kodu', 'yetkiler', ['yetki_kodu'])
    op.create_index('ix_yetkiler_kategori', 'yetkiler', ['kategori'])
    op.create_index('ix_kullanici_rolleri_kullanici_id', 'kullanici_rolleri', ['kullanici_id'])
    op.create_index('ix_kullanici_rolleri_rol_id', 'kullanici_rolleri', ['rol_id'])
    op.create_index('ix_rol_yetkileri_rol_id', 'rol_yetkileri', ['rol_id'])
    op.create_index('ix_rol_yetkileri_yetki_id', 'rol_yetkileri', ['yetki_id'])


def downgrade() -> None:
    """Downgrade migration - tabloları kaldır"""
    
    # Index'leri kaldır
    op.drop_index('ix_rol_yetkileri_yetki_id', table_name='rol_yetkileri')
    op.drop_index('ix_rol_yetkileri_rol_id', table_name='rol_yetkileri')
    op.drop_index('ix_kullanici_rolleri_rol_id', table_name='kullanici_rolleri')
    op.drop_index('ix_kullanici_rolleri_kullanici_id', table_name='kullanici_rolleri')
    op.drop_index('ix_yetkiler_kategori', table_name='yetkiler')
    op.drop_index('ix_yetkiler_yetki_kodu', table_name='yetkiler')
    op.drop_index('ix_roller_rol_adi', table_name='roller')
    op.drop_index('ix_kullanicilar_email', table_name='kullanicilar')
    op.drop_index('ix_kullanicilar_kullanici_adi', table_name='kullanicilar')
    op.drop_index('ix_terminaller_terminal_kodu', table_name='terminaller')
    op.drop_index('ix_terminaller_magaza_id', table_name='terminaller')
    op.drop_index('ix_magazalar_magaza_kodu', table_name='magazalar')
    op.drop_index('ix_magazalar_firma_id', table_name='magazalar')
    op.drop_index('ix_firmalar_firma_adi', table_name='firmalar')
    
    # Tabloları kaldır (foreign key sırasına dikkat et)
    op.drop_table('rol_yetkileri')
    op.drop_table('kullanici_rolleri')
    op.drop_table('yetkiler')
    op.drop_table('roller')
    op.drop_table('kullanicilar')
    op.drop_table('terminaller')
    op.drop_table('magazalar')
    op.drop_table('firmalar')