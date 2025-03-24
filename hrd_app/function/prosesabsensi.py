from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from multiprocessing import Pool
from ..models import *
from hrd_app.controllers.lib import nama_hari
import pandas as pd
from datetime import date, datetime, timedelta
import time
import sys, os
def nlh(att,luserid,ddr, rangetgl,pegawai,jamkerja,status_lh,cabang,ddt,ddtor,absensi):
    print(datetime.now())
    try:
        dt = ddt
        insertdr = []
        if not att:
            return False 
        dta = []
        [[dta.append(a) for a in att if str(a["userid"]) == str(ab["pegawai__userid"]) and ab["tgl_absen"] == datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S").date() and a["userid"] in luserid] for ab in absensi]
        print("Looping selesai")
        # print(dta)
        start = time.perf_counter()
        for a in dta:
            if not a:
                continue
            if not a in ddr:
                insertdr.append(a)
                
            jam_absen = datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S")
            hari = nama_hari(jam_absen.strftime("%A"))
            r = next((tgl for tgl in rangetgl if tgl.date() == jam_absen.date()),None)
            if not r:
                continue
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
                        ab["masuk"] = ab["masuk"] if ab["masuk"] != c["jam_absen"].time() else None
                        ab["pulang"] = ab["pulang"] if ab["pulang"] != c["jam_absen"].time() else None
                        ab["istirahat"] = ab["istirahat"] if ab["istirahat"] != c["jam_absen"].time() else None
                        ab["kembali"] = ab["kembali"] if ab["kembali"] != c["jam_absen"].time() else None
                        ab["istirahat2"] = ab["istirahat2"] if ab["istirahat2"] != c["jam_absen"].time() else None
                        ab["kembali2"] = ab["kembali2"] if ab["kembali2"] != c["jam_absen"].time() else None
                        ab["masuk_b"] = ab["masuk_b"] if ab["masuk_b"] != c["jam_absen"].time() else None
                        ab["pulang_b"] = ab["pulang_b"] if ab["pulang_b"] != c["jam_absen"].time() else None
                        ab["istirahat_b"] = ab["istirahat_b"] if ab["istirahat_b"] != c["jam_absen"].time() else None
                        ab["kembali_b"] = ab["kembali_b"] if ab["kembali_b"] != c["jam_absen"].time() else None
                        ab["istirahat2_b"] = ab["istirahat2_b"] if ab["istirahat2_b"] != c["jam_absen"].time() else None
                        ab["kembali2_b"] = ab["kembali2_b"] if ab["kembali2_b"] != c["jam_absen"].time() else None
                        data_trans_db.objects.using(cabang).filter(userid=int(c["userid"]),jam_absen=c["jam_absen"]).delete()
                else:
                    continue

            tmin = r + timedelta(days=-1)
            tplus = r + timedelta(days=1)
            ab = next((a for a in absensi if a["tgl_absen"] == r.date() and a["pegawai_id"] == pg["idp"]),None)
            bb_msk = jam_absen - timedelta(hours=4)
            ba_msk = jam_absen + timedelta(hours=4)
            jam = None
            if ab["pegawai__kelompok_kerja_id"] is not None:
                if a["punch"] == 0:
                    jkm = [jk for jk in jamkerja if jk["kk_id"] == ab["pegawai__kelompok_kerja_id"] and jk["jam_masuk"] >= bb_msk.time() and jk["jam_masuk"] <= ba_msk.time() and jk["hari"] == hari]
                    ds = []
                    data = []
                    for j in jkm:
                        if(j in data):
                            continue
                        data.append(j)
                        if j["jam_masuk"] is None:
                            continue
                        selisih = abs(datetime.combine(ab["tgl_absen"], j["jam_masuk"]) - datetime.combine(ab["tgl_absen"],jam_absen.time()))
                        ds.append(selisih)
                        getMin = min(ds)
                        jam = data[ds.index(getMin)]
                elif a['punch'] == 1:
                    jkp = [jk for jk in jamkerja if jk["kk_id"] == ab["pegawai__kelompok_kerja_id"] and jk["jam_pulang"] >= bb_msk.time() and jk["jam_pulang"] <= ba_msk.time() and jk["hari"] == hari]
                    data = []
                    ds = []
                    for j in jkp:
                        if(j in data):
                            continue
                        data.append(j)
                        if ab["masuk"] is not None:
                            selisih = (abs(datetime.combine(ab["tgl_absen"], j["jam_pulang"]) - datetime.combine(ab["tgl_absen"],jam_absen.time()))) + abs(datetime.combine(ab["tgl_absen"], j["jam_masuk"]) - datetime.combine(ab["tgl_absen"],ab["masuk"]))
                        elif ab["masuk_b"] is not None:
                            selisih = (abs(datetime.combine(ab["tgl_absen"], j["jam_pulang"]) - datetime.combine(ab["tgl_absen"],jam_absen.time()))) + abs(datetime.combine(ab["tgl_absen"], j["jam_masuk"]) - datetime.combine(ab["tgl_absen"],ab["masuk_b"]))
                        else:
                            selisih = abs(datetime.combine(ab["tgl_absen"], j["jam_pulang"]) - datetime.combine(ab["tgl_absen"],jam_absen.time()))
                        ds.append(selisih)
                        getMin = min(ds)
                        jam = data[ds.index(getMin)]
                if jam is not None:
                    ab["jam_masuk"] = jam["jam_masuk"]
                    ab["jam_pulang"] = jam["jam_pulang"]
                    ab["lama_istirahat"] = jam["lama_istirahat"]
                    ab["shift"] = jam["shift__shift"]
                else:
                    pass
        # +++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            if a["punch"] == 0 and jam_absen.hour >= 1 and jam_absen.hour < 18 :
                ab["masuk"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]),None)
                if ab["masuk"] is not None:
                    if ab["masuk"].hour > 18:
                        ab["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 6,
                            "mesin": a["mesin"],
                            "ket": "Masuk Malam"
                        }
                        dt.append(data)
                    else:
                        ab2["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 6,
                            "mesin": a["mesin"],
                            "ket": "Masuk Malam"
                        }
                        dt.append(data)
                elif ab["pulang"] is not None:
                    if ab["pulang"].hour > 9:
                        ab2["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 6,
                            "mesin": a["mesin"],
                            "ket": "Masuk Malam"
                        }
                        dt.append(data)
                    else:
                        ab["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 6,
                            "mesin": a["mesin"],
                            "ket": "Masuk Malam"
                        }
                        dt.append(data)
                else:
                    ab["masuk"] = jam_absen.time()
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
                ab["istirahat"] = jam_absen.time()
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
                    ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]),None)
                    if ab["istirahat"] is not None:
                        if int(ab["istirahat"].hour) > 21:
                            ab["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen,
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                        else:
                            ab2["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen + timedelta(days=1),
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                    elif ab["masuk"] is not None:
                        if ab["masuk"].hour > 18:
                            ab["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen,
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                        else:
                            ab2["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen + timedelta(days=1),
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)

                    else:
                        ab["istirahat"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 8,
                            "mesin": a["mesin"],
                            "ket": "Istirahat Malam"
                        }
                        dt.append(data)
                        
                elif int(jam_absen.hour) < 8:
                    ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tmin.date() and abs["pegawai_id"] == pg["idp"]),None)
                    if ab2["istirahat"] is not None:
                        if ab2["istirahat"].hour < 9:
                            ab2["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                        else:
                            ab["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen,
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                    elif ab2["masuk"] is not None:
                        if ab2["masuk"].hour > 18:
                            ab2["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen - timedelta(days=1),
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                        else:
                            ab["istirahat"] = jam_absen.time()
                            data = {
                                "userid": a["userid"],
                                "jam_absen": jam_absen,
                                "punch": 8,
                                "mesin": a["mesin"],
                                "ket": "Istirahat Malam"
                            }
                            dt.append(data)
                    else:
                        ab2["istirahat"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen  - timedelta(days=1),
                            "punch": 8,
                            "mesin": a["mesin"],
                            "ket": "Istirahat Malam"
                        }
                        dt.append(data)
            # +++++++++++++++++++++++++++++++++++  ISTIRAHAT 2  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif a["punch"] == 4 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                ab["istirahat2"] = jam_absen.time()
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": a["punch"],
                    "mesin": a["mesin"],
                    "ket": "Istirahat 2"
                }
                dt.append(data)
        # +++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif a["punch"] == 4 and int(jam_absen.hour) < 8:
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tmin.date() and abs["pegawai_id"] == pg["idp"]),None)
                if ab2["istirahat2"] is not None:
                    if ab2["istirahat2"].hour < 9:
                        ab2["isitirahat2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen - timedelta(days=1),
                            "punch": 10,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2 Malam"
                        }
                        dt.append(data)
                    else:
                        ab["isitirahat2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 10,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2 Malam"
                        }
                        dt.append(data)
                elif ab2["masuk"] is not None:
                    if ab2["masuk"].hour > 18:
                        ab2["istirahat2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen - timedelta(days=1),
                            "punch": 10,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2 Malam"
                        }
                        dt.append(data)
                    else:
                        ab["istirahat"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 10,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2 Malam"
                        }
                        dt.append(data)
                else:
                    ab2["istirahat2"] = jam_absen.time()
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
                ab["kembali"] = jam_absen.time()
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
                ab["kembali2"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tmin.date() and abs["pegawai_id"] == pg["idp"]),None)
                if ab2["kembali2"] is not None:
                    if ab2["kembali2"].hour < 9:
                        pass
                    else:
                        ab["kembali2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali 2 Malam"
                        }
                        dt.append(data)
                elif ab2["masuk"] is not None:
                    if ab2["masuk"].hour > 18:
                        ab2["kembali2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen - timedelta(days=1),
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali 2 Malam"
                        }
                        dt.append(data)
                    else:
                        ab["kembali2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali 2 Malam"
                        }
                        dt.append(data)
                else:
                    ab2["kembali2"] = jam_absen.time()
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen - timedelta(days=1),
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Kembali 2 Malam"
                    }
                    dt.append(data)
        # +++++++++++++++++++++++++++++++++++  KEMBALI MALAM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif a["punch"] == 3 and int(jam_absen.hour) < 9:
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tmin.date() and abs["pegawai_id"] == pg["idp"]),None)
                if ab2["kembali"] is not None:
                    if ab2["kembali"].hour < 9:
                        pass
                    else:
                        ab["kembali"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali Malam"
                        }
                        dt.append(data)
                elif ab2["masuk"] is not None:
                    if ab2["masuk"].hour > 18:
                        ab2["kembali"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen - timedelta(days=1) ,
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali Malam"
                        }
                        dt.append(data)
                    else:
                        ab["kembali"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 11,
                            "mesin": a["mesin"],
                            "ket": "Kembali Malam"
                        }
                        dt.append(data)
                else:
                    ab2["kembali"] = jam_absen.time()
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen - timedelta(days=1) ,
                        "punch": 11,
                        "mesin": a["mesin"],
                        "ket": "Kembali Malam"
                    }
                    dt.append(data)
        # +++++++++++++++++++++++++++++++++++  PULANG  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif a["punch"] == 1 and int(jam_absen.hour) > 9:
                ab["pulang"] = jam_absen.time()
                data = {
                    "userid": a["userid"],
                    "jam_absen": jam_absen,
                    "punch": 1,
                    "mesin": a["mesin"],
                    "ket": "Pulang"
                }
                dt.append(data)
        # +++++++++++++++++++++++++++++++++++  PULANG MALAM  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif a["punch"] == 1 and int(jam_absen.hour) < 9:
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tmin.date() and abs["pegawai_id"] == pg["idp"]),None)
                if ab2["pulang"] is not None:
                    if ab2["pulang"].hour < 9:
                        pass
                    else:
                        ab["pulang"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 7,
                            "mesin": a["mesin"],
                            "ket": "Pulang Malam"
                        }
                        dt.append(data)
                # elif ab["masuk"] is not None:
                #     if ab["masuk"].hour > 18:
                #         ab["pulang"] = jam_absen.time()
                #         data = {
                #             "userid": a["userid"],
                #             "jam_absen": jam_absen,
                #             "punch": 7,
                #             "mesin": a["mesin"],
                #             "ket": "Pulang Malam"
                #         }
                #         dt.append(data)
                #     else:
                #         ab2["pulang"] = jam_absen.time()
                #         data = {
                #             "userid": a["userid"],
                #             "jam_absen": jam_absen - timedelta(days=1),
                #             "punch": 7,
                #             "mesin": a["mesin"],
                #             "ket": "Pulang Malam"
                #         }
                #         dt.append(data)
                elif ab2["masuk"] is not None:
                    if ab2["masuk"].hour > 18:
                        ab2["pulang"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen - timedelta(days=1),
                            "punch": 7,
                            "mesin": a["mesin"],
                            "ket": "Pulang Malam"
                        }
                        dt.append(data)
                    else:
                        ab["pulang"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 7,
                            "mesin": a["mesin"],
                            "ket": "Pulang Malam"
                        }
                        dt.append(data)
                else:
                    ab2["pulang"] = jam_absen.time()
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen - timedelta(days=1),
                        "punch": 7,
                        "mesin": a["mesin"],
                        "ket": "Pulang Malam"
                    }
                    dt.append(data)
        end = time.perf_counter()
        print(f"PROSES ABSENSI LOOP {end-start} detik")

        start = time.perf_counter()
        absensi_db.objects.using(cabang).bulk_update([absensi_db(id=abs["id"],pegawai_id=abs["pegawai_id"],tgl_absen=abs["tgl_absen"],masuk=abs["masuk"],istirahat=abs['istirahat'],kembali=abs["kembali"],istirahat2=abs["istirahat2"],kembali2=abs["kembali2"],pulang=abs["pulang"],masuk_b=abs["masuk_b"],istirahat_b=abs["istirahat_b"],kembali_b=abs["kembali_b"],istirahat2_b=abs["istirahat2_b"],kembali2_b=abs["kembali2_b"],pulang_b=abs["pulang_b"],jam_masuk=abs["jam_masuk"],jam_pulang=abs["jam_pulang"],lama_istirahat=abs["lama_istirahat"],shift=abs["shift"]) for abs in absensi],["pegawai_id","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","jam_masuk","jam_pulang","lama_istirahat","shift"],batch_size=2300)   
        end = time.perf_counter()
        print(f"PROSES ABSENSI UPDATE {end-start} detik. {len(absensi)} data")

        start = time.perf_counter()
        bulkraw = [data_raw_db(userid=dr["userid"],jam_absen=dr["jam_absen"],punch=dr["punch"],mesin=dr["mesin"]) for dr in insertdr]
        data_raw_db.objects.using(cabang).bulk_create(bulkraw,batch_size=2300)    
        end = time.perf_counter()
        print(f"PROSES RAW {end-start} detik. {len(insertdr)} data")
            
        start = time.perf_counter()
        bulktrans = [data_trans_db(userid=t["userid"],jam_absen=t["jam_absen"],punch=t["punch"],mesin=t["mesin"],keterangan=t["ket"]) for t in dt if not t in ddtor]
        data_trans_db.objects.using(cabang).bulk_create(bulktrans,batch_size=2300)
        end = time.perf_counter()
        print(f"PROSES ABSENSI TRANS {end-start} detik. {len(bulktrans)} data")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

