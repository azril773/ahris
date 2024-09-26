from hrd_app.controllers.lib import *
import pika
import weasyprint
from django.template.loader import get_template 
import smtplib, ssl
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
@login_required
def broadcast(r,sid):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        status = status_pegawai_db.objects.all().order_by('id')
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except: 
            sid_lembur = 0
        pegawai = pegawai_db.objects.filter(status_id=sid)
        data = {       
            'akses':akses,
            'sid':sid,
            'status':status,
            "sil":sid_lembur,
            'pegawai':pegawai,
            'dsid': dsid,
            'modul_aktif' : 'Broadcast'     
        }
        return render(r,'hrd_app/broadcast/[sid]/broadcast.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

@login_required
def single_perjanjian_kontrak(r):
    idp = r.POST.get("idp")
    prd = r.POST.get('prd')
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    
    return JsonResponse({"status":"success","msg":"Success"},status=200)


@login_required
def single_absensi(r):
    idp = r.POST.get("idp")
    prd = int(r.POST.get('prd'))
    thn = str(r.POST.get('thn'))
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    # channel.basic_publish(exchange="email",routing_key="absensi",body=)
    data = []
    print(idp)
    if prd == 1:
        prd = 12
    else:
        prd -= 1
    dr = datetime.strptime(""+thn+"-"+str(prd)+"-25","%Y-%m-%d")
    sp = dr + timedelta(days=32)
    print(dr,sp)
    print(dr,sp)
    dari = dr.date()
    dari_loop = dr.date()
    sampai_today = datetime.today().date()
    sampai = sp.date()
    delta = timedelta(days=1)
    hari_count = 0
    while dari_loop <= sampai:
        dari_loop += delta
        hari_count += 1
    kehadiran = 0
    tselisih = 0.0
    trlmbt = 0
    for a in absensi_db.objects.select_related('pegawai').filter(tgl_absen__range=(dari,sampai_today),pegawai_id=idp).order_by('tgl_absen','pegawai__divisi__divisi'):
        if a.masuk is not None and a.pulang is not None:
            kehadiran += 1
        sket = " "
        
        ab = absensi_db.objects.get(id=a.id)     
        hari = ab.tgl_absen.strftime("%A")
        hari_ini = nama_hari(hari) 
        
        if ab.pegawai.counter_id is None:
            bagian = ab.pegawai.divisi.divisi
        else:
            bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
            
        if ab.masuk is not None:
            msk = f"{ab.masuk}"
        else:
            msk = None
        if ab.pulang is not None:
            plg = f"{ab.pulang}"
        else:
            plg = None
        if ab.masuk_b is not None:
            msk_b = f"{ab.masuk_b}"
        else:
            msk_b = None
        if ab.pulang_b is not None:
            plg_b = f"{ab.pulang_b}"
        else:
            plg_b = None
        if ab.istirahat is not None and ab.istirahat2 is not None:
            ist = f'{ab.istirahat} / {ab.istirahat2}'
        elif ab.istirahat is not None and ab.istirahat2 is None:                  
            ist = f'{ab.istirahat}'
        elif ab.istirahat is None and ab.istirahat2 is not None:                  
            ist = f'{ab.istirahat2}'
        else:
            ist = ""    
        if ab.istirahat_b is not None and ab.istirahat2_b is not None:
            ist_b += f" {ab.istirahat_b} / {ab.istirahat2_b})"
        elif ab.istirahat_b is not None and ab.istirahat2_b is None:
            ist_b += f" {ab.istirahat_b}"
        elif ab.istirahat_b is None and ab.istirahat2_b is not None:
            ist_b += f" {ab.istirahat2_b}"
        else:
            ist_b = ""
    
            
        if ab.kembali is not None and ab.kembali2 is not None:
            kmb = f'{ab.kembali} / {ab.kembali2}'
        elif ab.kembali is not None and ab.kembali2 is None:                  
            kmb = f'{ab.kembali}'
        elif ab.kembali is None and ab.kembali2 is not None:                  
            kmb = f'{ab.kembali2}'    
        else:
            kmb = ""        
        if ab.kembali_b is not None and ab.kembali2_b is not None:
            kmb_b += f" {ab.kembali_b} / {ab.kembali2_b})"
        elif ab.kembali_b is not None and ab.kembali2_b is None:
            kmb_b += f" {ab.kembali_b}"
        elif ab.kembali_b is None and ab.kembali2_b is not None:
            kmb_b += f" {ab.kembali2_b}"
        else:
            kmb_b = "" 
        
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
        if ab.istirahat is not None and ab.lama_istirahat is not None:
            jmkem = datetime.combine(ab.tgl_absen,ab.jam_istirahat) + timedelta(minutes=float(ab.lama_istirahat) * 60) + timedelta(minutes=5)
            jmkem = jmkem.time()
        else:
            jmkem = None
        print(dari)
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
            "jam_kembali":jmkem,
            "total_jam":ab.total_jam_kerja,
            'tj': ab.total_jam_kerja,
            'ket': sket,
            'sln': sln,
            'kehadiran': kehadiran,
            'ln': ab.libur_nasional
        }
        data.append(absen)
    pegawai = pegawai_db.objects.get(id=int(idp))
    tselisih = str(tselisih).split(".")
    slc = slice(0,2)
    template = get_template("hrd_app/templatespdf/absensi.html")
    ctx = template.render({"data":data})
    file = weasyprint.HTML(string=ctx)
    css = weasyprint.CSS(r"static/css/bootstrap/bootstrap.css")
    file.write_pdf(r'static/pdf/absensi.pdf',stylesheets=[css])
    msg = MIMEMultipart()
    msg["Subject"] = "Data Absensi"
    msg["From"] = "testingahris@gmail.com"
    msg["To"] = "azrilsugiarto06@gmail.com"
    body = f"Hai, {pegawai.nama}"
    part = MIMEText(body, 'plain')
    msg.attach(part)
    with open(r'static/pdf/absensi.pdf',"rb") as f:
        pdf = MIMEApplication(f.read(),_subtype="pdf")
    # encoders.encode_base64(pdf)
    pdf.add_header("Content-Disposition","attachment",filename=f"absensi {pegawai.nama}")
    msg.attach(pdf)

    context = ssl.create_default_context()
    conn = smtplib.SMTP_SSL("smtp.gmail.com",465)
    # conn.ehlo()
    # conn.starttls(context=context)
    # # conn.ehlo()
    conn.login("testingahris@gmail.com",'uyvl vdac uqad skpf')
    conn.sendmail("sugiartoazril02@gmail.com",['azrilsugiarto06@gmail.com'],msg.as_string())
    conn.quit()

    return JsonResponse({"status":"ok"})

@login_required
def ra(r):
    with open(r"static/pdf/absensi.pdf","rb") as f:
        resp = HttpResponse(f.read(),"application/pdf")
        resp["Content-Disposition"] = "filename=absensi.pdf"
        return resp
