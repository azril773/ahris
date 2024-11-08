from hrd_app.controllers.lib import *
import pandas as pd

# Jam Kerja
# ++++++++++++++
@login_required
def jam_kerja(r):
    iduser = r.user.id
    if akses_db.objects.filter(user_id=iduser).exists():
        # excel = pd.read_excel("static/jam_kerja.xlsx",sheet_name="Sheet1")
        # data = []
        # for n in excel.iloc[:,0]:
        #     if n != "Group":
        #         obj = {
        #             "status_pegawai":n,
        #         }
        #         data.append(obj)
        # i = 1
        # for d in data:
        #     d["jam_masuk"] = excel.iloc[i,1]
        #     d["jam_pulang"] = excel.iloc[i,2]
        #     d["lama_istirahat"] = excel.iloc[i,3]
        #     d["hari"] = excel.iloc[i,4]
        #     i+=1
        # hari = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
        # for d in data:
        #     
        #     sp = str(d["status_pegawai"]).strip()
        #     kk = kelompok_kerja_db.objects.using(r.session["ccabang"]).get(kelompok__iregex=r'^{}$'.format(sp))
        #     if d["hari"] == "Biasa":
        #         for i in range(0,6):
        #             jamkerja = jamkerja_db()
        #             jamkerja.kk = kk
        #             jamkerja.jam_masuk = d["jam_masuk"]
        #             jamkerja.jam_pulang = d["jam_pulang"]
        #             jamkerja.lama_istirahat = d["lama_istirahat"]
        #             jamkerja.hari = hari[i]
        #             jamkerja.save(r.session["ccabang"])
        #     elif d["hari"] == "All":
        #         for i in range(0,7):
        #             
        #             jamkerja = jamkerja_db()
        #             jamkerja.kk = kk
        #             jamkerja.jam_masuk = d["jam_masuk"]
        #             jamkerja.jam_pulang = d["jam_pulang"]
        #             jamkerja.lama_istirahat = d["lama_istirahat"]
        #             jamkerja.hari = hari[i]
        #             jamkerja.save(r.session["ccabang"])
        #     else:
        #             jamkerja = jamkerja_db()
        #             jamkerja.kk = kk
        #             jamkerja.jam_masuk = d["jam_masuk"]
        #             jamkerja.jam_pulang = d["jam_pulang"]
        #             jamkerja.lama_istirahat = d["lama_istirahat"]
        #             jamkerja.hari = d["hari"]
        #             jamkerja.save(r.session["ccabang"])

        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        kk = kelompok_kerja_db.objects.using(r.session["ccabang"]).all().order_by('kelompok')
        data = {       
            'dsid': dsid,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'kk': kk,
            'modul_aktif' : 'Jam Kerja'     
        }
        
        return render(r,'hrd_app/jam_kerja/jam_kerja.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def tambah_kk_json(r):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        tkk = r.POST.get('tkk')
        
        data = []
                
        if kelompok_kerja_db.objects.using(r.session["ccabang"]).filter(kelompok=tkk).exists():
            data = {}
            status = 'duplikat'
        else:
            tk = kelompok_kerja_db(
                kelompok = tkk
            )    
            tk.save(r.session["ccabang"])
            
            dkk = kelompok_kerja_db.objects.using(r.session["ccabang"]).last()
        
            data = {
                'id': dkk.id,
                'text': dkk.kelompok
            }
            
            status = 'ok'         
                                
        return JsonResponse({"status": status, "data":data})

@login_required
def edit_kk_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        ekk = r.POST.get('ekk')
        new_kk = r.POST.get('new_kk')
        try:
            if kelompok_kerja_db.objects.using(r.session["ccabang"]).filter(~Q(pk=int(ekk)),kelompok=new_kk).exists():
                return JsonResponse({"status": "duplikat"})
            kelompok_kerja_db.objects.using(r.session["ccabang"]).filter(pk=int(ekk)).update(kelompok=new_kk)
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "gagal update",})
                                
        


