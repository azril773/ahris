from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from multiprocessing import Pool
from ..models import *
from datetime import date, datetime, timedelta
def nlh(att,luserid,ddr, rangetgl,pegawai,jamkerja,dt,status_lh,hari,cabang,ddt):
    dt = []
    if not att:
        pass
    else:
        for a in att:
            if a['userid'] in luserid:
                
                # simpan data raw jika belum ada di list ddr
                for d in ddr:
                    if d["userid"] == a["userid"] and d["jam_absen"] == a["jam_absen"] == d["punch"] == a["punch"] and d["mesin"] == a["mesin"]:
                        data_raw_db(
                            userid = a['userid'],
                            jam_absen = a['jam_absen'],
                            punch = a['punch'],
                            mesin = a['mesin']             
                        ).save(using=cabang)
                    else:
                        pass 
                
                jam_absen = datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S")
                pg = next((pgw for pgw in pegawai if pgw["userid"] == a["userid"]),None)
                # # Versi
            
                for r in rangetgl:
                    if jam_absen.date() == r.date():
                        tmin = r + timedelta(days=-1)
                        tplus = r + timedelta(days=1)
                        ab = absensi_db.objects.using(cabang).select_related('pegawai','pegawai__kelompok_kerja').get(tgl_absen=r.date(), pegawai__userid=a['userid'])
                        bb_msk = jam_absen - timedelta(hours=4)
                        ba_msk = jam_absen + timedelta(hours=4)
                        jk = None
                        if ab.pegawai.kelompok_kerja is not None:
                            if a["punch"] == 0:
                                # jamkerja_db.objects.using(cabang).values("jam_masuk","jam_pulang","lama_istirahat").filter(kk_id=ab.pegawai.kelompok_kerja.pk,jam_masuk__gte=bb_msk.time(),jam_masuk__lte=ba_msk.time())
                                
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
                            elif a['punch'] == 1:
                                jkp = [jk for jk in jamkerja if jk.kk_id == ab.pegawai.kelompok_kerja.pk and jk.jam_pulang >= bb_msk.time() and jk.jam_pulang <= ba_msk.time() and jk.hari == hari]
                                data = []
                                ds = []
                                for j in jkp:
                                    if(j in data):
                                        continue
                                    data.append(j)
                                    selisih = abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))
                                    ds.append(selisih)
                                    getMin = min(ds)
                                    jam = data[ds.index(getMin)]
                                    ab.jam_masuk = jam.jam_masuk
                                    ab.jam_pulang = jam.jam_pulang
                                    ab.lama_istirahat = jam.lama_istirahat
                                
                                
