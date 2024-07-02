from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('logindispatch', views.logindispatch, name='dispatch'),
    path('login', auth_views.LoginView.as_view(template_name='hrd_app/login.html'), name='login'),
    path('logout', views.user_logout, name='logout'),
    
    path('', views.beranda, name='beranda'), 
    path('noakses', views.beranda_no_akses, name='noakses'), 
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Pegawai
    
    path('pegawai/<int:sid>', views.pegawai, name='pegawai'),
    path('epegawai/<int:idp>', views.edit_pegawai, name='epegawai'),
    path('non_aktif/<int:sid>', views.pegawai_non_aktif, name='non_aktif'),
    
    path('tkeluarga/<int:idp>', views.tambah_keluarga, name='tkeluarga'),
    path('tkl/<int:idp>', views.tambah_kl, name='tkl'),
    
    path('anon', views.aktif_nonaktif, name='anon'),
    
    path('general_data/<int:idp>', views.general_data, name='general_data'),
    path('dapri/<int:idp>', views.data_pribadi, name='dapri'),
    path('pkerja/<int:idp>', views.pendidikan_kerja, name='pkerja'),
    path('prodemo/<int:idp>', views.promosi_demosi, name='prodemo'),
    path('sangsi/<int:idp>', views.sangsi, name='sangsi'),
    
    path('pegawai_json/<int:sid>', views.pegawai_json, name='pegawai_json'),
    path('non_aktif_json/<int:sid>', views.non_aktif_json, name='non_aktif_json'),
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Absensi
    
    path('absensi/<int:sid>', views.absensi, name='absensi'),
    path('cabsen', views.cari_absensi, name='cabsen'),  
    path('cabsen_s/<str:dr>/<str:sp>/<int:sid>', views.cari_absensi_sid, name='cabsen_s'),
    path('absensi_json/<str:dr>/<str:sp>/<int:sid>', views.absensi_json, name='absensi_json'),    
    
    path('pbs', views.pabsen, name='pbs'),    
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
    # Ijin
    
    path('ijin/<int:sid>', views.ijin, name='ijin'),
    path('cijin', views.cari_ijin, name='cijin'),
    path('cijin_s/<str:dr>/<str:sp>/<int:sid>', views.cari_ijin_sid, name='cijin_s'),
    path('ijin_json/<str:dr>/<str:sp>/<int:sid>', views.ijin_json, name='ijin_json'),    
       
    path('tijin', views.tambah_ijin, name='tijin'),
    path('bijin', views.batal_ijin, name='bijin'),
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Geser OFF
    
    path('geser_off/<int:sid>', views.geser_off, name='geser_off'),
    path('cgeser_off', views.cari_geser_off, name='cgeser_off'),
    path('cgeser_off_s/<str:dr>/<str:sp>/<int:sid>', views.cari_geser_off_sid, name='cgeser_off_s'),
    path('gf_json/<str:dr>/<str:sp>/<int:sid>', views.geseroff_json, name='gf_json'),
    
    path('tgf', views.tambah_geseroff, name='tgf'),
    path('bgf', views.batal_geseroff, name='bgf'),
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # OPG
    
    path('opg/<int:sid>', views.opg, name='opg'),
    path('copg', views.cari_opg, name='copg'),
    path('copg_s/<str:dr>/<str:sp>/<int:sid>', views.cari_opg_sid, name='copg_s'),
    path('opg_json/<str:dr>/<str:sp>/<int:sid>', views.opg_json, name='opg_json'),
    
    path('topg', views.tambah_opg, name='topg'),
    path('popg', views.pakai_opg, name='popg'),
    path('bopg', views.batal_opg, name='bopg'),
    path('hopg', views.hapus_opg, name='hopg'),
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Cuti
    
    path('cuti/<int:sid>', views.cuti, name='cuti'),
    path('dcuti/<int:sid>/<int:idp>', views.detail_cuti, name='dcuti'),   
    
    path('cuti_json/<str:dr>/<str:sp>/<int:sid>', views.cuti_json, name='cuti_json'),
    path('dcuti_json/<int:idp>', views.dcuti_json, name='dcuti_json'),
    
    path('ccuti', views.cari_cuti, name='ccuti'),
    path('tcuti', views.tambah_cuti, name='tcuti'),
    path('ecuti', views.edit_sisa_cuti, name='ecuti'),
    path('bcuti', views.batal_cuti, name='bcuti'),    
    
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Lembur
    
    path('lembur/<int:sid>', views.lembur, name='lembur'),
    path('clembur', views.cari_lembur, name='clembur'),
    path('lembur_bproses/<int:sid>', views.lembur_belum_proses, name='lembur_bproses'),
    path('proses_ulembur/<int:idl>', views.proses_ulang_lembur, name='proses_ulembur'),
    path('blembur', views.batal_lembur, name='blembur'),
    path('bayar_lembur', views.bayar_lembur, name='bayar_lembur'),
    
    path('tlembur', views.tambah_lembur, name='tlembur'),
    path('dlembur_json/<int:idp>/<int:prd>/<int:thn>', views.lembur_json, name='dlembur_json'),
    path('dkompen_json/<int:idp>/<int:prd>/<int:thn>', views.kompen_json, name='dkompen_json'),
    path('lembur_json/<int:sid>/<int:prd>/<int:thn>', views.rekap_lembur_json, name='lembur_json'),
    path('lembur_bproses_json/<int:sid>', views.lembur_belum_proses_json, name='lembur_bproses_json'),
    
    path('tkompen', views.tambah_kompen, name='tkompen'),
    path('bkompen', views.batal_kompen, name='bkompen'),
    
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Pengaturan
    
    path('pengaturan', views.pengaturan, name='pengaturan'),
    
    path('status_pegawai', views.status_pegawai, name='status_pegawai'),
    path('status_pegawai_json', views.status_pegawai_json, name='status_pegawai_json'),
    path('tstatus_pegawai', views.tambah_status_pegawai, name='tstatus_pegawai'),
    path('estatus_pegawai', views.edit_status_pegawai, name='estatus_pegawai'),
    path('hstatus_pegawai', views.hapus_status_pegawai, name='hstatus_pegawai'),
    
    path('divisi', views.divisi, name='divisi'),
    path('divisi_json', views.divisi_json, name='divisi_json'),
    path('tdivisi', views.tambah_divisi, name='tdivisi'),
    path('edivisi', views.edit_divisi, name='edivisi'),
    path('hdivisi', views.hapus_divisi, name='hdivisi'),
    
    path('counter', views.counter, name='counter'),
    path('counter_json', views.counter_json, name='counter_json'),
    path('tcounter', views.tambah_counter, name='tcounter'),
    path('ecounter', views.edit_counter, name='ecounter'),
    path('hcounter', views.hapus_counter, name='hcounter'),
    
    path('libur_nasional', views.libur_nasional, name='libur_nasional'),
    path('libur_nasional_json', views.libur_nasional_json, name='libur_nasional_json'),
    path('tlibur_nasional', views.tambah_libur_nasional, name='tlibur_nasional'),
    path('elibur_nasional', views.edit_libur_nasional, name='elibur_nasional'),
    path('hlibur_nasional', views.hapus_libur_nasional, name='hlibur_nasional'),
    
    path('jam_kerja', views.jam_kerja, name='jam_kerja'),
    # path('jam_kerja_json', views.jam_kerja_json, name='jam_kerja_json'),
    path('tkk_json', views.tambah_kk_json, name='tkk_json'),
    
    path('jenis_ijin', views.jenis_ijin, name='jenis_ijin'),
    path('status_pegawai_lembur', views.status_pegawai_lembur, name='status_pegawai_lembur'),
    
    ]