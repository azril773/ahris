create trigger after_insert_status after insert on hrd_app_status_pegawai_db for each row insert into payroll.payroll_app_status_pegawai_db (status) values(status);
    
create trigger after_update_status after update on hrd_app_status_pegawai_db for each row update payroll.payroll_app_status_pegawai_db set status = new.status where id=old.id
create trigger after_delete_status after delete on hrd_app_status_pegawai_db for each row delete from payroll.payroll_app_status_pegawai_db where id=old.id
    

new.pegawai_id,new.tgl_absen,new.masuk,new.istirahat,new.kembali,new.istirahat2,new.kembali2,new.pulang,new.masuk_b,new.istirahat_b,new.kembali_b,new.istirahat2_b,new.kembali2_b,new.pulang_b,new.keterangan_absensi,new.keterangan_ijin,new.keterangan_lain,new.libur_nasional,new.insentif,new.jam_masuk,new.lama_istirahat,new.lama_istirahat2,new.jam_pulang,new.jam_istirahat,new.total_jam_kerja,new.total_jam_istirahat,new.total_jam_istirahat2,new.lebih_jam_kerja,new.add_by,new.edit_by,new.add_date,new.edit_date
    
    
    pegawai_id = new.pegawai_id
    tgl_absen = 
    masuk = 
    istirahat = 
    kembali = 
    istirahat2 = 
    kembali2 = 
    pulang = 
    masuk_b = 
    istirahat_b = 
    kembali_b = 
    istirahat2_b = 
    kembali2_b = 
    pulang_b = 
    keterangan_absensi = 
    keterangan_ijin = 
    keterangan_lain = 
    libur_nasional = 
    insentif = 
    jam_masuk = 
    lama_istirahat = 
    lama_istirahat2 = 
    jam_pulang = 
    jam_istirahat =  
    total_jam_kerja = 
    total_jam_istirahat = 
    total_jam_istirahat2 = 
    lebih_jam_kerja = 
    add_by = 
    edit_by = 
    add_date = 
    edit_date = 
    