# ++++++++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        if a["punch"] == 0 and jam_absen.hour >= 4 and jam_absen.hour < 18 :
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
                                    s = jam_absen - datetime.combine(ab.tgl_absen,ab.masuk)
                                    if s.total_seconds() / 3600 > 7:
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
                            elif ab.pulang is not None or ab.istirahat is not None or ab.kembali is not None:
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
# ++++++++++++++++++++++++++++++++++++++++  MASUK MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 0 and jam_absen.hour > 18:
                            # pastikan untuk userid hotel
                            if pg is not None:
                                if pg["status_id"] in status_lh:
                                    try:
                                        ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
                                        if ab.masuk is not None:
                                            if ab.masuk.hour > 18:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                if ab2.masuk is not None:
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen + timedelta(days=1),
                                                        "punch": 6,
                                                        "mesin": a["mesin"],
                                                        "ket": "Masuk Malam"
                                                    }
                                                    dt.append(data)
                                                else:
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
                                        elif ab.istirahat is not None:
                                            if ab.istirahat.hour < 9:
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
                                            else:
                                                if ab2.masuk is not None:
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
                                                else:
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
                                        elif ab.kembali is not None:
                                            if ab.kembali.hour < 9:
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
                                            else:
                                                if ab2.masuk is not None:
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen + timedelta(days=1),
                                                        "punch": 6,
                                                        "mesin": a["mesin"],
                                                        "ket": "Masuk Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen + timedelta(days=1),
                                                        "punch": 6,
                                                        "mesin": a["mesin"],
                                                        "ket": "Masuk Malam"
                                                    }
                                                    dt.append(data)
                                        elif ab.pulang is not None:
                                            if ab.pulang.hour < 9:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                if ab2.masuk is not None:
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen + timedelta(days=1),
                                                        "punch": 6,
                                                        "mesin": a["mesin"],
                                                        "ket": "Masuk Malam"
                                                    }
                                                    dt.append(data)
                                                else:
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
                                    except absensi_db.DoesNotExist:
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
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen + timedelta(days=1),
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
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            if ab.istirahat is not None:
                                if (int(jam_absen.hour) - int(ab.istirahat.hour)) > 5:
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
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": a["punch"],
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat"
                                    }
                                    dt.append(data)
                            elif ab.pulang is not None or ab.kembali is not None or ab.masuk_b is not None:
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
                                        
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
                            if int(jam_absen.hour) > 21:
                                if ab.masuk_b is not None:
                                    if int(ab.masuk_b.hour) > 18:
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
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 8,
                                            "mesin": a["mesin"],
                                            "ket": "Istirahat Malam"
                                        }
                                        dt.append(data)
                                else:
                                    if ab.pulang_b is not None:
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
                                if pg is not None:
                                    if pg["status_id"] in status_lh:
                                        try:
                                            ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
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
                                            elif ab2.kembali is not None:
                                                if ab2.kembali.hour > 9:
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
                                            elif ab2.pulang is not None:
                                                if ab2.pulang.hour > 9:
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
                                            dt.append(data)
                                    else:
                                        try:
                                            # tanda
                                            ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
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
                                            elif ab2.kembali is not None:
                                                if ab2.kembali.hour < 9:
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
                                            elif ab2.pulang is not None:
                                                if ab2.pulang.hour < 9:
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
                                            else:
                                                if ab2.masuk_b is not None:
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
                                            dt.append(data)
                                else:
                                    pass
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            if ab.istirahat2 is not None:
                                if (int(jam_absen.hour) - int(ab.istirahat2.hour)) > 5:
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
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": a["punch"],
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat 2"
                                    }
                                    dt.append(data)
                            elif ab.pulang is not None or ab.kembali2 is not None or ab.masuk_b is not None:
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
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
                            if pg is not None:
                                if pg["status_id"] in status_lh:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
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
                                            pass
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.istirahat2 is not None:
                                                if int(ab2.istirahat2.hour) < 9:
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
                                            elif ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
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
                                            elif ab2.kembali is not None:
                                                if int(ab2.kembali.hour) > 8:
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
                                            elif ab2.pulang is not None:
                                                if int(ab2.pulang.hour) < 9:
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
                                        except absensi_db.DoesNotExist:
                                            absensi_db(
                                                tgl_absen=tmin.date(),
                                                pegawai_id=ab.pegawai.pk,
                                                istirahat2=jam_absen.time()
                                            ).save(using=cabang)
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen - timedelta(days=1),
                                                "punch": 10,
                                                "mesin": a["mesin"],
                                                "ket": "Istirahat 2 Malam"
                                            }
                                            dt.append(data)
                                else:
                                    try:
                                        ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.istirahat2 is not None:
                                            if ab2.istirahat2.hour < 9:
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
                                        elif ab2.kembali is not None:
                                            if ab2.kembali.hour < 9:
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
                                        elif ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
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
                                        else:
                                            if ab2.masuk_b is not None:
                                                if int(ab2.masuk_b.hour) > 18:
                                                    ab2.istirahat2_b = jam_absen
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
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.istirahat2 = jam_absen
                                                ab2.save(using=cabang)
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                    except absensi_db.DoesNotExist:
                                        absensi_db(
                                            tgl_absen=tmin.date(),
                                            pegawai_id=ab.pegawai.pk,
                                            istirahat2=jam_absen
                                        ).save(using=cabang)
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen - timedelta(days=1),
                                            "punch": 10,
                                            "mesin": a["mesin"],
                                            "ket": "Istirahat 2 Malam"
                                        }
                                        dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and int(jam_absen.hour) > 9:
                            if ab.kembali is not None:
                                if int(jam_absen.hour) - int(ab.kembali.hour) > 5:
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
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 3,
                                        "mesin": a["mesin"],
                                        "ket": "Kembali"
                                    }
                                    dt.append(data)
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
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) > 9:
                            if ab.kembali2 is not None:
                                if int(jam_absen.hour) - int(ab.kembali2.hour) > 5:
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
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 5,
                                        "mesin": a["mesin"],
                                        "ket": "Kembali 2"
                                    }
                                    dt.append(data)
                            # elif ab.masuk_b is not None or ab.pulang is not None or ab.istirahat2_b is not None:
                            #     ab.kembali2_b = jam_absen.time()
                            #     ab.save(using=cabang)
                            #     data = {
                            #         "userid": a["userid"],
                            #         "jam_absen": jam_absen,
                            #         "punch": 15,
                            #         "mesin": a["mesin"],
                            #         "ket": "Kembali 2 B"
                            #     }
                            #     dt.append(data)
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
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) < 9:
                            if pg is not None:
                                if pg["status_id"] in status_lh:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
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
                                            ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.istirahat2 is not None:
                                                if ab2.kembali2.hour < 9:
                                                    ab2.kembali2 = jam_absen.time()
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
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
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
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save(using=cabang)
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.kembali2 is not None:
                                                if int(ab2.kembali2.hour) > 8 and int(ab2.kembali2.hour) < 21:
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
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save(using=cabang)
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.pulang is not None:
                                                if int(ab2.pulang.hour) > 9:
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
                                                    ab2.kembali2 = jam_absen.time()
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
                                                ab2.kembali2 = jam_absen.time()
                                                ab2.save(using=cabang)
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali 2 Malam"
                                                }
                                                dt.append(data)
                                        except absensi_db.DoesNotExist:
                                            ab.kembali  = jam_absen.time()
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
                                        ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.kembali2 is not None:
                                            if ab2.kembali2.hour < 9:
                                                ab2.kembali2 = jam_absen.time()
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
                                        elif ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
                                                ab2.kembali2 = jam_absen.time()
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
                                            if ab2.masuk_b is not None:
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
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.kembali2 = jam_absen.time()
                                                ab2.save(using=cabang)
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
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
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 9):
                            if int(jam_absen.hour) > 21:
                                if ab.masuk_b is not None:
                                    if int(ab.masuk_b.hour) > 18:
                                        ab.kembali_b = jam_absen
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
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 11,
                                            "mesin": a["mesin"],
                                            "ket": "Kembali Malam"
                                        }
                                        dt.append(data)
                                else:
                                    if ab.pulang_b is not None:
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 11,
                                            "mesin": a["mesin"],
                                            "ket": "Kembali Malam"
                                        }
                                        dt.append(data)
                                    else:
                                        ab.kembali = jam_absen
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
                                if pg is not None:
                                    if pg["status_id"] in status_lh:
                                        # hari esok
                                        if ab.masuk is not None:
                                            if int(ab.masuk.hour) > 18:
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
                                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                                if ab2.kembali is not None:
                                                    if ab2.kembali.hour < 9:
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
                                                            "jam_absen": jam_absen,
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                elif ab2.masuk is not None:
                                                    if int(ab2.masuk.hour) < 18:
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
                                                elif ab2.istirahat is not None:
                                                    if ab2.istirahat.hour < 9:
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
                                                elif ab2.pulang is not None:
                                                    if ab2.pulang.hour < 9:
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
                                                            "jam_absen": jam_absen,
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
                                            except absensi_db.DoesNotExist:
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
                                            ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.kembali is not None:
                                                if ab2.kembali.hour < 9:
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
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.pulang is not None:
                                                if ab2.pulang.hour < 9:
                                                    ab2.kembali = jam_absen.time()
                                                    ab2.save(using=cabang)
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
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
                                            else:
                                                if ab2.masuk_b is not None:
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
                                        except absensi_db.DoesNotExist:
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
                                    pass
