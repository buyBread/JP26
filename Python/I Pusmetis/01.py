import csv
import util
import os
import statistics
from dataclasses import dataclass

# =======
#    2
# =======

@dataclass
class studentas:
    vardas: str
    pavarde: str
    pazymiai: list[int]

    def __str__(self):
        vidurkis: str = f"vidurkis: {self.vidurkis}" if self.vidurkis is not None else "vidurkis neskaičiuojamas"

        return f"{self.vardas} {self.pavarde} -- {vidurkis}"

    @property
    def validus_vidurkis(self) -> bool:
        return len(self.pazymiai) >= 3

    @property
    def vidurkis(self) -> float | None:
        return sum(self.pazymiai) / len(self.pazymiai) if self.validus_vidurkis else None

# =======
#    3
# =======

def print_eilute(i: int, row: list[str], msg: str):
    print(f"[Eilutė: {i} -- {row[0]} {row[1]}] {msg}.")
    
def studentu_sarasas() -> list[studentas]:
    ret = []

    with util.open_file("pradiniai_duomenys/studentai_lietuviski_INT.csv") as fp:
        data = csv.reader(fp)

        for i, row in enumerate(data):
            if i == 0:
                continue
            
            pazymiai = []

            for n in row[2:]:
                try:
                    n = int(n)

                    if n < 1 or n > 10:
                        print_eilute(i, row, f"Pažymys \"{n}\" nėra 1-10 intervale.")

                        pazymiai = []
                        break

                    pazymiai.append(int(n))
                except ValueError:
                    if n != "": # tuščia eilutė
                        print_eilute(i, row, f"Pažymys \"{n}\" negalima versti sveikuoju skaičiumi.")

                        pazymiai = []
                        break

                    continue

            if not pazymiai:
                continue
                    
            ret.append(studentas(row[0], row[1], pazymiai))

    return ret

# =========
#    4.a
# =========

def stundetai_sorted(studentai: list[studentas] | None = None, reverse=True) -> list[studentas]:
    if not studentai:
        studentai = studentu_sarasas()

    # `s.vidurkis is not None` yra `boolean` reikšmė.
    # kadangi Python tikrins pirmąjį elementą (`boolean` reikšme), `False` praleis studentų rikiavimą kurių `vidurkis` yra `None`.
    studentai.sort(key=lambda s: (s.vidurkis is not None, s.vidurkis), reverse=reverse)

    return studentai

# =========
#    4.b   
# =========

def studentai_su_nevalidziu_vidurkiu(studentai: list[studentas] | None = None) -> list[studentas]:
    if not studentai:
        studentai = studentu_sarasas()

    return [ s for s in studentai if not s.validus_vidurkis ]

# =========
#    4.c
# =========

@dataclass
class studentu_grupes_statistika:
    vidurkiai: list[float]

    vidurkis: float
    medianas: float

    didziausias_vidurkis: float
    maziausias_vidurkis:  float

    studentu_su_geru_vidurkiu_num: int

def sukurti_studentu_grupes_statistika(studentai: list[studentas] | None = None) -> studentu_grupes_statistika:
    if not studentai:
        studentai = studentu_sarasas()

    vidurkiai = [ s.vidurkis for s in studentai if s.vidurkis ]
    vidurkiai.sort()

    if len(vidurkiai) > 0:
        vidurkiu_vidurkis = sum(vidurkiai) / len(vidurkiai)
        vidurkiu_medianas = statistics.median(vidurkiai)

        max_vidurkis = max(vidurkiai)
        min_vidurkis = min(vidurkiai)

        studentu_su_geru_vidurkiu_num = len([ v for v in vidurkiai if v >= 8 ])

        return studentu_grupes_statistika(vidurkiai,
                                          vidurkiu_vidurkis,
                                          vidurkiu_medianas,
                                          max_vidurkis,
                                          min_vidurkis,
                                          studentu_su_geru_vidurkiu_num)

    return studentu_grupes_statistika([], 0, 0, 0, 0, 0)