def lh(att,luserid,ddr, rangetgl,pegawai,jamkerja,status_lh,cabang,ddt,ddtor,absensi):
    print(datetime.now())
    try:
        dt = ddt
        insertdr =[]
        dta = []
        [[dta.append(a) for a in att if str(a["userid"]) == str(ab["pegawai__userid"]) and ab["tgl_absen"] == datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S").date() and a["userid"] in luserid] for ab in absensi]
        print("Looping selesai")
        # print(dta)
        start = time.perf_counter()
        for a in dta:
            if not a:
                continue
            if not a in ddr:
                insertdr.append(a)  


            jam_absen = datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S")
            hari = nama_hari(jam_absen.strftime("%A"))
            r = next((tgl for tgl in rangetgl if tgl.date() == jam_absen.date()),None)
            if not r:
                continue
            
            japlus = jam_absen + timedelta(minutes=2,seconds=30)
            jamin = jam_absen - timedelta(minutes=2,seconds=30)
            pg = next((pgw for pgw in pegawai if pgw["userid"] == a["userid"]),None)
            if not pg:
                continue
            cekuser = [du for du in dt if int(du["userid"]) == int(a["userid"]) and du["jam_absen"].date() == jam_absen.date() and du["jam_absen"] > jamin and du["jam_absen"] < japlus and du["punch"] != a["punch"]]
            if len(cekuser) > 0:
                cekddt = [d for d in cekuser if jam_absen > d["jam_absen"]]
                if len(cekddt) >0:
                    for c in cekddt:
                        ab["masuk"] = ab["masuk"] if ab["masuk"] != c["jam_absen"].time() else None
                        ab["pulang"] = ab["pulang"] if ab["pulang"] != c["jam_absen"].time() else None
                        ab["istirahat"] = ab["istirahat"] if ab["istirahat"] != c["jam_absen"].time() else None
                        ab["kembali"] = ab["kembali"] if ab["kembali"] != c["jam_absen"].time() else None
                        ab["istirahat2"] = ab["istirahat2"] if ab["istirahat2"] != c["jam_absen"].time() else None
                        ab["kembali2"] = ab["kembali2"] if ab["kembali2"] != c["jam_absen"].time() else None
                        ab["masuk_b"] = ab["masuk_b"] if ab["masuk_b"] != c["jam_absen"].time() else None
                        ab["pulang_b"] = ab["pulang_b"] if ab["pulang_b"] != c["jam_absen"].time() else None
                        ab["istirahat_b"] = ab["istirahat_b"] if ab["istirahat_b"] != c["jam_absen"].time() else None
                        ab["kembali_b"] = ab["kembali_b"] if ab["kembali_b"] != c["jam_absen"].time() else None
                        ab["istirahat2_b"] = ab["istirahat2_b"] if ab["istirahat2_b"] != c["jam_absen"].time() else None
                        ab["kembali2_b"] = ab["kembali2_b"] if ab["kembali2_b"] != c["jam_absen"].time() else None
                        data_trans_db.objects.using(cabang).filter(userid=int(c["userid"]),jam_absen=c["jam_absen"]).delete()
                else:
                    continue

            tplus = r + timedelta(days=1)
            ab = next((a for a in absensi if a["tgl_absen"] == r.date() and a["pegawai_id"] == pg["idp"]),None)

            bb_msk = jam_absen - timedelta(hours=4)
            ba_msk = jam_absen + timedelta(hours=4)
            jam = None
            if ab["pegawai__kelompok_kerja_id"] is not None:
                if a["punch"] == 0:
                    jkm = [jk for jk in jamkerja if jk["kk_id"] == ab["pegawai__kelompok_kerja_id"] and jk["jam_masuk"] >= bb_msk.time() and jk["jam_masuk"] <= ba_msk.time() and jk["hari"] == hari]
                    ds = []
                    data = []
                    for j in jkm:
                        if(j in data):
                            continue
                        data.append(j)
                        selisih = abs(datetime.combine(ab["tgl_absen"], j["jam_masuk"]) - datetime.combine(ab["tgl_absen"],jam_absen.time()))
                        ds.append(selisih)
                        getMin = min(ds)
                        jam = data[ds.index(getMin)]
                elif a['punch'] == 1:
                    jkp = [jk for jk in jamkerja if jk["kk_id"] == ab["pegawai__kelompok_kerja_id"] and jk["jam_pulang"] >= bb_msk.time() and jk["jam_pulang"] <= ba_msk.time() and jk["hari"] == hari]
                    data = []
                    ds = []
                    for j in jkp:
                        if(j in data):
                            continue
                        data.append(j)
                        if ab["masuk"] is not None:
                            selisih = (abs(datetime.combine(ab["tgl_absen"], j["jam_pulang"]) - datetime.combine(ab["tgl_absen"],jam_absen.time()))) + abs(datetime.combine(ab["tgl_absen"], j["jam_masuk"]) - datetime.combine(ab["tgl_absen"],ab["masuk"]))
                        else:
                            selisih = abs(datetime.combine(ab["tgl_absen"], j["jam_pulang"]) - datetime.combine(ab["tgl_absen"],jam_absen.time()))
                        ds.append(selisih)
                        getMin = min(ds)
                        jam = data[ds.index(getMin)]

                if jam is not None:
                    ab["jam_masuk"] = jam["jam_masuk"]
                    ab["jam_pulang"] = jam["jam_pulang"]
                    ab["lama_istirahat"] = jam["lama_istirahat"]
                    ab["shift"] = jam["shift__shift"]
                else:
                    pass
                    
                    
            # ++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            if a["punch"] == 0 and jam_absen.hour < 18 :
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]),None)
                if ab["masuk"] is not None:
                    if ab["masuk"].hour > 18:
                        ab2["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 0,
                            "mesin": a["mesin"],
                            "ket": "Masuk"
                        }
                        dt.append(data)
                    else:
                        ab["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 0,
                            "mesin": a["mesin"],
                            "ket": "Masuk"
                        }
                        dt.append(data)
                elif ab["istirahat"] is not None:
                    if ab["istirahat"].hour < 9:
                        ab2["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 0,
                            "mesin": a["mesin"],
                            "ket": "Masuk"
                        }
                        dt.append(data)
                    else:
                        ab["masuk"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 0,
                            "mesin": a["mesin"],
                            "ket": "Masuk"
                        }
                        dt.append(data)
                else:
                    ab["masuk"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]),None)
                ab2["masuk"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]),None)
                if ab["istirahat"] is not None:
                    if ab["istirahat"].hour > 9 and ab["istirahat"].hour < 21:
                        ab["istirahat"]  = jam_absen.time()
                        data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": a["punch"],
                        "mesin": a["mesin"],
                        "ket": "Istirahat"
                        }
                        dt.append(data)
                    else:
                        ab2["istirahat"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": a["punch"],
                            "mesin": a["mesin"],
                            "ket": "Istirahat"
                        }
                        dt.append(data)
                elif ab["pulang"] is not None:
                    if ab["pulang"].hour < 9:
                        ab2["istirahat"]  = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": a["punch"],
                            "mesin": a["mesin"],
                            "ket": "Istirahat"
                        }
                        dt.append(data)
                    else:
                        ab["istirahat"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": a["punch"],
                            "mesin": a["mesin"],
                            "ket": "Istirahat"
                        }
                        dt.append(data)
                else:
                    ab["istirahat"] = jam_absen.time()
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
                    if ab["istirahat"] is None:
                        ab["istirahat"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 8,
                            "mesin": a["mesin"],
                            "ket": "Istirahat Malam"
                        }
                        dt.append(data)
                else:
                    ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]))
                    ab2["istirahat"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]))
                if ab["istirahat2"] is not None:
                    if ab["istirahat2"].hour > 9 and ab["istirahat2"].hour < 21:
                        ab["istirahat2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 8,
                            "mesin": a["mesin"],
                            "ket": "Istirahat Malam"
                        }
                        dt.append(data)
                    else:
                        ab2["istirahat2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 4,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2"
                        }
                        dt.append(data)
                elif ab["pulang"] is not None:
                    if ab["pulang"].hour < 9:
                        ab2["istirahat2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 4,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2"
                        }
                        dt.append(data)
                    else:
                        ab["istirahat2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 4,
                            "mesin": a["mesin"],
                            "ket": "Istirahat 2"
                        }
                        dt.append(data)
                else:
                    ab["istirahat2"] = jam_absen.time()
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
                ab["istirahat2"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]))
                if ab["kembali"] is not None:
                    if ab["kembali"].hour > 9 and ab["kembali"].hour < 21:
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 3,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat"
                        }
                        dt.append(data)
                    else:
                        ab2["kembali"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 3,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat"
                        }
                        dt.append(data)
                elif ab["pulang"] is not None:
                    if ab["pulang"].hour < 9 :
                        ab2["kembali"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 3,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat"
                        }
                        dt.append(data)
                    else:
                        ab["kembali"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 3,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat"
                        }
                        dt.append(data)
                else:
                    ab["kembali"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]))
                if ab["kembali2"] is not None:
                    if ab["kembali2"].hour > 9 and ab["kembali2"].hour < 21:
                        ab["kembali2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 5,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat 2"
                        }
                        dt.append(data)
                    else:
                        ab2["kembali2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 5,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat 2"
                        }
                        dt.append(data)
                elif ab["pulang"] is not None:
                    if ab["pulang"].hour < 9 :
                        ab2["kembali2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 5,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat 2"
                        }
                        dt.append(data)
                    else:
                        ab["kembali2"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 5,
                            "mesin": a["mesin"],
                            "ket": "Kembali Istirahat 2"
                        }
                        dt.append(data)
                else:
                    ab["kembali2"] = jam_absen.time()
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
                ab["kembali2"] = jam_absen.time()
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
                ab["kembali"] = jam_absen.time()
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
                ab2 = next((abs for abs in absensi if abs["tgl_absen"] == tplus.date() and abs["pegawai_id"] == pg["idp"]))
                if ab["pulang"] is not None:
                    if ab["pulang"].hour > 9:
                        pass
                    else:
                        ab2["pulang"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 1,
                            "mesin": a["mesin"],
                            "ket": "Pulang"
                        }
                        dt.append(data)
                elif ab["masuk"] is not None:
                    if not ab["masuk"].hour > 18:
                        ab["pulang"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen,
                            "punch": 1,
                            "mesin": a["mesin"],
                            "ket": "Pulang"
                        }
                        dt.append(data)
                    else:
                        ab2["pulang"] = jam_absen.time()
                        data = {
                            "userid": a["userid"],
                            "jam_absen": jam_absen + timedelta(days=1),
                            "punch": 1,
                            "mesin": a["mesin"],
                            "ket": "Pulang"
                        }
                        dt.append(data)
                else:
                    ab["pulang"] = jam_absen.time()
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
                    ab["pulang"] = jam_absen.time()
                    data = {
                        "userid": a["userid"],
                        "jam_absen": jam_absen,
                        "punch": 7,
                        "mesin": a["mesin"],
                        "ket": "Pulang Malam"
                    }
                    dt.append(data)
        end = time.perf_counter()
        print(f"PROSES ABSENSI LOOP {end-start} detik")


        start = time.perf_counter()
        absensi_db.objects.using(cabang).bulk_update([absensi_db(id=abs["id"],pegawai_id=abs["pegawai_id"],tgl_absen=abs["tgl_absen"],masuk=abs["masuk"],istirahat=abs['istirahat'],kembali=abs["kembali"],istirahat2=abs["istirahat2"],kembali2=abs["kembali2"],pulang=abs["pulang"],jam_masuk=abs["jam_masuk"],jam_pulang=abs["jam_pulang"],lama_istirahat=abs["lama_istirahat"],shift=abs["shift"]) for abs in absensi],["pegawai_id","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","jam_masuk","jam_pulang","lama_istirahat","shift"],batch_size=2300)
        end = time.perf_counter()
        print(f"PROSES ABSENSI UPDATE {end-start} detik. {len(absensi)} data")

        start = time.perf_counter()
        bulkraw = [data_raw_db(userid=dr["userid"],jam_absen=dr["jam_absen"],punch=dr["punch"],mesin=dr["mesin"]) for dr in insertdr]
        data_raw_db.objects.using(cabang).bulk_create(bulkraw,batch_size=2300)    
        end = time.perf_counter()
        print(f"PROSES RAW {end-start} detik. {len(insertdr)} data")
            
        start = time.perf_counter()
        bulktrans = [data_trans_db(userid=t["userid"],jam_absen=t["jam_absen"],punch=t["punch"],mesin=t["mesin"],keterangan=t["ket"]) for t in dt if not t in ddtor]
        data_trans_db.objects.using(cabang).bulk_create(bulktrans,batch_size=2300)
        end = time.perf_counter()
        print(f"PROSES ABSENSI TRANS {end-start} detik. {len(bulktrans)} data")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)



