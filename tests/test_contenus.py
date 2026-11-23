"""Vérifie les contenus : structure des séances et chiffres recalculés indépendamment."""
import math
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



def _calcul(sid):
    s = charger_seance(sid)
    return s, {c["cle"]: c["valeur"] for c in next(e for e in s["etapes"] if e["type"] == "calcul")["champs"]}


def _proche(obtenu, attendu, tol=1e-6):
    assert set(obtenu) == set(attendu), (sorted(obtenu), sorted(attendu))
    for k in attendu:
        assert abs(obtenu[k] - attendu[k]) < tol, (k, obtenu[k], attendu[k])


def test_calcul_a1_s02():
    s, champs = _calcul("a1/s02")
    i, m, n = s["taux"], 12, 10
    v = 1 / (1 + i)
    im, dm = m * ((1 + i) ** (1 / m) - 1), m * (1 - v ** (1 / m))
    _proche(champs, {"im": im, "dm": dm, "am": (1 - v**n) / im, "adm": (1 - v**n) / dm})
    # Figures quoted in the quizzes.
    assert round(((1 + 0.06 / 12) ** 12 - 1) * 100, 3) == 6.168
    assert round(((1 + 0.06 / 4) ** 4 - 1) * 100, 3) == 6.136
    assert round(((1 + 0.04 / 12) ** 12 - 1) * 100, 2) == 4.07
    assert round(1200 * (1 - v**n) / im, 2) == 9910.25
    assert round(1200 * (1 - v**n) / i) == 9733
    assert round(i / im, 4) == 1.0182
    assert round(1.005**12, 6) == 1.061678 and round((1 + i) ** (1 / 12), 7) == 1.0032737
    assert round(v ** (1 / 12), 7) == 0.9967369 and round(1 - v**10, 6) == 0.324436
    assert [round(x * 100, 3) for x in (i * v, dm, math.log(1 + i), im, 2 * ((1 + i) ** 0.5 - 1))] == [3.846, 3.916, 3.922, 3.928, 3.961]


def test_calcul_a1_s03():
    s, champs = _calcul("a1/s03")
    i, n, g = s["taux"], 10, 0.02
    v = 1 / (1 + i)
    a = sum(v**k for k in range(1, n + 1))
    ia = sum(k * v**k for k in range(1, n + 1))
    da = sum((n + 1 - k) * v**k for k in range(1, n + 1))
    geo = sum((1 + g) ** (k - 1) * v**k for k in range(1, n + 1))
    _proche(champs, {"s": a * (1 + i) ** n, "ia": ia, "da": da, "geo": geo})
    assert round(a, 4) == 7.7217 and round(a * (1 + i), 4) == 8.1078 and round(v**n, 6) == 0.613913
    assert round((1 + i) ** n, 6) == 1.628895 and round(1000 * a * (1 + i) ** n, 2) == 12577.89
    assert 10000 / i == 200000 and round(10000 / (i * v)) == 210000 and round(1 / (i - g), 2) == 33.33
    assert round((n + 1) * a, 4) == 84.9391 and round(((1 + g) / (1 + i)) ** n, 6) == 0.748357
    assert round(1000 * geo, 2) == 8388.11 and round(1000 * a) == 7722


def test_calcul_a1_s04():
    s, champs = _calcul("a1/s04")
    i, n, loan = s["taux"], 5, 10000
    v = 1 / (1 + i)
    a = lambda k: (1 - v**k) / i
    p = loan / a(n)
    b, rows = loan, []
    for _ in range(n):
        interest = i * b
        b -= p - interest
        rows.append((interest, p - interest, b))
    _proche(champs, {"p": p, "b2": rows[1][2], "i3": rows[2][0], "pr3": rows[2][1]}, tol=1e-3)
    assert abs(rows[1][2] - (loan * (1 + i) ** 2 - p * ((1 + i) ** 2 - 1) / i)) < 1e-9
    assert abs(rows[-1][2]) < 1e-9 and round(a(n), 6) == 4.212364 and round(a(3), 6) == 2.673012
    assert round(rows[0][1], 2) == 1773.96 and round(n * p - loan, 2) == 1869.82
    assert round((1 + i) ** 2, 4) == 1.1236
    npv = lambda j: -1000 + 600 / (1 + j) + 600 / (1 + j) ** 2
    assert round(npv(0.10), 2) == 41.32 and round(600 / 1.1, 2) == 545.45 and round(600 / 1.21, 2) == 495.87
    assert abs(npv(0.130662)) < 1e-3 and npv(0.1306) > 0 > npv(0.1308)


def test_calcul_a1_s05():
    s, champs = _calcul("a1/s05")
    y, spot = s["taux"], [0.03, 0.035, 0.04]
    prix = lambda yy, n=5: sum(50 / (1 + yy) ** t for t in range(1, n + 1)) + 1000 / (1 + yy) ** n
    prix3 = 50 / 1.03 + 50 / 1.035**2 + 1050 / 1.04**3
    f12, f23 = 1.035**2 / 1.03 - 1, 1.04**3 / 1.035**2 - 1
    _proche(champs, {"prix5": prix(y), "prix3": prix3, "f12": f12, "f23": f23}, tol=1e-4)
    assert [round(prix(r), 2) for r in (0.04, 0.05, 0.06)] == [1044.52, 1000.0, 957.88]
    a5 = (1 - 1.04**-5) / 0.04
    assert round(a5, 4) == 4.4518 and round(1.04**-5, 4) == 0.8219 and round(10 * a5, 2) == 44.52
    assert round((1 - 1.06**-5) / 0.06, 4) == 4.2124 and round(1.06**-5, 4) == 0.7473
    assert round(1.035**2, 6) == 1.071225 and round(1.04**3, 6) == 1.124864 and round(1 + f23, 6) == 1.050073
    assert [round(x, 2) for x in (50 / 1.03, 50 / 1.035**2, 1050 / 1.04**3)] == [48.54, 46.68, 933.45]
    p3 = lambda yy: 50 / (1 + yy) + 50 / (1 + yy) ** 2 + 1050 / (1 + yy) ** 3
    assert p3(0.0396) > prix3 > p3(0.0398)


