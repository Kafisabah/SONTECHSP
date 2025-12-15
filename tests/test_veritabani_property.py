# Version: 0.1.0
# Last Update: 2024-12-15
# Module: tests.test_veritabani_property
# Description: SONTECHSP veritabanı property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Veritabanı Property Testleri

Bu modül veritabanı altyapısı için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import os
import re
import tempfile
import logging
import pytest
from hypothesis import given, strategies as st, settings
from sqlalchemy import inspect, MetaData
from sqlalchemy.exc import IntegrityError, ValueError as SQLValueError

from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.veritabani.modeller import (
    Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
    Firma, Magaza, Terminal, Depo
)
from sontechsp.uygulama.veritabani.baglanti import sqlite_session


class TestTabloIsimlendirmeStandardi:
    """Tablo isimlendirme standardı property testleri"""
    
    @given(st.sampled_from([
        Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
        Firma, Magaza, Terminal, Depo
    ]))
    @settings(max_examples=100)
    def test_tablo_isimleri_turkce_ascii_snake_case(self, model_class):
        """
        **Feature: veritabani-migration-tamamlama, Property 4: Tablo İsimlendirme Standardı**
        
        For any model class, table name should use Turkish ASCII characters and snake_case format
        """
        table_name = model_class.__tablename__
        
        # Türkçe ASCII karakterler kontrolü (a-z, 0-9, _, ç, ğ, ı, ö, ş, ü)
        turkce_ascii_pattern = r'^[a-z0-9_çğıöşü]+$'$'
        assert re.match(turkce_ascii_pattern, table_name), \
            f"Tablo adı '{table_name}' Türkçe ASCII standardına uygun değil"
        
        # snake_case formatı kontrolü
        snake_case_pattern = r'^[a-z0-9çğıöşü]+(_[a-z0-9çğıöşü]+)*$'
        assert re.match(snake_case_pattern, table_name), \
            f"Tablo adı '{table_name}' snake_case formatında değil"
        
        # Büyük harf kontrolü
        assert table_name.islower(), \
            f"Tablo adı '{table_name}' küçük harf olmalı"
    
    @given(st.sampled_from([
        Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
        Firma, Magaza, Terminal, Depo
    ]))
    @settings(max_examples=100)
    def test_kolon_isimleri_snake_case(self, model_class):
        """
        **Feature: veritabani-migration-tamamlama, Property 4: Tablo İsimlendirme Standardı**
        
        For any model class, column names should be in snake_case format
        """
        # Model sınıfının kolonlarını al
        columns = [col.name for col in model_class.__table__.columns]
        
        for column_name in columns:
            # snake_case formatı kontrolü
            snake_case_pattern = r'^[a-z0-9çğıöşü]+(_[a-z0-9çğıöşü]+)*$'
            assert re.match(snake_case_pattern, column_name), \
                f"Kolon adı '{column_name}' snake_case formatında değil"
            
            # Büyük harf kontrolü
            assert column_name.islower(), \
                f"Kolon adı '{column_name}' küçük harf olmalı"


