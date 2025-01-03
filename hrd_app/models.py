from django.db import models
from django.contrib.auth.models import User
from django.db import connection


# Mesin
# ==================================================================

pilihan_aktif = (("Active", "Active"),("Non Active", "Non Active"))

class mesin_db(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    ipaddress = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=100, choices=pilihan_aktif, default='Active')

    def __str__(self):
        return self.nama
    
    class Meta:
        verbose_name = 'Mesin'
        verbose_name_plural = 'Mesin'
    


# Data pegawai di mesin
# ==================================================================    
class datamesin_db(models.Model):
    uid = models.IntegerField()
    nama = models.CharField(max_length=100, null=True)
    userid = models.CharField(max_length=100, unique=True, null=True)
    level = models.IntegerField()
    password = models.CharField(max_length=20, null=True)

    def __int__(self):
        return self.uid

    class Meta:
        verbose_name = 'Data Mesin'
        verbose_name_plural = 'Data Mesin'    
        
        
class sidikjari_db(models.Model):
    uid = models.IntegerField()
    nama = models.CharField(max_length=100, null=True)
    userid = models.CharField(max_length=100, null=True)    
    size = models.IntegerField()
    fid = models.IntegerField()
    valid = models.IntegerField()
    template = models.BinaryField()

    def __str__(self):
        return self.userid        
    
    class Meta:
        verbose_name = 'Sidik Jari'
        verbose_name_plural = 'Sidik Jari'  
        


# Data Master
# ==================================================================
class status_pegawai_db(models.Model):
    status = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Status Pegawai'
        verbose_name_plural = 'Status Pegawai'
        
        
class divisi_db(models.Model):
    divisi = models.CharField(max_length=100, unique=True)
    alias = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.divisi

    class Meta:
        verbose_name = 'Divisi'
        verbose_name_plural = 'Divisi' 
        
        
class jabatan_db(models.Model):
    jabatan = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.jabatan

    class Meta:
        verbose_name = 'Jabatan'
        verbose_name_plural = 'Jabatan'   
        
        
class kelompok_kerja_db(models.Model):
    kelompok = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.kelompok

    class Meta:
        verbose_name = 'Kelompok Kerja'
        verbose_name_plural = 'Kelompok Kerja'   
        
        
class counter_db(models.Model):
    counter = models.CharField(max_length=100)

    def __str__(self):
        return self.counter

    class Meta:
        verbose_name = 'Counter'
        verbose_name_plural = 'Counter'           
           
        
class hari_db(models.Model):
    hari = models.CharField(max_length=50)

    def __str__(self):
        return self.hari

    class Meta:
        verbose_name = 'Nama Hari'
        verbose_name_plural = 'Nama Hari'      


class libur_nasional_db(models.Model):
    libur = models.CharField(max_length=100)
    tgl_libur = models.DateField()
    insentif_karyawan = models.IntegerField(null=True, blank=True, default=20000)
    insentif_staff = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.libur

    class Meta:
        verbose_name = 'Libur Nasional'
        verbose_name_plural = 'Libur Nasional'


class tutup_toko_db(models.Model):

    hari = models.CharField(max_length=50, null=True, blank=True)
    jam_tutup = models.TimeField()

    def __str__(self):
        return self.hari

    class Meta:
        verbose_name = 'Jam Tutup Toko'
        verbose_name_plural = 'Jam Tutup Toko'


class rp_lembur_db(models.Model):

    rupiah = models.IntegerField(default=0)

    def __int__(self):
        return self.rupiah

    class Meta:
        verbose_name = 'Rupiah Lembur'
        verbose_name_plural = 'Rupiah Lembur'
          
        

