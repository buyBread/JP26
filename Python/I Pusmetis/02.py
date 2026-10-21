import os
import util
import sys
import random
from dataclasses import dataclass

@dataclass
class preke:
    idx: str
    pavadinimas: str
    kategorija: str
    kaina: float
    likutis: int

# =============
#    2, 3, 4
# =============

def prekiu_sarasas() -> list[preke]:
    ret = []

    kategorijos_KK: dict[str, int] = {}

    def kategorija_ABKKNNNN(p: preke, i: int) -> str:
        A    = p.pavadinimas[0].upper()
        B    = p.kategorija[0].upper()
        KK   = f"{kategorijos_KK[p.kategorija]:02d}"
        NNNN = f"{i + 1:04d}"

        return A + B + KK + NNNN

    with util.open_file("pradiniai_duomenys/prekes250.txt") as fp:
        data = fp.read().split("\n")

        for i, ln in enumerate(data):
            ln = ln.split(";")

            if len(ln) != 3:
                continue

            prekes_pavadinimas = ln[0]
            prekes_kategorija  = ln[1]
            prekes_kaina       = ln[2]

            if prekes_pavadinimas == "" or prekes_kategorija == "":
                continue

            try:
                prekes_kaina = float(prekes_kaina) # type: ignore
            except ValueError:
                continue

            if prekes_kaina < 0.99 or prekes_kaina > 999.99:
                continue

            prekes_kaina = prekes_kaina

            if prekes_kategorija not in kategorijos_KK:
                kategorijos_KK[prekes_kategorija] = len(kategorijos_KK) + 1

            p = preke("", prekes_pavadinimas, prekes_kategorija, prekes_kaina, -1)

            p.idx     = kategorija_ABKKNNNN(p, i)
            p.likutis = random.randint(0, 200)

            ret.append(p)

    if not ret:
        print("Faile nėra tinkamų prekių.")

        sys.exit(1)

    return ret

# =======
#    4
# =======

def irasyti_prekiu_duomenis(prekes: list[preke]):
    out = "ID,Pavadinimas,Kategorija,Kaina,Likutis\n"

    for p in prekes:
        out += f"{p.idx},{p.pavadinimas},{p.kategorija},{p.kaina},{p.likutis}\n"

    with open("isvesti_duomenys/02/sandelis.csv", "w", encoding="utf-8") as fp:
        fp.write(out)

# =========
#    5.a
# =========

def brangiausia_preke(prekes: list[preke]) -> preke | list[preke]:
    p_bran = max(prekes, key=lambda p: p.kaina)

    # jeigu yra daugiai nei viena prekė su šia kaina, gausime visas prekes su didžiausia kaina
    ret = [ p for p in prekes if p.kaina == p_bran.kaina ]

    if len(ret) > 1:
        return ret

    return ret[0]

# =========
#    5.b
# =========

def maziausia_likuti_turinti_preke(prekes: list[preke]) -> preke | list[preke]:
    p_maz = min(prekes, key=lambda p: p.likutis)

    # jeigu yra daugiai nei viena prekė su šiuo likučiu, gausime visas prekes su mažiausiu likučiu
    ret = [ p for p in prekes if p.likutis == p_maz.likutis ]

    if len(ret) > 1:
        return ret

    return ret[0]

# =========
#    5.c
# =========

def sandelio_verte(prekes: list[preke]):
    return sum([ p.kaina * p.likutis for p in prekes ])

# =======
#    6
# =======

def kategoriju_sarasas(prekes: list[preke]):
    # padarant `dict`, galima gauti kategorijas kaip raktus;
    # verčiant atgal į `list`, gauname nepasikartojantį kategorijų sarašą.
    return list(dict.fromkeys(p.kategorija for p in prekes))

def kategorijos_analize(prekes: list[preke]):
    print("[ Pasirinktos kategorijos analizė ]\n")

    kategorijos = kategoriju_sarasas(prekes)
    
    for i, k in enumerate(kategorijos):
        print(f"  {i + 1}. {k}")

    print("")

    def ivesti_kategorija():
        try:
            kategorija = input(f"Įveskite kategorijos skaičių (pvz.: \"2\" dėl \"{kategorijos[2 - 1]}\"): ")
            kategorija = kategorijos[int(kategorija) - 1]

            return kategorija
        except ValueError:
            print("Įveskite skaičių, o ne žodį.")

            return ivesti_kategorija()
        except IndexError:
            print("Tokios kategorijos nėra.")

            return ivesti_kategorija()

    kategorija = ivesti_kategorija()

    prekes = [ p for p in prekes if p.kategorija == kategorija ]

    print(f"""\nKATEGORIJA: {kategorija.upper()}

Prekių įrašų skaičius: {len(prekes)}
Bendras vienetų likutis: {sum([p.likutis for p in prekes])}
Vidutinė vieneto kaina: {sum([p.kaina for p in prekes]) / len(prekes)} Eur
Bendra atsargų vertė: {sum([p.kaina for p in prekes])} Eur""")

