from ..lib import *

def trxabsen(r):
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