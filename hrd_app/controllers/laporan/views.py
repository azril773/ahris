from hrd_app.controllers.lib import *

@login_required
def laporan(r,sid):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dr = datetime.strptime("2015","%Y")
        sp = datetime.today()
        list_year = []
        for i in range(dr.year,sp.year+1):
            list_year.append(i)
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        jenis_ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).all()  
        sall = status_pegawai_db.objects.using(r.session["ccabang"]).all()
        divisi = divisi_db.objects.using(r.session["ccabang"]).all()
        shift = shift_db.objects.using(r.session["ccabang"]).all()
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
            'jenis_ijin' : jenis_ijin,
            "list_year":list_year,
            "bulan":sp.month,
            "pegawai":pegawai,
            "divisi":divisi,
            "shift":shift,
            "nama_bulan":nama_bulan(sp.month),
            "tahun":sp.year,
            "sall":sall,
            'modul_aktif' : 'Laporan'
        }
        
        return render(r,'hrd_app/laporan/[sid]/laporan.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

def laporan_json(r):
    sid = r.POST.get('sid')
    bulan = r.POST.get('bulan')
    tahun = r.POST.get('tahun')
    date = tahun+"-"+bulan+"-25"
    sp = datetime.strptime(date,"%Y-%m-%d")
    dr = sp - timedelta(days=30)

    data = []

    if int(sid) == 0:
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
        for pgw in pegawai:
            off = 0
            terlambat = 0
            terlambat_ijin = 0
            total_hari = 0
            sdp = 0
            sb = 0
            sdl = 0
            nkh = 0
            ma = 0
            ktn = 0
            im = 0
            cm = 0
            wft = 0
            kwft = 0
            urh = 0
            bs = 0
            ijin = 0
            af = 0
            ct = 0 #keterangan absensi
            opg = 0
            dl = 0
            ab = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id = pgw.id, tgl_absen__range=[dr,sp])
            if ab.exists():
                for a in ab:
                    if a.keterangan_absensi == "OFF":
                        off += 1
                    if a.masuk is not None and a.pulang is not None:
                        total_hari += 1
                    if a.jam_masuk is not None and a.masuk is not None:
                        if a.masuk > a.jam_masuk:
                            if a.keterangan_ijin is not None:
                                terlambat_ijin += 1
                            else:
                                terlambat += 1
                    if a.keterangan_ijin is not None:
                        if re.search("(sdp)",a.keterangan_ijin,re.I):
                            sdp += 1
                        elif re.search("(sb)",a.keterangan_ijin,re.I):
                            sb += 1
                        elif re.search("(cm)",a.keterangan_ijin,re.I):
                            cm += 1
                        elif re.search("(sdl)",a.keterangan_ijin,re.I):
                            sdl += 1
                        elif re.search("(nkh)",a.keterangan_ijin,re.I):
                            nkh += 1
                        elif re.search("(ma)",a.keterangan_ijin,re.I):
                            ma += 1
                        elif re.search("(ktn)",a.keterangan_ijin,re.I):
                            ktn += 1
                        elif re.search("(im)",a.keterangan_ijin,re.I):
                            im += 1
                        elif re.search("(kwft)",a.keterangan_ijin,re.I):
                            kwft += 1
                        elif re.search("(wft)",a.keterangan_ijin,re.I):
                            wft += 1
                        elif re.search("(urh)",a.keterangan_ijin,re.I):
                            urh += 1
                        elif re.search("(bs)",a.keterangan_ijin,re.I):
                            bs += 1
                        elif re.search("(ijin|izin)",a.keterangan_ijin,re.I):
                            ijin += 1
                        elif re.search("(dl)",a.keterangan_ijin,re.I):
                            dl += 1
                    if a.keterangan_absensi is not None:
                        if re.search("cuti",a.keterangan_absensi,re.I):
                            ct += 1
                        elif re.search("opg",a.keterangan_absensi,re.I):
                            opg += 1
                    elif a.keterangan_absensi is None and a.keterangan_ijin is None and a.keterangan_lain is None and (a.masuk is not None and a.pulang is not None or a.masuk_b is not None and a.pulang_b is not None):
                        pass
                        # af += 1
                    else:
                        af += 1

            
            obj = {
                "id" : pgw.id,
                "nik":pgw.nik,
                "jk":pgw.gender[0] if pgw.gender != "" else "",
                "nama": pgw.nama,
                "divisi":pgw.divisi.divisi,
                "off": off if off > 0 else "",
                "terlambat": terlambat if terlambat > 0 else "",
                "hari_off":pgw.hari_off.hari,
                "terlambat_ijin": terlambat_ijin if terlambat_ijin > 0 else "",
                "total_hari": total_hari if total_hari > 0 else "",
                "sdp":sdp if sdp > 0 else "",
                "sb":sb if sb > 0 else "",
                "sdl":sdl if sdl > 0 else "",
                "nkh":nkh if nkh > 0 else "",
                "im":im if im > 0 else "",
                "cm":cm if cm > 0 else "",
                "wft":wft if wft > 0 else "",
                "ktn":ktn if ktn > 0 else "",
                "ijin":ijin if ijin > 0 else "",
                "af":af if af > 0 else "",
                "ct":ct if ct > 0 else "",
                "ma":ma if ma > 0 else "",
                "kwft":kwft if kwft > 0 else "",
                "urh":urh if urh > 0 else "",
                "bs":bs if bs > 0 else "",
                "opg":opg if opg > 0 else "",
                "dl":dl if dl > 0 else ""
            }
            data.append(obj)
    else:
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(status_id = sid)
        for pgw in pegawai:
            off = 0
            terlambat = 0
            terlambat_ijin = 0
            total_hari = 0


            sdp = 0
            sb = 0
            sdl = 0
            nkh = 0
            ma = 0
            ktn = 0
            im = 0
            cm = 0
            wft = 0
            kwft = 0
            urh = 0
            bs = 0
            ijin = 0
            af = 0
            ct = 0 #keterangan absensi
            opg = 0
            dl = 0

            ab = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id = pgw.id, tgl_absen__range=[dr,sp])
            if ab.exists():
                for a in ab:
                    if a.keterangan_absensi == "OFF":
                        off += 1
                    if a.masuk is not None and a.pulang is not None:
                        total_hari += 1
                    if a.masuk_b is not None and a.pulang_b is not None:
                        total_hari += 1
                    if a.jam_masuk is not None and a.masuk is not None:
                        if a.masuk > a.jam_masuk:
                            if a.keterangan_ijin is not None:
                                terlambat_ijin += 1
                            else:
                                terlambat += 1
                    if a.keterangan_ijin is not None:
                        if re.search("(sdp)",a.keterangan_ijin,re.I):
                            sdp += 1
                        elif re.search("(sb)",a.keterangan_ijin,re.I):
                            sb += 1
                        elif re.search("(cm)",a.keterangan_ijin,re.I):
                            cm += 1
                        elif re.search("(sdl)",a.keterangan_ijin,re.I):
                            sdl += 1
                        elif re.search("(nkh)",a.keterangan_ijin,re.I):
                            nkh += 1
                        elif re.search("(ma)",a.keterangan_ijin,re.I):
                            ma += 1
                        elif re.search("(ktn)",a.keterangan_ijin,re.I):
                            ktn += 1
                        elif re.search("(im)",a.keterangan_ijin,re.I):
                            im += 1
                        elif re.search("(kwft)",a.keterangan_ijin,re.I):
                            kwft += 1
                        elif re.search("(wft)",a.keterangan_ijin,re.I):
                            wft += 1
                        elif re.search("(urh)",a.keterangan_ijin,re.I):
                            urh += 1
                        elif re.search("(bs)",a.keterangan_ijin,re.I):
                            bs += 1
                        elif re.search("(ijin|izin)",a.keterangan_ijin,re.I):
                            ijin += 1
                        elif re.search("(dl)",a.keterangan_ijin,re.I):
                            dl += 1
                    if a.keterangan_absensi is not None:
                        if re.search("cuti",a.keterangan_absensi,re.I):
                            ct += 1
                        elif re.search("opg",a.keterangan_absensi,re.I):
                            opg += 1
                    elif a.keterangan_absensi is None and a.keterangan_ijin is None and a.keterangan_lain is None and (a.masuk is not None and a.pulang is not None or a.masuk_b is not None and a.pulang_b is not None):
                        pass
                        # af += 1
                    else:
                        af += 1
            obj = {
                "id" : pgw.id,
                "nik":pgw.nik,
                "jk":pgw.gender[0] if pgw.gender != "" else "",
                "nama": pgw.nama,
                "divisi":pgw.divisi.divisi,
                "off": off if off > 0 else "",
                "terlambat": terlambat if terlambat > 0 else "",
                "hari_off":pgw.hari_off.hari,
                "terlambat_ijin": terlambat_ijin if terlambat_ijin > 0 else "",
                "total_hari": total_hari if total_hari > 0 else "",
                "sdp":sdp if sdp > 0 else "",
                "sb":sb if sb > 0 else "",
                "sdl":sdl if sdl > 0 else "",
                "nkh":nkh if nkh > 0 else "",
                "im":im if im > 0 else "",
                "cm":cm if cm > 0 else "",
                "wft":wft if wft > 0 else "",
                "ktn":ktn if ktn > 0 else "",
                "ijin":ijin if ijin > 0 else "",
                "af":af if af > 0 else "",
                "ct":ct if ct > 0 else "",
                "ma":ma if ma > 0 else "",
                "kwft":kwft if kwft > 0 else "",
                "urh":urh if urh > 0 else "",
                "bs":bs if bs > 0 else "",
                "opg":opg if opg > 0 else "",
                "dl":dl if dl > 0 else ""
            }
            data.append(obj)
    return JsonResponse({"data":data},status=200)



