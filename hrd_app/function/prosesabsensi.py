from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from multiprocessing import Pool
from ..models import *
from hrd_app.controllers.lib import nama_hari
import pandas as pd
from datetime import date, datetime, timedelta
import time
import sys, os
import re
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


def fn_pu(abs,dt,cabang,tgl,sid,username):
    try:
        abs["masuk"] = None
        abs["pulang"] = None
        abs["istirahat"] = None
        abs["kembali"] = None
        abs["pulang"] = None
        abs["masuk_b"] = None
        abs["istirahat_b"] = None
        abs["kembali_b"] = None
        abs["pulang_b"] = None
        abs["istirahat2"] = None
        abs["istirahat2_b"] = None
        abs["kembali2"] = None
        abs["kembali2_b"] = None
        for d in dt:
            if d.punch == 0:
                abs["masuk"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 1:
                abs["pulang"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 2:
                abs["istirahat"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 3:
                abs["kembali"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 4:
                abs["istirahat2"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 5:
                abs["kembali2"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 6:
                abs["masuk"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 7:
                abs["pulang"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 8:
                abs["istirahat"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 9:
                abs["kembali"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 10:
                abs["masuk_b"] = d.jam_absen.time().strftime('%H:%M:%S') 
            elif d.punch == 11:
                abs["pulang_b"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 12:
                abs["istirahat_b"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 13:
                abs["kembali_b"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 14:
                abs["istirahat2_b"] = d.jam_absen.time().strftime('%H:%M:%S')
            elif d.punch == 15:
                abs["kembali2_b"] = d.jam_absen.time().strftime('%H:%M:%S')
        ijin = []  
        libur = []
        cuti = []
        geser = []
        geserdr = []
        kompen = []
        opg = []
        opgdr = []
        dl = []
        dl_idp = []
        ijindl = []
        lsopg = []
        
        # list status pegawai yang dapat opg
        for s in list_pegawai_opg_db.objects.using(cabang).all():
            lsopg.append(s.pegawai_id) 
        # data ijin
        for i in ijin_db.objects.using(cabang).select_related('ijin','pegawai').filter(tgl_ijin=tgl).values("ijin__jenis_ijin","tgl_ijin","pegawai_id","keterangan"):
            data = {
                "ijin" : i["ijin__jenis_ijin"],
                "tgl_ijin" : i["tgl_ijin"],
                "idp" : i["pegawai_id"],
                "keterangan" : i["keterangan"]
            }
            ijin.append(data)
        
        # data libur nasional
        for l in libur_nasional_db.objects.using(cabang).filter(tgl_libur=tgl).values("libur","tgl_libur","insentif_karyawan","insentif_staff"):
            data = {
                'libur' : l["libur"],
                'tgl_libur' : l["tgl_libur"],
                'insentif_karyawan' : l["insentif_karyawan"],
                'insentif_staff' : l["insentif_staff"]
            }    
            libur.append(data)  
            
        # data cuti
        for c in cuti_db.objects.using(cabang).select_related('pegawai').filter(tgl_cuti=tgl).values("id","pegawai_id","tgl_cuti","keterangan"):
            data = {
                'id': c["id"],
                'idp' : c["pegawai_id"],
                'tgl_cuti' : c["tgl_cuti"],
                'keterangan' : c["keterangan"]
            }                
            cuti.append(data)
            
        # data geser off
        for g in geseroff_db.objects.using(cabang).select_related('pegawai').filter(ke_tgl=tgl).values("id","pegawai_id","dari_tgl","ke_tgl","keterangan"):
            data = {
                'id' : g["id"],
                'idp' : g["pegawai_id"], 
                'dari_tgl' : g["dari_tgl"],
                'ke_tgl' : g["ke_tgl"],
                'keterangan' : g["keterangan"]
            } 
            geser.append(data)
        for g in geseroff_db.objects.using(cabang).select_related('pegawai').filter(dari_tgl=tgl).values("id","pegawai_id","dari_tgl","ke_tgl","keterangan"):
            data = {
                'id' : g["id"],
                'idp' : g["pegawai_id"], 
                'dari_tgl' : g["dari_tgl"],
                'ke_tgl' : g["ke_tgl"],
                'keterangan' : g["keterangan"]
            } 
            geserdr.append(data)
        status_ln = [st.pegawai_id for st in list_pegawai_opg_libur_nasional_db.objects.using(cabang).all()]
        # data opg
        for o in opg_db.objects.using(cabang).select_related('pegawai').filter(diambil_tgl=tgl).values("id","pegawai_id","opg_tgl","diambil_tgl","keterangan","status","edit_by"):
            data = {
                'id':o["id"],
                'idp': o["pegawai_id"],
                'opg_tgl':o["opg_tgl"],
                'diambil_tgl':o["diambil_tgl"],
                'keterangan':o["keterangan"],
                "status":o["status"],
                "edit_by":o["edit_by"]
            }
            opg.append(data)
        for odr in opg_db.objects.using(cabang).select_related('pegawai').filter(opg_tgl=tgl).values("id","pegawai_id","opg_tgl","diambil_tgl","keterangan","status","edit_by"):
            data = {
                'id':odr["id"],
                'idp': odr["pegawai_id"],
                'opg_tgl':odr["opg_tgl"],
                'diambil_tgl':odr["diambil_tgl"],
                'keterangan':odr["keterangan"],
                "status":odr["status"],
                "edit_by":odr["edit_by"]
            }
            opgdr.append(data)
        print(opgdr)
        
        # data dinas luar
        for n in dinas_luar_db.objects.using(cabang).select_related('pegawai').filter(tgl_dinas=tgl).values("pegawai_id","tgl_dinas","keterangan"):
            data = {
                'idp': n["pegawai_id"],
                'tgl_dinas':n["tgl_dinas"],
                'keterangan':n["keterangan"]
            }
            dl.append(data)
            dl_idp.append(n.pegawai_id)
        for ij in ijin_db.objects.using(cabang).filter(tgl_ijin=tgl).values("tgl_ijin","pegawai_id","ijin_id","ijin__jenis_ijin"):
            if re.search('(dinas luar|dl)',ij["ijin__jenis_ijin"],re.IGNORECASE) is not None:
                data = {
                    "tgl":ij["tgl_ijin"],
                    "idp":ij["pegawai_id"],
                    "ijin":ij["ijin_id"]
                }
                ijindl.append(data)
        for k in kompen_db.objects.using(cabang).all().values("id","pegawai_id","jenis_kompen","kompen","tgl_kompen"):
            data = {
                "idl":k["id"],
                "idp":k["pegawai_id"],
                "jenis_kompen":k["jenis_kompen"],
                "kompen":k["kompen"],
                "tgl_kompen":k["tgl_kompen"],
            }
            kompen.append(data)
            
        # data absensi
        if int(sid) == 0:
            data = absensi_db.objects.using(cabang).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen=tgl).values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","pegawai__hari_off__hari","pegawai__hari_off2__hari","pegawai__status_id","pegawai__status__status","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift")
        elif int(sid) > 0:
            data = absensi_db.objects.using(cabang).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen=tgl,pegawai__status_id=sid).values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","pegawai__hari_off__hari","pegawai__hari_off2__hari","pegawai__status_id","pegawai__status__status","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift")
        insertopg = []
        insertijin  = []
        username = username
        cabang = cabang
        day = abs["tgl_absen"].strftime("%A")
        nh = nama_hari(day)  
        """ Rules OPG (staff & karyawan) & Insentif (hanya untuk karyawan) :
        
        Staff :
        --> jika ada libur nasional dan jatuh di hari biasa (senin - sabtu), maka staff yang memiliki off reguler bertepatan
        dengan libur nasional tersebut akan mendapat opg = 2 jika masuk (off pengganti reguler dan off pengganti tgl merah), 
        jika tidak masuk mendapat opg = 1 (off pengganti reguler)
        
        --> jika ada libur nasional dan jatuh di hari minggu, maka staff yang memiliki off reguler bertepatan dengan libur
        nasional tersebut jika masuk mendapat opg = 1 (off pengganti reguler)
        
        --> jika tidak ada libur nasional, maka staff yang masuk di hari off regulernya maka mendapat opg = 1 (off pengganti 
        reguler)2
        
        Karyawan + SPG dibayar oleh Asia:
        --> jika ada libur nasional (senin - minggu), maka Karyawan yang memiliki off reguler bertepatan
        dengan libur nasional tersebut akan mendapat opg = 1 jika masuk (off pengganti reguler) dan insentif = 1
                        
        --> jika tidak ada libur nasional, maka Karyawan yang masuk di hari off regulernya maka mendapat opg = 1 (off pengganti 
        reguler)
        
        """  
        # OFF & OFF Pengganti Reguler
        # jika ada absen masuk dan pulang
        # rencana cronjob jalan
        if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
            if nh in [str(abs["pegawai__hari_off__hari"]),str(abs["pegawai__hari_off2__hari"])]:
                if abs["pegawai_id"] in lsopg and re.search("security",abs["pegawai__status__status"],re.IGNORECASE) is None and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                    opgdr.append({
                        'id':0,
                        'idp':abs["pegawai_id"],
                        'opg_tgl':abs["tgl_absen"],
                        'diambil_tgl':"",
                        'keterangan':"OFF Pengganti Reguler"
                    })
                    insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                else:
                    pass
            else: 
                if str(abs["pegawai__hari_off__hari"]) == "On Off":
                    abs["keterangan_absensi"] = None
                        
        # jika tidak ada masuk dan pulang   
        else:
            # jika dinas luar
            if str(abs["pegawai__hari_off__hari"]) == 'On Off':
                abs["keterangan_absensi"] = 'OFF'
            for il in ijindl:
                if il["tgl"] == abs["tgl_absen"] and int(il["idp"]) == int(abs["pegawai_id"]) and nh in [str(abs["pegawai__hari_off__hari"]),str(abs["pegawai__hari_off2__hari"])] and  abs["pegawai_id"] in lsopg and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                    opgdr.append({
                        'id':0,
                        'idp':abs["pegawai_id"],
                        'opg_tgl':abs["tgl_absen"],
                        'diambil_tgl':"",
                        'keterangan':"OFF Pengganti Reguler"
                    })
                    insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                else:
                    pass
            # jika dia hari ini off
            if (abs["masuk"] is not None or abs["pulang"] is not None) or (abs["masuk_b"] is not None or abs["pulang_b"] is not None):
                if str(abs["pegawai__hari_off__hari"]) == "On Off":
                    abs["keterangan_absensi"] = None
            else:
                if str(abs["pegawai__hari_off__hari"]) == str(nh):
                    abs["keterangan_absensi"] = 'OFF'
                elif str(abs["pegawai__hari_off__hari"]) == 'On Off':
                    abs["keterangan_absensi"] = 'OFF'
                if str(abs["pegawai__hari_off2__hari"]) == str(nh):
                    abs["keterangan_absensi"] = 'OFF'
                else:
                    pass   
            # jika hari ini dia adalah off nya
        
        # libur nasional
        for l in libur:
        # jika ada absen di hari libur nasional
            abs["libur_nasional"] = None
            if l["tgl_libur"] == abs["tgl_absen"]:
                    abs["libur_nasional"] = l["libur"]
            if abs["pegawai_id"] in lsopg and l['tgl_libur'] == abs["tgl_absen"]:                            
                # if cabang != 'tasik':
                #     abs["libur_nasional"] = l['libur']
                    
                # Hari Minggu
                if str(nh) == 'Minggu':                        
                        # Staff
                    print( str(nh) in [str(abs["pegawai__hari_off__hari"]), str(abs["pegawai__hari_off2__hari"])])
                    if abs["pegawai_id"] in status_ln: # regex
                        # jika hari off nya adalah hari minggu dan masuk maka hanya akan mendapatkan 1 opg
                        if str(nh) in [str(abs["pegawai__hari_off__hari"]), str(abs["pegawai__hari_off2__hari"])]:
                            if ((abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None)) and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                                print("OKOKOK")
                                opgdr.append({
                                    'id':0,
                                    'idp':abs["pegawai_id"],
                                    'opg_tgl':abs["tgl_absen"],
                                    'diambil_tgl':"",
                                    'keterangan':"OFF Pengganti Reguler"
                                })
                                insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                            else:
                                pass        
                        else:
                            if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                                if next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True):
                                    if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                        print("OOKKOKO")
                                        opgdr.append({
                                            'id':0,
                                            'idp':abs["pegawai_id"],
                                            'opg_tgl':abs["tgl_absen"],
                                            'diambil_tgl':"",
                                            'keterangan':"OFF Pengganti Tgl Merah"
                                        })
                                        insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                            # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                            else:
                                pass                
                    # Karyawan
                    else:
                        pass         
                
                # Bukan Hari Minggu
                else:                                                        
                    # Staff
                    if abs["pegawai_id"] in status_ln:
                        if str(nh) in [str(abs["pegawai__hari_off__hari"]), str(abs["pegawai__hari_off2__hari"])]:
                            # JIKA DIA MASUK DIHARI MERAH DILIBUR REGULERNYA MAKA AKAN DAPAT 2 OPG
                            if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                                if next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True):
                                    if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                                        opgdr.append({
                                            'id':0,
                                            'idp':abs["pegawai_id"],
                                            'opg_tgl':abs["tgl_absen"],
                                            'diambil_tgl':"",
                                            'keterangan':"OFF Pengganti Reguler"
                                        })
                                        insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                                        
                                    if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                        opgdr.append({
                                            'id':0,
                                            'idp':abs["pegawai_id"],
                                            'opg_tgl':abs["tgl_absen"],
                                            'diambil_tgl':"",
                                            'keterangan':"OFF Pengganti Tgl Merah"
                                        })
                                        insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                            # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                            else:
                                if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                    opgdr.append({
                                        'id':0,
                                        'idp':abs["pegawai_id"],
                                        'opg_tgl':abs["tgl_absen"],
                                        'diambil_tgl':"",
                                        'keterangan':"OFF Pengganti Tgl Merah"
                                    })
                                    insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                        # JIKA HARI OFF TIDAK BERTEPATAN HARI LIBUR NASIONAL
                        else:
                            if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                                if next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True):
                                    if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                        print("OOKKOKO")
                                        opgdr.append({
                                            'id':0,
                                            'idp':abs["pegawai_id"],
                                            'opg_tgl':abs["tgl_absen"],
                                            'diambil_tgl':"",
                                            'keterangan':"OFF Pengganti Tgl Merah"
                                        })
                                        insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                            # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                            else:
                                pass
                    
                    # Karyawan
                    # JIKA MASUK HANYA MENDAPATKAN 1 OPG DAN INSENTIF
                    else:
                        if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None) and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):                                        
                                abs["insentif"] = l['insentif_karyawan']
                        else:
                            pass    
                    
        # ijin
        for i in ijin:
            if abs["pegawai_id"] == i['idp'] and i['tgl_ijin'] == abs["tgl_absen"]:
                ij = i['ijin']
                ket = i['keterangan']
                abs["keterangan_ijin"] = f'{ij}-({ket})'
            else:
                pass                                 
        
        for kmpn in kompen:
            if abs["pegawai_id"] == kmpn["idp"] and kmpn["tgl_kompen"] == abs["tgl_absen"]:
                if abs["jam_masuk"] is not None and abs["jam_pulang"] is None and abs["masuk"] is not None and abs["pulang"] is not None:
                    if abs["pulang"] > abs["masuk"]:
                        jm = datetime.combine(abs["tgl_absen"],abs["jam_masuk"])
                        jp = datetime.combine(abs["tgl_absen"],abs["jam_pulang"])
                        
                        jkompen = float(kmpn["kompen"])
                        
                        if kmpn["jenis_kompen"] == 'awal':
                            njm = jm - timedelta(hours=jkompen)
                            njp = abs["jam_pulang"]
                        elif kmpn["jenis_kompen"] == 'akhir':    
                            njm = abs["jam_masuk"]
                            njp = jp + timedelta(hours=jkompen)
                        else:    
                            njm = jm - timedelta(hours=jkompen)
                            njp = jp + timedelta(hours=jkompen)
                        
                        dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
                        dplg = f'{abs["tgl_absen"]} {abs["pulang"]}'
                        
                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih = plg - msk
                        djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
                        selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                        
                        if int(selisih.hour) <= 4:
                            tjk = 0
                        else:
                            detik = selisih.second / 3600
                            menit = selisih.minute / 60
                            hour = selisih.hour
                            
                            jam = int(hour) + float(menit) + float(detik)
                            
                            tjk = jam       
                        
                        status = 'ok'                
                        abs["jam_masuk"] = njm
                        abs["jam_pulang"] = njp
                    else: 
                        tjk = 0   
                else:
                    tjk = 0
                if kmpn["jenis_kompen"] == 'awal':
                    abs["keterangan_lain"] = f"Kompen/PJK-Awal {kmpn['kompen']} Jam"
                elif kmpn["jenis_kompen"] == "akhir":
                    abs["keterangan_lain"] = f"Kompen/PJK-Akhir {kmpn['kompen']} Jam"
                else:
                    abs["keterangan_lain"] = f"Kompen/PJK 1 hari"
                nama_user = username
                abs["total_jam_kerja"] = round(tjk,1)
                abs["edit_by"] = nama_user
            else:
                pass
        
        # cuti
        for c in cuti:
            # jika didalam data cuti ada pegawai id
            if abs["pegawai_id"] == c['idp'] and c['tgl_cuti'] == abs["tgl_absen"]:
                # jika tidak masuk dan pulang
                if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                    dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
                    dplg = f'{abs["tgl_absen"]} {abs["pulang"]}'
                    
                    msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                    plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih = plg - msk
                    djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
                    selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S') 
                    # jika jam kerja kurang dari 4 jam
                    if int(selisih.hour) <= 4:
                        abs["keterangan_absensi"] = c['keterangan']
                    # jika jam kerja lebih dari 4 jam
                    else:
                        cuti_db.objects.using(cabang).get(id=int(c['id'])).delete()
                        pg = pegawai_db.objects.using(cabang).get(pk=abs["pegawai_id"])
                        sc = pg.sisa_cuti
                        abs["keterangan_absensi"] = ""
                        pg.sisa_cuti = sc + 1
                        pg.save(using=cabang)          
                else:
                    abs["keterangan_absensi"] = c['keterangan']
            else:
                pass        
            
        # geser off
        for g in geser:
            if abs["pegawai_id"] == g['idp']:
                if g['ke_tgl'] == abs["tgl_absen"]:
                    # jika ada geser off dan dia tidak masuk
                    if (abs["masuk"] is None and abs["pulang"] is None) or (abs["masuk_b"] is None and abs["pulang_b"] is None):
                        drt = datetime.strftime(g['dari_tgl'], '%d-%m-%Y')
                        abs["keterangan_absensi"] = f'Geser OFF-({drt})' 
                    # jika ada geser off dan dia masuk
                    else:
                        geseroff_db.objects.using(cabang).get(id=int(g['id'])).delete()    
                elif g["dari_tgl"] == abs["tgl_absen"]:
                    if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                        abs["keterangan_absensi"] = None
                    else:
                        pass
                else:
                    pass
            else:
                pass
        # opg
        for o in opg:
            if abs["pegawai_id"] == o['idp'] and o['diambil_tgl'] == abs["tgl_absen"]:
                opg_detail = opg_db.objects.using(cabang).get(pk=int(o["id"]))
                # jika tidak masuk dan tidak ada pulang
                if abs["masuk"] is None and abs["pulang"] is None and abs["masuk_b"] is None and abs["pulang_b"] is None:
                    topg = datetime.strftime(o['opg_tgl'], '%d-%m-%Y')
                    abs["keterangan_absensi"] = f'OPG-({topg})'
                    
                    opg_detail.status = 1
                    opg_detail.edit_by ='Program'
                    opg_detail.save(using=cabang)
                # jika masuk dan pulang
                else:
                    opg_detail["diambil_tgl"] = None
                    opg_detail.edit_by = 'Program'
                    opg_detail.save(using=cabang)
                        
            else:
                pass        
        
        # dinas luar   
        for n in dl:
            if abs["pegawai_id"] == n['idp'] and n['tgl_dinas'] == abs["tgl_absen"]:
                ket = n['keterangan']
                abs["keterangan_absensi"] = f'Dinas Luar-({ket})'
            else:
                pass    
                                
        # total jam kerja         
        if abs["masuk"] is not None and abs["pulang"] is not None:
            if abs["pulang"] > abs["masuk"]:
                
                dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
                dplg = f'{abs["tgl_absen"]} {abs["pulang"]}'
                
                msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                
                dselisih = plg - msk
                djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
                selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                
                if int(selisih.hour) <= 4:
                    tjk = 0
                else:
                    detik = selisih.second / 3600
                    menit = selisih.minute / 60
                    hour = selisih.hour
                    
                    jam = int(hour) + float(menit) + float(detik)
                    
                    tjk = jam                   
            else: 
                
                tplus = abs["tgl_absen"]        
                
                dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
                dplg = f'{tplus} {abs["pulang"]}'
                
                msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                
                dselisih = plg - msk
                djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
                # Split the string to separate the date and time parts
                date_part = djam_selisih.split(' ', 2)
                # Parse the date and time
                # Adjust the date based on the delta part
                if len(date_part) > 2:
                    base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                    if date_part[1] == '-1':
                        adjusted_datetime = base_datetime - timedelta(days=1)
                    elif date_part[1] == '+1':
                        adjusted_datetime = base_datetime + timedelta(days=1)
                else:
                    base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                    adjusted_datetime = base_datetime
                selisih = adjusted_datetime
                if int(selisih.hour) <= 4:
                    tjk = 0
                else:
                    detik = selisih.second / 3600
                    menit = selisih.minute / 60
                    hour = selisih.hour
                    
                    jam = int(hour) + float(menit) + float(detik)
                    tjk = jam                
        else:
            tjk = 0
        if abs["masuk_b"] is not None and abs["pulang_b"] is not None:
            if abs["pulang_b"] > abs["masuk_b"]:
                
                dmsk_b = f'{abs["tgl_absen"]} {abs["masuk_b"]}'
                dplg_b = f'{abs["tgl_absen"]} {abs["pulang_b"]}'
                
                msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_b = plg_b - msk_b
                djam_selisih_b = f'{abs["tgl_absen"]} {dselisih_b}'
                selisih_b = datetime.strptime(djam_selisih_b, '%Y-%m-%d %H:%M:%S')
                
                if int(selisih_b.hour) <= 4:
                    tjk_b = 0
                else:
                    detik_b = selisih_b.second / 3600
                    menit_b = selisih_b.minute / 60
                    hour_b = selisih_b.hour
                    
                    jam_b = int(hour_b) + float(menit_b) + float(detik_b)
                    
                    tjk_b = jam_b                   
            else: 
                
                tplus_b = abs["tgl_absen"]
                dmsk_b = f'{abs["tgl_absen"]} {abs["masuk_b"]}'
                dplg_b = f'{tplus_b} {abs["pulang_b"]}'
                
                msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                dselisih_b = plg_b - msk_b
                # if dselisih_b.hour < 10
                djam_selisih_b = f'{abs["tgl_absen"]} {dselisih_b}'
                date_part = djam_selisih_b.split(' ', 2)
                # Split the string to separate the date and time parts
                if len(date_part) > 2:
                    base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                    if date_part[1] == '-1':
                        adjusted_datetime = base_datetime - timedelta(days=1)
                    elif date_part[1] == '+1':
                        adjusted_datetime = base_datetime + timedelta(days=1)
                else:
                    base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                    adjusted_datetime = base_datetime
                selisih_b = adjusted_datetime
                if int(selisih_b.hour) <= 4:
                    tjk_b = 0
                else:
                    detik_b = selisih_b.second / 3600
                    menit_b = selisih_b.minute / 60
                    hour_b = selisih_b.hour
                    
                    jam_b = int(hour_b) + float(menit_b) + float(detik_b)
                    
                    tjk_b = jam_b                
        else:
            tjk_b = 0
            
        # total jam istirahat
        if abs["istirahat"] is not None and abs["kembali"] is not None:
            if abs["kembali"] > abs["istirahat"]:
                
                dist = f'{abs["tgl_absen"]} {abs["istirahat"]}'
                dkmb = f'{abs["tgl_absen"]} {abs["kembali"]}'
                
                ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i = kmb - ist
                djam_selisih_i = f'{abs["tgl_absen"]} {dselisih_i}'
                selisih_i = datetime.strptime(djam_selisih_i, '%Y-%m-%d %H:%M:%S')
                    
                detik_i = selisih_i.second / 3600
                menit_i = selisih_i.minute / 60
                hour_i = selisih_i.hour
                
                jam_i = int(hour_i) + float(menit_i) + float(detik_i)
                
                tji = jam_i                   
            else:
                
                tplus = abs["tgl_absen"] + timedelta(days=1)
                
                dist = f'{abs["tgl_absen"]} {abs["istirahat"]}'
                dkmb = f'{tplus} {abs["kembali"]}'
                
                ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i = kmb - ist
                djam_selisih_i = f'{abs["tgl_absen"]} {dselisih_i}'
                # Split the string to separate the date and time parts
                date_part = djam_selisih_i.split(' ', 2)
                # Parse the date and time
                # Adjust the date based on the delta part
                if len(date_part) > 2:
                    base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                    if date_part[1] == '-1':
                        adjusted_datetime = base_datetime - timedelta(days=1)
                    elif date_part[1] == '+1':
                        adjusted_datetime = base_datetime + timedelta(days=1)
                else:
                    base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                    adjusted_datetime = base_datetime
                selisih_i = adjusted_datetime
                    
                detik_i = selisih_i.second / 3600
                menit_i = selisih_i.minute / 60
                hour_i = selisih_i.hour
                
                jam_i = int(hour_i) + float(menit_i) + float(detik_i)
                
                tji = jam_i                      
        else:
            tji = 0        
        
        if abs["istirahat_b"] is not None and abs["kembali_b"] is not None:
            if abs["kembali_b"] > abs["istirahat_b"]:
                
                dist_b = f'{abs["tgl_absen"]} {abs["istirahat_b"]}'
                dkmb_b = f'{abs["tgl_absen"]} {abs["kembali_b"]}'
                
                ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i_b = kmb_b - ist_b
                djam_selisih_i_b = f'{abs["tgl_absen"]} {dselisih_i_b}'
                selisih_i_b = datetime.strptime(djam_selisih_i_b, '%Y-%m-%d %H:%M:%S')
                    
                detik_i_b = selisih_i_b.second / 3600
                menit_i_b = selisih_i_b.minute / 60
                hour_i_b = selisih_i_b.hour
                
                jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
                
                tji_b = jam_i_b                   
            else:
                if int(abs["pegawai"].status.id) == 3:
                    tplus_b = abs["tgl_absen"] + timedelta(days=1)
                else:
                    tplus_b = abs["tgl_absen"]
                dist_b = f'{abs["tgl_absen"]} {abs["istirahat_b"]}'
                dkmb_b = f'{tplus_b} {abs["kembali_b"]}'
                
                ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i_b = kmb_b - ist_b
                djam_selisih_i_b = f'{abs["tgl_absen"]} {dselisih_i_b}'
                # Split the string to separate the date and time parts
                date_part = djam_selisih_i_b.split(' ', 2)
                # Parse the date and time
                # Adjust the date based on the delta part
                if len(date_part) > 2:
                    base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                    if date_part[1] == '-1':
                        adjusted_datetime = base_datetime - timedelta(days=1)
                    elif date_part[1] == '+1':
                        adjusted_datetime = base_datetime + timedelta(days=1)
                else:
                    base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                    adjusted_datetime = base_datetime
                selisih_i_b = adjusted_datetime
                    
                detik_i_b = selisih_i_b.second / 3600
                menit_i_b = selisih_i_b.minute / 60
                hour_i_b = selisih_i_b.hour
                
                jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
                
                tji_b = jam_i_b                      
        else:
            tji_b = 0        
        
        # total jam istirahat2
        if abs["istirahat2"] is not None and abs["kembali2"] is not None:
            if abs["kembali2"] > abs["istirahat2"]:
                
                dist2 = f'{abs["tgl_absen"]} {abs["istirahat2"]}'
                dkmb2 = f'{abs["tgl_absen"]} {abs["kembali2"]}'
                
                ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2 = kmb2 - ist2
                djam_selisih_i2 = f'{abs["tgl_absen"]} {dselisih_i2}'
                selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                    
                detik_i2 = selisih_i2.second / 3600
                menit_i2 = selisih_i2.minute / 60
                hour_i2 = selisih_i2.hour
                
                jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                
                tji2 = jam_i2                   
            else:
                
                tplus = abs["tgl_absen"] + timedelta(days=1)
                
                dist2 = f'{abs["tgl_absen"]} {abs["istirahat2"]}'
                dkmb2 = f'{tplus} {abs["kembali2"]}'
                
                ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2 = kmb2 - ist2
                djam_selisih_i2 = f'{abs["tgl_absen"]} {dselisih_i2}'
                selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                    
                detik_i2 = selisih_i2.second / 3600
                menit_i2 = selisih_i2.minute / 60
                hour_i2 = selisih_i2.hour
                
                jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                
                tji2 = jam_i2
        else:
            tji2 = 0   
        if abs["istirahat2_b"] is not None and abs["kembali2_b"] is not None:
            if abs["kembali2_b"] > abs["istirahat2_b"]:
                
                dist2_b = f'{abs["tgl_absen"]} {abs["istirahat2_b"]}'
                dkmb2_b = f'{abs["tgl_absen"]} {abs["kembali2_b"]}'
                
                ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2_b = kmb2_b - ist2_b
                djam_selisih_i2_b = f'{abs["tgl_absen"]} {dselisih_i2_b}'
                selisih_i2_b = datetime.strptime(djam_selisih_i2_b, '%Y-%m-%d %H:%M:%S')
                    
                detik_i2_b = selisih_i2_b.second / 3600
                menit_i2_b = selisih_i2_b.minute / 60
                hour_i2_b = selisih_i2_b.hour
                
                jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
                
                tji2_b = jam_i2_b                   
            else:
                
                if int(abs["pegawai__status_id"]) == 3:
                    tplus_b = abs["tgl_absen"] + timedelta(days=1)
                else:
                    tplus_b = abs["tgl_absen"]
                
                dist2_b = f'{abs["tgl_absen"]} {abs["istirahat2_b"]}'
                dkmb2_b = f'{tplus_b} {abs["kembali2_b"]}'
                
                ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2_b = kmb2_b - ist2_b
                djam_selisih_i2_b = f'{abs["tgl_absen"]} {dselisih_i2_b}'
                # Split the string to separate the date and time parts
                date_part = djam_selisih_i2_b.split(' ', 2)
                # Parse the date and time
                # Adjust the date based on the delta part
                if len(date_part) > 2:
                    base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                    if date_part[1] == '-1':
                        adjusted_datetime = base_datetime - timedelta(days=1)
                    elif date_part[1] == '+1':
                        adjusted_datetime = base_datetime + timedelta(days=1)
                else:
                    opgdr.append({
                        'id':0,
                        'idp':abs["pegawai_id"],
                        'opg_tgl':abs["tgl_absen"],
                        'diambil_tgl':"",
                        'keterangan':"OFF Pengganti Reguler"
                    })
                    insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                    base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                    adjusted_datetime = base_datetime
                    selisih_i2_b = adjusted_datetime
                        
                    detik_i2_b = selisih_i2_b.second / 3600
                    menit_i2_b = selisih_i2_b.minute / 60
                    hour_i2_b = selisih_i2_b.hour
                    
                    jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
                    
                    tji2_b = jam_i2_b
        else:
            tji2_b = 0    
        abs["total_jam_kerja"] = tjk + tjk_b
        abs["total_jam_istirahat"] = tji + tji_b
        abs["total_jam_istirahat2"] = tji2 + tji2_b
        absensi_db.objects.using(cabang).bulk_update([absensi_db(id=abs["id"],pegawai_id=abs["pegawai_id"],tgl_absen=abs["tgl_absen"],masuk=abs["masuk"],istirahat=abs['istirahat'],kembali=abs["kembali"],istirahat2=abs["istirahat2"],kembali2=abs["kembali2"],pulang=abs["pulang"],masuk_b=abs["masuk_b"],istirahat_b=abs["istirahat_b"],kembali_b=abs["kembali_b"],istirahat2_b=abs["istirahat2_b"],kembali2_b=abs["kembali2_b"],pulang_b=abs["pulang_b"],keterangan_absensi=abs["keterangan_absensi"],keterangan_ijin=abs["keterangan_ijin"],keterangan_lain=abs["keterangan_lain"],libur_nasional=abs["libur_nasional"],insentif=abs["insentif"],jam_masuk=abs["jam_masuk"],jam_pulang=abs["jam_pulang"],lama_istirahat=abs["lama_istirahat"],shift=abs["shift"],total_jam_kerja=abs["total_jam_kerja"],total_jam_istirahat=abs["total_jam_istirahat"],total_jam_istirahat2=abs["total_jam_istirahat2"],edit_by=abs["edit_by"])],["pegawai_id","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift"]) 
        opg_db.objects.using(cabang).bulk_create(insertopg)
        return True
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