@login_required
def jam_kerja_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in jamkerja_db.objects.using(r.session["ccabang"]).all().order_by('kk_id__kelompok'):            
            
            jk = {
                'id': i.id,
                'kk': i.kk_id,
                'kk_nama':i.kk.kelompok,
                'masuk': i.jam_masuk,
                'lama_ist': i.lama_istirahat,
                'pulang': i.jam_pulang,
                'hari':i.hari
            }
            data.append(jk)
        return JsonResponse({"data": data})


@login_required
def tambah_jam_kerja(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        kk = r.POST.get("kk")
        jam_masuk = r.POST.get("jam_masuk")
        lama_istirahat = r.POST.get("lama_istirahat")
        jam_pulang = r.POST.get("jam_pulang")
        hari = r.POST.getlist("hari[]")


        # try:
        #     # index = hari.index("Semua Hari")
        #     for 
        #     hari = [hari[index]]
        # except:
        #     hari = hari

        for h in hari:
            if h.lower() == 'semua hari':
                hari = ["Semua Hari"]
                break
                


        if len(hari) >= 7:
            hari = ["Semua Hari"]


        if jamkerja_db.objects.using(r.session["ccabang"]).filter(kk_id=int(kk),jam_masuk=jam_masuk,jam_pulang=jam_pulang).exists():
            status = "gagal tambah"
        else:
            
            for h in hari:
                # if jamkerja_db.objects.using(r.session["ccabang"]).filter(kk_id=int(kk),hari=h).exists():
                #     continue
                
                if h.lower() == 'semua hari':
                    if jamkerja_db.objects.using(r.session["ccabang"]).filter(~Q(hari='semua hari'),jam_masuk=jam_masuk,jam_pulang=jam_pulang,kk_id=int(kk)).exists():
                        break

                jamkerja_db(
                    kk_id=kk,
                    jam_masuk=jam_masuk,
                    jam_pulang=jam_pulang,
                    lama_istirahat=lama_istirahat,
                    hari=h
                ).save(r.session["ccabang"])
            status = "ok"
        return JsonResponse({"status": status})


@login_required
def edit_jam_kerja(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = r.POST.get('id')
        jam_masuk = r.POST.get("jam_masuk")
        jam_pulang = r.POST.get("jam_pulang")
        lama_istirahat = r.POST.get("lama_istirahat")
        kk = r.POST.get("kk")
        hari = r.POST.getlist("hari[]")
        for h in hari:
            if h.lower() == 'semua hari':
                hari = ["Semua Hari"]
                break
                
        

        if len(hari) >= 7:
            hari = ["Semua Hari"]
        jamkerja_db.objects.using(r.session["ccabang"]).filter(id=int(eid)).delete(using=r.session["ccabang"])
        for h in hari:
            # if jamkerja_db.objects.using(r.session["ccabang"]).filter(kk_id=int(kk),hari=h).exists():
            #     continue
            
            if h.lower() == 'semua hari':
                if jamkerja_db.objects.using(r.session["ccabang"]).filter(~Q(hari='semua hari'),kk_id=int(kk)).exists():
                    break
            
            jamkerja_db(
                kk_id=kk,
                jam_masuk=jam_masuk,
                jam_pulang=jam_pulang,
                lama_istirahat=lama_istirahat,
                hari=h
            ).save(r.session["ccabang"])
        status = "ok"
        return JsonResponse({"status": status})


@login_required
def hapus_jam_kerja(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = r.user.username
        
        hid = r.POST.get('hid')
        
        try:
            ln = jamkerja_db.objects.using(r.session["ccabang"]).get(id=int(hid))           
        except:
            return JsonResponse({'status':'gagal hapus'})

        thapus = histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus jam kerja : {ln.kk.kelompok}'
        )
        thapus.save(r.session["ccabang"])
        
        ln.delete(using=r.session["ccabang"])
        
        status = 'ok'
        
        return JsonResponse({"status": status})