@login_required
def print_laporan(r,sid,id,bulan,tahun):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).get(id=id)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        statuslh = status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).all()
        lh = len([lh for lh in statuslh if lh.status_pegawai.pk == pegawai.status.pk])
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        jenis_ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).all()   
        date = tahun+"-"+bulan+"-25"
        sp = datetime.strptime(date,"%Y-%m-%d")
        dr = sp - timedelta(days=30)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'status' : status,
            'dsid': dsid,
            "dari":dr.date(),
            "sampai":sp.date(),
            "dr":dr,
            "now":datetime.now().date(),
            "pegawai":pegawai,
            "id":id,
            "sp":sp,
            "lh":lh,
            'sid': sid,
            'sil': sid_lembur,
            'jenis_ijin' : jenis_ijin,
            'modul_aktif' : 'Print Laporan'
        }
        
        return render(r,'hrd_app/laporan/[sid]/[id]/[bulan]/[tahun]/print_laporan.html', data)
    # return render(r,"hrd_app/laporan/print_laporan.html")


def laporan_json_periode(r,sid,id,dr,sp):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        dari = datetime.strptime(dr,'%Y-%m-%d %H:%M:%S').date()
        dari_loop = datetime.strptime(dr,'%Y-%m-%d %H:%M:%S').date()
        sampai_today = datetime.today().date()
        sampai = datetime.strptime(sp,'%Y-%m-%d %H:%M:%S').date()
        delta = timedelta(days=1)
        hari_count = 0
        while dari_loop <= sampai:
            dari_loop += delta
            hari_count += 1
        kehadiran = 0
        tselisih = 0.0
        trlmbt = 0
        lhstatus = 1
        lh = status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).all()
        for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(tgl_absen__range=(dari,sampai),pegawai_id=id).order_by('tgl_absen','pegawai__divisi__divisi'):
            if a.masuk is not None and a.pulang is not None:
                kehadiran += 1
            elif a.masuk_b is not None and a.pulang_b is not None and a.masuk is not None and a.pulang is not None:
                kehadiran += 2
            sket = " "
            
            ab = absensi_db.objects.using(r.session["ccabang"]).get(id=a.id)     
            hari = ab.tgl_absen.strftime("%A")
            hari_ini = nama_hari(hari) 
            
            if ab.pegawai.counter_id is None:
                bagian = ab.pegawai.divisi.divisi
            else:
                bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
            if ab.masuk is not None:
                if ab.jam_masuk is not None:
                    if ab.masuk > ab.jam_masuk:
                        msk = f"<span class='text-danger'>{ab.masuk}</span>"
                    else:
                        msk = f"{ab.masuk}"
                else:
                    msk = f"{ab.masuk}"
            else:
                msk = "-"
            if ab.pulang is not None:
                if ab.jam_pulang is not None:
                    if ab.pulang < ab.jam_pulang:
                        plg = f"<span class='text-danger'>{ab.pulang}</span>"
                    else:
                        plg = f"{ab.pulang}"
                else:
                    plg = f"{ab.pulang}"
            else:
                plg = "-"


            if ab.masuk_b is not None:
                msk_b = f"{ab.masuk_b}"
            else:
                msk_b = "-"
            if ab.pulang_b is not None:
                plg_b = f"{ab.pulang_b}"
            else:
                plg_b = "-"



                
            if ab.istirahat is not None and ab.istirahat2 is not None:
                ist = f'{ab.istirahat} / {ab.istirahat2}'
            elif ab.istirahat is not None and ab.istirahat2 is None:                  
                ist = f'{ab.istirahat}'
            elif ab.istirahat is None and ab.istirahat2 is not None:                  
                ist = f'{ab.istirahat2}'
            else:
                ist = "-"   


            if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                ist_b = f" {ab.istirahat_b} / {ab.istirahat2_b}"
            elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                ist_b = f" {ab.istirahat_b}"
            elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                ist_b = f" {ab.istirahat2_b}"
            else:
                ist_b = "-"
        
                
            bataskmb = ''
            if ab.kembali is not None:
                if ab.lama_istirahat is not None and ab.istirahat is not None:
                    if datetime.combine(ab.tgl_absen,ab.kembali) > (datetime.combine(ab.tgl_absen,ab.istirahat) + timedelta(hours=int(ab.lama_istirahat))): 
                        bataskmb = f'<span class="text-danger">{ab.kembali}</span>'
                    else:
                        bataskmb = f"{ab.kembali}"
                else:
                    bataskmb = f'{ab.kembali}'
            if ab.kembali is not None and ab.kembali2 is not None:
                kmb = f'{bataskmb} / {ab.kembali2}'
            elif ab.kembali is not None and ab.kembali2 is None:    
                kmb = f'{bataskmb}'
            elif ab.kembali is None and ab.kembali2 is not None:                  
                kmb = f'{bataskmb}'    
            else:
                kmb = "-"               
            
            if ab.kembali_b is not None and ab.kembali2_b is not None:
                kmb_b = f" {ab.kembali_b} / {ab.kembali2_b}"
            elif ab.kembali_b is not None and ab.kembali2_b is None:
                kmb_b = f" {ab.kembali_b}"
            elif ab.kembali_b is None and ab.kembali2_b is not None:
                kmb_b = f" {ab.kembali2_b}"
            else:
                kmb_b = "-" 
            
            if ab.keterangan_absensi is not None:
                sket += f'{ab.keterangan_absensi}, '                 
            if ab.keterangan_ijin is not None:
                sket += f'{ab.keterangan_ijin}, '
                kijin = ''
            else:
                if ab.masuk is not None and ab.jam_masuk is not None:
                    if ab.masuk > ab.jam_masuk:
                        tselisih += (datetime.combine(ab.tgl_absen,ab.masuk) - datetime.combine(ab.tgl_absen,ab.jam_masuk)).total_seconds() /60
                        trlmbt += 1
                        sket += f"Terlambat masuk tanpa ijin, "
            if ab.keterangan_lain is not None:
                sket += f'{ab.keterangan_lain}, '                    
            if ab.libur_nasional is not None:
                sket += f'{ab.libur_nasional}, '
                sln = 1
            else:
                sln = 0
            absen = {
                'id': ab.id,
                'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                'hari': hari_ini,
                "tgl_absen":ab.tgl_absen,
                'nama': ab.pegawai.nama,
                'nik': ab.pegawai.nik,
                'userid': ab.pegawai.userid,
                'bagian': bagian,
                "jam_masuk":ab.jam_masuk,
                "jam_pulang":ab.jam_pulang,
                'masuk': msk,
                'keluar': ist,
                'kembali': kmb,
                'pulang': plg,
                'masuk_b': msk_b,
                'keluar_b': ist_b,
                'kembali_b': kmb_b,
                'pulang_b': plg_b,
                "total_jam":ab.total_jam_kerja,
                'tj': ab.total_jam_kerja,
                'ket': sket,
                'sln': sln,
                'kehadiran': kehadiran,
                'ln': ab.libur_nasional
            }
            data.append(absen)
            if lhstatus > 0:
                if len([l for l in lh if l.status_pegawai.pk == a.pegawai.status.pk]) > 0:
                    lhstatus = 1
                else:
                    if a.masuk_b is not None or a.pulang_b is not None or a.istirahat_b is not None or a.kembali_b is not None or a.istirahat2_b is not None or a.kembali2_b is not None:
                        lhstatus = 0
                    else:
                        lhstatus = 1
        tselisih = str(tselisih).split(".")
        slc = slice(0,2)
        return JsonResponse({"data": data,"kehadiran":kehadiran,"hari":hari_count,"tselisih":f"{tselisih[0]},{tselisih[1][slc]}","trlmbt":trlmbt,"lh":lhstatus })
    

