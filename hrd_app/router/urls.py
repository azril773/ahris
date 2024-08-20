from django.urls import path,include
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('logindispatch', views.logindispatch, name='dispatch'),
    path('login', auth_views.LoginView.as_view(template_name='hrd_app/login.html'), name='login'),
    path('logout', views.user_logout, name='logout'),
    
    path('', views.beranda, name='beranda'),

    # +++++++++++++++++++ URLS ABSENSI +++++++++++++++++++
    path('', include("hrd_app.router.absensi.ui.urls")),
    path('', include("hrd_app.router.absensi.backend.urls")),
    # +++++++++++++++++++ URLS ABSENSI +++++++++++++++++++

    # +++++++++++++++++++ URLS COUNTER +++++++++++++++++++
    path('', include("hrd_app.router.counter.ui.urls")),
    path('', include("hrd_app.router.counter.backend.urls")),
    # +++++++++++++++++++ URLS COUNTER +++++++++++++++++++

    # +++++++++++++++++++ URLS CUTI +++++++++++++++++++
    path('', include("hrd_app.router.cuti.ui.urls")),
    path('', include("hrd_app.router.cuti.backend.urls")),
    # +++++++++++++++++++ URLS CUTI +++++++++++++++++++

    # +++++++++++++++++++ URLS DIVISI +++++++++++++++++++
    path('', include("hrd_app.router.divisi.ui.urls")),
    path('', include("hrd_app.router.divisi.backend.urls")),
    # +++++++++++++++++++ URLS DIVISI +++++++++++++++++++

    # +++++++++++++++++++ URLS GESER OFF +++++++++++++++++++
    path('', include("hrd_app.router.geser_off.ui.urls")),
    path('', include("hrd_app.router.geser_off.backend.urls")),
    # +++++++++++++++++++ URLS GESER OFF +++++++++++++++++++

    # +++++++++++++++++++ URLS IJIN +++++++++++++++++++
    path('', include("hrd_app.router.ijin.ui.urls")),
    path('', include("hrd_app.router.ijin.backend.urls")),
    # +++++++++++++++++++ URLS IJIN +++++++++++++++++++

    # +++++++++++++++++++ URLS JAM KERJA +++++++++++++++++++
    path('', include("hrd_app.router.jam_kerja.ui.urls")),
    path('', include("hrd_app.router.jam_kerja.backend.urls")),
    # +++++++++++++++++++ URLS JAM KERJA +++++++++++++++++++

    # +++++++++++++++++++ URLS LEMBUR +++++++++++++++++++
    path('', include("hrd_app.router.lembur.ui.urls")),
    path('', include("hrd_app.router.lembur.backend.urls")),
    # +++++++++++++++++++ URLS LEMBUR +++++++++++++++++++

    # +++++++++++++++++++ URLS LIBUR NASIONAL +++++++++++++++++++
    path('', include("hrd_app.router.libur_nasional.ui.urls")),
    path('', include("hrd_app.router.libur_nasional.backend.urls")),
    # +++++++++++++++++++ URLS LIBUR NASIONAL +++++++++++++++++++

    # +++++++++++++++++++ URLS OPG +++++++++++++++++++
    path('', include("hrd_app.router.opg.ui.urls")),
    path('', include("hrd_app.router.opg.backend.urls")),
    # +++++++++++++++++++ URLS OPG +++++++++++++++++++

    # +++++++++++++++++++ URLS PEGAWAI +++++++++++++++++++
    path('', include("hrd_app.router.pegawai.ui.urls")),
    path('', include("hrd_app.router.pegawai.backend.urls")),
    # +++++++++++++++++++ URLS PEGAWAI +++++++++++++++++++

    # +++++++++++++++++++ URLS STATUS PEGAWAI +++++++++++++++++++
    path('', include("hrd_app.router.status_pegawai.ui.urls")),
    path('', include("hrd_app.router.status_pegawai.backend.urls")),
    # +++++++++++++++++++ URLS STATUS PEGAWAI +++++++++++++++++++

    # +++++++++++++++++++ URLS PRODEMO +++++++++++++++++++
    path('', include("hrd_app.router.prodemo.ui.urls")),
    path('', include("hrd_app.router.prodemo.backend.urls")),
    # +++++++++++++++++++ URLS PRODEMO +++++++++++++++++++

    # +++++++++++++++++++ URLS SANGSI +++++++++++++++++++
    path('', include("hrd_app.router.sangsi.ui.urls")),
    path('', include("hrd_app.router.sangsi.backend.urls")),
    # +++++++++++++++++++ URLS SANGSI +++++++++++++++++++

    
    path('pengaturan', views.pengaturan, name='pengaturan'),



    
]