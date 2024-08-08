from django.urls import path
from hrd_app import views

urlsAjaxLembur = [
    path('blembur', views.batal_lembur, name='blembur'),
    path('bayar_lembur', views.bayar_lembur, name='bayar_lembur'),
    
    path('dlembur_json/<int:idp>/<int:prd>/<int:thn>', views.lembur_json, name='dlembur_json'),
    path('dkompen_json/<int:idp>/<int:prd>/<int:thn>', views.kompen_json, name='dkompen_json'),
    path('lembur_json/<int:sid>/<int:prd>/<int:thn>', views.rekap_lembur_json, name='lembur_json'),
    path('lembur_bproses_json/<int:sid>', views.lembur_belum_proses_json, name='lembur_bproses_json'),
]


urlsRenderLembur = [
    path('lembur/<int:sid>', views.lembur, name='lembur'),
    path('cari_lembur', views.cari_lembur, name='clembur'),
    path('belum_proses/<int:sid>', views.lembur_belum_proses, name='lembur_bproses'),
    path('proses_ulembur/<int:idl>', views.proses_ulang_lembur, name='proses_ulembur'),
    path('tlembur', views.tambah_lembur, name='tlembur'),
]