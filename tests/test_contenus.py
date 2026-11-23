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


def test_calcul_a1_s01():
    import math
    s = charger_seance("a1/s01")
    calc = next(e for e in s["etapes"] if e["type"] == "calcul")
    i = s["taux"]
    v = 1 / (1 + i)
    attendu = {"d": i * v, "delta": math.log(1 + i), "a": v + v**2 + v**3, "ad": 1 + v + v**2}
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


def test_config_supabase_refuse_les_cles_secretes():
    import pytest
    from tools.construire import config_supabase
    url = "https://abcdefghijklmnopqrst.supabase.co"
    assert config_supabase({}) == {}
    assert config_supabase({"SUPABASE_URL": url, "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_abc"}) == {"url": url, "key": "sb_publishable_abc"}
    for cle in ["sb_secret_abc", "eyJhbGciOi.service_role.x", ""]:
        with pytest.raises(SystemExit):
            config_supabase({"SUPABASE_URL": url, "SUPABASE_PUBLISHABLE_KEY": cle})
    with pytest.raises(SystemExit):
        config_supabase({"SUPABASE_URL": "https://exemple.com", "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_abc"})


def test_migration_active_rls_sur_chaque_table():
    for f in sorted((RACINE / "supabase" / "migrations").glob("*.sql")):
        sql = f.read_text(encoding="utf-8").lower()
        for table in __import__("re").findall(r"create table if not exists (public\.\w+)", sql):
            assert f"alter table {table} enable row level security" in sql, f"{f.name} : RLS manquante sur {table}"


def test_aucune_cle_secrete_dans_le_depot():
    """Une vraie clé secrète Supabase (ou un JWT) ne doit jamais être committée."""
    import re
    motif = re.compile(r"sb_secret_[A-Za-z0-9_-]{10,}|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}")
    for p in RACINE.rglob("*"):
        if ".git" in p.parts or "_site" in p.parts or "vendor" in p.parts or not p.is_file() or p.suffix in {".pyc", ".png"}:
            continue
        assert not motif.search(p.read_text(encoding="utf-8", errors="ignore")), p


def test_chaque_seance_a_sa_traduction_anglaise():
    from tools.construire import verifier_traduction
    for _, _, sid in seances(charger_parcours()):
        assert verifier_traduction(sid) == [], sid


def test_traduction_ne_touche_pas_aux_chiffres():
    import pytest
    from tools.construire import fusion
    base = {"etapes": [{"type": "quiz", "questions": [{"q": "Question ?", "reponse": 1}]}]}
    with pytest.raises(ValueError):
        fusion(base, {"etapes": [{"questions": [{"reponse": 0}]}]}, "test")
    with pytest.raises(ValueError):
        fusion(base, {"etapes": [{}, {}]}, "test")
    with pytest.raises(ValueError):
        fusion(base, {"nouveau": "texte"}, "test")


def test_traduction_ne_change_ni_formule_ni_nombre_ni_type():
    import pytest
    from tools.construire import fusion
    base = {"formule": r"\text{VA} = \frac{1}{1{,}025}", "solution": "$d = 0{,}0244$ et 716 046 survivants.", "minutes": 3, "intro": "Quatre questions."}
    ok = fusion(base, {"formule": r"\text{PV} = \frac{1}{1{,}025}", "solution": "$d = 0.0244$ and 716,046 survivors."}, "t")
    assert ok["formule"].startswith(r"\text{PV}")
    for trad in ({"formule": r"\text{PV} = \frac{1}{1{,}25}"},            # constant changed in a formula
                 {"formule": r"\text{PV} = \frac{2}{1{,}025}"},
                 {"solution": "$d = 0.244$ and 716,046 survivors."},     # number changed in a text
                 {"solution": "$d = 0.0244$ and 716,046 survivors, 3 times."},
                 {"intro": ""}, {"intro": "   "},                          # empty translation
                 {"intro": 4},                                          # other type
                 {"minutes": 4}):                                       # numeric field
        with pytest.raises(ValueError):
            fusion(base, trad, "t")


