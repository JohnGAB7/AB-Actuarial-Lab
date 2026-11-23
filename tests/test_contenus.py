"""Vérifie les contenus : structure des séances et chiffres recalculés indépendamment."""
import math
from pathlib import Path

import yaml

from tools.construire import charger_parcours, charger_seance, nombres_tex_en, seances, verifier_seance

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


def test_calcul_a2_s03():
    _, champs = _calcul("a2/s03")
    phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
    z = math.log(5000) - 7
    _proche(champs, {"s1": math.exp(-2.5), "q1": -2000 * math.log(0.01), "m2": math.exp(7.5), "s2": 1 - phi(z)}, tol=1e-4)
    assert round(2000 * math.log(2), 2) == 1386.29 and round(math.exp(7), 2) == 1096.63 and round(math.log(2), 6) == 0.693147
    assert round(math.log(5000), 4) == 8.5172 and round(z, 4) == 1.5172
    pareto = lambda x: (4000 / (4000 + x)) ** 3
    assert round(pareto(5000), 4) == 0.0878 and abs(pareto(5000) - 64 / 729) < 1e-15 and round(pareto(20000) * 100, 2) == 0.46
    assert round(math.exp(-10) * 100, 4) == 0.0045 and 4000 / (3 - 1) == 2000
    assert round(phi(1.645), 3) == 0.95 and round(phi(1.96), 3) == 0.975
    assert 1000 + 1.645 * 200 == 1329 and round(1000 + 1.96 * 200) == 1392


def test_calcul_a2_s04():
    _, champs = _calcul("a2/s04")
    phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
    mu, sigma = 0.01 * 10000, 10000 * math.sqrt(0.01 * 0.99)
    sn = sigma / 100
    _proche(champs, {"sigma": sigma, "sigma_n": sn, "prob": 1 - phi(10 / sn), "prime": mu + 1.645 * sn}, tol=1e-4)
    assert mu == 100 and round(sigma**2) == 990000 and round(sigma, 2) == 994.99
    assert round(sigma / 10, 2) == 99.50 and round(sn, 2) == 9.95 and round(10 / sn, 3) == 1.005
    assert round(1 - phi(10 / (sigma / 10)), 3) == 0.460 and round(1.645 * sn, 2) == 16.37
    assert round((sigma / (0.05 * mu)) ** 2) == 39600 and round(sigma / (0.05 * mu), 3) == 198.997
    assert round(sn / mu * 100, 2) == 9.95


def test_calcul_a2_s05():
    _, champs = _calcul("a2/s05")
    phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
    lam, theta = 50, 2000
    var = lam * 2 * theta**2
    _proche(champs, {"es": lam * theta, "vs": var / 1e6, "sd": math.sqrt(var), "p": 1 - phi(30000 / math.sqrt(var))})
    assert round(math.sqrt(lam * theta**2)) == 14142 and round(1 - phi(1.5), 4) == 0.0668
    var_nb = 50 * theta**2 + 100 * theta**2
    assert var_nb == 6e8 and round(math.sqrt(var_nb), 2) == 24494.90 and round(math.sqrt(var_nb / var) - 1, 2) == 0.22
    assert round(math.sqrt(2 * var)) == 28284 and round(0.1 * 2 * 0.5 * 0.5, 10) == 0.05


def test_calcul_a2_s06():
    _, champs = _calcul("a2/s06")
    pd = 0.05 * 2000 * math.exp(-500 / 2000)
    p = pd * 1.2 / 0.75
    _proche(champs, {"pd": pd, "ler": 1 - math.exp(-0.25), "p": p, "lr": pd / p}, tol=1e-4)
    assert 0.02 * 500 == 10 and 0.02 * 400 == 8 and round(10 * 1.2 / 0.75, 10) == 16
    assert (10000 + 4000) / 16000 == 0.875 and round(math.exp(-0.25), 4) == 0.7788
    assert [round(x, 2) for x in (pd * 1.2 / 0.75 * 0.25, pd * 1.2, p - pd - 0.25 * p, pd * 1.2 * 1.25, 0.25 * pd * 1.2 * 1.25, pd * 1.25)] == \
        [31.15, 93.46, 15.58, 116.82, 29.21, 97.35]
    assert round(pd * 1.2, 3) == 93.456 and round(2000 * math.exp(-0.25), 2) == 1557.60

