import os
import yaml

AUTHOR_MAP = {
    "adonai-oliveira": "Adonai Oliveira",
    "alessandroloiola": "Alessandro Loiola",
    "milah44": "Camila Batista",
    "carlosduna2019": "Carlos Alberto",
    "danberg1000": "Dan Berg",
    "edicleiaalveslima": "Edicliea Alves Lima",
    "eduardoplaton": "Eduardo Platon",
    "fteodoro10": "Fernanda Teodoro",
    "hermes-rodrigues-nery": "Hermes Rodrigues Nery",
    "jesshutter": "Jessica Jaconetti",
    "joabsonjoao": "Joabson Joao",
    "joicemariasc": "Joice Ferreira",
    "Leonardo": "Leonardo Gabossa",
    "Marcos Ferreira": "Marcos Ferreira",
    "drnataliabellan": "Natalia Bellan",
    "nazarethefonseca": "Nazareth Fonseca",
    "debarrospaulo": "Paulo Fernando De Barros",
    "pmbizz": "Paulo Mello",
    "sabervirtuosodunapress": "Saber Virtuoso",
    "Thami": "Thami Bernardo da Silva",
    "qualividaonline": "Vanessa Fagundes",
    "vamatti": "Vera Amatti",
    "Vitor Guerino": "Vitor Guerino",
    "wesleylima": "Wesley Lima"
}

def fix(fp):
    try:
        c = open(fp, "r", encoding="utf-8").read()
        if not c.startswith("---"): return False
        p = c.split("---", 2)
        if len(p) < 3: return False
        d = yaml.safe_load(p[1])
        if d and "author" in d:
            old = str(d["author"]).strip()
            if old in AUTHOR_MAP:
                d["author"] = AUTHOR_MAP[old]
                fm = yaml.dump(d, allow_unicode=True, sort_keys=False, default_flow_style=False)
                open(fp, "w", encoding="utf-8").write("---\n" + fm + "---\n" + p[2])
                print("OK: " + fp + " (" + old + " -> " + AUTHOR_MAP[old] + ")")
                return True
        return False
    except Exception as e:
        print("ERR: " + fp + " " + str(e))
        return False

t, c = 0, 0
for r, ds, fs in os.walk("./artigos"):
    for f in fs:
        if f.endswith(".md"):
            t += 1
            if fix(os.path.join(r, f)): c += 1
print(str(c) + " de " + str(t) + " corrigidos.")
