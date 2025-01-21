from hrd_app.controllers.lib import *

@authorization(["root","it"])
def pkwt(r):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    if akses is not None:
        aksesdiv = akses_divisi_db.objects.using(r.session['ccabang']).filter(user_id=id_user)
        if not aksesdiv.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    
        div = [div.divisi.pk for div in aksesdiv]
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=div)
        jabatan = jabatan_db.objects.using(r.session["ccabang"]).all()
        pertama = pihak_pertama_db.objects.using(r.session["ccabang"]).filter().last()
        if pertama is not None:
            messages.error(r,"Silahkan isi terlebih dahulu pihak pertama")
            return redirect("beranda")
        data = {
            "dsid":akses.sid.pk,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "sid":akses.sid.pk,
            "pegawai":pegawai,
            "jabatan":jabatan,
            "pertama":pertama
        }
        return render(r,"hrd_app/pkwt/pkwt.html",data)


@authorization(["root","it"])
def pkwt_json(r):
    try:
        cabang = r.session["ccabang"]
        print(cabang)
        static = "http://localhost:8006/static"
        if r.method == "POST":
            id_user = r.session["user"]["id"]
            print("Ok")
            akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
            now = datetime.now()
            hari = datetime.strftime(now.date(),"%A")
            hari = nama_hari(hari)
            tanggal = now.day
            bulan = nama_bulan(now.month)
            tahun = now.year
            pegawai1 = r.POST.get("pegawai1")
            p1 = pegawai_db.objects.select_related("jabatan").using(r.session["ccabang"]).filter(pk=int(pegawai1)).last()
            if p1 is None:
                messages.error(r,"Pegawai pertama tidak ada")
                return redirect("pkwt")
            nama1 = p1.nama
            jabatan1 = p1.jabatan.jabatan
            pegawai2 = r.POST.get("pegawai2")
            p2 = pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(pegawai2)).last()
            if p2 is None:
                messages.error(r,"Pegawai kedua tidak ada")
                return redirect("pkwt")
            pribadi = pribadi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p2.pk).last()
            if pribadi is None:
                messages.error(r,"Data pribadi pegawai tidak ada")
                return redirect("pkwt")
            nama2 = p2.nama
            ttl2 = f"{pribadi.kota_lahir}, {pribadi.tgl_lahir}"
            alamat2 = pribadi.alamat
            nohp2 = pribadi.phone
            jabatan2 = p2.jabatan.jabatan
            tugas = ''
            
            noktp2 = r.POST.get("noktp2")
            jangka = r.POST.get("jangka")
            tipe = "Bulan"
            if int(jangka) >= 12:
                jangka = int(int(jangka) / 12)
                tipe = "Tahun"
            
            dari = r.POST.get("dari")
            sampai = r.POST.get("sampai")
            tempat = r.POST.get("tempat")
            gaji = r.POST.get("gaji")
            cbg = r.POST.get("cabang")
            bank = r.POST.get("bank")
            print(dari,sampai)
            darif = datetime.strptime(dari,"%d-%m-%Y")
            sampaif = datetime.strptime(sampai,"%d-%m-%Y")
            dr = f"{darif.day} {nama_bulan(darif.month)} {darif.year}"
            sp = f"{sampaif.day} {nama_bulan(sampaif.month)} {sampaif.year}"
            gaji = "".join(str(gaji).split("."))
            bilang = terbilang(int(gaji)).strip()
            gaji = "{:,}".format(int(gaji))
            data = {"nama1":nama1,"jabatan1":jabatan1, "nama2":nama2, "ttl2":ttl2, "noktp2":noktp2, "alamat2":alamat2, "nohp2":nohp2, "jabatan2":jabatan2, "tugas":tugas, "jangka":jangka, "tipe":tipe, "dari":dr, "sampai":sp, "tempat":tempat, "gaji":gaji, "bank":bank,"hari":hari,"tanggal":tanggal,"bulan":bulan,"tahun":tahun,"terbilang":bilang,"cabang":cbg,"static":static}
            # return render(r,f"hrd_app/pkwt/{cabang}/format.html",data)
            html = get_template(f"hrd_app/pkwt/{cabang}/format.html")
            ctx = html.render(data)
            html = weasyprint.HTML(string=ctx)
            css = weasyprint.CSS(filename="static/bootstrap/css/bootstrap.min.css")
            file = html.write_pdf(f"static/pdf/pkwt_{cabang}.pdf",stylesheets=[css])
            return redirect("pkwt_json")
        else:
            with open(f"static/pdf/pkwt_{cabang}.pdf","rb") as f:
                response = HttpResponse(f.read(),"application/pdf")
                response["Content-Dispotion"] = f'filename=pkwt_{cabang}.pdf'
                return response
    except Exception as e:
        print(e)
        messages.error(r,"Terjadi kesalahan")
        return redirect("pkwt")
        