def test_calcul_a2b_s01():
    _, champs = _calcul("a2b/s01")
    xs = [1200, 800, 3500, 600, 2100, 950, 1700, 4200]
    n, m = len(xs), sum(xs) / len(xs)
    ss = sum((x - m) ** 2 for x in xs)
    s = math.sqrt(ss / (n - 1))
    v = ss / n
    _proche(champs, {"s": s, "se": s / math.sqrt(n), "alpha": m * m / v, "theta": v / m}, tol=1e-4)
    assert sum(xs) == 15050 and m == 1881.25 and ss == 12219687.5 and m * m == 3539101.5625
    assert sorted(xs)[3:5] == [1200, 1700] and (1200 + 1700) / 2 == 1450
    assert round(ss / 7, 2) == 1745669.64 and round(v, 2) == 1527460.94 and round(8 / 7 - 1, 3) == 0.143
    assert round(s) == 1321 and round(s / math.sqrt(8)) == 467 and round(s / math.sqrt(32)) == 234
    assert round(v / (m * m), 3) == 0.432 and round(m * m / v, 3) == 2.317 and round(v / m, 2) == 811.94

def test_calcul_a2b_s02():
    _, champs = _calcul("a2b/s02")
    xs = [1200, 800, 3500, 600, 2100, 950, 1700, 4200]
    counts = [3, 1, 4, 2, 0, 5, 2, 3, 1, 4]
    somme = sum(math.log(1 + x / 2000) for x in xs)
    alpha = 8 / somme
    m = sum(xs) / 8
    loglik = -8 * math.log(m) - sum(xs) / m
    _proche(champs, {"somme": somme, "alpha": alpha, "queue": (2000 / 7000) ** alpha, "loglik": loglik}, tol=1e-4)
    lam = sum(counts) / len(counts)
    assert sum(counts) == 25 and lam == 2.5 and math.sqrt(lam / 10) == 0.5 and round(math.sqrt(lam), 2) == 1.58
    assert round(math.exp(-lam), 4) == 0.0821 and counts.count(0) == 1
    assert round(somme, 4) == 4.9335 and round(alpha, 4) == 1.6216 and round(alpha - 1, 2) == 0.62
    assert round(2000 / (alpha - 1)) == 3218 and round((2000 / 7000) ** alpha, 3) == 0.131
    assert round(math.exp(-5000 / m), 3) == 0.070 and round(2000 / 7000, 3) == 0.286
    assert round(-8 * math.log(m) - 8, 4) == round(loglik, 4) == -68.3175

def _student_cdf(t, nu, pas=20000):
    """Student CDF by Simpson's rule, to check the quoted t quantile without scipy."""
    c = math.gamma((nu + 1) / 2) / (math.sqrt(nu * math.pi) * math.gamma(nu / 2))
    f = lambda x: c * (1 + x * x / nu) ** (-(nu + 1) / 2)
    h = t / pas
    s = f(0) + f(t) + sum((4 if k % 2 else 2) * f(k * h) for k in range(1, pas))
    return 0.5 + s * h / 3


def test_calcul_a2b_s03():
    _, champs = _calcul("a2b/s03")
    p, n = 120 / 2000, 2000
    se = math.sqrt(p * (1 - p) / n)
    besoin = 1.96**2 * p * (1 - p) / 0.01**2
    _proche(champs, {"se": se, "bas": p - 1.96 * se, "haut": p + 1.96 * se, "n": math.ceil(besoin)}, tol=1e-4)
    assert abs(_student_cdf(2.364624, 7) - 0.975) < 1e-6
    assert [round(100 * x, 2) for x in (p - 1.96 * se, p + 1.96 * se, p - se, p + se)] == [4.96, 7.04, 5.47, 6.53]
    assert round(besoin, 1) == 2166.7 and math.ceil(besoin) == 2167 and round(p * (1 - p) / 0.01**2) == 564
    assert math.ceil(1.96 * p * (1 - p) / 0.01**2) == 1106 and round(100 * 1.96 * se, 2) == 1.04
    xs = [1200, 800, 3500, 600, 2100, 950, 1700, 4200]
    m = sum(xs) / 8
    sem = math.sqrt(sum((x - m) ** 2 for x in xs) / 7 / 8)
    assert [round(m + k * sem) for k in (-2.364624, 2.364624, -1.96, 1.96, -1, 1)] == [777, 2986, 966, 2797, 1414, 2348]
    assert round(2.365 * 467.13, 1) == 1104.8 and round(2.364624 * sem, 1) == 1104.6 and round(2.365 / 1.96 - 1, 2) == 0.21
    assert round(2.576 / 1.96, 2) == 1.31 and round(2.5 - 1.96 * 0.5, 2) == 1.52 and round(2.5 + 1.96 * 0.5, 2) == 3.48
    assert round(2.5 - 1.96 * math.sqrt(2.5), 2) == -0.60 and round(2.5 + 1.96 * math.sqrt(2.5), 2) == 5.60

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
                assert [{**c, "libelle": nombres_tex_en(c["libelle"])} for c in a["champs"]] == b["champs"], sid


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