def laporan_json_periode_excel(r,sid,id,bulan,tahun):        
        data = []
        sampai = datetime.strptime(f'{tahun}-{bulan}-26',"%Y-%m-%d").date()
        dari = sampai - timedelta(days=30)
        
        kehadiran = 0
        tselisih = 0.0
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(id))
        trlmbt = 0
        obj = {
            'tgl':[],
            'hari': [],
            "tgl_absen":[],
            'nama': [],
            'nik': [],
            'userid': [],
            'bagian': [],
            'masuk': [],
            'keluar': [],
            'kembali': [],
            'pulang': [],
            'masuk_b': [],
            'keluar_b': [],
            'kembali_b': [],
            'pulang_b': [],
            "total_jam":[],
            'tj': [],
            'ket': [],
            'sln': [],
            'kehadiran': [],
            'ln': []
        }
        for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(tgl_absen__range=(dari,sampai),pegawai_id=id).order_by('tgl_absen','pegawai__divisi__divisi'):
            if a.masuk is not None and a.pulang is not None:
                kehadiran += 1
            elif a.masuk_b is not None and a.pulang_b is not None and a.masuk is not None and a.pulang is not None:
                kehadiran += 2
            sket = " "
            
            ab = absensi_db.objects.using(r.session["ccabang"]).get(id=a.id)     
            hari = ab.tgl_absen.strftime("%A")
            hari_ini = nama_hari(hari) 
            
            if ab.pegawai.counter_id is None:
                bagian = ab.pegawai.divisi.divisi
            else:
                bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
            if ab.masuk is not None:
                if ab.jam_masuk is not None:
                    if ab.masuk > ab.jam_masuk:
                        msk = f"{ab.masuk}"
                    else:
                        msk = f"{ab.masuk}"
                else:
                    msk = f"{ab.masuk}"
            else:
                msk = "-"
            if ab.pulang is not None:
                if ab.jam_pulang is not None:
                    if ab.pulang < ab.jam_pulang:
                        plg = f"{ab.pulang}"
                    else:
                        plg = f"{ab.pulang}"
                else:
                    plg = f"{ab.pulang}"
            else:
                plg = "-"


            if ab.masuk_b is not None:
                msk_b = f"{ab.masuk_b}"
            else:
                msk_b = "-"
            if ab.pulang_b is not None:
                plg_b = f"{ab.pulang_b}"
            else:
                plg_b = "-"



                
            if ab.istirahat is not None and ab.istirahat2 is not None:
                ist = f'{ab.istirahat} / {ab.istirahat2}'
            elif ab.istirahat is not None and ab.istirahat2 is None:                  
                ist = f'{ab.istirahat}'
            elif ab.istirahat is None and ab.istirahat2 is not None:                  
                ist = f'{ab.istirahat2}'
            else:
                ist = "-"   


            if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                ist_b = f" {ab.istirahat_b} / {ab.istirahat2_b}"
            elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                ist_b = f" {ab.istirahat_b}"
            elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                ist_b = f" {ab.istirahat2_b}"
            else:
                ist_b = "-"
        
                
            bataskmb = ''
            if ab.kembali is not None:
                if ab.lama_istirahat is not None and ab.istirahat is not None:
                    if datetime.combine(ab.tgl_absen,ab.kembali) > (datetime.combine(ab.tgl_absen,ab.istirahat) + timedelta(hours=int(ab.lama_istirahat))): 
                        bataskmb = f'{ab.kembali}'
                    else:
                        bataskmb = f"{ab.kembali}"
                else:
                    bataskmb = f'{ab.kembali}'
            
            if ab.kembali is not None and ab.kembali2 is not None:
                kmb = f'{bataskmb} / {ab.kembali2}'
            elif ab.kembali is not None and ab.kembali2 is None:    
                kmb = f'{bataskmb}'
            elif ab.kembali is None and ab.kembali2 is not None:                  
                kmb = f'{bataskmb}'    
            else:
                kmb = "-"               
            
            if ab.kembali_b is not None and ab.kembali2_b is not None:
                kmb_b = f" {ab.kembali_b} / {ab.kembali2_b}"
            elif ab.kembali_b is not None and ab.kembali2_b is None:
                kmb_b = f" {ab.kembali_b}"
            elif ab.kembali_b is None and ab.kembali2_b is not None:
                kmb_b = f" {ab.kembali2_b}"
            else:
                kmb_b = "-" 
            
            if ab.keterangan_absensi is not None:
                sket += f'{ab.keterangan_absensi}, '                 
            if ab.keterangan_ijin is not None:
                sket += f'{ab.keterangan_ijin}, '
                kijin = ''
            else:
                if ab.masuk is not None and ab.jam_masuk is not None:
                    if ab.masuk > ab.jam_masuk:
                        tselisih += (datetime.combine(ab.tgl_absen,ab.masuk) - datetime.combine(ab.tgl_absen,ab.jam_masuk)).total_seconds() /60
                        trlmbt += 1
                        sket += f"Terlambat masuk tanpa ijin, "
            if ab.keterangan_lain is not None:
                sket += f'{ab.keterangan_lain}, '                    
            if ab.libur_nasional is not None:
                sket += f'{ab.libur_nasional}, '
                sln = 1
            else:
                sln = 0
            if msk != "-" or plg != "-" or kmb != "-" or ist != "-" or msk_b != "-" or plg_b != "-" or kmb_b != "-" or ist_b != "-":
                obj["tgl"].append(datetime.strftime(ab.tgl_absen,'%d-%m-%Y'))
                obj["hari"].append(hari_ini)
                obj["tgl_absen"].append(ab.tgl_absen)
                obj["nama"].append(ab.pegawai.nama)
                obj["nik"].append(ab.pegawai.nik)
                obj["userid"].append(ab.pegawai.userid)
                obj["bagian"].append(bagian)
                obj["masuk"].append(msk)
                obj["keluar"].append(ist)
                obj["kembali"].append(kmb)
                obj["pulang"].append(plg)
                obj["masuk_b"].append(msk_b)
                obj["keluar_b"].append(ist_b)
                obj["kembali_b"].append(kmb_b)
                obj["pulang_b"].append(plg_b)
                obj["total_jam"].append(ab.total_jam_kerja)
                obj["tj"].append(ab.total_jam_kerja)
                obj["ket"].append(sket)
                obj["sln"].append(sln)
                obj["kehadiran"].append(kehadiran)
                obj["ln"].append(ab.libur_nasional)
            # absen = {
            #     'id': ab.id,
            #     'tgl': ,
            #     'hari': hari_ini,
            #     "tgl_absen":ab.tgl_absen,
            #     'nama': ab.pegawai.nama,
            #     'nik': ab.pegawai.nik,
            #     'userid': ab.pegawai.userid,
            #     'bagian': bagian,
            #     "jam_masuk":ab.jam_masuk,
            #     "jam_pulang":ab.jam_pulang,
            #     'masuk': msk,
            #     'keluar': ist,
            #     'kembali': kmb,
            #     'pulang': plg,
            #     'masuk_b': msk_b,
            #     'keluar_b': ist_b,
            #     'kembali_b': kmb_b,
            #     'pulang_b': plg_b,
            #     "total_jam":ab.total_jam_kerja,
            #     'tj': ab.total_jam_kerja,
            #     'ket': sket,
            #     'sln': sln,
            #     'kehadiran': kehadiran,
            #     'ln': ab.libur_nasional
            # }
            # dat  a.append(absen)
        
        tselisih = str(tselisih).split(".")
        slc = slice(0,2)
        df = pd.DataFrame(obj)
        if pegawai.exists():
            df.to_excel(f"static/excel/{pegawai[0].nama}-{pegawai[0].divisi.divisi}-{dari}-{sampai}.xlsx")
            with open(f"static/excel/{pegawai[0].nama}-{pegawai[0].divisi.divisi}-{dari}-{sampai}.xlsx","rb") as file:
                http = HttpResponse(file.read(),content_type="application/vnd.ms-excel")
                http["Content-Disposition"] = f"attachment; filename={pegawai[0].nama}-{pegawai[0].divisi.divisi}-{dari}-{sampai}.xlsx"
                return http
        else:
            df.to_excel(f"static/excel/{dari}-{sampai}-dummy.xlsx")
        # with open("static/excel/")
        # return JsonResponse({"data": data,"kehadiran":kehadiran,"hari":hari_count,"tselisih":f"{tselisih[0]},{tselisih[1][slc]}","trlmbt":trlmbt })
        # return redirect("laporan",sid=sid)

