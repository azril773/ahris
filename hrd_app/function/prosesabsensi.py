from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from multiprocessing import Pool
from ..models import *
import pandas as pd
from datetime import date, datetime, timedelta
def nlh(att,luserid,ddr, rangetgl,pegawai,jamkerja,status_lh,hari,cabang,ddt,ddtor,absensi):
    dt = ddt
    insertdr = []
    if not att:
        return False 
    print("Looping mulai")
    dta = []
    [[dta.append(a) for a in att if str(a["userid"]) == str(ab.pegawai.userid) and ab.tgl_absen == datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S").date() and a["userid"] in luserid] for ab in absensi]
    print("Looping selesai")
    # print(dta)
    for a in dta:
        if not a:
            continue
        if not a in ddr:
            insertdr.append(a)
            
        jam_absen = datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S")
        japlus = jam_absen + timedelta(minutes=2,seconds=30)
        jamin = jam_absen - timedelta(minutes=2,seconds=30)
        pg = next((pgw for pgw in pegawai if pgw["userid"] == a["userid"]),None)
        if pg is None:
            continue
        cekuser = [du for du in dt if int(du["userid"]) == int(a["userid"]) and du["jam_absen"].date() == jam_absen.date() and du["jam_absen"] > jamin and du["jam_absen"] < japlus and du["punch"] != a["punch"]]
        if len(cekuser) > 0:
            cekddt = [d for d in cekuser if jam_absen > d["jam_absen"]]
            if len(cekddt) >0:
                for c in cekddt:
                    ab = absensi_db.objects.using(cabang).filter(tgl_absen=jam_absen.date(),pegawai_id=pg["idp"])
                    if ab.exists():
                        ab = ab[0]
                        ab.masuk = ab.masuk if ab.masuk != c["jam_absen"].time() else None
                        ab.pulang = ab.pulang if ab.pulang != c["jam_absen"].time() else None
                        ab.istirahat = ab.istirahat if ab.istirahat != c["jam_absen"].time() else None
                        ab.kembali = ab.kembali if ab.kembali != c["jam_absen"].time() else None
                        ab.istirahat2 = ab.istirahat2 if ab.istirahat2 != c["jam_absen"].time() else None
                        ab.kembali2 = ab.kembali2 if ab.kembali2 != c["jam_absen"].time() else None
                        ab.masuk_b = ab.masuk_b if ab.masuk_b != c["jam_absen"].time() else None
                        ab.pulang_b = ab.pulang_b if ab.pulang_b != c["jam_absen"].time() else None
                        ab.istirahat_b = ab.istirahat_b if ab.istirahat_b != c["jam_absen"].time() else None
                        ab.kembali_b = ab.kembali_b if ab.kembali_b != c["jam_absen"].time() else None
                        ab.istirahat2_b = ab.istirahat2_b if ab.istirahat2_b != c["jam_absen"].time() else None
                        ab.kembali2_b = ab.kembali2_b if ab.kembali2_b != c["jam_absen"].time() else None
                        ab.save(using=cabang)
                        data_trans_db.objects.using(cabang).filter(userid=int(c["userid"]),jam_absen=c["jam_absen"]).delete()
                    else:
                        pass
            else:
                continue
        r = next((tgl for tgl in rangetgl if tgl == jam_absen.date()),None)
        if not r:
            continue
        tmin = r + timedelta(days=-1)
        tplus = r + timedelta(days=1)
        ab = absensi_db.objects.using(cabang).select_related('pegawai__kelompok_kerja').get(tgl_absen=r.date(), pegawai_id=pg['idp'])
        bb_msk = jam_absen - timedelta(hours=4)
        ba_msk = jam_absen + timedelta(hours=4)
        if ab.pegawai.kelompok_kerja is not None:
            if a["punch"] == 0:
                
                jkm = [jk for jk in jamkerja if jk.kk_id == ab.pegawai.kelompok_kerja.pk and jk.jam_masuk >= bb_msk.time() and jk.jam_masuk <= ba_msk.time() and jk.hari == hari]
                ds = []
                data = []
                for j in jkm:
                    if(j in data):
                        continue
                    data.append(j)
                    selisih = abs(datetime.combine(ab.tgl_absen, j.jam_masuk) - datetime.combine(ab.tgl_absen,jam_absen.time()))
                    ds.append(selisih)
                    getMin = min(ds)
                    jam = data[ds.index(getMin)]
                    ab.jam_masuk = jam.jam_masuk
                    ab.jam_pulang = jam.jam_pulang
                    ab.lama_istirahat = jam.lama_istirahat
                    ab.shift = jam.shift.shift if jam.shift is not None else None
            elif a['punch'] == 1:
                jkp = [jk for jk in jamkerja if jk.kk_id == ab.pegawai.kelompok_kerja.pk and jk.jam_pulang >= bb_msk.time() and jk.jam_pulang <= ba_msk.time() and jk.hari == hari]
                data = []
                ds = []
                for j in jkp:
                    if(j in data):
                        continue
                    data.append(j)
                    if ab.masuk is not None:
                        selisih = (abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))) + abs(datetime.combine(ab.tgl_absen, j.jam_masuk) - datetime.combine(ab.tgl_absen,ab.masuk))
                    elif ab.masuk_b is not None:
                        selisih = (abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))) + abs(datetime.combine(ab.tgl_absen, j.jam_masuk) - datetime.combine(ab.tgl_absen,ab.masuk_b))
                    else:
                        selisih = abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))
                    ds.append(selisih)
                    getMin = min(ds)
                    jam = data[ds.index(getMin)]
                    ab.jam_masuk = jam.jam_masuk
                    ab.jam_pulang = jam.jam_pulang
                    ab.lama_istirahat = jam.lama_istirahat
                    ab.shift = jam.shift.shift if jam.shift is not None else None
                
                
    # +++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if a["punch"] == 0 and jam_absen.hour >= 3 and jam_absen.hour < 18 :
            if ab.masuk is not None:
                if ab.masuk.hour > 18:
                    ab.masuk_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 10,
                        "mesin": a["mesin"],
                        "ket": "Masuk B"
                    }
                    dt.append(data)
                else:
                    ab.masuk = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": a["punch"],
                            "mesin": a["mesin"],
                            "ket": "Masuk"
                    }
                    dt.append(data)
            else:
                ab.masuk = jam_absen.time()
                ab.save(using=cabang)
                data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Masuk"
                }
                dt.append(data)
    # +++++++++++++++++++++++++++++++++++  MASUK MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 0 and jam_absen.hour > 18:
            if pg["status_id"] in status_lh:
                try:
                    ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
                    ab2.masuk = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 6,
                        "mesin": a["mesin"],
                        "ket": "Masuk Malam"
                    }
                    dt.append(data)
                except absensi_db.DoesNotExist:
                        absensi_db(tgl_absen=tplus.date(),pegawai_id=pg["idp"],masuk=jam_absen.time()).save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 6,
                            "mesin": a["mesin"],
                            "ket": "Masuk Malam"
                        }
                        dt.append(data)
            else:
                if ab.masuk is not None:
                    d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab.tgl_absen,ab.masuk)
                    if d.total_seconds() / 3600 > 7:
                        ab.masuk_b = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 6,
                            "mesin": a["mesin"],
                            "ket": "Masuk Malam"
                        }
                        dt.append(data)
                    else:
                        ab.masuk = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 6,
                            "mesin": a["mesin"],
                            "ket": "Masuk Malam"
                        }
                        dt.append(data)
                elif ab.pulang is not None or ab.istirahat is not None or ab.kembali is not None:
                    ab.masuk_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 6,
                        "mesin": a["mesin"],
                        "ket": "Masuk Malam"
                    }
                    dt.append(data)
                else:
                    ab.masuk = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 6,
                        "mesin": a["mesin"],
                        "ket": "Masuk Malam"
                    }
                    dt.append(data)
                    # continue
    # +++++++++++++++++++++++++++++++++++  ISTIRAHAT  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 2 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
            if ab.istirahat is not None:
                d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab.tgl_absen,ab.istirahat)
                if d.total_seconds() / 3600 > 5:
                    ab.istirahat_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 12,
                        "mesin": a["mesin"],
                        "ket": "Istirahat B"
                    }
                    dt.append(data)
                else:
                    ab.istirahat = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Istirahat"
                    }
                    dt.append(data)
            elif ab.pulang is not None or ab.masuk_b is not None:
                ab.istirahat_b = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 12,
                    "mesin": a["mesin"],
                    "ket": "Istirahat B"
                }
                dt.append(data)
            else:
                ab.istirahat = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": a["punch"],
                    "mesin": a["mesin"],
                    "ket": "Istirahat"
                }
                dt.append(data)
                        
    # +++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 2 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
            if int(jam_absen.hour) > 21:
                if ab.istirahat is not None:
                    if int(ab.istirahat.hour) > 21:
                        ab.istirahat = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 8,
                            "mesin": a["mesin"],
                            "ket": "Istirahat Malam"
                        }
                        dt.append(data)
                    else:
                        ab.istirahat_b = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 8,
                            "mesin": a["mesin"],
                            "ket": "Istirahat Malam"
                        }
                        dt.append(data)
                elif ab.pulang is not None or ab.masuk_b is not None:
                    ab.istirahat_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 8,
                        "mesin": a["mesin"],
                        "ket": "Istirahat Malam"
                    }
                    dt.append(data)
                else:
                    ab.istirahat = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 8,
                        "mesin": a["mesin"],
                        "ket": "Istirahat Malam"
                    }
                    dt.append(data)
                    
            elif int(jam_absen.hour) < 8:
                if pg["status_id"] in status_lh:
                    ab.istirahat = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 8,
                        "mesin": a["mesin"],
                        "ket": "Istirahat Malam"
                    }
                    dt.append(data)
                else:
                    try:
                        # tanda
                        ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai_id=pg["idp"])
                        if ab2.istirahat is not None:
                            if ab2.istirahat.hour < 9:
                                ab2.istirahat = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 8,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.istirahat_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 8,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat Malam"
                                }
                                dt.append(data)
                        elif ab2.masuk is not None:
                            if ab2.masuk.hour > 18:
                                ab2.istirahat = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 8,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.istirahat_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 8,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat Malam"
                                }
                                dt.append(data)
                        elif ab2.masuk_b is not None:
                            if int(ab2.masuk_b.hour) > 18:
                                ab2.istirahat_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 8,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.istirahat = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 8,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat Malam"
                                }
                                dt.append(data)
                        else:
                            ab.istirahat = jam_absen.time()
                            ab.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen,
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                    except absensi_db.DoesNotExist:
                        ab.istirahat = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 8,
                            "mesin": a["mesin"],
                            "ket": "Istirahat Malam"
                        }
        elif a["punch"] == 4 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
            if ab.istirahat2 is not None:
                d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab.tgl_absen,ab.istirahat2)
                if d.total_seconds() / 3600 > 5:
                    ab.istirahat2_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 14,
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2 B"
                    }
                    dt.append(data)
                else:
                    ab.istirahat2 = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2"
                    }
                    dt.append(data)
            elif ab.kembali2 is not None or ab.masuk_b is not None:
                ab.istirahat2_b = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 14,
                    "mesin": a["mesin"],
                    "ket": "Istirahat 2 B"
                }
                dt.append(data)
            else:
                ab.istirahat2 = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": a["punch"],
                    "mesin": a["mesin"],
                    "ket": "Istirahat 2"
                }
                dt.append(data)
    # +++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 4 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
            if int(jam_absen.hour) > 21:
                if ab.istirahat2 is not None:
                    if ab.istirahat2.hour > 21:
                        ab.istirahat2 = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 10,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2 Malam"
                        }
                        dt.append(data)
                    else:
                        ab.istirahat2_b = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 10,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2 Malam"
                        }
                        dt.append(data)
                elif ab.masuk_b is not None or ab.istirahat_b is not None and ab.pulang_b is not None:
                    ab.istirahat2_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 10,
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2 Malam"
                    }
                else:
                    ab.istirahat2 = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 10,
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2 Malam"
                    }
                    dt.append(data)
            if pg["status_id"] in status_lh:                                            
                ab.istirahat2 = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 10,
                    "mesin": a["mesin"],
                    "ket": "Istirahat 2 Malam"
                }
                dt.append(data)
            else:
                try:
                    ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai_id=pg["idp"])
                    if ab2.istirahat2 is not None:
                        if not ab2.istirahat2.hour < 9:
                            ab2.istirahat2_b = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 10,
                                "mesin": a["mesin"],
                                "ket": "Istirahat 2 Malam"
                            }
                            dt.append(data)
                        else:
                            pass
                    elif ab2.masuk is not None:
                        if ab2.masuk.hour > 18:
                            ab2.istirahat2 = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 10,
                                "mesin": a["mesin"],
                                "ket": "Istirahat 2 Malam"
                            }
                            dt.append(data)
                        else:
                            ab2.istirahat2_b = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 10,
                                "mesin": a["mesin"],
                                "ket": "Istirahat 2 Malam"
                            }
                            dt.append(data)
                    elif ab2.masuk_b is not None:
                        if int(ab2.masuk_b.hour) > 18:
                            ab2.istirahat2_b = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 10,
                                "mesin": a["mesin"],
                                "ket": "Istirahat 2 Malam"
                            }
                            dt.append(data)
                        else:
                            ab2.istirahat2 = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 10,
                                "mesin": a["mesin"],
                                "ket": "Istirahat 2 Malam"
                            }
                            dt.append(data)
                    else:
                        ab.istirahat2 = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 10,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2 Malam"
                        }
                        dt.append(data)
                except absensi_db.DoesNotExist:
                    if not absensi_db.objects.using(cabang).filter(tgl_absen=jam_absen.date(),pegawai_id=ab.pegawai.pk).exists():
                        absensi_db(
                            tgl_absen=jam_absen.date(),
                            pegawai_id=ab.pegawai.pk,
                            istirahat2=jam_absen.time()
                        ).save(using=cabang)
                    else:
                        abm = absensi_db.objects.using(cabang).get(tgl_absen=jam_absen.date(),pegawai_id=ab.pegawai.pk)
                        abm.istirahat2 = jam_absen.time()
                        abm.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen - timedelta(days=1),
                        "punch": 10,
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2 Malam"
                    }
                    dt.append(data)
    # +++++++++++++++++++++++++++++++++++  KEMBALI +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 3 and int(jam_absen.hour) > 9:
            if ab.kembali is not None:
                d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab.tgl_absen,ab.kembali)
                if d.total_seconds() / 3600 > 5:
                    ab.kembali_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 13,
                        "mesin": a["mesin"],
                        "ket": "Kembali B"
                    }
                    dt.append(data)
                else:
                    pass
            elif ab.masuk_b is not None or ab.pulang is not None or ab.istirahat_b is not None:
                ab.kembali_b = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 13,
                    "mesin": a["mesin"],
                    "ket": "Kembali B"
                }
                dt.append(data)
            else:
                ab.kembali = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 3,
                    "mesin": a["mesin"],
                    "ket": "Kembali"
                }
                dt.append(data)
    # +++++++++++++++++++++++++++++++++++  KEMBALI 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 5 and int(jam_absen.hour) > 9:
            if ab.kembali2 is not None:
                d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab.tgl_absen,ab.istirahat2)
                if d.total_seconds() / 3600 > 5:
                    ab.kembali2_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 15,
                        "mesin": a["mesin"],
                        "ket": "Kembali 2 B"
                    }
                    dt.append(data)
                else:
                    pass
            elif ab.masuk_b is not None or ab.pulang is not None or ab.istirahat_b is not None:
                ab.kembali2_b = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 15,
                    "mesin": a["mesin"],
                    "ket": "Kembali 2 B"
                }
                dt.append(data)
            else:
                ab.kembali2 = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 5,
                    "mesin": a["mesin"],
                    "ket": "Kembali 2"
                }
                dt.append(data)
    # +++++++++++++++++++++++++++++++++++  KEMBALI MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 5 and int(jam_absen.hour) < 9:
            if pg["status_id"] in status_lh:
                ab.kembali2 = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 11,
                    "mesin": a["mesin"],
                    "ket": "Kembali 2 Malam"
                }
                dt.append(data)
            else:
                try:
                    ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai_id=pg["idp"])
                    if ab2.kembali2 is not None:
                        if not ab2.kembali2.hour < 9:
                            ab2.kembali2_b = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 11,
                                "mesin": a["mesin"],
                                "ket": "Kembali 2 Malam"
                            }
                            dt.append(data)
                        else:
                            pass
                    elif ab2.masuk is not None:
                        if ab2.masuk.hour > 18:
                            ab.kembali2 = jam_absen.time()
                            ab.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen ,
                                "punch": 11,
                                "mesin": a["mesin"],
                                "ket": "Kembali 2 Malam"
                            }
                            dt.append(data)
                        else:
                            ab2.kembali2_b = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 11,
                                "mesin": a["mesin"],
                                "ket": "Kembali 2 Malam"
                            }
                            dt.append(data)
                    elif ab2.masuk_b is not None:
                        if int(ab2.masuk_b.hour) > 18:
                            ab2.kembali2_b = jam_absen.time()
                            ab2.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 11,
                                "mesin": a["mesin"],
                                "ket": "Kembali 2 Malam"
                            }
                            dt.append(data)
                        else:
                            ab.kembali2 = jam_absen.time()
                            ab.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen ,
                                "punch": 11,
                                "mesin": a["mesin"],
                                "ket": "Kembali 2 Malam"
                            }
                            dt.append(data)
                    else:
                        ab.kembali2 = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen ,
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali 2 Malam"
                        }
                        dt.append(data)
                except absensi_db.DoesNotExist:
                    ab.kembali2 = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen - timedelta(days=1),
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Kembali 2 Malam"
                    }
                    dt.append(data)
    # +++++++++++++++++++++++++++++++++++  KEMBALI MALAM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 3 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 9):
            if int(jam_absen.hour) > 21:
                if ab.kembali is not None:
                    if not int(ab.kembali.hour) > 21:
                        ab.kembali_b = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali Malam"
                        }
                        dt.append(data)
                    else:
                        pass
                elif ab.pulang is not None or ab.masuk_b is not None or ab.istirahat_b is not None:
                    ab.kembali_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Kembali Malam"
                    }
                    dt.append(data)
                else:
                    ab.kembali = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Kembali Malam"
                    }
                    dt.append(data)
            elif int(jam_absen.hour) < 9:
                if pg["status_id"] in status_lh:
                    ab.kembali = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Kembali Malam"
                    }
                    dt.append(data)
                else:
                    try:
                        ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai_id=pg["idp"])
                        if ab2.kembali is not None:
                            if not ab2.kembali.hour < 9:
                                ab2.kembali_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 11,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali Malam"
                                }
                                dt.append(data)
                            else:
                                pass
                        elif ab2.masuk is not None:
                            if ab2.masuk.hour > 18:
                                ab2.kembali = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 11,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.kembali_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 11,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali Malam"
                                }
                                dt.append(data)
                        elif ab2.masuk_b is not None:
                            if int(ab2.masuk_b.hour) > 18:
                                ab2.kembali_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 11,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.kembali = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 11,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali Malam"
                                }
                                dt.append(data)
                        else:
                            ab.kembali = jam_absen.time()
                            ab.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1) ,
                                "punch": 11,
                                "mesin": a["mesin"],
                                "ket": "Kembali Malam"
                            }
                            dt.append(data)
                    except absensi_db.DoesNotExist:
                        ab.kembali = jam_absen.time()
                        ab.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen - timedelta(days=1),
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali Malam"
                        }
                        dt.append(data)
    # +++++++++++++++++++++++++++++++++++  PULANG  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 1 and int(jam_absen.hour) > 9:
            if ab.pulang is None: 
                if ab.istirahat_b is not None or ab.kembali_b is not None:
                    ab.pulang_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Pulang B"
                    }
                    dt.append(data)
                else:
                    ab.pulang = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 1,
                        "mesin": a["mesin"],
                        "ket": "Pulang"
                    }
                    dt.append(data)
            else:
                d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(r.date(),ab.pulang)
                if d.total_seconds() / 3600 >= 5:
                    ab.pulang_b = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Pulang B"
                    }
                    dt.append(data)
                else:
                   pass
    # +++++++++++++++++++++++++++++++++++  PULANG MALAM  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 1 and int(jam_absen.hour) < 9:
            if pg is not None:
                if pg["status_id"] in status_lh:
                    ab.pulang = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 7,
                        "mesin": a["mesin"],
                        "ket": "Pulang Malam"
                    }
                    dt.append(data)
                else:
                    try:
                        ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai_id=pg["idp"])
                        if ab2.pulang is not None:
                            if not ab2.pulang.hour < 9:
                                ab2.pulang_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen  - timedelta(days=1),
                                    "punch": 7,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang Malam"
                                }
                                dt.append(data)
                            else:
                                pass
                        elif ab2.masuk is not None:
                            if ab2.masuk.hour > 18:
                                ab2.pulang = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 7,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.pulang_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 7,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang Malam"
                                }
                                dt.append(data)
                        elif ab2.istirahat is not None:
                            if ab2.istirahat.hour < 9:
                                ab2.pulang = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 7,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.pulang_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 7,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang Malam"
                                }
                                dt.append(data)
                        elif ab2.masuk_b is not None:
                            if int(ab2.masuk_b.hour) > 18:
                                ab2.pulang_b = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 7,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang Malam"
                                }
                                dt.append(data)
                            else:
                                ab2.pulang = jam_absen.time()
                                ab2.save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen - timedelta(days=1),
                                    "punch": 7,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang Malam"
                                }
                                dt.append(data)
                        else:
                            ab.pulang = jam_absen.time()
                            ab.save(using=cabang)
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 7,
                                "mesin": a["mesin"],
                                "ket": "Pulang Malam"
                            }
                            dt.append(data)
                    except absensi_db.DoesNotExist:
                        if not absensi_db.objects.using(cabang).filter(tgl_absen=tmin.date(),pegawai_id=ab.pegawai.pk).exists():
                            absensi_db(
                                tgl_absen=tmin.date(),
                                pegawai_id=ab.pegawai.pk,
                                pulang=jam_absen.time()
                            ).save(using=cabang)
                        else:
                            abm = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai_id=ab.pegawai.pk)
                            abm.pulang = jam_absen.time()
                            abm.save(using=cabang)
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen - timedelta(days=1),
                            "punch": 7,
                            "mesin": a["mesin"],
                            "ket": "Pulang Malam"
                        }
                        dt.append(data)
                        
    bulk = [data_raw_db(userid=dr["userid"],jam_absen=dr["jam_absen"],punch=dr["punch"],mesin=dr["mesin"]) for dr in insertdr]
    data_raw_db.objects.using(cabang).bulk_create(bulk)
    for dt2 in dt:
        if not dt2 in ddtor:
            data_trans_db(
                userid=dt2["userid"],
                jam_absen=dt2["jam_absen"],
                punch=dt2["punch"],
                mesin=dt2["mesin"], 
                keterangan=dt2["ket"],
            ).save(using=cabang)
            