pilihan_pengelola = (("Owner", "Owner"),("HRD", "HRD"), ("Lainnya", "Lainnya"))         
          
        
class pegawai_db(models.Model):
    nama = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    no_telp = models.CharField(max_length=100, null=True)
    userid = models.CharField(max_length=100, unique=True, null=True)
    gender = models.CharField(max_length=10, null=True)

    status = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE)
    nik = models.CharField(max_length=100, null=True)
    divisi = models.ForeignKey(divisi_db, on_delete=models.CASCADE)
    jabatan = models.ForeignKey(jabatan_db, on_delete=models.CASCADE, null=True)

    no_rekening = models.CharField(max_length=50, null=True, blank=True)
    no_bpjs_ks = models.CharField(max_length=50, null=True, blank=True)
    no_bpjs_tk = models.CharField(max_length=50, null=True, blank=True)
    payroll_by = models.CharField(max_length=50, choices=pilihan_pengelola, default='HRD')

    ks_premi = models.IntegerField(default=0)
    tk_premi = models.IntegerField(default=0)

    aktif = models.IntegerField(null=True)
    tgl_masuk = models.DateField(null=True, blank=True)
    tgl_aktif = models.DateTimeField(null=True, blank=True)
    tgl_nonaktif = models.DateTimeField(null=True, blank=True)

    hari_off = models.ForeignKey(hari_db, on_delete=models.CASCADE)
    hari_off2 = models.ForeignKey(hari_db, on_delete=models.CASCADE, related_name='hari_off2',null=True, blank=True)
    kelompok_kerja = models.ForeignKey(kelompok_kerja_db, on_delete=models.CASCADE, null=True, blank=True)
    sisa_cuti = models.IntegerField(null=True)
    cuti_awal = models.IntegerField(null=True)
    shift = models.CharField(max_length=100, null=True, blank=True)
    counter = models.ForeignKey(counter_db, on_delete=models.CASCADE, null=True, blank=True)
    
    rekening = models.CharField(max_length=50, null=True, blank=True)

    add_by = models.CharField(max_length=100, null=True, blank=True)
    edit_by = models.CharField(max_length=100, null=True, blank=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    item_edit = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = 'Pegawai'
        verbose_name_plural = 'Pegawai'


class pribadi_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    alamat = models.TextField(null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=50, null=True)
    kota_lahir = models.CharField(max_length=200,null=True)
    tgl_lahir = models.DateField(null=True)
    tinggi_badan = models.FloatField(default=0)
    berat_badan = models.FloatField(default=0)
    gol_darah = models.CharField(max_length=5, null=True)
    agama = models.CharField(max_length=30, null=True)
    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Data Pribadi'
        verbose_name_plural = 'Data Pribadi'
        
        
class keluarga_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    hubungan = models.CharField(max_length=30, null=True)
    nama = models.CharField(max_length=100, null=True)
    tgl_lahir = models.DateField(null=True)
    gender = models.CharField(max_length=10, null=True)
    gol_darah = models.CharField(max_length=5, null=True)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Data Keluarga'
        verbose_name_plural = 'Data Keluarga'        


class kontak_lain_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    hubungan = models.CharField(max_length=30, null=True)
    nama = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=10, null=True)
    phone = models.CharField(max_length=20, null=True)
    
    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Orang yg dapat dihubungi'
        verbose_name_plural = 'Orang yg dapat dihubungi'

class kota_kabupaten_db(models.Model):
    id_provinsi = models.IntegerField(null=True)
    nama_koka = models.CharField(max_length=150,null=True)

    def __str__(self):
        return self.nama_koka

    def __int__(self):
        return self.nama_koka
        
        
class pengalaman_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    perusahaan = models.CharField(max_length=50, null=False)
    kota = models.ForeignKey(kota_kabupaten_db,on_delete=models.CASCADE, null=False)
    dari_tahun = models.IntegerField()
    sampai_tahun = models.IntegerField()
    jabatan = models.CharField(max_length=50, null=False)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Pengalaman Kerja'
        verbose_name_plural = 'Pengalaman Kerja'
        
        