# ++++++++++++++++++++++++++++++++++++++++  PULANG  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
# ++++++++++++++++++++++++++++++++++++++++  PULANG MALAM  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 1 and int(jam_absen.hour) < 9:
                            if pg is not None:
                                if pg["status_id"] in status_lh:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
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
                                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                                ab2.pulang = jam_absen.time()
                                                ab2.save(using=cabang)
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            except:
                                                absensi_db(
                                                    tgl_absen=tmin.date(),
                                                    pegawai_id=pg["id"],
                                                    pulang=jam_absen.time(),
                                                ).save(using=cabang)
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
                                            ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.pulang is not None:
                                                if ab2.pulang.hour < 9:
                                                    ab2.pulang = jam_absen.time()
                                                    ab2.save(using=cabang)
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
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
                                            elif ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
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
                                            elif ab.istirahat is not None or ab.kembali is not None or ab.masuk is not None:
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
                                        except absensi_db.DoesNotExist:
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
                                        ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
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
                                                    "jam_absen": jam_absen,
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.masuk is not None:
                                            if ab2.masuk.hour > 18:
                                                ab2.pulang = jam_absen
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
                                                ab2.pulang_b = jam_absen
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
                                                ab2.pulang = jam_absen
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
                                                ab2.pulang_b = jam_absen
                                                ab2.save(using=cabang)
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.kembali is not None:
                                            if ab2.kembali.hour < 9:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save(using=cabang)
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
                                                ab2.pulang = jam_absen
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
                                                ab2.pulang_b = jam_absen
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
                                            if ab2.masuk_b is not None:
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
                                                    pass
                                            else:
                                                ab2.pulang = jam_absen.time()
                                                ab2.save(using=cabang)
                                    except absensi_db.DoesNotExist:
                                        absensi_db(
                                            pulang=jam_absen.time(),
                                            tgl_absen=tmin.date(),
                                            pegawai_id=ab.pegawai.pk
                                        ).save(using=cabang)
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen - timedelta(days=1),
                                            "punch": 7,
                                            "mesin": a["mesin"],
                                            "ket": "Pulang Malam"
                                        }
                                        dt.append(data)


                            # if ab.masuk is not None:
                            #     if int(ab.masuk.hour) < 18:
                            #         ab.kembali = jam_absen.time()
                            #         ab.save(using=cabang)
                            #     else:
                            #         pass
                            # else:
                            #     if ab.pulang is not None:
                            #        pass
                            #     else:
                            #         ab.kembali = jam_absen.time()
                            #         ab.save(using=cabang)


                            
                    else:
                        pass
    for b in dt:
        for dts in ddt:
            if dts["userid"] == b["userid"] and dts["jam_absen"] == b["jam_absen"] and dts["punch"] == b["punch"] and dts["mesin"] == b["mesin"] and dts["ket"] == b["ket"]:
                data_trans_db(
                    userid = b['userid'],
                    jam_absen = b['jam_absen'],
                    punch = b['punch'],
                    mesin = b['mesin'],
                    keterangan = b['ket']             
                ).save(using=cabang)
            else:
                pass  


