from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from hrd_app.router.pegawai.router import urlsAjaxPegawai, urlsRenderPegawai
# from hrd_app.router.absensi.router import urlsAjaxAbsensi, urlsRenderAbsensi
from hrd_app.router.ijin.router import urlsAjaxIjin, urlsRenderIjin
from hrd_app.router.geser_off.router import urlsAjaxGeserOff, urlsRenderGeserOff
from hrd_app.router.opg.router import urlsAjaxOpg, urlsRenderOpg
from hrd_app.router.status_pegawai.router import urlsAjaxStatusPegawai, urlsRenderStatusPegawai
from hrd_app.router.cuti.router import urlsAjaxCuti, urlsRenderCuti
from hrd_app.router.lembur.router import urlsAjaxLembur, urlsRenderLembur
from hrd_app.router.divisi.router import urlsAjaxDivisi, urlsRenderDivisi
from hrd_app.router.counter.router import urlsAjaxCounter, urlsRenderCounter
from hrd_app.router.libur_nasional.router import urlsAjaxLiburNasional, urlsRenderLiburNasional
from hrd_app.router.jam_kerja.router import urlsAjaxJamKerja, urlsRenderJamKerja
urlpatterns = [
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Pegawai
    # urlsAjaxPegawai[0]
    path("", include(urlsAjaxPegawai)),
    path("", include(urlsRenderPegawai)),
    
    path('tkeluarga/<int:idp>', views.tambah_keluarga, name='tkeluarga'),
    path('tkl/<int:idp>', views.tambah_kl, name='tkl'),
    
    path('anon', views.aktif_nonaktif, name='anon'),
    
    path('general_data/<int:idp>', views.general_data, name='general_data'),
    path('dapri/<int:idp>', views.data_pribadi, name='dapri'),
    path('pkerja/<int:idp>', views.pendidikan_kerja, name='pkerja'),
    path('prodemo/<int:idp>', views.promosi_demosi, name='prodemo'),
    path('tambah_prodemo/',views.tambah_prodemo,name="tambah_prodemo"),
    path("promodemo_json/<int:idp>",views.promodemo_json,name="promodemo_json"),
    path('sangsi/<int:idp>', views.sangsi, name='sangsi'),
    path('get_sangsi_pegawai/<int:idp>', views.get_sangsi_pegawai, name='get_sangsi_pegawai'),
    path('sangsi_json/<int:idp>', views.sangsi_json, name='sangsi_json'),
    path('tambah_sangsi/<int:idp>', views.tambah_sangsi, name='tambah_sangsi'),
    
    path('pegawai_json/<int:sid>', views.pegawai_json, name='pegawai_json'),
    path('non_aktif_json/<int:sid>', views.non_aktif_json, name='non_aktif_json'),
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Absensi Ajax
    path("", include("hrd_app.router.absensi.urls")),    
    # Absensi Render
    # path("", include("router.absensi.urls")),
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
     
    

    # Ijin Ajax
    path("", include(urlsAjaxIjin)),

    # Ijin Render
    path("", include(urlsRenderIjin)),



    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    
    
    # Geser OFF Ajax
    path("", include(urlsAjaxGeserOff)),
    # Geser OFF Render
    path("", include(urlsRenderGeserOff)),




    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   
   
   
   
    # OPG Ajax
    path("", include(urlsAjaxOpg)),

    # OPG Render
    path("", include(urlsRenderOpg)),




    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    
    
    # Cuti Ajax
    path("", include(urlsAjaxCuti)),

    # Cuti Render
    path("", include(urlsRenderCuti)),




    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
    # Lembur Ajax
    path("", include(urlsAjaxLembur)),

    # Lembur Render
    path("", include(urlsRenderLembur)),

    
    path('tkompen', views.tambah_kompen, name='tkompen'),
    path('bkompen', views.batal_kompen, name='bkompen'),
    
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Pengaturan
    path('pengaturan', views.pengaturan, name='pengaturan'),

    # status pegawai
    path("", include(urlsAjaxStatusPegawai)),
    path("", include(urlsRenderStatusPegawai)),

    # divisi
    path("", include(urlsAjaxDivisi)),
    path("", include(urlsRenderDivisi)),

    # counter
    path("", include(urlsAjaxCounter)),
    path("", include(urlsRenderCounter)),
    
    # libur nasional
    path("", include(urlsAjaxLiburNasional)),
    path("", include(urlsRenderLiburNasional)),
    
    # jam_kerja
    path("", include(urlsAjaxJamKerja)),
    path("", include(urlsRenderJamKerja)),
    
    



    


    
    


]