class TestForeignKeyButunlugu:
    """Foreign key bütünlüğü property testleri"""
    
    @pytest.fixture
    def test_db_session(self):
        """Test için SQLite session"""
        with sqlite_session() as session:
            # Test tabloları oluştur
            Taban.metadata.create_all(session.bind)
            yield session
            # Test sonrası temizlik
            Taban.metadata.drop_all(session.bind)
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters=' -.'
    )))
    @settings(max_examples=50)
    def test_firma_magaza_foreign_key_butunlugu(self, test_db_session, firma_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 5: Foreign Key Bütünlüğü**
        
        For any firma-magaza relationship, foreign key integrity should be maintained
        """
        session = test_db_session
        
        # Firma oluştur
        firma = Firma(firma_adi=firma_adi)
        session.add(firma)
        session.commit()
        
        # Mağaza oluştur
        magaza = Magaza(
            firma_id=firma.id,
            magaza_adi=f"{firma_adi} Mağaza",
            magaza_kodu="MG001"
        )
        session.add(magaza)
        session.commit()
        
        # Foreign key ilişkisini kontrol et
        assert magaza.firma_id == firma.id
        assert magaza.firma == firma
        assert magaza in firma.magazalar
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters=' -.'
    )))
    @settings(max_examples=50)
    def test_magaza_terminal_foreign_key_butunlugu(self, test_db_session, magaza_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 5: Foreign Key Bütünlüğü**
        
        For any magaza-terminal relationship, foreign key integrity should be maintained
        """
        session = test_db_session
        
        # Firma ve mağaza oluştur
        firma = Firma(firma_adi="Test Firma")
        session.add(firma)
        session.commit()
        
        magaza = Magaza(
            firma_id=firma.id,
            magaza_adi=magaza_adi,
            magaza_kodu="MG001"
        )
        session.add(magaza)
        session.commit()
        
        # Terminal oluştur
        terminal = Terminal(
            magaza_id=magaza.id,
            terminal_adi=f"{magaza_adi} Terminal",
            terminal_kodu="T001"
        )
        session.add(terminal)
        session.commit()
        
        # Foreign key ilişkisini kontrol et
        assert terminal.magaza_id == magaza.id
        assert terminal.magaza == magaza
        assert terminal in magaza.terminaller


class TestUniqueConstraintKorunumu:
    """Unique constraint korunumu property testleri"""
    
    @pytest.fixture
    def test_db_session(self):
        """Test için SQLite session"""
        with sqlite_session() as session:
            # Test tabloları oluştur
            Taban.metadata.create_all(session.bind)
            yield session
            # Test sonrası temizlik
            Taban.metadata.drop_all(session.bind)
    
    @given(st.text(min_size=3, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-'
    )))
    @settings(max_examples=50)
    def test_kullanici_adi_unique_constraint(self, test_db_session, kullanici_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 6: Unique Constraint Korunumu**
        
        For any unique constraint field, duplicate values should be rejected
        """
        session = test_db_session
        
        # İlk kullanıcı oluştur
        kullanici1 = Kullanici(
            kullanici_adi=kullanici_adi,
            email=f"{kullanici_adi}@test.com",
            sifre_hash="hash123",
            ad="Test",
            soyad="User"
        )
        session.add(kullanici1)
        session.commit()
        
        # Aynı kullanıcı adıyla ikinci kullanıcı oluşturmaya çalış
        kullanici2 = Kullanici(
            kullanici_adi=kullanici_adi,  # Aynı kullanıcı adı
            email=f"{kullanici_adi}2@test.com",
            sifre_hash="hash456",
            ad="Test2",
            soyad="User2"
        )
        session.add(kullanici2)
        
        # Unique constraint ihlali bekleniyor
        with pytest.raises(IntegrityError):
            session.commit()
    
    @given(st.text(min_size=5, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='@.-_'
    )).filter(lambda x: '@' in x and '.' in x))
    @settings(max_examples=50)
    def test_email_unique_constraint(self, test_db_session, email):
        """
        **Feature: veritabani-migration-tamamlama, Property 6: Unique Constraint Korunumu**
        
        For any unique email field, duplicate values should be rejected
        """
        session = test_db_session
        
        # İlk kullanıcı oluştur
        kullanici1 = Kullanici(
            kullanici_adi="user1",
            email=email,
            sifre_hash="hash123",
            ad="Test",
            soyad="User"
        )
        session.add(kullanici1)
        session.commit()
        
        # Aynı email ile ikinci kullanıcı oluşturmaya çalış
        kullanici2 = Kullanici(
            kullanici_adi="user2",
            email=email,  # Aynı email
            sifre_hash="hash456",
            ad="Test2",
            soyad="User2"
        )
        session.add(kullanici2)
        
        # Unique constraint ihlali bekleniyor
        with pytest.raises(IntegrityError):
            session.commit()


class TestBaglantiTestTutarliligi:
    """Bağlantı test tutarlılığı property testleri"""
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-.'
    )))
    @settings(max_examples=50)
    def test_sqlite_baglanti_test_tutarliligi(self, db_dosya_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 1: Bağlantı Test Tutarlılığı**
        
        For any valid database connection parameters, connection test should be consistent
        """
        from sontechsp.uygulama.veritabani.baglanti_yardimci import sqlite_engine_olustur, baglanti_test_et_yardimci
        import tempfile
        import os
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(suffix=f"_{db_dosya_adi}.db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Engine oluştur
            engine = sqlite_engine_olustur(db_path)
            
            # İlk test
            result1 = baglanti_test_et_yardimci(engine, "SQLite")
            
            # İkinci test (aynı parametrelerle)
            result2 = baglanti_test_et_yardimci(engine, "SQLite")
            
            # Tutarlılık kontrolü
            assert result1 == result2, "Bağlantı test sonuçları tutarlı olmalı"
            assert result1 is True, "Geçerli parametrelerle bağlantı başarılı olmalı"
            
        finally:
            # Temizlik
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_postgresql_baglanti_test_tutarliligi(self):
        """
        **Feature: veritabani-migration-tamamlama, Property 1: Bağlantı Test Tutarlılığı**
        
        For PostgreSQL connection, test should be consistent with same parameters
        """
        from sontechsp.uygulama.veritabani.baglanti import veritabani_baglanti
        
        # Aynı bağlantı ile iki kez test et
        result1 = veritabani_baglanti.baglanti_test_et("postgresql")
        result2 = veritabani_baglanti.baglanti_test_et("postgresql")
        
        # Tutarlılık kontrolü
        assert result1 == result2, "PostgreSQL bağlantı test sonuçları tutarlı olmalı"


class TestSQLiteBaglantiGuvenilirligi:
    """SQLite bağlantı güvenilirliği property testleri"""
    
    @given(st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-'
    )))
    @settings(max_examples=50)
    def test_sqlite_dosya_olusturma(self, dosya_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 2: SQLite Bağlantı Güvenilirliği**
        
        For any valid SQLite file path, connection should succeed and file should be created
        """
        from sontechsp.uygulama.veritabani.baglanti_yardimci import sqlite_engine_olustur, baglanti_test_et_yardimci
        import tempfile
        import os
        
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, f"{dosya_adi}.db")
            
            # Engine oluştur
            engine = sqlite_engine_olustur(db_path)
            
            # Bağlantı testi
            result = baglanti_test_et_yardimci(engine, "SQLite")
            
            # Kontroller
            assert result is True, "SQLite bağlantı testi başarılı olmalı"
            assert os.path.exists(db_path), "SQLite dosyası oluşturulmalı"
    
    def test_sqlite_memory_database(self):
        """
        **Feature: veritabani-migration-tamamlama, Property 2: SQLite Bağlantı Güvenilirliği**
        
        For SQLite memory database, connection should always succeed
        """
        from sontechsp.uygulama.veritabani.baglanti_yardimci import sqlite_engine_olustur, baglanti_test_et_yardimci
        
        # Memory database engine oluştur
        engine = sqlite_engine_olustur(":memory:")
        
        # Bağlantı testi
        result = baglanti_test_et_yardimci(engine, "SQLite")
        
        assert result is True, "SQLite memory database bağlantısı başarılı olmalı"


class TestBaglantiTestLoglama:
    """Bağlantı test loglama property testleri"""
    
    @given(st.sampled_from(["postgresql", "sqlite"]))
    @settings(max_examples=20)
    def test_baglanti_test_log_kaydi(self, veritabani_tipi, caplog):
        """
        **Feature: veritabani-migration-tamamlama, Property 3: Bağlantı Test Loglama**
        
        For any connection test, log record should be created regardless of result
        """
        from sontechsp.uygulama.veritabani.baglanti import veritabani_baglanti
        import logging
        
        # Log seviyesini ayarla
        caplog.set_level(logging.INFO)
        
        # Bağlantı testi yap
        try:
            result = veritabani_baglanti.baglanti_test_et(veritabani_tipi)
            
            # Log kaydı kontrolü
            log_messages = [record.message for record in caplog.records]
            
            # En az bir log kaydı olmalı
            assert len(log_messages) > 0, "Bağlantı testi log kaydı oluşturmalı"
            
            # Veritabanı tipine göre log mesajı kontrolü
            relevant_logs = [msg for msg in log_messages if veritabani_tipi.lower() in msg.lower()]
            assert len(relevant_logs) > 0, f"{veritabani_tipi} için log kaydı bulunmalı"
            
        except Exception:
            # Hata durumunda da log kaydı olmalı
            log_messages = [record.message for record in caplog.records]
            assert len(log_messages) > 0, "Hata durumunda da log kaydı oluşturulmalı"
    
    def test_sqlite_baglanti_test_log_detayi(self, caplog):
        """
        **Feature: veritabani-migration-tamamlama, Property 3: Bağlantı Test Loglama**
        
        For SQLite connection test, detailed log should be created
        """
        from sontechsp.uygulama.veritabani.baglanti_yardimci import sqlite_engine_olustur, baglanti_test_et_yardimci
        import tempfile
        import os
        import logging
        
        # Log seviyesini ayarla
        caplog.set_level(logging.INFO)
        
        # Geçici SQLite dosyası
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Engine oluştur ve test et
            engine = sqlite_engine_olustur(db_path)
            result = baglanti_test_et_yardimci(engine, "SQLite")
            
            # Log mesajlarını kontrol et
            log_messages = [record.message for record in caplog.records]
            
            # SQLite engine oluşturma logu
            engine_logs = [msg for msg in log_messages if "SQLite engine oluşturuldu" in msg]
            assert len(engine_logs) > 0, "SQLite engine oluşturma logu bulunmalı"
            
            # Bağlantı test logu
            if result:
                test_logs = [msg for msg in log_messages if "bağlantı testi başarılı" in msg]
                assert len(test_logs) > 0, "Başarılı bağlantı test logu bulunmalı"
            
        finally:
            # Temizlik
            if os.path.exists(db_path):
                os.unlink(db_path)

class TestSessionCommitDavranisi:
    """Session commit davranışı property testleri"""
    
    @pytest.fixture
    def test_db_session(self):
        """Test için SQLite session"""
        from sontechsp.uygulama.veritabani.baglanti import sqlite_session
        from sontechsp.uygulama.veritabani.taban import Taban
        
        with sqlite_session() as session:
            # Test tabloları oluştur
            Taban.metadata.create_all(session.bind)
            yield session
            # Test sonrası temizlik
            Taban.metadata.drop_all(session.bind)
    
    @given(st.text(min_size=3, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-'
    )))
    @settings(max_examples=50)
    def test_basarili_islem_commit_edilir(self, test_db_session, firma_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 7: Session Commit Davranışı**
        
        For any successful database operation, session should be automatically committed
        """
        session = test_db_session
lı"ck yapılmalba rolüm işlemlerunda teption durumsted exc"Net == 0, ma_coun  assert fir   
       count()uery(Firma).sion.q = sesirma_count         fsion:
   s sessession() ath sqlite_    wieli
    lmemydediçbir veri ka   # Hi   
     "
     akalanmalıon ytiş excepeption, "Dıt outer_exc   asser  malı"
   ion yakalanxcept"İç eption, exceert inner_ ass
       akalanmalıeption da y excer iki H #          
 e
    n = Tru_exceptio      outer   
   ror:Er Runtime    except         
  
         on")exceptir ("OutetimeErrorunaise R         rlat
       ception fırDış ex      #                  
     rue
    eption = Ter_exc   inn            r:
     lueErro except Va              
                       n")
  tioxcep"Inner ealueError(raise V                   rlat
     on fıptice ex       # İç                         
           ma)
     dd(inner_firr_session.a      inne                  Firma")
 _adi="InnerFirma(firmaer_firma = inn                      
  urluştfirma oession'da # İç s                      ession:
  _snners ission() ate_sesqliith    w                 
     try:  
              
           _firma)n.add(outerssio outer_se              
 rma")r Fi_adi="Outeirma(frma = Firma  outer_fi          ştur
    irma olusession'da f   # Dış              
          d)
      binssion._seoutereate_all(adata.craban.met         T:
       r_sessionon() as outeessih sqlite_s  wit         
    try: 
       False
     xception =     inner_e   False
 = tion  outer_excep et
       manager testntext co İç içe     #          
 ban
 n import Taabani.tabama.veritsp.uygulaontechm s fro    sion
   te_sesimport sqlibaglanti ni.taba.veri.uygulamaspom sontech        fr    """

    k correctlyuld worandling shoxception h managers, ed context nesteFor    
    *
        on Handling*er ExceptiManagtext 10: Cony ertopma, Pramlagration-tambani-mieritae: v*Featur     *"""
     f):
      dling(selception_hanr_ext_manageexnested_conttest_ def   
   
  malı"llback yapılurumunda roption dxce 0, "Ecount == firma_ert    ass       unt()
 irma).coion.query(F = sesscountma_  fir          
sion:sesas ssion()  sqlite_se        with
yapılmış)ack rollblı (lma omişedilme Veri kayd
        #  lı"
      akalanma y} exceptioname__pe.__nption_tyxce"{e_occurred, fexceptiont er     assl et
   ını kontroalandığon yak  # Excepti   
      
     ered = Truurception_occ   ex        pe:
 ption_tyxce   except e     
               
 xception")st e"Ten_type(ceptio   raise ex         ırlat
    n tipini f exceptioelirtilen   # B     
                   a)
     n.add(firmsioses              ")
  a="Test Firmma(firma_adia = Fir        firm       uştur
 irma ol        # F        
           ind)
     ssion.bate_all(secretadata. Taban.me               
session:() as ite_sessionqlwith s             try:
  
     alse Fd =recurexception_oc        le test et
Exception i        #      
t Taban
   an importabani.tabrilama.vechsp.uygusonte    from ion
    te_sesst sqlianti impori.baglbantaama.veriuluygtechsp.    from son""
     "k
       d worup shoul and cleantic rollbackr, automaanageontext mype in con txcepti   For any e    
     ling**
    Hand Exception  Manager10: Contextoperty  Prn-tamamlama,i-migratioitabanereature: v       **F"""
       ype):
  eption_telf, excandling(s_hreurlerine_goxception_t def test_e0)
   ples=2gs(max_examsettin))
    @
    ]eErroributError, Attrror, Type, RuntimeEr  ValueError     from([
 pled_t.samiven(s@g
    
    """tleriproperty teson handling ceptier exanag""Context m  "andling:
  ptionHerExceContextManag Test

classtılmalı"
kapassion  sonrası septiontive, "Excef.is_act session_re assert noı"
       ınmal alsıion referanne, "Sess No_ref is notionrt sess        asseiş olmalı
lenmession temiz# S             
  niyor
 klexception be E  pass  #
          meError: Runti      except
                ")
  t exception"TestimeError(Run     raise            at
ion fırlcept# Ex             
                   dd(firma)
.a  session           rma")
   st Fi_adi="TermaFirma(fi = irma      f          ma oluştur
       # Fir             
            ession
sion_ref = s    ses        .bind)
    ssion_all(sedata.createTaban.meta            
    on:sessiion() as _sessitesql     with :
        try et
       ager testontext man ile cionept     # Exc     
 ne
     ref = Nosion_es
        s
        Tabanmport i.taban iritabanygulama.veechsp.u from sont       on
e_sessilitport sqaglanti imeritabani.bulama.vp.uygm sontechs   fro""
         "ns
    exception even with ould happeeanup sh clnager,matext    For con 
     
       Temizliği**ak ion Kayny 9: Sessama, Propertmamlgration-tabani-mirita veeature:     **F"""
   ):
        ock(selfinally_bl_manager_ft_contextdef tes  
    
  lı"gisi korunma bil bindion, "Sessned is not Noion.bin assert sess           
 olmalı"patılmışn kave, "Sessiocti.is_asessiont sert no     as:
       sionsion in ses  for sesslı
      olmatılmış ar kapa session'lTüm    #     
  
      lik olmalıizında temış çıkext managerCont   #            
              )
    (firmaion.add   sess            {i}")
 irma est Fa_adi=f"Tfirm = Firma(     firma         
  işlem yap  # Basit              
                 ssion)
append(seions.        sess       )
  içinreferanssteye ekle (Session'ı li         #           
       ind)
      .bll(sessiona.create_adataban.meta        T       session:
 () as ssionh sqlite_seit         wayisi):
   ge(session_sn ranfor i i
        atkape ur vssion oluştfazla se# Birden            
   
  ions = []        sess    
n
    aban import Ttabaeritabani.p.uygulama.vontechs   from ssion
      sqlite_ses importani.baglantiitabama.verechsp.uygulntom so     fr"""
           it
exn rmed operfould be eanup sho cl, resourcen usagey sessio  For an   
        ği**
   izlin Kaynak TemssioSey 9: ma, Properton-tamamlamigrativeritabani-: ure      **Feat    """

      yisi):n_saself, sessio_temizligi(a_kaynakssion_kapanm test_se    defles=20)
gs(max_examptin))
    @setx_value=101, mae=valuntegers(min_ven(st.i @gi 
   "
   ri""tley tesropertemizliği pkaynak t"Session "   "
 zligi:nakTemissionKayclass TestSeı"


al yapılmackda rollbon durumunpti 0, "Excerma_count == assert fi     
      .count()ma)ry(Firon.quet = sessiounfirma_c       sion:
     s ses aon()sie_ses with sqliteli
       ilmemveri kaydedr çbi hiol et - Kontr   #     
     r
   niyobekleException s  #  pas
           ValueError:     except  
               
   ption")xceTest eError("alueise V          ralat
      on fıreptiasıtlı exc         # K
                       firma)
ession.add(    s         
    Firma")st"Te(firma_adi= Firmama =fir                 oluştur
  # Firma              
            bind)
    all(session..create_.metadata   Taban            session:
 on() as sqlite_sessi with        
    ry:    t
     test ett manager ile contex Exception     #   
   n
     bat Taan imporritabani.tabygulama.ventechsp.uso   from     e_session
 import sqlitaglanti bani.bama.veritahsp.uygulntecsofrom        "
  ""     
   automaticshould beback er, rollt managntexcoin ion ptr any exce   Fo     
     
   nışı**ck Davrabaion Rollty 8: Sessera, Propamlamion-tam-migrat: veritabani  **Feature"
         ""    k(self):
 acndling_rollbtion_ha test_excep
    def
    "lıpılmallback yaumunda roa dur == 1, "Hatfirmalar)ssert len(           a).all()
 i=firma_adiirma_adfilter_by(f(Firma).ryn.quear = sessio      firmaln:
       sessioion() as sqlite_sess    with
    a olmalık firmadece il- s Kontrol et  # 
             
 ekleniyora b  # Hatass        ption:
    except Excep        yapılacak
ollback  ve rşacaka burada olu     # Hat           irma2)
sion.add(f     ses      
      Aynı isimdi)  #rma_arma_adi=firma(fi firma2 = Fi            ession:
   ion() as ssssqlite_se     with      
  try:)
         olacakçalış (hatauşturmaya rma olnci fiimle iki # Aynı is
       
        a1)(firmssion.add          se  a_adi)
ma_adi=firmirma(fir firma1 = F        .bind)
   ssionate_all(sea.cretadatn.me        Taba
    s session:ion() assh sqlite_se    witur
     oluşt # İlk firma
       
        rorErntegrityport Ichemy.exc imfrom sqlaln
        t Tabaan imporbani.tabrita.uygulama.veom sontechsp      fr_session
  itei import sqlntaglaeritabani.bgulama.vhsp.uy sontec  from
      ""
        "ed backtically rollbe automauld ho, session s condition error  For any     
         şı**
back Davranıoll R Sessionty 8:, Properamamlamaion-tbani-migrat: veritaure  **Feat       """

       a_adi):self, firmollback(munda_r_duruataest_hdef t  =50)
  amplesx_exngs(masetti @    )))
   