def lh(att,luserid,ddr, rangetgl,pegawai,jamkerja,dt,status_lh,hari,cabang,ddt):
    dt = []
    if not att:
        pass
    else:
        for a in att:
            if a['userid'] in luserid:
                
                # simpan data raw jika belum ada di list ddr
                for d in ddr:
                    if d["userid"] == a["userid"] and d["jam_absen"] == a["jam_absen"] == d["punch"] == a["punch"] and d["mesin"] == a["mesin"]:
                        data_raw_db(
                            userid = a['userid'],
                            jam_absen = a['jam_absen'],
                            punch = a['punch'],
                            mesin = a['mesin']             
                        ).save(using=cabang)
                    else:
                        pass 
                
                jam_absen = datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S")
                pg = next((pgw for pgw in pegawai if pgw["userid"] == a["userid"]),None)
                # # Versi
            
                for r in rangetgl:
                    if jam_absen.date() == r.date():
                        tmin = r + timedelta(days=-1)
                        tplus = r + timedelta(days=1)
                        ab = absensi_db.objects.using(cabang).select_related('pegawai','pegawai__kelompok_kerja').get(tgl_absen=r.date(), pegawai__userid=a['userid'])
                        bb_msk = jam_absen - timedelta(hours=4)
                        ba_msk = jam_absen + timedelta(hours=4)
                        jk = None
                        if ab.pegawai.kelompok_kerja is not None:
                            if a["punch"] == 0:
                                # jamkerja_db.objects.using(cabang).values("jam_masuk","jam_pulang","lama_istirahat").filter(kk_id=ab.pegawai.kelompok_kerja.pk,jam_masuk__gte=bb_msk.time(),jam_masuk__lte=ba_msk.time())
                                
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
                            elif a['punch'] == 1:
                                jkp = [jk for jk in jamkerja if jk.kk_id == ab.pegawai.kelompok_kerja.pk and jk.jam_pulang >= bb_msk.time() and jk.jam_pulang <= ba_msk.time() and jk.hari == hari]
                                data = []
                                ds = []
                                for j in jkp:
                                    if(j in data):
                                        continue
                                    data.append(j)
                                    selisih = abs(datetime.combine(ab.tgl_absen, j.jam_pulang) - datetime.combine(ab.tgl_absen,jam_absen.time()))
                                    ds.append(selisih)
                                    getMin = min(ds)
                                    jam = data[ds.index(getMin)]
                                    ab.jam_masuk = jam.jam_masuk
                                    ab.jam_pulang = jam.jam_pulang
                                    ab.lama_istirahat = jam.lama_istirahat
                                
                                
