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
    list_display = ('user_id','divisi')  


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
    
    
@admin.register(list_pegawai_opg_db)
class pegawai_opg(ImportExportModelAdmin):
    list_display = ('pegawai',)


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
    list_display = ("pegawai","nama","hubungan",'gender')
    
    
@admin.register(list_pegawai_lembur_db)
class pegawai_lembur(ImportExportModelAdmin):
    list_display = ('pegawai',)                    


@admin.register(status_pegawai_lintas_hari_db)
class status_pegawai_lintas_hari(ImportExportModelAdmin):
    list_display = ('status_pegawai',)                    


@admin.register(data_raw_db)
class data_raw(ImportExportModelAdmin):
    list_display = ('userid','jam_absen','punch') 
    
    
@admin.register(data_trans_db)
class data_trans(ImportExportModelAdmin):
    list_display = ('userid','jam_absen','punch')                       

@admin.register(pribadi_db)
class data_pribadi(ImportExportModelAdmin):
    list_display = ('pegawai','alamat','kota_lahir','tgl_lahir')

@admin.register(kontak_lain_db)
class kontak_lain(ImportExportModelAdmin):
    list_display =  ("pegawai","hubungan",'nama')

# @admin.register(pendidikan_db)
# class pendidikan(ImportExportModelAdmin):
#     list_display = ("pegawai","nama","kota","dari_tahun","sampai_tahun","jurusan","gelar")

# @admin.register(pengalaman_db)
# class pengalaman_db(ImportExportModelAdmin):
#     list_display = ("pegawai","perusahaan","kota","dari_tahun","sampai_tahun","jabatan")

@admin.register(kota_kabupaten_db)
class kota_kabupaten(ImportExportModelAdmin):
    list_display = ("nama_koka",)
    
@admin.register(cuti_db)
class cuti_db(ImportExportModelAdmin):
    list_display = ("pegawai","tgl_cuti")
@admin.register(promosi_demosi_db)
class promo_demo(ImportExportModelAdmin):
    list_display = ("pegawai","tgl","status")

@admin.register(sangsi_db)
class sangsi(ImportExportModelAdmin):
    list_display = ("pegawai","tgl_berlaku","tgl_berakhir")

@admin.register(ijin_db)
class ijin(ImportExportModelAdmin):
    list_display = ("pegawai","ijin")
@admin.register(geseroff_db)
class ijin(ImportExportModelAdmin):
    list_display = ("pegawai","dari_tgl","ke_tgl")

@admin.register(absensi_db)
class absensi(ImportExportModelAdmin):
    list_display = ("pegawai","tgl_absen")
@admin.register(lembur_db)
class lembur(ImportExportModelAdmin):
    list_display = ("tgl_lembur","pegawai")
@admin.register(rekap_lembur_db)
class lembur(ImportExportModelAdmin):
    list_display = ("periode","tahun","pegawai")
@admin.register(kompen_db)
class lembur(ImportExportModelAdmin):
    list_display = ("tgl_kompen","pegawai")
@admin.register(opg_db)
class lembur(ImportExportModelAdmin):
    list_display = ("opg_tgl",)
# @admin.register(akses_cabang_db)
# class lembur(ImportExportModelAdmin):
#     list_display = ("user","cabang")
admin.site.site_header = "AHRIS"
admin.site.site_title = "AHRIS"
admin.site.site_url = "/hrd/pengaturan"    

class MultiDBModelAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(
            db_field, request, using=self.using, **kwargs
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(
            db_field, request, using=self.using, **kwargs
        )
    
class CirebonAdmin(MultiDBModelAdmin):
    using = "cirebon"

class TasikAdmin(MultiDBModelAdmin):
    using = "tasik"

class SumedangAdmin(MultiDBModelAdmin):
    using = "sumedang"

class CihideungAdmin(MultiDBModelAdmin):
    using = "cihideung"
class GarutAdmin(MultiDBModelAdmin):
    using = "garut"


cirebon = admin.AdminSite("cirebon")
tasik = admin.AdminSite("tasik")
sumedang = admin.AdminSite("sumedang")
garut = admin.AdminSite("garut")
cihideung = admin.AdminSite("cihideung")


cirebon.register(awal_cuti_db,CirebonAdmin)
tasik.register(awal_cuti_db,TasikAdmin)
sumedang.register(awal_cuti_db,TasikAdmin)
garut.register(awal_cuti_db,TasikAdmin)
cihideung.register(awal_cuti_db,TasikAdmin)