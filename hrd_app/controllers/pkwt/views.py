from hrd_app.controllers.lib import *

@login_required
def pkwt(r):
    id_user = r.user.id
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    if akses is not None:
        if akses.akses == 'hrd' or akses.akses == 'admin' or akses.akses == "root":
            data = {
                "dsid":akses.sid.pk,
                "sid":akses.sid.pk
            }
            return render(r,"hrd_app/pkwt/pkwt.html",data)


@login_required
def pkwt_json(r):
    try:
        if r.method == "POST":
            id_user = r.user.id
            print("Ok")
            akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
            if akses is not None:
                if akses.akses == 'hrd' or akses.akses == 'admin' or akses.akses == "root":
                    now = datetime.now()
                    hari = datetime.strftime(now.date(),"%A")
                    hari = nama_hari(hari)
                    tanggal = now.day
                    bulan = nama_bulan(now.month)
                    tahun = now.year
                    nama1 = r.POST.get("nama1")
                    jabatan1 = r.POST.get("jabatan1")
                    nama2 = r.POST.get("nama2")
                    ttl2 = r.POST.get("ttl2")
                    noktp2 = r.POST.get("noktp2")
                    alamat2 = r.POST.get("alamat2")
                    nohp2 = r.POST.get("nohp2")
                    jabatan2 = r.POST.get("jabatan2")
                    tugas = r.POST.get("tugas")
                    jangka = r.POST.get("jangka")
                    tipe = r.POST.get("tipe")
                    dari = r.POST.get("dari")
                    sampai = r.POST.get("sampai")
                    tempat = r.POST.get("tempat")
                    gaji = r.POST.get("gaji")
                    bank = r.POST.get("bank")
                    darif = datetime.strptime(dari,"%d-%m-%Y")
                    sampaif = datetime.strptime(sampai,"%d-%m-%Y")
                    dr = f"{darif.day} {nama_bulan(darif.month)} {darif.year}"
                    sp = f"{sampaif.day} {nama_bulan(sampaif.month)} {sampaif.year}"
                    gaji = "".join(str(gaji).split("."))
                    bilang = terbilang(int(gaji)).strip()
                    gaji = "{:,}".format(int(gaji))


                    html = get_template("hrd_app/pkwt/format.html")
                    data = {"nama1":nama1,"jabatan1":jabatan1, "nama2":nama2, "ttl2":ttl2, "noktp2":noktp2, "alamat2":alamat2, "nohp2":nohp2, "jabatan2":jabatan2, "tugas":tugas, "jangka":jangka, "tipe":tipe, "dari":dr, "sampai":sp, "tempat":tempat, "gaji":gaji, "bank":bank,"hari":hari,"tanggal":tanggal,"bulan":bulan,"tahun":tahun,"terbilang":bilang}
                    ctx = html.render(data)
                    html = weasyprint.HTML(string=ctx)
                    css = weasyprint.CSS(filename="static/bootstrap/css/bootstrap.min.css")
                    file = html.write_pdf("static/pdf/pkwt.pdf",stylesheets=[css])
                    return redirect("pkwt_json")
        else:
            with open("static/pdf/pkwt.pdf","rb") as f:
                response = HttpResponse(f.read(),"application/pdf")
                response["Content-Dispotion"] = 'filename=pkwt.pdf'
                return response
    except Exception as e:
        messages.error(r,"Terjadi kesalahan")
        return redirect("pkwt")
        