# ++++++++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        if a["punch"] == 0 and jam_absen.hour >= 4 and jam_absen.hour < 18 :
                            try:
                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
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
                            except absensi_db.DoesNotExist:
                                absensi_db(
                                    pegawai_id=ab.pegawai.pk,
                                    tgl_absen=tplus.date(),
                                    masuk=jam_absen.time()
                                ).save(using=cabang)
                                data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen + timedelta(days=1),
                                        "punch": a["punch"],
                                        "mesin": a["mesin"],
                                        "ket": "Masuk"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  MASUK MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 0 and jam_absen.hour > 18:
                            # pastikan untuk userid hotel
                            try:
                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
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
                            

# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            try:
                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
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

                                else:
                                    if ab.pulang is not None:
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
                            except absensi_db.DoesNotExist:
                                absensi_db(
                                    pegawai_id=ab.pegawai.pk,
                                    tgl_absen=tplus.date(),
                                    masuk=jam_absen.time()
                                ).save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen + timedelta(days=1),
                                    "punch": a["punch"],
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
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
                                pass
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            try:
                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
                                if ab.istirahat2 is not None:
                                    if ab.istirahat2.hour > 9 and ab.istirahat2.hour < 21:
                                        pass
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
                                else:
                                    if ab.pulang is not None:
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
                            except absensi_db.DoesNotExist:
                                absensi_db(
                                    pegawai_id=ab.pegawai.pk,
                                    tgl_absen=tplus.date(),
                                    masuk=jam_absen.time()
                                ).save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen + timedelta(days=1),
                                    "punch": 4,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat 2"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
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
                                pass
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and int(jam_absen.hour) > 9:
                            try:
                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
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
                                else:
                                    if ab.pulang is not None:
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
                            except absensi_db.DoesNotExist:
                                absensi_db(
                                    pegawai_id=ab.pegawai.pk,
                                    tgl_absen=tplus.date(),
                                    masuk=jam_absen.time()
                                ).save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen + timedelta(days=1),
                                    "punch": 3,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali Istirahat"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) > 9:
                            try:
                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
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
                                else:
                                    if ab.pulang is not None:
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
                            except:
                                absensi_db(
                                    pegawai_id=ab.pegawai.pk,
                                    tgl_absen=tplus.date(),
                                    masuk=jam_absen.time()
                                ).save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen + timedelta(days=1),
                                    "punch": 5,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali Istirahat 2"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) < 9:
                            if ab.kembali2 is None:
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
                            else:
                                pass
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 9):
                            if ab.kembali is None:
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
                            else:
                                pass
# ++++++++++++++++++++++++++++++++++++++++  PULANG  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 1 and int(jam_absen.hour) > 9:
                            try:
                                ab2 = absensi_db.objects.using(cabang).get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
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
                                else:
                                    if ab.pulang is not None:
                                        if ab.pulang.hour < 9 :
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
                            except absensi_db.DoesNotExist:
                                absensi_db(
                                    pegawai_id=ab.pegawai.pk,
                                    tgl_absen=tplus.date(),
                                    masuk=jam_absen.time()
                                ).save(using=cabang)
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen + timedelta(days=1),
                                    "punch": 1,
                                    "mesin": a["mesin"],
                                    "ket": "Pulang"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  PULANG MALAM  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 1 and int(jam_absen.hour) < 9:
                            if ab.pulang is None:
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
                                pass

                            # if ab.masuk is not None:
                            #     if int(ab.masuk.hour) < 18:
                            #         ab.kembali = jam_absen.time()
                            #         ab.save(using=cabang)
                            #     else:
                            #         pass
                            # else:
                            #     if ab.pulang is not None:
                            #        pass
                            #     else:
                            #         ab.kembali = jam_absen.time()
                            #         ab.save(using=cabang)


                            
                    else:
                        pass
                    
    for b in dt:
        for dts in ddt:
            if dts["userid"] == b["userid"] and dts["jam_absen"] == b["jam_absen"] and dts["punch"] == b["punch"] and dts["mesin"] == b["mesin"] and dts["ket"] == b["ket"]:
                data_trans_db(
                    userid = b['userid'],
                    jam_absen = b['jam_absen'],
                    punch = b['punch'],
                    mesin = b['mesin'],
                    keterangan = b['ket']             
                ).save(using=cabang)
            else:
                pass 