pendidikan_choices = (("KULIAH","KULIAH"),("SMK/SMA","SMK/SMA"),("SMP","SMP"))
class pendidikan_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    pendidikan = models.CharField(max_length=100,choices=pendidikan_choices,null=False)
    nama = models.CharField(max_length=100, null=False)
    kota = models.ForeignKey(kota_kabupaten_db,on_delete=models.CASCADE, null=False)
    dari_tahun = models.IntegerField()
    sampai_tahun = models.IntegerField()
    jurusan = models.CharField(max_length=50, null=True)    
    gelar = models.CharField(max_length=50, null=True)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Pendidikan'
        verbose_name_plural = 'Pendidikan'    


pilihan_status = (("Promosi", "Promosi"),("Demosi", "Demosi"))

class promosi_demosi_db(models.Model):
    tgl = models.DateField(null=True)
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=pilihan_status, null=True)
    jabatan_sebelum = models.ForeignKey(jabatan_db,related_name="jabatan_sebelum", on_delete=models.CASCADE,null=True)
    jabatan_sekarang = models.ForeignKey(jabatan_db,related_name="jabatan_setelah",on_delete=models.CASCADE, null=True)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Promsi / Demosi'
        verbose_name_plural = 'Promsi / Demosi' 
        
        
pilihan_sangsi = (("SP1", "SP1"),("SP2", "SP2"),("SP3", "SP3"))         
        
class sangsi_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    tgl_berlaku = models.DateField(null=True)
    tgl_berakhir = models.DateField(null=True)
    status_sangsi = models.CharField(max_length=50, choices=pilihan_sangsi, null=True)
    deskripsi_pelanggaran = models.TextField(null=True)

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Sangsi'
        verbose_name_plural = 'Sangsi'                                 


class shift_db(models.Model):
    shift = models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.shift
    
    class Meta:
        verbose_name = 'Shift'

pilihan_hari = (("Semua Hari", "Semua Hari"), ("Senin", "Senin"), ("Selasa", "Selasa"), ("Rabu", "Rabu"), ("Kamis", "Kamis"), ("Jumat", "Jumat"), ("Sabtu", "Sabtu"), ("Minggu", "Minggu"))

class jamkerja_db(models.Model):
    kk = models.ForeignKey(kelompok_kerja_db, on_delete=models.CASCADE, null=True)
    
    jam_masuk = models.TimeField(null=True)
    jam_pulang = models.TimeField(null=True)
    lama_istirahat = models.FloatField(null=True)
    hari = models.CharField(max_length=50, choices=pilihan_hari)
    shift = models.ForeignKey(shift_db,on_delete=models.CASCADE,null=True)
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.hari
    
    class Meta:
        verbose_name = 'Jam Kerja'
        verbose_name_plural = 'Jam Kerja'


class list_status_opg_db(models.Model):
    status = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE, null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)

    def __int__(self):
        return self.status
    
    class Meta:
        verbose_name = 'Status Pegawai yang dapat OPG'
        verbose_name_plural = 'Status Pegawai yang dapat OPG'

class list_status_opg_libur_nasional_db(models.Model):
    status = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE, null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)

    def __int__(self):
        return self.status
    
    class Meta:
        verbose_name = 'Status Pegawai yang dapat OPG Libur Nasional'
        verbose_name_plural = 'Status Pegawai yang dapat OPG Libur Nasional'


class awal_cuti_db(models.Model):
    tgl = models.DateField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)

    def __date__(self):
        return self.tgl
    
    class Meta:
        verbose_name = 'Awal Cuti'
        verbose_name_plural = 'Awal Cuti'

 
class status_pegawai_lembur_db(models.Model):
    status_pegawai = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE, null=True)
    
    def __int__(self):
        return self.status_pegawai
    
    class Meta:
        verbose_name = 'Status Pegawai yg Lembur'
        verbose_name_plural = 'Status Pegawai yg Lembur'
    
    
class status_pegawai_lintas_hari_db(models.Model):
    status_pegawai = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE, null=True)    
    
    def __int__(self):
        return self.status_pegawai
    
    class Meta:
        verbose_name = 'Status Pegawai yg Lintas Hari'
        verbose_name_plural = 'Status Pegawai yg Lintas Hari'
