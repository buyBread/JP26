import util
import sys
import statistics
import operator
import os
import math
from datetime import date, timedelta
from dataclasses import dataclass

@dataclass
class meteo_diena:
    data: date
    temperatura: float # celsius
    krituliai: float # mm
    vejas: float # m/s

    @property
    def diena(self):
        return self.data.day

    @property
    def menesis(self):
        return self.data.month

    @property
    def diena_str(self):
        return [ "Pirmadienis",
                 "Antradienis",
                 "Trečiadienis",
                 "Ketvirtadienis",
                 "Penktadienis",
                 "Šeštadienis",
                 "Sekmadienis" ][self.data.weekday()]

    @property
    def menesis_str(self):
        return [ "Sausis",
                 "Vasaris",
                 "Kovas",
                 "Balandis",
                 "Gegužė",
                 "Birželis",
                 "Liepa",
                 "Rugpjūtis",
                 "Rugsėjis",
                 "Spalis",
                 "Lapkritis",
                 "Gruodis" ][self.menesis - 1]

    @property
    def metu_laikas(self):
        match self.data.month:
            case 12 | 1 | 2:
                return "Žiema"
            case 3 | 4 | 5:
                return "Pavasaris"
            case 6 | 7 | 8:
                return "Vasara"
            case 9 | 10 | 11:
                return "Ruduo"

@dataclass
class meteo:
    dienos: list[meteo_diena]

    # =======
    #    3
    # =======

    @property
    def metu_temp_vidutine(self):
        return sum([ d.temperatura for d in self.dienos ]) / len(self.dienos)

    @property
    def metu_temp_medianas(self):
        return statistics.median([ d.temperatura for d in self.dienos ])

    def dienos_su_auksciausia_temp(self):
        didziausia = max([ d.temperatura for d in self.dienos ])

        return [ d for d in self.dienos if d.temperatura == didziausia ]

    def dienos_su_maziausia_temp(self):
        didziausia = min([ d.temperatura for d in self.dienos ])

        return [ d for d in self.dienos if d.temperatura == didziausia ]

    def dienu_skaicius_su_temp(self, temp: float, op: str = "==") -> int:
        ops = { "<":  operator.lt,
                ">":  operator.gt,
                "==": operator.eq,
                "<=": operator.le,
                ">=": operator.ge,
                "!=": operator.ne }

        return sum(ops[op](d.temperatura, temp) for d in self.dienos)

# =======
#    2
# =======

def meteo_dienu_sarasas() -> list[meteo_diena]:
    dienos = []

    with util.open_file("pradiniai_duomenys/meteo365_no_date.txt") as fp:
        lines = fp.read().split("\n")

        for ln in lines:
            ln = ln.split(";")

            if ln[0] == "Diena":
                continue

            if len(ln) != 4:
                continue

            ln[0] = int(ln[0]) # type: ignore

            if ln[0] < 1 or ln[0] > 365:
                continue

            data = date(2023, 1, 1) + timedelta(days=ln[0] - 1)

            if any(data == d.data for d in dienos):
                continue

            dienos.append(meteo_diena(data, float(ln[1]), float(ln[2]), float(ln[3])))

    if len(dienos) == 0:
        print("Nėra tinkamų įrašų. Analizė neatliekama.")

        sys.exit(1)

    return dienos

# =======
#    3
# =======