@login_required
def print_laporan_pegawai(r):
    pgw = r.POST.getlist("pegawai[]")
    dr = r.POST.get("dari")
    sp = r.POST.get("sampai")
    # 
    try:
        iduser = r.user.id
        
        if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
            dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
            sid = dakses.pegawai.status.pk
            data = [] 
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=pgw)
        lh = status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).all()
        for p in pegawai:
            dari = datetime.strptime(str(dr),'%d-%m-%Y').date()
            sampai = datetime.strptime(str(sp),'%d-%m-%Y').date()
            dari_loop = datetime.strptime(str(dr),'%d-%m-%Y').date()
            delta = timedelta(days=1)
            hari_count = 0
            while dari_loop <= sampai:
                dari_loop += delta
                hari_count += 1
            obj = {
                "nama":p.nama,
                "nik":p.nik,
                "divisi":p.divisi,
                "dari":dari,
                "sampai":sampai,
                "kehadiran":0,
                "b":1,
                "selisih":0,
                "terlambat":0,
                "hari":hari_count,
                "absensi":[]
            }
            kehadiran = 0
            tselisih = 0.0
            trlmbt = 0
            for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(tgl_absen__range=(dari,sampai),pegawai_id=p.pk).order_by('tgl_absen','pegawai__divisi__divisi'):
                ab = absensi_db.objects.using(r.session["ccabang"]).get(id=a.id)     
                if a.masuk is not None and a.pulang is not None and a.masuk_b is None and a.pulang_b is None:
                    kehadiran += 1
                elif a.masuk_b is not None and a.pulang_b is not None and a.masuk is not None and a.pulang is not None:
                    kehadiran += 2
                sket = " "
                msk = ''
                hari = ab.tgl_absen.strftime("%A")
                hari_ini = nama_hari(hari) 
                if ab.masuk is not None:
                    if ab.jam_masuk is not None:
                        if ab.masuk > ab.jam_masuk:
                            msk = f"<span class='text-danger'>{ab.masuk}</span>"
                        else:
                            msk = f"{ab.masuk}"
                    else:
                        msk = f"{ab.masuk}"
                else:
                    msk = "-"


                if ab.masuk_b is not None:
                    msk_b = f"{ab.masuk_b}"
                else:
                    msk_b = "-"
                if ab.pulang_b is not None:
                    plg_b = f"{ab.pulang_b}"
                else:
                    plg_b = "-"
                plg = ""
                if ab.pulang is not None:
                    if ab.jam_pulang is not None:
                        if ab.pulang < ab.jam_pulang:
                            plg = f"<span class='text-danger'>{ab.pulang}</span>"
                        else:
                            plg = f'{ab.pulang}'
                    else:
                        plg = f"{ab.pulang}"
                else:
                    plg = "-"

                
                if ab.pegawai.counter_id is None:
                    bagian = ab.pegawai.divisi.divisi
                else:
                    bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
                    
                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = "-"    
                if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                    ist_b = f" {ab.istirahat_b} / {ab.istirahat2_b}"
                elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                    ist_b = f" {ab.istirahat_b}"
                elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                    ist_b = f" {ab.istirahat2_b}"
                else:
                    ist_b = "-"
                bataskmb = ''
                if ab.kembali is not None:
                    if ab.lama_istirahat is not None and ab.istirahat is not None:
                        if datetime.combine(ab.tgl_absen,ab.kembali) > (datetime.combine(ab.tgl_absen,ab.istirahat) + timedelta(hours=int(ab.lama_istirahat))): 
                            bataskmb = f'<span class="text-danger">{ab.kembali}</span>'
                        else:
                            bataskmb = f"{ab.kembali}"
                    else:
                        bataskmb = f'{ab.kembali}'
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{bataskmb} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:    
                    kmb = f'{bataskmb}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{bataskmb}'    
                else:
                    kmb = "-"        
                if ab.kembali_b is not None and ab.kembali2_b is not None:
                    kmb_b = f" {ab.kembali_b} / {ab.kembali2_b}"
                elif ab.kembali_b is not None and ab.kembali2_b is None:
                    kmb_b = f" {ab.kembali_b}"
                elif ab.kembali_b is None and ab.kembali2_b is not None:
                    kmb_b = f" {ab.kembali2_b}"
                else:
                    kmb_b = "-" 
                
                if ab.keterangan_absensi is not None:
                    sket += f'{ab.keterangan_absensi}, '                 
                if ab.keterangan_ijin is not None:
                    sket += f'{ab.keterangan_ijin}, '
                    kijin = ''
                else:
                    if ab.masuk is not None and ab.jam_masuk is not None:
                        if ab.masuk > ab.jam_masuk:
                            tselisih += (datetime.combine(ab.tgl_absen,ab.masuk) - datetime.combine(ab.tgl_absen,ab.jam_masuk)).total_seconds() /60
                            trlmbt += 1
                            sket += f"Terlambat masuk tanpa ijin, "
                if ab.keterangan_lain is not None:
                    sket += f'{ab.keterangan_lain}, '                    
                if ab.libur_nasional is not None:
                    sket += f'{ab.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=ab.tgl_absen).exists():
                    tgl_absen = True
                else:
                    tgl_absen = False
                
                absen = {
                    'id': ab.id,
                    'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    "tgl_absen":ab.tgl_absen,
                    "lbr":tgl_absen,
                    'nama': ab.pegawai.nama,
                    'nik': ab.pegawai.nik,
                    'userid': ab.pegawai.userid,
                    'bagian': bagian,
                    "jam_masuk":ab.jam_masuk,
                    "jam_pulang":ab.jam_pulang,
                    'masuk': msk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': plg,
                    'masuk_b': msk_b,
                    'keluar_b': ist_b,
                    'kembali_b': kmb_b,
                    'pulang_b': plg_b,
                    "total_jam":ab.total_jam_kerja,
                    'tj': ab.total_jam_kerja,
                    'ket': sket,
                    'sln': sln,
                    'kehadiran': kehadiran,
                    'ln': ab.libur_nasional
                }
                obj["absensi"].append(absen)
                if obj["b"] > 0:
                    if len([l for l in lh if l.status_pegawai.pk == a.pegawai.status.pk]) > 0:
                        obj["b"] = 1
                    else:
                        if a.masuk_b is not None or a.pulang_b is not None or a.istirahat_b is not None or a.kembali_b is not None or a.istirahat2_b is not None or a.kembali2_b is not None:
                            obj["b"] = 0
                        else:
                            obj["b"] = 1
            obj["kehadiran"] = kehadiran
            obj["terlambat"] = trlmbt
            tselisih = str(tselisih).split(".")
            slc = slice(0,2)
            obj["selisih"] =f"{tselisih[0]},{tselisih[1][slc]}"
            obj["now"] = datetime.now().date()
            data.append(obj)
    except Exception as e:
        messages.error(r,"Terjadi kesalahan hubungi IT {}".format(e))
        return redirect("laporan",sid=sid)
    return render(r,"hrd_app/laporan/print_laporan_pegawai.html",{"data":data})

