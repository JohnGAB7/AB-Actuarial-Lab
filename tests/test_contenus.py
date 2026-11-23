"""Vérifie les contenus : structure des séances et chiffres recalculés indépendamment."""
from pathlib import Path

import yaml

from tools.construire import charger_parcours, charger_seance, seances, verifier_seance

RACINE = Path(__file__).resolve().parents[1]


def test_structure_des_seances():
    p = charger_parcours()
    for _, _, sid in seances(p):
        assert verifier_seance(charger_seance(sid)) == []


def test_calcul_a3_s01_coherent_avec_le_tableau():
    s = charger_seance("a3/s01")
    calc = next(e for e in s["etapes"] if e["type"] == "calcul")
    lx = [int(v.replace(" ", "")) for v in calc["donnees"]["lignes"][0][1:]]
    attendu = {"p1": lx[1] / lx[0], "p2": lx[2] / lx[0], "p3": lx[3] / lx[0], "e3": sum(lx[1:]) / lx[0]}
    for c in calc["champs"]:
        assert abs(c["valeur"] - attendu[c["cle"]]) < 1e-6, c["cle"]


def test_tableau_a3_s01_issu_de_la_table_mk():
    s = charger_seance("a3/s01")
    t = s["table"]
    calc = next(e for e in s["etapes"] if e["type"] == "calcul")
    lx = [int(v.replace(" ", "")) for v in calc["donnees"]["lignes"][0][1:]]
    for x, v in zip(range(65, 69), lx):
        assert round(t["k"] * t["s"] ** x * t["g"] ** (t["c"] ** x)) == v


def test_calcul_a3_s02_coherent_avec_le_tableau():
    s = charger_seance("a3/s02")
    calc = next(e for e in s["etapes"] if e["type"] == "calcul")
    lx = [int(v.replace(" ", "")) for v in calc["donnees"]["lignes"][0][1:]]
    v = 1 / (1 + s["taux"])
    temp = sum(v ** (k + 1) * (lx[k] - lx[k + 1]) for k in range(3)) / lx[0]
    diff = v**3 * lx[3] / lx[0]
    attendu = {"temp": temp, "diff": diff, "mixte": temp + diff}
    for c in calc["champs"]:
        assert abs(c["valeur"] - attendu[c["cle"]]) < 1e-6, c["cle"]


def test_aucun_support_de_cours_ni_cv_dans_le_depot():
    """Supports de cours et CV restent dans la bibliothèque du projet, jamais sur un dépôt."""
    interdits = {".pdf", ".pptx", ".ppt", ".docx", ".doc", ".tex", ".xlsx"}
    trouves = [
        p for p in RACINE.rglob("*")
        if ".git" not in p.parts and p.is_file()
        and (p.suffix.lower() in interdits or "cv" in p.stem.lower().replace("-", "_").split("_"))
    ]
    assert trouves == [], f"Fichiers interdits sur le dépôt : {trouves}"


SECTIONS_A_PRODUIRE = ["## 1. Notions", "## 2. Exercices corrigés", "## 3. Pièges", "## 4. Vocabulaire anglais", "## 5. Pour la vidéo"]


def test_fichiers_a_produire_suivent_le_modele():
    for f in sorted((RACINE / "a-produire").glob("*.md")):
        if f.name == "README.md":
            continue
        texte = f.read_text(encoding="utf-8")
        positions = [texte.find(s) for s in SECTIONS_A_PRODUIRE]
        assert -1 not in positions, f"{f.name} : section manquante"
        assert positions == sorted(positions), f"{f.name} : sections dans le désordre"