def bendroji_temperaturu_statistika(meteo_dienos: list[meteo_diena]):
    duomenys = meteo(meteo_dienos)

    statistika = "BENDROJI TEMPERATŪRŲ STATISTIKA\n\n"

    statistika += f"Analizuotų dienų skaičius: {len(duomenys.dienos)}\n"
    statistika += f"Vidutinė temperatūra: {round(duomenys.metu_temp_vidutine, 1)} °C\n"
    statistika += f"Temperatūros mediana: {duomenys.metu_temp_medianas} °C\n\n"

    statistika += "Karščiausios dienos:\n"
    for d in duomenys.dienos_su_auksciausia_temp():
        statistika += f"2023-{d.diena}-{d.menesis} ({d.diena_str}) -- {d.temperatura} °C\n"
    statistika += "\n"

    statistika += "Šalčiausios dienos:\n"
    for d in duomenys.dienos_su_maziausia_temp():
        statistika += f"2023-{d.diena}-{d.menesis} ({d.diena_str}) -- {d.temperatura} °C\n"
    statistika += "\n"

    statistika += f"Dienų, kai temperatūra >  25 °C: {duomenys.dienu_skaicius_su_temp( 25, ">")}\n"
    statistika += f"Dienų, kai temperatūra < -10 °C: {duomenys.dienu_skaicius_su_temp(-10, "<")}"

    with open("isvesti_duomenys/03/bendra_statistika.txt", "w", encoding="utf-8") as fp:
        fp.write(statistika)

# =======
#    4
# =======

def krituliu_histograma(meteo_dienos: list[meteo_diena]):
    duomenys = meteo(meteo_dienos)

    histograma = {
        "iki_5mm": [],
        "virs_5mm_iki_15mm": [],
        "virs_15mm_iki_30mm": [],
        "virs_30mm": []
    }

    for d in duomenys.dienos:
        if 0 <= d.krituliai <= 5:
            histograma["iki_5mm"].append(d)
        elif 5 < d.krituliai <= 15:
            histograma["virs_5mm_iki_15mm"].append(d)
        elif 15 < d.krituliai <= 30:
            histograma["virs_15mm_iki_30mm"].append(d)
        else:
            histograma["virs_30mm"].append(d)

    iki_5mm            = "#" * math.ceil(len(histograma["iki_5mm"]) / 5)
    virs_5mm_iki_15mm  = "#" * math.ceil(len(histograma["virs_5mm_iki_15mm"]) / 5)
    virs_15mm_iki_30mm = "#" * math.ceil(len(histograma["virs_15mm_iki_30mm"]) / 5)
    virs_30mm          = "#" * math.ceil(len(histograma["virs_30mm"]) / 5)

    with open("isvesti_duomenys/03/krituliai.txt", "w", encoding="utf-8") as fp:
        out  = f"Iki 5 mm          ({len(histograma["iki_5mm"]):<3}) | {iki_5mm:<73}\n"
        out += f"Virš 5 iki 15 mm  ({len(histograma["virs_5mm_iki_15mm"]):<3}) | {virs_5mm_iki_15mm:<73}\n"
        out += f"Virš 15 iki 30 mm ({len(histograma["virs_15mm_iki_30mm"]):<3}) | {virs_15mm_iki_30mm:<73}\n"
        out += f"Virš 30 mm        ({len(histograma["virs_30mm"]):<3}) | {virs_30mm:<73}"

        fp.write(out)

# =======
#    5
# =======

def audringos_dienos(meteo_dienos: list[meteo_diena]):
    duomenys = meteo(meteo_dienos)

    out = ""
    audringos: list[meteo_diena] = []

    for d in duomenys.dienos:
        if d.vejas < 15:
            continue

        if d.krituliai < 10:
            continue

        audringos.append(d)

    if len(audringos) == 0:
        out = "Dienų, atitinkančių audros kriterijus, nėra."
    else:
        for d in audringos:
            out += f"{d.data.year}-{d.data.month:02d}-{d.data.day:02d} ({d.diena_str}) -- AUDRA: krituliai {d.krituliai} mm, vėjas {d.vejas} m/s\n"

    with open("isvesti_duomenys/03/audra.txt", "w", encoding="utf-8") as fp:
        fp.write(out)

# ==========
#    6, 7
# ==========

def apskaiciuoti_statistika(dienos: list[meteo_diena]):
    duomenys = meteo(dienos)
    
    return { "dienu_skaicius": len(dienos),
             "temp_vidutine": duomenys.metu_temp_vidutine,
             "temp_auksciausia": duomenys.dienos_su_auksciausia_temp()[0].temperatura,
             "temp_zemiausia": duomenys.dienos_su_maziausia_temp()[0].temperatura,
             "krituliu_suma": sum([ d.krituliai for d in dienos ]),
             "krituliai_didziausi": max([ d.krituliai for d in dienos ]),
             "vejas_vidutinis": sum([ d.vejas for d in dienos ]) / len(dienos) }

