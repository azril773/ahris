from ..lib import *

def trxabsen_non(r):
    mesin = mesin_db.objects.using(r.session["ccabang"]).filter(status="Active")
    absen = []
    for m in mesin:
        zk = ZK(m.ipaddress,4370,60)
        conn = zk.connect()
        conn.disable_device()
        absen += conn.get_attendance()
        conn.enable_device()
        conn.disconnect()
    today = datetime.today()
    absen = sorted(absen, key=lambda i: i.timestamp,reverse=True)
    userids = []
    # print(absen)    
    data = []
    for ab in absen:
        kode = str(today - ab.timestamp).split(" ")
        if len(kode) > 1:
            if int(kode[0]) > 2 and ab.user_id not in userids:
                userids.append(ab.user_id)
                data.append({"userid":ab.user_id,"lastabsen":ab.timestamp})
            else:
                pass
        else:
            pass
    print(userids)
    print(data)

# def trxabsen(r):
#     mesin = mesin_db.objects.using(r.session["ccabang"]).filter(status="Active")
#     pegawai = pegawai_db.objects.using(r.session['ccabang']).all().values("id","nama","userid")
#     pegawai_arsip = pegawai_db_arsip.objects.using(r.session['ccabang']).all().values("id","nama","userid")
#     pegawais = pegawai + pegawai_arsip
#     absen = []
#     for m in mesin:
#         zk = ZK(m.ipaddress,4370,60)
#         conn = zk.connect()
#         conn.disable_device()
#         for ab in conn.get_attendance():
#             pg = next((pgw for pgw in ))
#             absen.append({
#                 "userid":ab.user_id,
#                 "jam_absen":ab.timestamp,
#             })
#         conn.enable_device()
#         conn.disconnect()
#     return JsonResponse({''})