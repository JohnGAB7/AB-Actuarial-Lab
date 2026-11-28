"""Numerical and bilingual checks for the A2b/S01 estimation reference sheet."""
from math import isclose, sqrt
from pathlib import Path
from statistics import median

import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction
from tools.fiche_reference import verifier_fiche

ROOT = Path(__file__).resolve().parents[2]
CLAIMS = [1200, 800, 3500, 600, 2100, 950, 1700, 4200]


def test_a2b_s01_reference_sheet_is_ready_and_bilingual():
    fr = charger_seance("a2b/s01", "fr")
    en = charger_seance("a2b/s01", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2b/s01.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "prete"
    assert not verifier_fiche(fr["fiche"], session_id="a2b/s01")
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2b/s01")
    assert en["fiche"]["cours_complet"]["sections"][0]["titre"] == "1. Parameter, estimator, estimate"


def test_a2b_s01_figures_reconcile():
    n = len(CLAIMS)
    mean = sum(CLAIMS) / n
    ss = sum((x - mean) ** 2 for x in CLAIMS)
    s2 = ss / (n - 1)
    s = sqrt(s2)
    assert sum(CLAIMS) == 15050 and isclose(mean, 1881.25) and isclose(ss, 12219687.5)
    assert round(s2, 2) == 1745669.64 and round(s, 2) == 1321.24
    assert round(s / sqrt(n), 2) == 467.13
    assert median(CLAIMS) == 1450 and round(100 * (n / (n - 1) - 1), 1) == 14.3
    var_n = ss / n
    theta, alpha = var_n / mean, mean**2 / var_n
    assert round(var_n, 2) == 1527460.94 and round(theta, 2) == 811.94
    assert round(mean**2, 2) == 3539101.56 and round(alpha, 4) == 2.3170
    assert isclose(alpha * theta, mean) and isclose(alpha * theta**2, var_n)
    small = [3, 7, 1, 9, 4]
    m = sum(small) / 5
    ss_small = sum((x - m) ** 2 for x in small)
    assert isclose(m, 4.8) and isclose(ss_small, 40.8)
    assert isclose(ss_small / 4, 10.2) and isclose(ss_small / 5, 8.16)
    assert round(sqrt(10.2 / 5), 2) == 1.43
    assert 500000 / 1000 == 500 and 1000**2 / 500000 == 2
    assert round(s / sqrt(32), 2) == 233.56


def test_a2b_s01_lab_code_runs():
    session = yaml.safe_load((ROOT / "contenus/a2b/s01.yaml").read_text(encoding="utf-8"))
    app = session["fiche"]["applications_labs"]["applications"][0]
    block = next(item for item in app["procedure"] if "alpha, theta" in item)
    fence = chr(96) * 3
    code = block.split(fence + "python", 1)[1].split(fence, 1)[0].strip()
    namespace = {}
    exec(compile(code, "a2b_s01_reference_lab.py", "exec"), namespace)
    assert round(namespace["alpha"], 4) == 2.3170 and round(namespace["theta"], 2) == 811.94