@login_required
def print_laporan_divisi(r):
    dvs = r.POST.getlist("divisi[]")
    dr = r.POST.get("dari")
    sp = r.POST.get("sampai")
    # 
    try:
        iduser = r.user.id
        
        if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
            dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
            sid = dakses.pegawai.status.pk
            data = [] 
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=dvs)
        for p in divisi:
            for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id=p.pk):
                dari = datetime.strptime(str(dr),'%d-%m-%Y').date()
                sampai = datetime.strptime(str(sp),'%d-%m-%Y').date()
                obj = {
                    "nama":p.nama,
                    "nik":p.nik,
                    "divisi":p.divisi,
                    "dari":dari,
                    "sampai":sampai,
                    "kehadiran":0,
                    "selisih":0,
                    "terlambat":0,
                    "absensi":[]
                }
                dari_loop = datetime.strptime(str(dr),'%d-%m-%Y').date()
                delta = timedelta(days=1)
                hari_count = 0
                while dari_loop <= sampai:
                    dari_loop += delta
                    hari_count += 1
                kehadiran = 0
                tselisih = 0.0
                trlmbt = 0
                for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(tgl_absen__range=(dari,sampai),pegawai_id=p.pk).order_by('tgl_absen','pegawai__divisi__divisi'):
                    ab = absensi_db.objects.using(r.session["ccabang"]).get(id=a.id)     
                    if a.masuk is not None and a.pulang is not None and a.masuk_b is None and a.pulang_b is None:
                        kehadiran += 1
                    elif a.masuk_b is not None and a.pulang_b is not None and a.masuk is not None and a.pulang is not None:
                        kehadiran += 2
                    sket = " "
                    msk = ''
                    hari = ab.tgl_absen.strftime("%A")
                    hari_ini = nama_hari(hari) 
                    if ab.masuk is not None:
                        if ab.jam_masuk is not None:
                            if ab.masuk > ab.jam_masuk:
                                msk = f"<span class='text-danger'>{ab.masuk}</span>"
                            else:
                                msk = f"{ab.masuk}"
                        else:
                            msk = f"{ab.masuk}"
                    else:
                        msk = "-"


                    if ab.masuk_b is not None:
                        msk_b = f"{ab.masuk_b}"
                    else:
                        msk_b = "-"
                    if ab.pulang_b is not None:
                        plg_b = f"{ab.pulang_b}"
                    else:
                        plg_b = "-"
                    plg = ""
                    if ab.pulang is not None:
                        if ab.jam_pulang is not None:
                            if ab.pulang < ab.jam_pulang:
                                plg = f"<span class='text-danger'>{ab.pulang}</span>"
                            else:
                                plg = f'{ab.pulang}'
                        else:
                            plg = f"{ab.pulang}"
                    else:
                        plg = "-"

                    
                    if ab.pegawai.counter_id is None:
                        bagian = ab.pegawai.divisi.divisi
                    else:
                        bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
                        
                    if ab.istirahat is not None and ab.istirahat2 is not None:
                        ist = f'{ab.istirahat} / {ab.istirahat2}'
                    elif ab.istirahat is not None and ab.istirahat2 is None:                  
                        ist = f'{ab.istirahat}'
                    elif ab.istirahat is None and ab.istirahat2 is not None:                  
                        ist = f'{ab.istirahat2}'
                    else:
                        ist = "-"    
                    if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                        ist_b = f" {ab.istirahat_b} / {ab.istirahat2_b}"
                    elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                        ist_b = f" {ab.istirahat_b}"
                    elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                        ist_b = f" {ab.istirahat2_b}"
                    else:
                        ist_b = "-"
                    bataskmb = ''
                    if ab.kembali is not None:
                        if ab.lama_istirahat is not None and ab.istirahat is not None:
                            if datetime.combine(ab.tgl_absen,ab.kembali) > (datetime.combine(ab.tgl_absen,ab.istirahat) + timedelta(hours=int(ab.lama_istirahat))): 
                                bataskmb = f'<span class="text-danger">{ab.kembali}</span>'
                            else:
                                bataskmb = f"{ab.kembali}"
                        else:
                            bataskmb = f'{ab.kembali}'
                    if ab.kembali is not None and ab.kembali2 is not None:
                        kmb = f'{bataskmb} / {ab.kembali2}'
                    elif ab.kembali is not None and ab.kembali2 is None:    
                        kmb = f'{bataskmb}'
                    elif ab.kembali is None and ab.kembali2 is not None:                  
                        kmb = f'{bataskmb}'    
                    else:
                        kmb = "-"        
                    if ab.kembali_b is not None and ab.kembali2_b is not None:
                        kmb_b = f" {ab.kembali_b} / {ab.kembali2_b}"
                    elif ab.kembali_b is not None and ab.kembali2_b is None:
                        kmb_b = f" {ab.kembali_b}"
                    elif ab.kembali_b is None and ab.kembali2_b is not None:
                        kmb_b = f" {ab.kembali2_b}"
                    else:
                        kmb_b = "-" 
                    
                    if ab.keterangan_absensi is not None:
                        sket += f'{ab.keterangan_absensi}, '                 
                    if ab.keterangan_ijin is not None:
                        sket += f'{ab.keterangan_ijin}, '
                        kijin = ''
                    else:
                        if ab.masuk is not None and ab.jam_masuk is not None:
                            if ab.masuk > ab.jam_masuk:
                                tselisih += (datetime.combine(ab.tgl_absen,ab.masuk) - datetime.combine(ab.tgl_absen,ab.jam_masuk)).total_seconds() /60
                                trlmbt += 1
                                sket += f"Terlambat masuk tanpa ijin, "
                    if ab.keterangan_lain is not None:
                        sket += f'{ab.keterangan_lain}, '                    
                    if ab.libur_nasional is not None:
                        sket += f'{ab.libur_nasional}, '
                        sln = 1
                    else:
                        sln = 0          

                    if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=ab.tgl_absen).exists():
                        tgl_absen = True
                    else:
                        tgl_absen = False
                    
                    absen = {
                        'id': ab.id,
                        'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                        'hari': hari_ini,
                        "tgl_absen":ab.tgl_absen,
                        "lbr":tgl_absen,
                        'nama': ab.pegawai.nama,
                        'nik': ab.pegawai.nik,
                        'userid': ab.pegawai.userid,
                        'bagian': bagian,
                        "jam_masuk":ab.jam_masuk,
                        "jam_pulang":ab.jam_pulang,
                        'masuk': msk,
                        'keluar': ist,
                        'kembali': kmb,
                        'pulang': plg,
                        'masuk_b': msk_b,
                        'keluar_b': ist_b,
                        'kembali_b': kmb_b,
                        'pulang_b': plg_b,
                        "total_jam":ab.total_jam_kerja,
                        'tj': ab.total_jam_kerja,
                        'ket': sket,
                        'sln': sln,
                        'kehadiran': kehadiran,
                        'ln': ab.libur_nasional
                    }
                    obj["absensi"].append(absen)
                obj["kehadiran"] = kehadiran
                obj["terlambat"] = trlmbt
                tselisih = str(tselisih).split(".")
                slc = slice(0,2)
                obj["selisih"] =f"{tselisih[0]},{tselisih[1][slc]}"
                data.append(obj)
    except Exception as e:
        messages.error(r,"Terjadi kesalahan hubungi IT {}".format(e))
        return redirect("laporan",sid=sid)
    return render(r,"hrd_app/laporan/print_laporan_pegawai.html",{"data":data})