def test_calcul_a2_s01():
    _, champs = _calcul("a2/s01")
    ps = 0.2 * 0.15 + 0.8 * 0.05
    _proche(champs, {"ps": ps, "pjs": 0.2 * 0.15 / ps, "aucun": 0.95**10, "un": 1 - 0.95**10})
    assert round(ps, 10) == 0.07 and round(0.03 / ps, 4) == 0.4286 and round(0.05**2, 4) == 0.0025
    assert round(0.95**10, 6) == 0.598737 and round(1 - 0.95**10, 6) == 0.401263


def test_calcul_a2_s02():
    _, champs = _calcul("a2/s02")
    pois = lambda k, lam: math.exp(-lam) * lam**k / math.factorial(k)
    binom = lambda k, n, p: math.comb(n, k) * p**k * (1 - p) ** (n - k)
    _proche(champs, {"p0": pois(0, 0.3), "p2": 1 - pois(0, 0.3) - pois(1, 0.3),
                     "b1": binom(1, 20, 0.05), "b0": 1 - binom(0, 20, 0.05)})
    assert round(pois(1, 0.3), 4) == 0.2222 and round(1 - pois(0, 0.3), 4) == 0.2592 and round(pois(3, 0.3), 4) == 0.0033
    assert round(binom(0, 20, 0.05), 4) == 0.3585 and round(math.exp(-1), 4) == 0.3679 and round(0.95**19, 6) == 0.377354
    m = 0.2 + 0.2
    var = 0.2 + 0.4 - m**2
    assert round(m, 10) == 0.4 and round(var, 10) == 0.44 and round(500**2 * var) == 110000
    assert round(math.sqrt(500**2 * var), 2) == 331.66 and round(20 * 0.05 * 0.95, 10) == 0.95

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
    with pytest.raises(ValueError):
        fusion(base_codes, {"solution": "Use A3, x2 and ch1; then calculate n+1."}, "test")


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

    # Navigation pages and account pages must expose valid language alternates too.
    for chemin in ("", "fondamentaux", "a1", "compte"):
        profondeur = len([part for part in chemin.split("/") if part])
        base_fr = "../" * profondeur
        base_en = "../" * (profondeur + 1)
        fr_path = tmp_path / "site" / chemin / "index.html" if chemin else tmp_path / "site" / "index.html"
        en_path = tmp_path / "site" / "en" / chemin / "index.html" if chemin else tmp_path / "site" / "en" / "index.html"
        fr_page = fr_path.read_text(encoding="utf-8")
        en_page = en_path.read_text(encoding="utf-8")
        suffix = (chemin + "/" if chemin else "") + "index.html"
        assert f'hreflang="fr" href="{base_fr}{suffix}"' in fr_page
        assert f'hreflang="en" href="{base_fr}en/{suffix}"' in fr_page
        assert f'hreflang="fr" href="{base_en}{suffix}"' in en_page
        assert f'hreflang="en" href="{base_en}en/{suffix}"' in en_page
        assert f'href="{base_fr}en/{suffix}"' in fr_page
        assert f'href="{base_en}{suffix}"' in en_page


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


def test_formules_makeham_et_udd():
    """Garde les signes et l'égalité exacte de l'espérance complète sous UDD."""
    import math

    s = charger_seance("a3/s01")
    recap = next(e for e in s["etapes"] if e["type"] == "rappel")
    formules = [bloc.get("formule", "") for bloc in recap["blocs"]]
    assert any(r"\underbrace{-\ln s}_{A} + \underbrace{-\,\ln g\,\ln c}_{B}\,c^{x}" in f for f in formules)
    assert any(r"\mathring{e}_x = \int_0^{\infty} {}_tp_x\,\mathrm{d}t = e_x + \tfrac12" in f for f in formules)

    table = s["table"]
    k, a, g, c = table["k"], table["s"], table["g"], table["c"]

    def log_l(x):
        return math.log(k) + x * math.log(a) + c**x * math.log(g)

    A = -math.log(a)
    B = -math.log(g) * math.log(c)
    for age in (0, 40, 65, 100):
        h = 1e-5
        derivative = -(log_l(age + h) - log_l(age - h)) / (2 * h)
        assert math.isclose(derivative, A + B * c**age, rel_tol=1e-8, abs_tol=1e-10)


def test_aucun_texte_court_ne_contient_de_saut_de_ligne():
    """Options, titles and labels are one line: a newline there means a broken edit (e.g. a pasted copy of the file)."""
    for _, _, sid in seances(charger_parcours()):
        for langue in ("fr", "en"):
            s = charger_seance(sid, langue)
            for e in s["etapes"]:
                assert "\n" not in e["titre"], (sid, langue)
                for q in e.get("questions", []):
                    assert all("\n" not in o for o in q["options"]), (sid, langue, q["q"])