# =======
#    7
# =======

def padaryti_ataskaita(prekes: list[preke]):
    out = "Brangiausios prekės:\n"

    brangiausios = ""
    prekes.sort(key=lambda p: p.kaina, reverse=True)

    for i, p in enumerate(prekes):
        if i == 10:
            break

        brangiausios += f"{i + 1}. {p.idx} | {p.pavadinimas} | {p.kategorija} | {p.kaina} Eur\n"

    out += brangiausios

    out += "\nPrekės, kurių likutis yra mažiau nei 5 vnt.:\n"

    mazas_likutis = ""
    prekes.sort(key=lambda p: p.likutis)

    for i, p in enumerate(prekes):
        if p.likutis >= 5:
            continue

        mazas_likutis += f"{i + 1}. {p.idx} | {p.pavadinimas} | {p.kategorija} | {p.likutis} vnt.\n"

    if mazas_likutis == "":
        mazas_likutis = "Prekių, kurių likutis mažesnis nei 5, nėra.\n"

    out += mazas_likutis

    out += "\nVisų kategorijų statistika:\n"
    kategoriju_analize: dict[str, list[preke]] = {}

    for p in prekes:
        try:
            kategoriju_analize[p.kategorija].append(p)
        except KeyError:
            kategoriju_analize[p.kategorija] = [ p ]

    out += f"| {'Kategorija':^24} | {'Prekių įrašų skaičius':^24} | {'Bendras likutis':^24} | {'Vidutinė kaina, Eur':^24} | {'Atsargų vertė, Eur':^24} |\n"
    out += f"--{'-' * 24}---{'-' * 24}---{'-' * 24}---{'-' * 24}---{'-' * 24}--\n"

    for k, ps in kategoriju_analize.items():
        prekiu_skaicius = len(ps)
        prekiu_bendras_likutis = sum([ p.likutis for p in ps ])
        prekiu_vidutine_kaina = sum([ p.kaina for p in ps ]) / prekiu_skaicius
        prekiu_visa_verte = sum([ p.kaina * p.likutis for p in ps ])

        out += f"| {k:^24} | {prekiu_skaicius:>24} | {prekiu_bendras_likutis:>24} | {prekiu_vidutine_kaina:>24.2f} | {prekiu_visa_verte:>24.2f} |\n"

    out += "\nSANDĖLIO SUVESTINĖ\n"
    out += f"Prekių įrašų skaičius: {len(prekes)}\n"
    out += f"Kategorijų skaičius: {len(kategoriju_analize)}\n"
    out += f"Bendras vienetų likutis: {sum([ p.likutis for p in prekes ])}\n"
    out += f"Bendra sandėlio vertė: {round(sandelio_verte(prekes), 2)} Eur\n"

    with open("isvesti_duomenys/02/ataskaita.txt", "w", encoding="utf-8") as fp:
        fp.write(out)

if __name__ == "__main__":
    try:
        os.makedirs("isvesti_duomenys/02")
    except FileExistsError:
        pass

    random.seed(42)

    prekes = prekiu_sarasas()

    irasyti_prekiu_duomenis(prekes)

    brangiausios = brangiausia_preke(prekes)

    if isinstance(brangiausios, list):
        print("Brangiausios prekės:")

        for p in brangiausios:
            print(f"- [{p.idx}] {p.pavadinimas} | {p.kategorija} | {p.kaina} €")
    else:
        p = brangiausios

        print(f"Brangiausia prekė: [{p.idx}] {p.pavadinimas} | {p.kategorija} | {p.kaina} Eur")

    print("---")

    maziausi_likuciai = maziausia_likuti_turinti_preke(prekes)

    if isinstance(maziausi_likuciai, list):
        print("Prekės su mažiausiais likučiais:")

        for p in maziausi_likuciai:
            print(f"- [{p.idx}] {p.pavadinimas} | {p.kategorija} | {p.likutis}")
    else:
        p = maziausi_likuciai

        print(f"Mažiausiais likutis: [{p.idx}] {p.pavadinimas} | {p.kategorija} | {p.likutis}")

    print("---")

    print(f"Sandėlio vertė: {round(sandelio_verte(prekes), 2)} Eur")

    print("---")

    kategorijos_analize(prekes)

    padaryti_ataskaita(prekes)