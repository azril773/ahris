from hrd_app.controllers.lib import *
import pika
import weasyprint
from django.template.loader import get_template 
import smtplib, ssl
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pickle
@authorization(["*"])
def broadcast(r,sid):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('id')
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except: 
            sid_lembur = 0
        if sid == 0:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1)
        else:    
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1,status_id=sid)
        data = {       
            'akses':akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
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
    

@authorization(["*"])
def single_perjanjian_kontrak(r):
    idp = r.POST.get("idp")
    prd = r.POST.get('prd')
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    
    return JsonResponse({"status":"success","msg":"Success"},status=200)


@authorization(["*"])
def single_absensi(r):
    idp = r.POST.get("idp")
    prd = r.POST.get('prd')
    thn = r.POST.get('thn')
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    # channel.basic_publish(exchange="email",routing_key="absensi",body=)
    data = []
    p = pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).filter(pk=int(idp))
    if p.exists():
        if prd == '' or thn == '':
            return JsonResponse({"status":"error","msg":"Silahkan lengkapi form yang ada"},status=400)
            # return redirect("broadcast",sid=sid)
        if p[0].email is not None or p[0].no_telp is not None:
            js = json.dumps({"idp":str(idp),"prd":str(prd),"thn":str(thn)})
            channel.basic_publish(exchange="broadcast",routing_key="broadcast",body=js)
    else:
        return JsonResponse({"status":"error","msg":"Silahkan lengkapi form yang ada"},status=400)

    return JsonResponse({"status":"ok"})

@authorization(["*"])
def ra(r):
    with open(r"static/pdf/absensi.pdf","rb") as f:
        resp = HttpResponse(f.read(),"application/pdf")
        resp["Content-Disposition"] = "filename=absensi.pdf"
        return resp


@authorization(["*"])
def bpa(r,sid):
    pegawai = r.POST.getlist("pegawai[]")
    if len(pegawai) <= 0:
        messages.error(r,"Silahkan lengkapi form yang ada")
        return redirect("broadcast",sid=sid)

    for p in pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=pegawai):


        idp = p.pk
        prd = r.POST.get('bulanb')
        thn = r.POST.get('tahunb')
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        # channel.basic_publish(exchange="email",routing_key="absensi",body=)

        if prd == '' or thn == '':
            messages.error(r,"Silahkan lengkapi form yang ada")
            return redirect("broadcast",sid=sid)
        data = []
        if p.email is not None or p.no_telp is not None:
            js = json.dumps({"idp":str(idp),"prd":str(prd),"thn":str(thn)})
            channel.basic_publish(exchange="broadcast",routing_key="broadcast",body=js)

    return redirect("broadcast",sid=sid)



class ApiMessage(APIView):
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        # todos = Todo.objects.filter(user = request.user.id)
        # serializer = TodoSerializer(todos, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        pass
    # 2. Create
    def post(self, r, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        data = json.loads(r.data.get("data"))
        kehadiran = r.data.get("kehadiran")
        trlmbt = r.data.get("trlmbt")
        tselisih = r.data.get("tselisih")
        dari = r.data.get("dr")
        sampai = r.data.get("sp")
        p = json.loads(r.data.get("pegawai"))[0]
        data = sorted(data, key=lambda i: datetime.strptime(i['tgl_absen'],"%d-%m-%Y"))
        template = get_template("hrd_app/templatespdf/absensi.html")
        ctx = template.render({"data":data,"kehadiran":kehadiran,"terlambat":trlmbt,'selisih':tselisih,"dari":dari,"sampai":sampai,"pegawai":p})
        # pribadi = pribadi_db.objects.get(pk=int(p["id"]))
        file = weasyprint.HTML(string=ctx)
        css = weasyprint.CSS(r"static/css/bootstrap/bootstrap.css")
        file.write_pdf(r'static/pdf/absensi.pdf',stylesheets=[css])
        msg = MIMEMultipart()
        msg["Subject"] = "Data Absensi"
        msg["From"] = "testingahris@gmail.com"
        with open(r'static/pdf/absensi.pdf',"rb") as f:
            filepdf = f.read()
            pdf = MIMEApplication(filepdf,_subtype="pdf")
        if p["email"] != "":
            msg["To"] = p["email"]



            nama = p["nama"]
            body = f"Hai, {nama}"
            part = MIMEText(body, 'plain')
            msg.attach(part)
            pdf.add_header("Content-Disposition","attachment",filename=f"absensi {nama}")
            msg.attach(pdf)
            # encoders.encode_base64(pdf)

            context = ssl.create_default_context()
            conn = smtplib.SMTP_SSL("smtp.gmail.com",465)
            conn.login("testingahris@gmail.com",'uyvl vdac uqad skpf')
            conn.sendmail("testingahris@gmail.com",[p["email"]],msg.as_string())
            conn.quit()
        # # data = {
        #     'task': request.data.get('task'), 
        #     'completed': request.data.get('completed'), 
        #     'user': request.user.id
        # }
        # serializer = TodoSerializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()
        f = open(r'static/pdf/absensi.pdf',"rb")
        response = HttpResponse(filepdf,'application/pdf')
        # response["Content-Disposition"] = "attachment;filename=absensi.pdf"
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response("sdsdsd",status=200)
        return response