# japlus = jam_absen + timedelta(minutes=2,seconds=30)
#         jamin = jam_absen - timedelta(minutes=2,seconds=30)
#         pg = next((pgw for pgw in pegawai if pgw["userid"] == a["userid"]),None)
#         cekuser = [du for du in dt if int(du["userid"]) == int(a["userid"]) and du["jam_absen"].date() == jam_absen.date() and du["jam_absen"] > jamin and du["jam_absen"] < japlus and du["punch"] != a["punch"]]
#         if len(cekuser) > 0:
#             cekddt = [d for d in cekuser if jam_absen > d["jam_absen"]]
#             if len(cekddt) >0:
#                 for c in cekddt:
#                     ab = absensi_db.objects.using(cabang).filter(tgl_absen=jam_absen.date(),pegawai_id=pg["idp"])
#                     if ab.exists():
#                         ab = ab[0]
#                         ab.masuk = ab.masuk if ab.masuk != c["jam_absen"].time() else None
#                         ab.pulang = ab.pulang if ab.pulang != c["jam_absen"].time() else None
#                         ab.istirahat = ab.istirahat if ab.istirahat != c["jam_absen"].time() else None
#                         ab.kembali = ab.kembali if ab.kembali != c["jam_absen"].time() else None
#                         ab.istirahat2 = ab.istirahat2 if ab.istirahat2 != c["jam_absen"].time() else None
#                         ab.kembali2 = ab.kembali2 if ab.kembali2 != c["jam_absen"].time() else None
#                         ab.masuk_b = ab.masuk_b if ab.masuk_b != c["jam_absen"].time() else None
#                         ab.pulang_b = ab.pulang_b if ab.pulang_b != c["jam_absen"].time() else None
#                         ab.istirahat_b = ab.istirahat_b if ab.istirahat_b != c["jam_absen"].time() else None
#                         ab.kembali_b = ab.kembali_b if ab.kembali_b != c["jam_absen"].time() else None
#                         ab.istirahat2_b = ab.istirahat2_b if ab.istirahat2_b != c["jam_absen"].time() else None
#                         ab.kembali2_b = ab.kembali2_b if ab.kembali2_b != c["jam_absen"].time() else None
#                         ab.save(using=cabang)
#                         data_trans_db.objects.using(cabang).filter(userid=int(c["userid"]),jam_absen=c["jam_absen"]).delete()
#                     else:
#                         pass
#             else:
#                 continue
#         # # Versi