@login_required
def print_laporan_divisi_excel(r):
    dvs = r.POST.getlist("divisi[]")
    dr = r.POST.get("dari")
    sp = r.POST.get("sampai")
    # 
    obj = {
                    'pegawai':[],
                    'tgl':[],
                    'hari': [],
                    "tgl_absen":[],
                    'nama': [],
                    'nik': [],
                    'userid': [],
                    'bagian': [],
                    'masuk': [],
                    'keluar': [],
                    'kembali': [],
                    'pulang': [],
                    'masuk_b': [],
                    'keluar_b': [],
                    'kembali_b': [],
                    'pulang_b': [],
                    "total_jam":[],
                    'tj': [],
                    'ket': [],
                    'sln': [],
                    'kehadiran': [],
                    'ln': []
                }
    try:
        iduser = r.user.id
        
        if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
            dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
            sid = dakses.pegawai.status.pk
            data = [] 
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=dvs)
        for p in divisi:
            for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id=p.pk):
                dari = datetime.strptime(str(dr),'%d-%m-%Y').date()
                sampai = datetime.strptime(str(sp),'%d-%m-%Y').date()
                kehadiran = 0
                tselisih = 0.0
                trlmbt = 0
                for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(tgl_absen__range=(dari,sampai),pegawai_id=p.pk).order_by('tgl_absen','pegawai__divisi__divisi'):
                    ab = absensi_db.objects.using(r.session["ccabang"]).get(id=a.id)     
                    if a.masuk is not None and a.pulang is not None and a.masuk_b is None and a.pulang_b is None:
                        kehadiran += 1
                    elif a.masuk_b is not None and a.pulang_b is not None and a.masuk is not None and a.pulang is not None:
                        kehadiran += 2
                    sket = " "
                    msk = ''
                    hari = ab.tgl_absen.strftime("%A")
                    hari_ini = nama_hari(hari) 
                    if ab.masuk is not None:
                        if ab.jam_masuk is not None:
                            if ab.masuk > ab.jam_masuk:
                                msk = f"{ab.masuk}"
                            else:
                                msk = f"{ab.masuk}"
                        else:
                            msk = f"{ab.masuk}"
                    else:
                        msk = "-"


                    if ab.masuk_b is not None:
                        msk_b = f"{ab.masuk_b}"
                    else:
                        msk_b = "-"
                    if ab.pulang_b is not None:
                        plg_b = f"{ab.pulang_b}"
                    else:
                        plg_b = "-"
                    plg = ""
                    if ab.pulang is not None:
                        if ab.jam_pulang is not None:
                            if ab.pulang < ab.jam_pulang:
                                plg = f"{ab.pulang}"
                            else:
                                plg = f'{ab.pulang}'
                        else:
                            plg = f"{ab.pulang}"
                    else:
                        plg = "-"

                    
                    if ab.pegawai.counter_id is None:
                        bagian = ab.pegawai.divisi.divisi
                    else:
                        bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
                        
                    if ab.istirahat is not None and ab.istirahat2 is not None:
                        ist = f'{ab.istirahat} / {ab.istirahat2}'
                    elif ab.istirahat is not None and ab.istirahat2 is None:                  
                        ist = f'{ab.istirahat}'
                    elif ab.istirahat is None and ab.istirahat2 is not None:                  
                        ist = f'{ab.istirahat2}'
                    else:
                        ist = "-"    
                    if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                        ist_b = f" {ab.istirahat_b} / {ab.istirahat2_b}"
                    elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                        ist_b = f" {ab.istirahat_b}"
                    elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                        ist_b = f" {ab.istirahat2_b}"
                    else:
                        ist_b = "-"
                    bataskmb = ''
                    if ab.kembali is not None:
                        if ab.lama_istirahat is not None and ab.istirahat is not None:
                            if datetime.combine(ab.tgl_absen,ab.kembali) > (datetime.combine(ab.tgl_absen,ab.istirahat) + timedelta(hours=int(ab.lama_istirahat))): 
                                bataskmb = f'{ab.kembali}'
                            else:
                                bataskmb = f"{ab.kembali}"
                        else:
                            bataskmb = f'{ab.kembali}'
                    if ab.kembali is not None and ab.kembali2 is not None:
                        kmb = f'{bataskmb} / {ab.kembali2}'
                    elif ab.kembali is not None and ab.kembali2 is None:    
                        kmb = f'{bataskmb}'
                    elif ab.kembali is None and ab.kembali2 is not None:                  
                        kmb = f'{bataskmb}'    
                    else:
                        kmb = "-"        
                    if ab.kembali_b is not None and ab.kembali2_b is not None:
                        kmb_b = f" {ab.kembali_b} / {ab.kembali2_b}"
                    elif ab.kembali_b is not None and ab.kembali2_b is None:
                        kmb_b = f" {ab.kembali_b}"
                    elif ab.kembali_b is None and ab.kembali2_b is not None:
                        kmb_b = f" {ab.kembali2_b}"
                    else:
                        kmb_b = "-" 
                    
                    if ab.keterangan_absensi is not None:
                        sket += f'{ab.keterangan_absensi}, '                 
                    if ab.keterangan_ijin is not None:
                        sket += f'{ab.keterangan_ijin}, '
                        kijin = ''
                    else:
                        if ab.masuk is not None and ab.jam_masuk is not None:
                            if ab.masuk > ab.jam_masuk:
                                tselisih += (datetime.combine(ab.tgl_absen,ab.masuk) - datetime.combine(ab.tgl_absen,ab.jam_masuk)).total_seconds() /60
                                trlmbt += 1
                                sket += f"Terlambat masuk tanpa ijin, "
                    if ab.keterangan_lain is not None:
                        sket += f'{ab.keterangan_lain}, '                    
                    if ab.libur_nasional is not None:
                        sket += f'{ab.libur_nasional}, '
                        sln = 1
                    else:
                        sln = 0          

                    if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=ab.tgl_absen).exists():
                        tgl_absen = True
                    else:
                        tgl_absen = False
                    if msk != "-" or plg != "-" or kmb != "-" or ist != "-" or msk_b != "-" or plg_b != "-" or kmb_b != "-" or ist_b != "-":
                        obj["tgl"].append(datetime.strftime(ab.tgl_absen,'%d-%m-%Y'))
                        obj["pegawai"].append(p.nama)
                        obj["hari"].append(hari_ini)
                        obj["tgl_absen"].append(ab.tgl_absen)
                        obj["nama"].append(ab.pegawai.nama)
                        obj["nik"].append(ab.pegawai.nik)
                        obj["userid"].append(ab.pegawai.userid)
                        obj["bagian"].append(bagian)
                        obj["masuk"].append(msk)
                        obj["keluar"].append(ist)
                        obj["kembali"].append(kmb)
                        obj["pulang"].append(plg)
                        obj["masuk_b"].append(msk_b)
                        obj["keluar_b"].append(ist_b)
                        obj["kembali_b"].append(kmb_b)
                        obj["pulang_b"].append(plg_b)
                        obj["total_jam"].append(ab.total_jam_kerja)
                        obj["tj"].append(ab.total_jam_kerja)
                        obj["ket"].append(sket)
                        obj["sln"].append(sln)
                        obj["kehadiran"].append(kehadiran)
                        obj["ln"].append(ab.libur_nasional)
        
        tselisih = str(tselisih).split(".")
        slc = slice(0,2)
        df = pd.DataFrame(obj)
        if divisi.exists():
            df.to_excel(f"static/excel/{divisi[0].divisi}-{dr}-{sp}.xlsx")
            with open(f"static/excel/{divisi[0].divisi}-{dr}-{sp}.xlsx","rb") as file:
                http = HttpResponse(file.read(),content_type="application/vnd.ms-excel")
                http["Content-Disposition"] = f"attachment; filename={divisi[0].divisi}-{dr}-{sp}.xlsx"
                return http
        else:
            df.to_excel(f"static/excel/{dr}-{sp}-dummy.xlsx")
    except Exception as e:
        messages.error(r,"Terjadi kesalahan hubungi IT {}".format(e))
        return redirect("laporan",sid=sid)
    return render(r,"hrd_app/laporan/print_laporan_pegawai.html",{"data":data})