# =======
#    5
# =======

def irasyti_pazangius_studentus(studentai: list[studentas] | None = None):
    if not studentai:
        studentai = studentu_sarasas()

    studentai = stundetai_sorted(studentai)

    out = [ str("Vardas,Pavarde,Vidurkis").split(",") ]

    for s in studentai:
        if not s.validus_vidurkis:
            continue

        if s.vidurkis < 8: # type: ignore
            continue

        out.append([ s.vardas, s.pavarde, str(round(s.vidurkis, 2)) ]) # type: ignore

    with open("isvesti_duomenys/01/pazangus.csv", "w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)

        writer.writerows(out)

# =======
#    6
# =======

def top_10_studentu(studentai: list[studentas] | None = None):
    if not studentai:
        studentai = studentu_sarasas()

    studentai = stundetai_sorted(studentai)

    ret  = "GERIAUSIAI BESIMOKANTYS STUDENTAI\n"
    visi = False

    if len([s for s in studentai if s.validus_vidurkis]) < 10:
        visi = True

    for i, s in enumerate(studentai):
        if not visi and i == 10:
            break

        ret += f"{i + 1} {s.vardas} {s.pavarde} -- {round(s.vidurkis, 2)}\n" # type: ignore

    return ret + "\n"

def studentai_be_vidurkiu(studentai: list[studentas] | None = None):
    if not studentai:
        studentai = studentu_sarasas()

    ret = "STUDENTAI, KURIEMS TRŪKSTA PAŽYMIŲ\n"

    if len([s for s in studentai if s.validus_vidurkis]) == len(studentai):
        return ret + "Visi studentai turi bent 3 pažymius.\n\n"

    for s in studentai:
        if s.validus_vidurkis:
            continue

        ret += f"{s.vardas} {s.pavarde} -- turi {len(s.pazymiai)}, iki 3 pažymių trūksta: {3 - len(s.pazymiai)}.\n"

    return ret + "\n"

def studentu_grupes_ataskaita(studentai: list[studentas] | None = None):
    if not studentai:
        studentai = studentu_sarasas()

    grupes_statistika = sukurti_studentu_grupes_statistika(studentai)

    ret = """GRUPĖS STATISTIKA
Studentų, kurių vidurkis skaičiuojamas: {}
Studentų vidurkių vidurkis: {}
Studentų vidurkių mediana: {}
Didžiausias vidurkis: {}
Mažiausias vidurkis: {}
Pažangių studentų (vidurkis ≥ 8): {}"""

    if len(grupes_statistika.vidurkiai) == 0:
        return ret.format("Nepakanka duomenų.",
                          "Nepakanka duomenų.",
                          "Nepakanka duomenų.",
                          "Nepakanka duomenų.",
                          "Nepakanka duomenų.",
                          0)

    return ret.format(len(grupes_statistika.vidurkiai),
                      round(grupes_statistika.vidurkis, 2),
                      round(grupes_statistika.medianas, 2),
                      round(grupes_statistika.didziausias_vidurkis, 2),
                      round(grupes_statistika.maziausias_vidurkis, 2),
                      grupes_statistika.studentu_su_geru_vidurkiu_num)

def irasyti_ataskaita(studentai: list[studentas] | None = None):
    if not studentai:
        studentai = studentu_sarasas()

    out  = top_10_studentu(studentai)
    out += studentai_be_vidurkiu(studentai)
    out += studentu_grupes_ataskaita(studentai)

    with open("isvesti_duomenys/01/ataskaita.txt", "w", encoding="utf-8") as fp:
        fp.write(out)
    
if __name__ == "__main__":
    try:
        os.makedirs("isvesti_duomenys/01")
    except FileExistsError:
        pass

    irasyti_pazangius_studentus()
    irasyti_ataskaita()
