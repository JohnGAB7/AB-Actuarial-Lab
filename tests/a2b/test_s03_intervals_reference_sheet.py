"""Numerical and bilingual checks for the A2b/S03 confidence interval reference sheet."""
from math import ceil, sqrt
from pathlib import Path
from statistics import stdev

import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction
from tools.fiche_reference import verifier_fiche

ROOT = Path(__file__).resolve().parents[2]
CLAIMS = [1200, 800, 3500, 600, 2100, 950, 1700, 4200]


def test_a2b_s03_reference_sheet_is_ready_and_bilingual():
    fr = charger_seance("a2b/s03", "fr")
    en = charger_seance("a2b/s03", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2b/s03.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "prete"
    assert not verifier_fiche(fr["fiche"], session_id="a2b/s03")
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2b/s03")
    assert en["fiche"]["cours_complet"]["sections"][0]["titre"] == "1. What a confidence interval says"


def test_a2b_s03_figures_reconcile():
    p, n = 120 / 2000, 2000
    se = sqrt(p * (1 - p) / n)
    assert p == 0.06 and round(se, 5) == 0.00531 and round(1.96 * se, 4) == 0.0104
    assert (round(p - 1.96 * se, 4), round(p + 1.96 * se, 4)) == (0.0496, 0.0704)
    assert round(1.96**2 * 0.0564 / 0.01**2, 1) == 2166.7 and ceil(1.96**2 * 0.0564 / 0.01**2) == 2167
    assert ceil(1.96**2 * 0.0564 / 0.005**2) == 8667
    assert round(2.576 / 1.96, 2) == 1.31
    assert (round(p - 2.576 * se, 4), round(p + 2.576 * se, 4)) == (0.0463, 0.0737)
    mean = sum(CLAIMS) / 8
    se_mean = stdev(CLAIMS) / sqrt(8)
    assert round(se_mean, 2) == 467.13 and round(2.3646 * 467.13, 1) == 1104.6
    assert (round(mean - 2.364624 * se_mean), round(mean + 2.364624 * se_mean)) == (777, 2986)
    assert (round(mean - 2.364624 * se_mean, 2), round(mean + 2.364624 * se_mean, 2)) == (776.67, 2985.83)
    assert (round(mean - 1.96 * se_mean), round(mean + 1.96 * se_mean)) == (966, 2797)
    assert round(100 * 2.364624 * se_mean / mean) == 59
    assert (round(2.5 - 1.96 * 0.5, 2), round(2.5 + 1.96 * 0.5, 2)) == (1.52, 3.48)
    assert 2.5 - 1.96 * sqrt(2.5) < 0
    q = 45 / 1500
    se_q = sqrt(q * (1 - q) / 1500)
    assert q == 0.03 and round(se_q, 4) == 0.0044
    assert (round(q - 1.96 * se_q, 4), round(q + 1.96 * se_q, 4)) == (0.0214, 0.0386)
    assert round(1.96**2 * 0.03 * 0.97 / 0.005**2, 1) == 4471.6 and ceil(1.96**2 * 0.03 * 0.97 / 0.005**2) == 4472
    small = [3, 7, 1, 9, 4]
    s = stdev(small)
    assert round(s, 4) == 3.1937 and round(s / sqrt(5), 4) == 1.4283
    half = 2.7764 * 1.4283
    assert round(half, 4) == 3.9655
    assert (round(4.8 - half, 2), round(4.8 + half, 2)) == (0.83, 8.77)
    assert round(1.96 * s / sqrt(5), 2) == 2.80 and round(100 * (2.776445 / 1.96 - 1)) == 42


def test_a2b_s03_lab_code_runs():
    session = yaml.safe_load((ROOT / "contenus/a2b/s03.yaml").read_text(encoding="utf-8"))
    app = session["fiche"]["applications_labs"]["applications"][0]
    block = next(item for item in app["procedure"] if "needed =" in item)
    fence = chr(96) * 3
    code = block.split(fence + "python", 1)[1].split(fence, 1)[0].strip()
    namespace = {}
    exec(compile(code, "a2b_s03_reference_lab.py", "exec"), namespace)
    assert namespace["needed"] == 2167 and round(namespace["low"], 4) == 0.0496