@login_required
def print_laporan_shift(r):
    id_user = r.user.id
    akses_divisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    adiv = [div.divisi.pk for div in akses_divisi]
    shift = r.POST.getlist("shift[]")
    tanggal = r.POST.getlist("tanggal")
    # try:
    #     date = datetime.strptime(tgl,"%Y-%m-%d")
    # except:
    try:
        date = []
        for dt in tanggal[0].split(","):
            date.append(datetime.strptime(dt.strip(),"%d-%m-%Y").strftime("%Y-%m-%d"))
    except Exception as e:
        date = [datetime.today().date()]
    shiftdata = shift_db.objects.using(r.session["ccabang"]).filter(id__in=shift)
    result = []
    shifts = [int(sh) for sh in shift]
    for d in date:    
        obj = {}
        for s in shiftdata:
            obj[s.pk] = {"shift":s.shift,"divisi":{}}
        absensi = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai","pegawai__divisi").filter(jam_kerja__shift_id__in=shifts,tgl_absen=d)
        for ab in absensi:
            shift = ab.jam_kerja.shift_id
            div = obj[shift]["divisi"].keys()
            if ab.pegawai.divisi.pk in div:
                if ab.masuk is not None and ab.pulang is not None:
                    obj[shift]["divisi"][ab.pegawai.divisi.pk]["masuk"] += 1
                if ab.keterangan_absensi is not None:
                    if ab.keterangan_absensi == "OFF":
                        obj[shift]["divisi"][ab.pegawai.divisi.pk]["off"] += 1
                    else:
                        pass
                else:
                    pass
                if ab.keterangan_ijin is not None:
                    if re.match("/sakit/",ab.keterangan_ijin) is not None:
                        obj[shift]["divisi"][ab.pegawai.divisi.pk]["sakit"] += 1
                    else:
                        obj[shift]["divisi"][ab.pegawai.divisi.pk]["izin"] += 1

                if ab.keterangan_absensi is None and ab.keterangan_ijin is None and ab.keterangan_lain is None:
                    obj[shift]["divisi"][ab.pegawai.divisi.pk]["tanpa_keterangan"] += 1
                if re.match("/(?i)^m$/",ab.jam_kerja.shift.shift):
                    obj[shift]["divisi"][ab.pegawai.divisi.pk]["m"] += 1
                elif re.match("/(?i)^mf$/",ab.jam_kerja.shift.shift):
                    obj[shift]["divisi"][ab.pegawai.divisi.pk]["mf"] += 1
            else:
                obj[shift]["divisi"][ab.pegawai.divisi.pk] = {
                    "divisi":ab.pegawai.divisi.divisi,
                    "divisi_id":ab.pegawai.divisi.pk,
                    "masuk":0,
                    "cuti":0,
                    "off":0,
                    "sakit":0,
                    "izin":0,
                    "tanpa_keterangan":0,
                }

        data = []
        for s2 in shiftdata:
            dv = []
            for key in obj[s2.pk]["divisi"].keys():
                dv.append(obj[s2.pk]["divisi"][key])
            obj[s2.pk]["divisi_count"] = len(dv)
            obj[s2.pk]["divisi"] = dv
            data.append(obj[s2.pk])
        result.append({"tanggal":d,"data":data})

    print(result)
    return render(r,"hrd_app/laporan/[shift]/print_laporan_shift.html",{"data":result})