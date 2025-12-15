# Veritabanı Migration Tamamlama Gereksinimleri

## Giriş

SONTECHSP projesi için PostgreSQL bağlantı katmanı ve Alembic göç (migration) sisteminin tamamlanması. Mevcut veritabanı altyapısı büyük ölçüde hazır durumda ancak ilk migration ve bazı temel tablolar eksik. Bu spec, eksik kısımları tamamlayarak tam işlevsel bir veritabanı altyapısı sağlayacak.

## Sözlük

- **Migration**: Veritabanı şema değişikliklerini yönetmek için kullanılan Alembic göç dosyaları
- **Alembic**: SQLAlchemy için veritabanı migration aracı
- **DeclarativeBase**: SQLAlchemy ORM için temel model sınıfı
- **SessionLocal**: SQLAlchemy session factory
- **Engine**: SQLAlchemy veritabanı bağlantı motoru
- **SONTECHSP**: Geliştirilen POS+ERP+CRM sistemi

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, veritabanı bağlantısını test edebilmek istiyorum ki sistem kurulumunun doğru çalıştığından emin olabileyim.

#### Kabul Kriterleri

1. WHEN bağlantı testi çalıştırıldığında THEN sistem PostgreSQL bağlantısını doğrulayacak
2. WHEN bağlantı başarısız olduğunda THEN sistem anlamlı hata mesajı verecek
3. WHEN bağlantı başarılı olduğunda THEN sistem onay mesajı döndürecek
4. WHEN SQLite bağlantısı test edildiğinde THEN sistem offline veritabanı bağlantısını doğrulayacak
5. WHEN bağlantı testi yapıldığında THEN sistem log kaydı oluşturacak

### Gereksinim 2

**Kullanıcı Hikayesi:** Geliştirici olarak, ilk migration dosyasını çalıştırabilmek istiyorum ki temel sistem tabloları oluşturulabilsin.

#### Kabul Kriterleri

1. WHEN ilk migration çalıştırıldığında THEN sistem kullanicilar tablosunu oluşturacak
2. WHEN ilk migration çalıştırıldığında THEN sistem roller tablosunu oluşturacak
3. WHEN ilk migration çalıştırıldığında THEN sistem firmalar tablosunu oluşturacak
4. WHEN ilk migration çalıştırıldığında THEN sistem magazalar tablosunu oluşturacak
5. WHEN ilk migration çalıştırıldığında THEN sistem terminaller tablosunu oluşturacak

### Gereksinim 3

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, tablo yapılarının Türkçe ASCII standardına uygun olmasını istiyorum ki veritabanı yönetimi tutarlı olsun.

#### Kabul Kriterleri

1. WHEN tablolar oluşturulduğunda THEN tablo isimleri Türkçe ASCII karakterler kullanacak
2. WHEN kolon isimleri tanımlandığında THEN snake_case formatında olacak
3. WHEN foreign key ilişkileri kurulduğunda THEN referans bütünlüğü sağlanacak
4. WHEN unique constraint'ler tanımlandığında THEN veri tekrarı engellenecek
5. WHEN index'ler oluşturulduğunda THEN performans optimizasyonu sağlanacak

### Gereksinim 4

**Kullanıcı Hikayesi:** Geliştirici olarak, session yönetiminin güvenli olmasını istiyorum ki veri tutarlılığı sağlansın.

#### Kabul Kriterleri

1. WHEN session açıldığında THEN otomatik commit kapalı olacak
2. WHEN işlem başarılı olduğunda THEN session commit edilecek
3. WHEN hata oluştuğunda THEN session rollback yapılacak
4. WHEN session kapatıldığında THEN kaynak temizliği yapılacak
5. WHEN context manager kullanıldığında THEN exception handling otomatik çalışacak

### Gereksinim 5

**Kullanıçı Hikayesi:** Sistem yöneticisi olarak, migration'ların geri alınabilir olmasını istiyorum ki şema değişikliklerini güvenle yönetebileyim.

#### Kabul Kriterleri

1. WHEN migration upgrade çalıştırıldığında THEN şema ileri doğru güncellenecek
2. WHEN migration downgrade çalıştırıldığında THEN şema geri alınacak
3. WHEN migration durumu sorgulandığında THEN mevcut versiyon bilgisi döndürülecek
4. WHEN migration geçmişi incelendiğinde THEN tüm değişiklikler listelenecek
5. WHEN migration çakışması olduğunda THEN sistem uyarı verecek

### Gereksinim 6

**Kullanıcı Hikayesi:** Geliştirici olarak, temel sistem verilerinin otomatik yüklenmesini istiyorum ki sistem ilk kurulumda kullanıma hazır olsun.

#### Kabul Kriterleri

1. WHEN sistem ilk kurulduğunda THEN admin kullanıcısı oluşturulacak
2. WHEN temel roller yüklendiğinde THEN sistem rolleri tanımlanacak
3. WHEN temel yetkiler yüklendiğinde THEN sistem yetkileri oluşturulacak
4. WHEN varsayılan firma oluşturulduğunda THEN ana mağaza tanımlanacak
5. WHEN temel veriler yüklendiğinde THEN veri tutarlılığı kontrol edilecek