# =======
#    6
# =======

def menesiu_statistika(meteo_dienos: list[meteo_diena]):
    duomenys = meteo(meteo_dienos)

    out = ""

    for menesis in range(1, 13):
        dienos = [ d for d in duomenys.dienos if d.menesis == menesis ]

        out += f"{date(2023, menesis, 1).strftime('%m')} -- "

        if len(dienos) == 0:
            out += "Duomenų nėra.\n"

            continue

        out += f"{dienos[0].menesis_str.upper()}\n"

        statistika = apskaiciuoti_statistika(dienos)

        out += f"Analizuotų dienų skaičius: {statistika['dienu_skaicius']}\n"
        out += f"Vidutinė temperatūra: {statistika['temp_vidutine']:.1f} °C\n"
        out += f"Aukščiausia temperatūra: {statistika['temp_auksciausia']:.1f} °C\n"
        out += f"Žemiausia temperatūra: {statistika['temp_zemiausia']:.1f} °C\n"
        out += f"Kritulių suma: {statistika['krituliu_suma']:.1f} mm\n"
        out += f"Vidutinis vėjo greitis: {statistika['vejas_vidutinis']:.1f} m/s\n"
        out += "\n"

    with open("isvesti_duomenys/03/menesiai.txt", "w", encoding="utf-8") as fp:
        fp.write(out)

# =======
#    7
# =======

def metu_laiku_statistika(meteo_dienos: list[meteo_diena]):
    duomenys = meteo(meteo_dienos)

    out = ""

    for metu_laikas in [ "Žiema", "Pavasaris", "Vasara", "Ruduo" ]:
        dienos = [ d for d in duomenys.dienos if d.metu_laikas == metu_laikas ]
        dienos.sort(key=lambda d: d.data)

        out += f"{metu_laikas.upper()}\n"

        if len(dienos) == 0:
            out += "Duomenų nėra.\n"

            continue

        statistika = apskaiciuoti_statistika(dienos)

        out += f"Analizuotų dienų skaičius: {statistika['dienu_skaicius']}\n"
        out += f"Vidutinė temperatūra: {statistika['temp_vidutine']:.1f} °C\n"
        out += f"Kritulių suma: {statistika['krituliu_suma']:.1f} mm\n"
        out += f"Vidutinis vėjo greitis: {statistika['vejas_vidutinis']:.1f} m/s\n\n"

        salciausios = [ d for d in dienos if d.temperatura == statistika["temp_zemiausia"] ]
        silciausios = [ d for d in dienos if d.temperatura == statistika["temp_auksciausia"] ]
        lietingiausios = [ d for d in dienos if d.krituliai == statistika["krituliai_didziausi"] ]

        for pavadinimas, atrinktos in [ ("Šalčiausios dienos", salciausios),
                                        ("Šilčiausios dienos", silciausios),
                                        ("Daugiausia kritulių", lietingiausios) ]:

            out += f"{pavadinimas}:\n"

            for d in atrinktos:
                out += f"{d.data} ({d.diena_str}) -- temperatūra: {d.temperatura:.1f} °C; krituliai: {d.krituliai:.1f} mm; vėjas: {d.vejas:.1f} m/s\n"

        out += "\n\n\n"

    with open("isvesti_duomenys/03/metu_laikai.txt", "w", encoding="utf-8") as fp:
        fp.write(out)

if __name__ == "__main__":
    try:
        os.makedirs("isvesti_duomenys/03")
    except FileExistsError:
        pass

    dienos = meteo_dienu_sarasas()

    bendroji_temperaturu_statistika(dienos)
    krituliu_histograma(dienos)
    audringos_dienos(dienos)
    menesiu_statistika(dienos)
    metu_laiku_statistika(dienos)