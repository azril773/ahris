from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login') # Added last_login


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(akses_db)
class akses(ImportExportModelAdmin):
    list_display = ('user','akses','sid')
    list_per_page = 30    
    
    
@admin.register(akses_divisi_db)
class akses_divisi(ImportExportModelAdmin):
    list_display = ('user','divisi')  
    search_fields = ('user__username',)             


@admin.register(mesin_db)
class mesin(ImportExportModelAdmin):
    search_fields = ('nama','ipaddress')
    list_display = ('nama','ipaddress','status')
    list_per_page = 30
    

@admin.register(status_pegawai_db)
class status_pegawai(ImportExportModelAdmin):
    search_fields = ('status',)
    list_display = ('status',)
    list_per_page = 30
    
    
@admin.register(divisi_db)
class divisi(ImportExportModelAdmin):
    search_fields = ('divisi','alias')
    list_display = ('divisi',)
    list_per_page = 30
    
    
@admin.register(jabatan_db)
class jabatan(ImportExportModelAdmin):
    search_fields = ('jabatan',)
    list_display = ('jabatan',)
    list_per_page = 30
    
    
@admin.register(kelompok_kerja_db)
class kelompok_kerja(ImportExportModelAdmin):
    search_fields = ('kelompok',)
    list_display = ('kelompok',)
    list_per_page = 30  
    
    
@admin.register(counter_db)
class counter(ImportExportModelAdmin):
    search_fields = ('counter',)
    list_display = ('counter',)
    list_per_page = 30
 
    
@admin.register(hari_db)
class hari(ImportExportModelAdmin):
    search_fields = ('hari',)
    list_display = ('hari',)
    list_per_page = 30


@admin.register(libur_nasional_db)
class libur_nasional(ImportExportModelAdmin):
    search_fields = ('libur','tgl_libur','insentif_karyawan','insentif_staff')
    list_display = ('libur','tgl_libur','insentif_karyawan','insentif_staff')
    list_per_page = 30
  
    
@admin.register(jenis_ijin_db)
class jenis_ijin(ImportExportModelAdmin):
    search_fields = ('jenis_ijin',)
    list_display = ('jenis_ijin',)
    list_per_page = 30
    
    
@admin.register(pegawai_db)
class pegawai(ImportExportModelAdmin):
    search_fields = ('nama','nik','userid')
    list_display = ('nama','nik','userid','status','divisi','hari_off','aktif','edit_by','edit_date')
    list_per_page = 50    
    
    
@admin.register(jamkerja_db)
class jam_kerja(ImportExportModelAdmin):
    list_display = ('hari',)
    
    
@admin.register(list_status_opg_db)
class status_opg(ImportExportModelAdmin):
    list_display = ('status',)


@admin.register(awal_cuti_db)
class awal_cuti(ImportExportModelAdmin):
    list_display = ('tgl',)
    
    
@admin.register(tutup_toko_db)
class tutup_toko(ImportExportModelAdmin):
    list_display = ('hari',)
    
    
@admin.register(rp_lembur_db)
class rupiah_lembur(ImportExportModelAdmin):
    list_display = ('rupiah',)
    
    
@admin.register(keluarga_db)
class keluarga(ImportExportModelAdmin):
    list_display = ('pegawai','hubungan','nama','tgl_lahir','gender','gol_darah')
    
    
@admin.register(status_pegawai_lembur_db)
class status_pegawai_lembur(ImportExportModelAdmin):
    list_display = ('status_pegawai',)                    


@admin.register(status_pegawai_lintas_hari_db)
class status_pegawai_lintas_hari(ImportExportModelAdmin):
    list_display = ('status_pegawai',)                    


@admin.register(data_raw_db)
class data_raw(ImportExportModelAdmin):
    list_display = ('userid','jam_absen','punch') 
    
    
@admin.register(data_trans_db)
class data_trans(ImportExportModelAdmin):
    list_display = ('userid','jam_absen','punch')                       
                
    
admin.site.site_header = "AHRIS"
admin.site.site_title = "AHRIS"
admin.site.site_url = "/hrd/pengaturan"    