def lh(att,luserid,ddr, rangetgl,pegawai,jamkerja,status_lh,hari,cabang,ddt,ddtor,absensi):
    dt = ddt
    insertdr =[]
    dta = []
    [[dta.append(a) for a in att if str(a["userid"]) == str(ab.pegawai.userid) and ab.tgl_absen == datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S").date() and a["userid"] in luserid] for ab in absensi]
    print("Looping selesai")
    # print(dta)
    for a in dta:
        if not a:
            continue
        if not a in ddr:
            insertdr.append(a)  
        print("OK")
        jam_absen = datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S")
        japlus = jam_absen + timedelta(minutes=2,seconds=30)
        jamin = jam_absen - timedelta(minutes=2,seconds=30)
        pg = next((pgw for pgw in pegawai if pgw["userid"] == a["userid"]),None)
        cekuser = [du for du in dt if int(du["userid"]) == int(a["userid"]) and du["jam_absen"].date() == jam_absen.date() and du["jam_absen"] > jamin and du["jam_absen"] < japlus and du["punch"] != a["punch"]]
        if len(cekuser) > 0:
            cekddt = [d for d in cekuser if jam_absen > d["jam_absen"]]
            if len(cekddt) >0:
                for c in cekddt:
                    ab = absensi_db.objects.using(cabang).filter(tgl_absen=jam_absen.date(),pegawai_id=pg["idp"])
                    if ab.exists():
                        ab = ab[0]
                        ab.masuk = ab.masuk if ab.masuk != c["jam_absen"].time() else None
                        ab.pulang = ab.pulang if ab.pulang != c["jam_absen"].time() else None
                        ab.istirahat = ab.istirahat if ab.istirahat != c["jam_absen"].time() else None
                        ab.kembali = ab.kembali if ab.kembali != c["jam_absen"].time() else None
                        ab.istirahat2 = ab.istirahat2 if ab.istirahat2 != c["jam_absen"].time() else None
                        ab.kembali2 = ab.kembali2 if ab.kembali2 != c["jam_absen"].time() else None
                        ab.masuk_b = ab.masuk_b if ab.masuk_b != c["jam_absen"].time() else None
                        ab.pulang_b = ab.pulang_b if ab.pulang_b != c["jam_absen"].time() else None
                        ab.istirahat_b = ab.istirahat_b if ab.istirahat_b != c["jam_absen"].time() else None
                        ab.kembali_b = ab.kembali_b if ab.kembali_b != c["jam_absen"].time() else None
                        ab.istirahat2_b = ab.istirahat2_b if ab.istirahat2_b != c["jam_absen"].time() else None
                        ab.kembali2_b = ab.kembali2_b if ab.kembali2_b != c["jam_absen"].time() else None
                        ab.save(using=cabang)
                        data_trans_db.objects.using(cabang).filter(userid=int(c["userid"]),jam_absen=c["jam_absen"]).delete()
                    else:
                        pass
            else:
                continue
        # # Versi
        r = next((tgl for tgl in rangetgl if tgl.date() == jam_absen.date()),None)
        if not r:
            continue
        tplus = r + timedelta(days=1)
        ab = absensi_db.objects.using(cabang).select_related('pegawai__kelompok_kerja').get(tgl_absen=r.date(), pegawai_id=pg['idp'])
        bb_msk = jam_absen - timedelta(hours=4)
        ba_msk = jam_absen + timedelta(hours=4)
        jk = None
        if ab.pegawai.kelompok_kerja is not None:
            if a["punch"] == 0:
                jkm = [jk for jk in jamkerja if jk.kk_id == ab.pegawai.kelompok_kerja.pk and jk.jam_masuk >= bb_msk.time() and jk.jam_masuk <= ba_msk.time() and jk.hari == hari]
                ds = []
                data = []
                for j in jkm:
                    if(j in data):
                        continue
                    data.append(j)
                    selisih = abs(datetime.combine(ab.tgl_absen, j.jam_masuk) - datetime.combine(ab.tgl_absen,jam_absen.time()))
                    ds.append(selisih)
                    getMin = min(ds)
                    jam = data[ds.index(getMin)]
                    ab.jam_masuk = jam.jam_masuk
                    ab.jam_pulang = jam.jam_pulang
                    ab.lama_istirahat = jam.lama_istirahat
                    ab.shift = jam.shift.shift if jam.shift is not None else None
            elif a['punch'] == 1:
                jkp = [jk for jk in jamkerja if jk.kk_id == ab.pegawai.kelompok_kerja.pk and jk.jam_pulang >= bb_msk.time() and jk.jam_pulang <= ba_msk.time() and jk.hari == hari]
                data = []
                ds = []
                for j in jkp:
                    if(j in data):
                        continue
                    data.append(j)
                    if ab.masuk is not None:
                        selisih = (abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))) + abs(datetime.combine(ab.tgl_absen, j.jam_masuk) - datetime.combine(ab.tgl_absen,ab.masuk))
                    elif ab.masuk_b is not None:
                        selisih = (abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))) + abs(datetime.combine(ab.tgl_absen, j.jam_masuk) - datetime.combine(ab.tgl_absen,ab.masuk_b))
                    else:
                        selisih = abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))
                    ds.append(selisih)
                    getMin = min(ds)
                    jam = data[ds.index(getMin)]
                    ab.jam_masuk = jam.jam_masuk
                    ab.jam_pulang = jam.jam_pulang
                    ab.lama_istirahat = jam.lama_istirahat
                    ab.shift = jam.shift.shift if jam.shift is not None else None
                
                
        # ++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if a["punch"] == 0 and jam_absen.hour >= 4 and jam_absen.hour < 18 :
            try:
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            except absensi_db.DoesNotExist:
                absensi_db(
                    tgl_absen=tplus.date(),
                    pegawai_id=ab.pegawai.pk,
                ).save(using=cabang)
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            if ab.masuk is not None:
                if ab.masuk.hour > 18:
                    ab2.masuk = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 0,
                        "mesin": a["mesin"],
                        "ket": "Masuk"
                    }
                    dt.append(data)
                else:
                    ab.masuk = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 0,
                        "mesin": a["mesin"],
                        "ket": "Masuk"
                    }
                    dt.append(data)
            if ab.istirahat is not None:
                if ab.istirahat.hour < 9:
                    ab2.masuk = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 0,
                        "mesin": a["mesin"],
                        "ket": "Masuk"
                    }
                    dt.append(data)
                else:
                    ab.masuk = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 0,
                        "mesin": a["mesin"],
                        "ket": "Masuk"
                    }
                    dt.append(data)
            else:
                ab.masuk = jam_absen.time()
                ab.save(using=cabang)
                data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Masuk"
                }
                dt.append(data)
        # ++++++++++++++++++++++++++++++++++  MASUK MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 0 and jam_absen.hour > 18:
            # pastikan untuk userid hotel
            try:
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
                ab2.masuk = jam_absen.time()
                ab2.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen + timedelta(days=1),
                    "punch": 6,
                    "mesin": a["mesin"],
                    "ket": "Masuk Malam"
                }
                dt.append(data)
            except absensi_db.DoesNotExist:
                absensi_db(
                    pegawai_id=ab.pegawai.pk,
                    tgl_absen=tplus.date(),
                    masuk=jam_absen.time()
                ).save(using=cabang)
                data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 6,
                        "mesin": a["mesin"],
                        "ket": "Masuk Malam"
                }
                dt.append(data)
            
        # ++++++++++++++++++++++++++++++++++  ISTIRAHAT  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 2 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
            try:
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            except absensi_db.DoesNotExist:
                absensi_db(
                    tgl_absen=tplus.date(),
                    pegawai_id=ab.pegawai.pk,
                ).save(using=cabang)
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            if ab.istirahat is not None:
                if ab.istirahat.hour > 9 and ab.istirahat.hour < 21:
                    ab.istirahat  = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": a["punch"],
                    "mesin": a["mesin"],
                    "ket": "Istirahat"
                    }
                    dt.append(data)
                else:
                    ab2.istirahat  = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Istirahat"
                    }
                    dt.append(data)
            elif ab.pulang is not None:
                if ab.pulang.hour < 9:
                    ab2.istirahat  = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Istirahat"
                    }
                    dt.append(data)
                else:
                    ab.istirahat = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Istirahat"
                    }
                    dt.append(data)
            else:
                ab.istirahat = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": a["punch"],
                    "mesin": a["mesin"],
                    "ket": "Istirahat"
                }
                dt.append(data)
        # ++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 2 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
            if int(jam_absen.hour) < 8:
                if ab.istirahat is None:
                    ab.istirahat = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 8,
                        "mesin": a["mesin"],
                        "ket": "Istirahat Malam"
                    }
                    dt.append(data)
            else:
                ab2 = absensi_db.objects.using(cabang).filter(tgl_absen=tplus.date(),pegawai_id=pg["idp"]).last()
                if not ab2:
                    absensi_db(
                        tgl_absen=tplus.date(),
                        pegawai_id=pg["idp"],
                        istirahat=jam_absen.time()
                    ).save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 8,
                        "mesin": a["mesin"],
                        "ket": "Istirahat Malam"
                    }
                    dt.append(data)
                else:
                    ab2.istirahat = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 8,
                        "mesin": a["mesin"],
                        "ket": "Istirahat Malam"
                    }
                    dt.append(data)
        # ++++++++++++++++++++++++++++++++++  ISTIRAHAT 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 4 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
            try:
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            except absensi_db.DoesNotExist:
                absensi_db(
                    tgl_absen=tplus.date(),
                    pegawai_id=ab.pegawai.pk,
                ).save(using=cabang)
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            if ab.istirahat2 is not None:
                if ab.istirahat2.hour > 9 and ab.istirahat2.hour < 21:
                    ab.istirahat2 = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 8,
                        "mesin": a["mesin"],
                        "ket": "Istirahat Malam"
                    }
                    dt.append(data)
                else:
                    ab2.istirahat2 = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 4,
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2"
                    }
                    dt.append(data)
            elif ab.pulang is not None:
                if ab.pulang.hour < 9:
                    ab2.istirahat2 = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 4,
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2"
                    }
                    dt.append(data)
                else:
                    ab.istirahat2 = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 4,
                        "mesin": a["mesin"],
                        "ket": "Istirahat 2"
                    }
                    dt.append(data)
            else:
                ab.istirahat2 = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 4,
                    "mesin": a["mesin"],
                    "ket": "Istirahat 2"
                }
                dt.append(data)
        # ++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 4 and int(jam_absen.hour) < 8:
            ab.istirahat2 = jam_absen.time()
            ab.save(using=cabang)
            data = {
                "userid": a["userid"],
                "jam_absen": jam_absen,
                "punch": 8,
                "mesin": a["mesin"],
                "ket": "Istirahat 2 Malam"
            }
            dt.append(data)
        # ++++++++++++++++++++++++++++++++++  KEMBALI +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 3 and int(jam_absen.hour) > 9:
            try:
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            except absensi_db.DoesNotExist:
                absensi_db(
                    tgl_absen=tplus.date(),
                    pegawai_id=ab.pegawai.pk,
                ).save(using=cabang)
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            if ab.kembali is not None:
                if ab.kembali.hour > 9 and ab.kembali.hour < 21:
                    pass
                else:
                    ab2.kembali = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 3,
                        "mesin": a["mesin"],
                        "ket": "Kembali Istirahat"
                    }
                    dt.append(data)
            elif ab.pulang is not None:
                if ab.pulang.hour < 9 :
                    ab2.kembali = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 3,
                        "mesin": a["mesin"],
                        "ket": "Kembali Istirahat"
                    }
                    dt.append(data)
                else:
                    ab.kembali = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 3,
                        "mesin": a["mesin"],
                        "ket": "Kembali Istirahat"
                    }
                    dt.append(data)
            else:
                ab.kembali = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 3,
                    "mesin": a["mesin"],
                    "ket": "Kembali Istirahat"
                }
                dt.append(data)
        # ++++++++++++++++++++++++++++++++++  KEMBALI 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 5 and int(jam_absen.hour) > 9:
            try:
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            except absensi_db.DoesNotExist:
                absensi_db(
                    tgl_absen=tplus.date(),
                    pegawai_id=ab.pegawai.pk,
                ).save(using=cabang)
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            if ab.kembali2 is not None:
                if ab.kembali2.hour > 9 and ab.kembali2.hour < 21:
                    pass
                else:
                    ab2.kembali2 = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 5,
                        "mesin": a["mesin"],
                        "ket": "Kembali Istirahat 2"
                    }
                    dt.append(data)
            elif ab.pulang is not None:
                if ab.pulang.hour < 9 :
                    ab2.kembali2 = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 5,
                        "mesin": a["mesin"],
                        "ket": "Kembali Istirahat 2"
                    }
                    dt.append(data)
                else:
                    ab.kembali2 = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 5,
                        "mesin": a["mesin"],
                        "ket": "Kembali Istirahat 2"
                    }
                    dt.append(data)
            else:
                ab.kembali2 = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 5,
                    "mesin": a["mesin"],
                    "ket": "Kembali Istirahat 2"
                }
                dt.append(data)
        # ++++++++++++++++++++++++++++++++++  KEMBALI MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 5 and int(jam_absen.hour) < 9:
            ab.kembali2 = jam_absen.time()
            ab.save(using=cabang)
            data = {
                "userid": a["userid"],
                "jam_absen": jam_absen,
                "punch": 11,
                "mesin": a["mesin"],
                "ket": "Kembali Istirahat 2 Malam"
            }
            dt.append(data)
        # ++++++++++++++++++++++++++++++++++  KEMBALI MALAM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 3 and int(jam_absen.hour) < 9:
            ab.kembali = jam_absen.time()
            ab.save(using=cabang)
            data = {
                "userid": a["userid"],
                "jam_absen": jam_absen,
                "punch": 9,
                "mesin": a["mesin"],
                "ket": "Kembali Istirahat Malam"
            }
            dt.append(data)
        # ++++++++++++++++++++++++++++++++++  PULANG  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 1 and int(jam_absen.hour) > 9:
            try:
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            except absensi_db.DoesNotExist:
                absensi_db(
                    tgl_absen=tplus.date(),
                    pegawai_id=ab.pegawai.pk,
                ).save(using=cabang)
                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai_id=pg["idp"])
            if ab.pulang is not None:
                if ab.pulang.hour > 9:
                    pass
                else:
                    ab2.pulang = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 1,
                        "mesin": a["mesin"],
                        "ket": "Pulang"
                    }
                    dt.append(data)
            elif ab.masuk is not None:
                if not ab.masuk.hour > 18:
                    ab.pulang = jam_absen.time()
                    ab.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 1,
                        "mesin": a["mesin"],
                        "ket": "Pulang"
                    }
                    dt.append(data)
                else:
                    ab2.pulang = jam_absen.time()
                    ab2.save(using=cabang)
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen + timedelta(days=1),
                        "punch": 1,
                        "mesin": a["mesin"],
                        "ket": "Pulang"
                    }
                    dt.append(data)
            else:
                ab.pulang = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 1,
                    "mesin": a["mesin"],
                    "ket": "Pulang"
                }
                dt.append(data)
        # ++++++++++++++++++++++++++++++++++  PULANG MALAM  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        elif a["punch"] == 1 and int(jam_absen.hour) < 9:
                ab.pulang = jam_absen.time()
                ab.save(using=cabang)
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 7,
                    "mesin": a["mesin"],
                    "ket": "Pulang Malam"
                }
                dt.append(data)

    bulk = [data_raw_db(userid=dr["userid"],jam_absen=dr["jam_absen"],punch=dr["punch"],mesin=dr["mesin"]) for dr in insertdr]
    data_raw_db.objects.using(cabang).bulk_create(bulk)            
    for dt2 in dt:
        if not dt2 in ddtor:
            data_trans_db(
                userid=dt2["userid"],
                jam_absen=dt2["jam_absen"],
                punch=dt2["punch"],
                mesin=dt2["mesin"], 
                keterangan=dt2["ket"],
            ).save(using=cabang)
            