def test_traduction_preserve_signe_unite_et_exposant():
    import pytest
    from tools.construire import fusion

    base = {"solution": r"Le taux est -2{,}5\,\% et epsilon vaut 1e-5."}
    valide = {"solution": "The rate is -2.5% and epsilon is 1e-5."}
    assert fusion(base, valide, "test")["solution"] == valide["solution"]

    # Same digits are not enough: sign, percentage unit and exponent sign carry meaning.
    for invalide in (
        {"solution": "The rate is 2.5% and epsilon is 1e-5."},
        {"solution": "The rate is -2.5 and epsilon is 1e-5."},
        {"solution": "The rate is -2.5% and epsilon is 1e5."},
    ):
        with pytest.raises(ValueError):
            fusion(base, invalide, "test")

    # Numbers embedded in identifiers must remain protected too (A3 must not become A4).
    base_codes = {"solution": "Use A3, x2 and ch1; then calculate n-1."}
    valide_codes = {"solution": "Use A3, x2 and ch1; then calculate n-1."}
    assert fusion(base_codes, valide_codes, "test") == base_codes
    with pytest.raises(ValueError):
        fusion(base_codes, {"solution": "Use A4, x2 and ch1; then calculate n-1."}, "test")
    with pytest.raises(ValueError):
        fusion(base_codes, {"solution": "Use A3, x3 and ch1; then calculate n-1."}, "test")
    with pytest.raises(ValueError):
        fusion(base_codes, {"solution": "Use A3, x2 and ch2; then calculate n-1."}, "test")


def test_tableaux_anglais_identiques_au_francais():
    """The English tables only change the number format (2,5 % → 2.5%, 716 046 → 716,046)."""
    def norme(v, langue):
        v = str(v).replace(" ", "").replace("%", "")
        return v.replace(",", "") if langue == "en" else v.replace(",", ".")
    for _, _, sid in seances(charger_parcours()):
        fr, en = charger_seance(sid), charger_seance(sid, "en")
        for a, b in zip(fr["etapes"], en["etapes"]):
            if a["type"] == "calcul":
                assert [[norme(x, "fr") for x in l] for l in a["donnees"]["lignes"]] == \
                       [[norme(x, "en") for x in l] for l in b["donnees"]["lignes"]], sid
                assert a["champs"] == b["champs"]


def test_site_bilingue(tmp_path, monkeypatch):
    import tools.construire as c
    monkeypatch.setattr(c, "SORTIE", tmp_path / "site")
    c.construire()
    for sid in [s for _, _, s in seances(charger_parcours())]:
        fr = (tmp_path / "site" / sid / "index.html").read_text(encoding="utf-8")
        en = (tmp_path / "site" / "en" / sid / "index.html").read_text(encoding="utf-8")
        assert '<html lang="fr">' in fr and '<html lang="en">' in en
        assert f'href="../../en/{sid}/index.html"' in fr and f'href="../../../{sid}/index.html"' in en
        for page, base in ((fr, "../../"), (en, "../../../")):
            assert f'hreflang="fr" href="{base}{sid}/index.html"' in page
            assert f'hreflang="en" href="{base}en/{sid}/index.html"' in page
    accueil = (tmp_path / "site" / "en" / "index.html").read_text(encoding="utf-8")
    assert 'hreflang="fr" href="../index.html"' in accueil and "Foundations" in accueil


def test_traduction_ne_peut_pas_modifier_les_metadonnees_de_session():
    import pytest
    from tools.construire import fusion

    base = {
        "id": "a1/s01",
        "module": "a1",
        "en": "Compound interest and annuities certain",
        "actu_basics": {
            "episode": "A1 · Financial mathematics",
            "statut": "à proposer",
        },
        "titre": "Intérêt composé",
    }

    with pytest.raises(ValueError, match=r"\.en"):
        fusion(base, {"en": "Different metadata title"}, "a1/s01")
    with pytest.raises(ValueError, match=r"\.actu_basics"):
        fusion(base, {"actu_basics": {"statut": "published"}}, "a1/s01")