class status_pegawai_payroll_db(models.Model):
    status_pegawai = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE, null=True)    
    
    def __int__(self):
        return self.status_pegawai
    
    class Meta:
        verbose_name = 'Status Pegawai yg Payroll'
        verbose_name_plural = 'Status Pegawai yg Payroll'
     
     
class cabang_db(models.Model):
    cabang = models.CharField(max_length=100)


    def __str__(self) -> str:
        return self.cabang
    
    class Meta:
        verbose_name = "Cabang DB"
        verbose_name_plural = "Cabang DB"
# Akses
# ==================================================================

pilihan_akses = (("root", "root"),("admin", "admin"),("it", "it"),("user", "user"),("tamu", "tamu"),) 

class akses_db(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    akses = models.CharField(max_length=100, choices=pilihan_akses, default="user")
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE, null=True, blank=True)
    sid = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE, null=True, blank=True)

    def __int__(self):
        return self.user


class akses_divisi_db(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    divisi = models.ForeignKey(divisi_db, on_delete=models.CASCADE)

    def __int__(self):
        return self.user 


# Ijin, Geser OFF, OPG dan Cuti
# ==================================================================        
class jenis_ijin_db(models.Model):
    jenis_ijin = models.CharField(max_length=50)

    def __str__(self):
        return self.jenis_ijin

    class Meta:
        verbose_name = 'Jenis Ijin'
        verbose_name_plural = 'Jenis Ijin'


class ijin_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    ijin = models.ForeignKey(jenis_ijin_db, on_delete=models.CASCADE)
    tgl_ijin = models.DateField(null=True)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Ijin Pegawai'
        verbose_name_plural = 'Ijin Pegawai'


class geseroff_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    dari_tgl = models.DateField()
    ke_tgl = models.DateField()
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Geser OFF'
        verbose_name_plural = 'Geser OFF'


class opg_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    opg_tgl = models.DateField(null=True)
    diambil_tgl = models.DateField(null=True)
    keterangan = models.TextField(null=True)
    status = models.IntegerField(default=0)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.keterangan

    class Meta:
        verbose_name = 'OPG'
        verbose_name_plural = 'OPG'


class cuti_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    tgl_cuti = models.DateField()
    cuti_ke = models.IntegerField(default=0)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Cuti'
        verbose_name_plural = 'Cuti'


class dinas_luar_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    tgl_dinas = models.DateField(null=True)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Dinas Luar'
        verbose_name_plural = 'Dinas Luar'


# Absensi
# ==================================================================       
class absensi_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    
    tgl_absen = models.DateField()
    
    masuk = models.TimeField(null=True)
    istirahat = models.TimeField(null=True)
    kembali = models.TimeField(null=True)
    istirahat2 = models.TimeField(null=True)
    kembali2 = models.TimeField(null=True)
    pulang = models.TimeField(null=True)
    
    masuk_b = models.TimeField(null=True)
    istirahat_b = models.TimeField(null=True)
    kembali_b = models.TimeField(null=True)
    istirahat2_b = models.TimeField(null=True)
    kembali2_b = models.TimeField(null=True)
    pulang_b = models.TimeField(null=True)
    
    keterangan_absensi = models.TextField(null=True)
    keterangan_ijin = models.TextField(null=True)
    keterangan_lain = models.TextField(null=True)
    libur_nasional = models.CharField(max_length=100, null=True)
    insentif = models.IntegerField(default=0,null=True)
    
    jam_masuk = models.TimeField(null=True)
    lama_istirahat = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    lama_istirahat2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    jam_pulang = models.TimeField(null=True)
    jam_istirahat = models.TimeField(null=True) 
    jam_kerja = models.ForeignKey(jamkerja_db,on_delete=models.CASCADE,null=True)
    
    total_jam_kerja = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    total_jam_istirahat = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    total_jam_istirahat2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    lebih_jam_kerja = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
        
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Absensi'
        verbose_name_plural = 'Absensi'


class data_raw_db(models.Model):
    userid = models.CharField(max_length=100)
    jam_absen = models.DateTimeField(null=True, blank=True)
    punch = models.IntegerField(null=True, blank=True)
    mesin = models.CharField(max_length=100, null=True)
    
    
class data_trans_db(models.Model):
    userid = models.CharField(max_length=100)
    jam_absen = models.DateTimeField(null=True, blank=True)
    punch = models.IntegerField(null=True, blank=True)
    mesin = models.CharField(max_length=100, null=True) 
    keterangan = models.CharField(max_length=100, null=True)    
 

class tarik_terakhir_db(models.Model):
    userid = models.CharField(max_length=100)
    jam = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.userid

    class Meta:
        verbose_name = 'Tarik Terakhir'
        verbose_name_plural = 'Tarik Terakhir'


class last_te(models.Model):
    userid = models.CharField(max_length=100)
    jam = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.userid

    class Meta:
        verbose_name = 'Last data today enrollment'
        verbose_name_plural = 'Last data today enrollment'

       
# Lembur dan Kompensasi
# ==================================================================               

class lembur_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    
    tgl_lembur = models.DateField()
    
    lembur_awal = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    lembur_akhir = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    istirahat = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    istirahat2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    lebih_nproses = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    proses_lembur = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    status = models.IntegerField(default=0)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Lembur'
        verbose_name_plural = 'Lembur'
        

class rekap_lembur_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    
    periode = models.IntegerField()
    tahun = models.IntegerField()
    
    total_lembur = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    total_kompen = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    sisa_lembur = models.DecimalField(max_digits=5, decimal_places=2, null=True,default=0)
    lembur_jam_bayar = models.DecimalField(max_digits=5, decimal_places=2, null=True,default=0)
    lembur_rupiah_bayar = models.IntegerField(default=0, null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Rekap Lembur'
        verbose_name_plural = 'Rekap Lembur'




class data_ijin_db(models.Model):
    # nik = models.IntegerField(default=0)
    # userid = models.CharField(max_length=100, null=True)
    pegawai = models.ForeignKey(pegawai_db,on_delete=models.CASCADE)
    periode = models.IntegerField(default=0)
    tahun = models.IntegerField(null=True)
    sb = models.IntegerField(default=0, null=True)
    sdl = models.IntegerField(default=0, null=True)
    sdp = models.IntegerField(default=0, null=True)
    ijin = models.IntegerField(default=0, null=True)
    alfa = models.IntegerField(default=0, null=True)
    insentif = models.IntegerField(default=0, null=True)
    ket = models.TextField(null=True)



class rekap_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(status_pegawai_db,on_delete=models.CASCADE, null=True)
    tharikerja = models.IntegerField(null=True)
    periode = models.IntegerField(null=True)
    tahun = models.IntegerField(null=True)
    sb = models.IntegerField(null=True)
    sdl = models.IntegerField(null=True)
    sdp = models.IntegerField(null=True)
    ijin = models.IntegerField(null=True)
    af = models.IntegerField(null=True)
    insentif = models.IntegerField(null=True)
    cm = models.IntegerField(null=True)
    keterangan = models.TextField(null=True)

pilihan_kompen = (("Awal", "Awal"),("Akhir", "Akhir"), ("1 Hari", "1 Hari"))


class kompen_db(models.Model):
    pegawai = models.ForeignKey(pegawai_db, on_delete=models.CASCADE)
    
    tgl_kompen = models.DateField()
    
    kompen = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    jenis_kompen = models.CharField(max_length=50, choices=pilihan_kompen)
    
    status = models.IntegerField(default=0)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Kompensasi'
        verbose_name_plural = 'Kompensasi'        
        
        
# Histori Hapus
# ==================================================================        
class histori_hapus_db(models.Model):
    delete_by = models.CharField(max_length=100, null=True)
    delete_item = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.delete_by

    class Meta:
        verbose_name = 'Histori Hapus'
        verbose_name_plural = 'Histori Hapus'        

cabang =  (("tasik","tasik"),("sumedang","sumedang"),("cirebon","cirebon"),("garut","garut"),("cihideung","cihideung"))

class akses_cabang_db(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    cabang = models.ForeignKey(cabang_db,on_delete=models.CASCADE,null=False)
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.cabang

    class Meta:
        verbose_name = 'Akses Cabang'
        verbose_name_plural = 'Akses Cabang'   





    







# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++= ARSIP DATABASE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class pegawai_db_arsip(models.Model):
    nama = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    no_telp = models.CharField(max_length=100, null=True)
    userid = models.CharField(max_length=100, unique=True, null=True)
    gender = models.CharField(max_length=10, null=True)

    status = models.ForeignKey(status_pegawai_db, related_name="status_arsip", on_delete=models.CASCADE)
    nik = models.CharField(max_length=100, null=True)
    divisi = models.ForeignKey(divisi_db,related_name="divisi_arsip", on_delete=models.CASCADE)
    jabatan = models.ForeignKey(jabatan_db,related_name="jabatan_arsip", on_delete=models.CASCADE, null=True)

    no_rekening = models.CharField(max_length=50, null=True, blank=True)
    no_bpjs_ks = models.CharField(max_length=50, null=True, blank=True)
    no_bpjs_tk = models.CharField(max_length=50, null=True, blank=True)
    payroll_by = models.CharField(max_length=50, choices=pilihan_pengelola, default='HRD')

    ks_premi = models.IntegerField(default=0)
    tk_premi = models.IntegerField(default=0)

    aktif = models.IntegerField(null=True)
    tgl_masuk = models.DateField(null=True, blank=True)
    tgl_aktif = models.DateTimeField(null=True, blank=True)
    tgl_nonaktif = models.DateTimeField(null=True, blank=True)

    hari_off = models.ForeignKey(hari_db,related_name="hari_off_arsip", on_delete=models.CASCADE)
    hari_off2 = models.ForeignKey(hari_db, on_delete=models.CASCADE, related_name='hari_off2_arsip',null=True, blank=True)
    kelompok_kerja = models.ForeignKey(kelompok_kerja_db,related_name="kelompok_kerja_arsip", on_delete=models.CASCADE, null=True, blank=True)
    sisa_cuti = models.IntegerField(null=True)
    cuti_awal = models.IntegerField(null=True)
    shift = models.CharField(max_length=100, null=True, blank=True)
    counter = models.ForeignKey(counter_db,related_name="counter_arsip", on_delete=models.CASCADE, null=True, blank=True)
    
    rekening = models.CharField(max_length=50, null=True, blank=True)

    add_by = models.CharField(max_length=100, null=True, blank=True)
    edit_by = models.CharField(max_length=100, null=True, blank=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    item_edit = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = 'Pegawai'
        verbose_name_plural = 'Pegawai'


class pribadi_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    alamat = models.TextField(null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=50, null=True)
    kota_lahir = models.CharField(max_length=200,null=True)
    tgl_lahir = models.DateField(null=True)
    tinggi_badan = models.FloatField(default=0)
    berat_badan = models.FloatField(default=0)
    gol_darah = models.CharField(max_length=5, null=True)
    agama = models.CharField(max_length=30, null=True)
    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Data Pribadi'
        verbose_name_plural = 'Data Pribadi'
        
        
class keluarga_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    hubungan = models.CharField(max_length=30, null=True)
    nama = models.CharField(max_length=100, null=True)
    tgl_lahir = models.DateField(null=True)
    gender = models.CharField(max_length=10, null=True)
    gol_darah = models.CharField(max_length=5, null=True)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Data Keluarga'
        verbose_name_plural = 'Data Keluarga'        


class kontak_lain_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    hubungan = models.CharField(max_length=30, null=True)
    nama = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=10, null=True)
    phone = models.CharField(max_length=20, null=True)
    
    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Orang yg dapat dihubungi'
        verbose_name_plural = 'Orang yg dapat dihubungi'


class pengalaman_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    perusahaan = models.CharField(max_length=50, null=False)
    kota = models.ForeignKey(kota_kabupaten_db,on_delete=models.CASCADE, null=False)
    dari_tahun = models.IntegerField()
    sampai_tahun = models.IntegerField()
    jabatan = models.CharField(max_length=50, null=False)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Pengalaman Kerja'
        verbose_name_plural = 'Pengalaman Kerja'
        
        



pendidikan_choices = (("KULIAH","KULIAH"),("SMK/SMA","SMK/SMA"),("SMP","SMP"))
class pendidikan_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    pendidikan = models.CharField(max_length=100,choices=pendidikan_choices,null=False)
    nama = models.CharField(max_length=100, null=False)
    kota = models.ForeignKey(kota_kabupaten_db,on_delete=models.CASCADE, null=False)
    dari_tahun = models.IntegerField()
    sampai_tahun = models.IntegerField()
    jurusan = models.CharField(max_length=50, null=True)    
    gelar = models.CharField(max_length=50, null=True)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Pendidikan'
        verbose_name_plural = 'Pendidikan'    


pilihan_status = (("Promosi", "Promosi"),("Demosi", "Demosi"))

class promosi_demosi_db_arsip(models.Model):
    tgl = models.DateField(null=True)
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=pilihan_status, null=True)
    jabatan_sebelum = models.ForeignKey(jabatan_db,related_name="jabatan_sebelum_arsip", on_delete=models.CASCADE,null=True)
    jabatan_sekarang = models.ForeignKey(jabatan_db,related_name="jabatan_setelah_arsip",on_delete=models.CASCADE, null=True)    

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Promsi / Demosi'
        verbose_name_plural = 'Promsi / Demosi' 
        
        
pilihan_sangsi = (("SP1", "SP1"),("SP2", "SP2"),("SP3", "SP3"))         
        
class sangsi_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    tgl_berlaku = models.DateField(null=True)
    tgl_berakhir = models.DateField(null=True)
    status_sangsi = models.CharField(max_length=50, choices=pilihan_sangsi, null=True)
    deskripsi_pelanggaran = models.TextField(null=True)

    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Sangsi'
        verbose_name_plural = 'Sangsi'                                 


class ijin_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    ijin = models.ForeignKey(jenis_ijin_db, on_delete=models.CASCADE)
    tgl_ijin = models.DateField(null=True)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Ijin Pegawai'
        verbose_name_plural = 'Ijin Pegawai'


class geseroff_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    dari_tgl = models.DateField()
    ke_tgl = models.DateField()
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Geser OFF'
        verbose_name_plural = 'Geser OFF'


class opg_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    opg_tgl = models.DateField(null=True)
    diambil_tgl = models.DateField(null=True)
    keterangan = models.TextField(null=True)
    status = models.IntegerField(default=0)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai__nama

    class Meta:
        verbose_name = 'OPG'
        verbose_name_plural = 'OPG'


class cuti_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    tgl_cuti = models.DateField()
    cuti_ke = models.IntegerField(default=0)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Cuti'
        verbose_name_plural = 'Cuti'


class dinas_luar_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip,on_delete=models.CASCADE)
    tgl_dinas = models.DateField(null=True)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Dinas Luar'
        verbose_name_plural = 'Dinas Luar'


# Absensi
# ==================================================================       
class absensi_db_arsip(models.Model):
    pegawai = models.CharField(max_length=200)
    
    tgl_absen = models.DateField()
    
    masuk = models.TimeField(null=True)
    istirahat = models.TimeField(null=True)
    kembali = models.TimeField(null=True)
    istirahat2 = models.TimeField(null=True)
    kembali2 = models.TimeField(null=True)
    pulang = models.TimeField(null=True)
    
    masuk_b = models.TimeField(null=True)
    istirahat_b = models.TimeField(null=True)
    kembali_b = models.TimeField(null=True)
    istirahat2_b = models.TimeField(null=True)
    kembali2_b = models.TimeField(null=True)
    pulang_b = models.TimeField(null=True)
    
    keterangan_absensi = models.TextField(null=True)
    keterangan_ijin = models.TextField(null=True)
    keterangan_lain = models.TextField(null=True)
    libur_nasional = models.CharField(max_length=100, null=True)
    insentif = models.IntegerField(default=0,null=True)
    
    jam_masuk = models.TimeField(null=True)
    lama_istirahat = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    lama_istirahat2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    jam_pulang = models.TimeField(null=True)
    jam_istirahat = models.TimeField(null=True) 
    
    total_jam_kerja = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    total_jam_istirahat = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    total_jam_istirahat2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    lebih_jam_kerja = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
        
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Absensi'
        verbose_name_plural = 'Absensi'


class lembur_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    
    tgl_lembur = models.DateField()
    
    lembur_awal = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    lembur_akhir = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    istirahat = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    istirahat2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    lebih_nproses = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    proses_lembur = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    
    status = models.IntegerField(default=0)
    keterangan = models.TextField(null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Lembur'
        verbose_name_plural = 'Lembur'
        

class rekap_lembur_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    
    periode = models.IntegerField()
    tahun = models.IntegerField()
    
    total_lembur = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    total_kompen = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0)
    sisa_lembur = models.DecimalField(max_digits=5, decimal_places=2, null=True,default=0)
    lembur_jam_bayar = models.DecimalField(max_digits=5, decimal_places=2, null=True,default=0)
    lembur_rupiah_bayar = models.IntegerField(default=0, null=True)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __int__(self):
        return self.pegawai

    class Meta:
        verbose_name = 'Rekap Lembur'
        verbose_name_plural = 'Rekap Lembur'


pilihan_kompen = (("Awal", "Awal"),("Akhir", "Akhir"), ("1 Hari", "1 Hari"))


class kompen_db_arsip(models.Model):
    pegawai = models.ForeignKey(pegawai_db_arsip, on_delete=models.CASCADE)
    
    tgl_kompen = models.DateField()
    
    kompen = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    jenis_kompen = models.CharField(max_length=50, choices=pilihan_kompen)
    
    status = models.IntegerField(default=0)
    
    add_by = models.CharField(max_length=100, null=True)
    edit_by = models.CharField(max_length=100, null=True)
    add_date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.pegawai.nama

    class Meta:
        verbose_name = 'Kompensasi'
        verbose_name_plural = 'Kompensasi'        
        


    
# ++++++++++++++++++++++++++++++++++
# # Payroll
# class pegawai_payroll_db(models.Model):
#     nama = models.CharField(max_length=200, null=True)
#     userid = models.CharField(max_length=100, unique=True, null=True)
#     gender = models.CharField(max_length=10, null=True)

#     status = models.ForeignKey(status_pegawai_db, on_delete=models.CASCADE)
#     nik = models.CharField(max_length=100, null=True)
#     divisi = models.ForeignKey(divisi_db, on_delete=models.CASCADE)

#     no_rekening = models.CharField(max_length=50, null=True, blank=True)
#     no_bpjs_ks = models.CharField(max_length=50, null=True, blank=True)
#     no_bpjs_tk = models.CharField(max_length=50, null=True, blank=True)
#     payroll_by = models.CharField(max_length=50, choices=pilihan_pengelola, default='HRD')

#     ks_premi = models.IntegerField(default=0)
#     tk_premi = models.IntegerField(default=0)

#     aktif = models.IntegerField(null=True)
#     tgl_masuk = models.DateField(null=True, blank=True)
#     status_payroll = models.IntegerField()

#     add_by = models.CharField(max_length=100, null=True, blank=True)
#     edit_by = models.CharField(max_length=100, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     update_at = models.DateTimeField(auto_now=True, null=True)

#     class Meta:
#         managed = False
#         db_table = "payroll_app_pegawai_db"

class counter_payroll_db(models.Model):
    counter = models.CharField(max_length=100)

    def __str__(self):
        return self.counter

    class Meta:
        managed=False
        db_table="payroll_app_counter_db"   



class status_pegawai_payroll_app_db(models.Model):
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.status

    class Meta:
        managed=False
        db_table="payroll_app_status_pegawai_db"     

class divisi_payroll_db(models.Model):
    divisi = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.divisi
    
    class Meta:
        managed=False
        db_table="payroll_app_divisi_db" 