_-'characters='ist_tel   whi, 
     Ll', 'Nd'), 'Lu'('ries=egot_catwhitelis
        (rs=st.characteet alphab=50,_sizeze=3, max_si.text(min   @given(st    
 d)
session.binll(rop_adata.dban.meta      Ta      ı temizlik
 Test sonras           #d session
     yiel
        ion.bind)sesscreate_all(n.metadata.  Taba
          urları oluştlo# Test tab           :
 as sessionion() esslite_sh sq    wit
      ban
      mport Taan ibani.tabveritasp.uygulama.m sontechfro      n
  _sessioqliteort sti impni.baglanritabauygulama.vep.om sontechs fr       sion"""
 sesQLite Sinest iç"T       ""(self):
 sionest_db_ses
    def ture@pytest.fixt
    
    ri"""perty testlenışı prok davraion rollbacss  """Se  si:
backDavranissionRollclass TestSeeli"


ilmğru kaydeddoeri ma_adi, "Vir== fma_adi firma.firaved_rt s asse          pmalı"
  commit yamatik otoagertext manConnot None, "ed_firma is ssert sav       a   rst()
  fi).adima_di=firfirma_a.filter_by(query(Firma)new_session._firma = ved       saion:
     _sess new() aslite_session   with sqet
     e kontrol  session ilni      # Ye        
  lmalı
mmit ootomatik conda r çıkışıaget man  # Contex      a)
    add(firmion.ss      se
      irma_adi)=f_adirma(firma firma = Fi     
      uşturirma ol    # F         
        ind)
   l(session.breate_aletadata.c    Taban.m   
     arı oluşturtablolest      # T       on:
() as sessiessionith sqlite_s      wp
  yar ile işlem ntext manage# Co    
     
       nTabat n imporbaani.taitaberygulama.vntechsp.uom so   frsion
     ite_sesort sqlanti impni.baglama.veritabasp.uygulntechom so        fr  """
  matic
    auto be mmit shouldnager, coext man in conttio operaful successny      For a   
  ı**
     mit Davranışion Com Sess 7: Propertytamamlama,igration-abani-mite: vereatur
        **F"" "
       ):rma_adi(self, fiik_commitatager_otomtext_man_con test   def
 mples=50)exas(max_ @setting
      )))-.'
 aracters=' st_chwhiteli 
        l', 'Nd'),=('Lu', 'Liestegorist_ca whitel       
ters(t=st.characbelphasize=50, a, max_size=1t.text(min_(sgiven   @
 i"
    aydedilmelVeri doğru k, "firma_adima_adi == _firma.firert saved         ass"
   eli edilmcommitı işlem aşarıl "Bot None,irma is n saved_fsert      as
      ()adi).firstma_ma_adi=fir(fir.filter_byry(Firma)_session.que_firma = new      saved:
      sion as new_sesession()ite_ssql      with ession
  e_simport sqlitglanti bani.baeritaama.v.uygulchspfrom sonte    rol et
    onte ksion il  # Yeni ses
        
      commit()ion.     sess   lı)
matik olmato(commit oık  çsion'dan       # Ses       
 (firma)
 ssion.add    se_adi)
    firmai=irma_ada(fa = Firm        firm oluştur
# Firma                
