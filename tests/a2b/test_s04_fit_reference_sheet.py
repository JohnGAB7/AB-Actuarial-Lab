"""Numerical and bilingual checks for the A2b/S04 goodness-of-fit reference sheet."""
from math import exp, factorial, log, sqrt
from pathlib import Path

import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction
from tools.fiche_reference import verifier_fiche

ROOT = Path(__file__).resolve().parents[2]
CLAIMS = [1200, 800, 3500, 600, 2100, 950, 1700, 4200]


def ks(xs, cdf):
    xs = sorted(xs)
    n = len(xs)
    return max(max((i + 1) / n - cdf(x), cdf(x) - i / n) for i, x in enumerate(xs))


def test_a2b_s04_reference_sheet_is_ready_and_bilingual():
    fr = charger_seance("a2b/s04", "fr")
    en = charger_seance("a2b/s04", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2b/s04.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "prete"
    assert not verifier_fiche(fr["fiche"], session_id="a2b/s04")
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2b/s04")
    assert en["fiche"]["cours_complet"]["sections"][1]["titre"] == "2. The chi-square test"


def test_a2b_s04_figures_reconcile():
    observed = [610, 300, 70, 20]
    expected = [1000 * exp(-0.5) * 0.5**k / factorial(k) for k in range(3)]
    expected.append(1000 - sum(expected))
    assert [round(e, 2) for e in expected] == [606.53, 303.27, 75.82, 14.39]
    assert round(sum(expected[:3]), 2) == 985.61 and min(expected) > 5
    parts = [(o - e) ** 2 / e for o, e in zip(observed, expected)]
    assert [round(c, 4) for c in parts] == [0.0198, 0.0352, 0.4462, 2.1892]
    chi2 = sum(parts)
    assert round(chi2, 4) == 2.6905 and round(exp(-chi2 / 2), 4) == 0.2605 and chi2 < 5.99
    mean = sum(CLAIMS) / 8
    cdf = lambda x: 1 - exp(-x / mean)
    assert round(ks(CLAIMS, cdf), 4) == 0.2731 and round(cdf(600), 4) == 0.2731
    assert round(1.36 / sqrt(8), 3) == 0.481 and round(1 - cdf(4200), 4) == 0.1073
    ll_exp = -8 * log(mean) - 8
    assert round(ll_exp, 4) == -68.3175 and round(2 - 2 * ll_exp, 2) == 138.64
    alpha = 8 / sum(log(1 + x / 2000) for x in CLAIMS)
    ll_par = sum(log(alpha) + alpha * log(2000) - (alpha + 1) * log(2000 + x) for x in CLAIMS)
    assert round(alpha, 4) == 1.6216 and round(ll_par, 4) == -69.8736 and round(2 - 2 * ll_par, 2) == 141.75
    assert round(2 * 1 + 240.8, 1) == 242.8 and round(2 * 2 + 237.8, 1) == 241.8
    c = 25 / 45 + 25 / 35
    assert round(25 / 45, 4) == 0.5556 and round(25 / 35, 4) == 0.7143
    assert round(c, 4) == 1.2698 and round(exp(-c / 2), 4) == 0.5300
    assert round(ks([0.1, 0.4, 0.6, 0.9], lambda x: x), 10) == 0.15 and round(1.36 / sqrt(4), 2) == 0.68


def test_a2b_s04_lab_code_runs():
    session = yaml.safe_load((ROOT / "contenus/a2b/s04.yaml").read_text(encoding="utf-8"))
    app = session["fiche"]["applications_labs"]["applications"][0]
    block = next(item for item in app["procedure"] if "aic_exp" in item)
    fence = chr(96) * 3
    code = block.split(fence + "python", 1)[1].split(fence, 1)[0].strip()
    namespace = {}
    exec(compile(code, "a2b_s04_reference_lab.py", "exec"), namespace)
    assert round(namespace["chi2"], 4) == 2.6905 and round(namespace["d"], 4) == 0.2731
    assert round(namespace["aic_exp"], 2) == 138.64
