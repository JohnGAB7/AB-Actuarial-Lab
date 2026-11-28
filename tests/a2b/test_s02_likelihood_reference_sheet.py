"""Numerical and bilingual checks for the A2b/S02 maximum likelihood reference sheet."""
from math import exp, isclose, log, sqrt
from pathlib import Path

import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction
from tools.fiche_reference import verifier_fiche

ROOT = Path(__file__).resolve().parents[2]
CLAIMS = [1200, 800, 3500, 600, 2100, 950, 1700, 4200]


def test_a2b_s02_reference_sheet_is_ready_and_bilingual():
    fr = charger_seance("a2b/s02", "fr")
    en = charger_seance("a2b/s02", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2b/s02.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "prete"
    assert not verifier_fiche(fr["fiche"], session_id="a2b/s02")
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2b/s02")
    assert en["fiche"]["cours_complet"]["sections"][0]["titre"] == "1. The likelihood"


def test_a2b_s02_figures_reconcile():
    counts = [3, 1, 4, 2, 0, 5, 2, 3, 1, 4]
    lam = sum(counts) / len(counts)
    assert sum(counts) == 25 and lam == 2.5 and isclose(sqrt(lam / 10), 0.5)
    assert round(exp(-lam), 4) == 0.0821 and round(sqrt(lam), 2) == 1.58
    total = sum(log(1 + x / 2000) for x in CLAIMS)
    alpha = 8 / total
    assert round(total, 4) == 4.9335 and round(alpha, 4) == 1.6216
    assert round((2000 / 7000) ** alpha, 4) == 0.1311
    assert round(2000 / (alpha - 1)) == 3218 and round(alpha / sqrt(8), 4) == 0.5733
    mean = sum(CLAIMS) / 8
    assert isclose(mean, 1881.25) and round(exp(-5000 / mean), 4) == 0.0701
    assert round(-8 * log(mean) - 8, 4) == -68.3175
    small = [2, 0, 1, 3, 1, 0, 2, 1]
    lam2 = sum(small) / 8
    assert lam2 == 1.25 and round(sqrt(lam2 / 8), 4) == 0.3953 and round(exp(-lam2), 4) == 0.2865
    assert small.count(0) / 8 == 0.25
    total2 = sum(log(1 + x / 1000) for x in [500, 1500, 1000, 3000])
    assert round(total2, 4) == 3.4012 and round(4 / total2, 4) == 1.1761
    assert round(1500 * log(2), 2) == 1039.72 and round(exp(-5000 / 1500), 4) == 0.0357


def test_a2b_s02_lab_code_runs():
    session = yaml.safe_load((ROOT / "contenus/a2b/s02.yaml").read_text(encoding="utf-8"))
    app = session["fiche"]["applications_labs"]["applications"][0]
    block = next(item for item in app["procedure"] if "tail_pareto" in item)
    fence = chr(96) * 3
    code = block.split(fence + "python", 1)[1].split(fence, 1)[0].strip()
    namespace = {}
    exec(compile(code, "a2b_s02_reference_lab.py", "exec"), namespace)
    assert round(namespace["alpha"], 4) == 1.6216 and round(namespace["loglik"], 4) == -68.3175
    ll = lambda t: -8 * log(t) - sum(CLAIMS) / t
    assert ll(1500) < namespace["loglik"] and ll(2500) < namespace["loglik"]
