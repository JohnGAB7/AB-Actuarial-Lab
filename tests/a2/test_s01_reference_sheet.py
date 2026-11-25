"""Numerical and bilingual checks for the A2/S01 self-contained reference sheet."""
from math import isclose
from pathlib import Path
import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction

ROOT = Path(__file__).resolve().parents[2]


def test_a2_s01_reference_sheet_is_complete_and_bilingual():
    fr = charger_seance("a2/s01", "fr")
    en = charger_seance("a2/s01", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2/s01.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "brouillon"
    assert len(fr["fiche"]["cours_complet"]["sections"]) == 7
    assert len(fr["fiche"]["methodes"]["methodes"]) == 3
    assert len(fr["fiche"]["exemples_guides"]["exemples"]) == 3
    assert len(fr["fiche"]["exercices_corriges"]["exercices"]) == 3
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2/s01")
    assert en["fiche"]["cours_complet"]["sections"][0]["titre"] == "1. Events and conditional probability"


def test_a2_s01_bayes_and_portfolio_examples_reconcile():
    weights = [0.20, 0.80]
    rates = [0.15, 0.05]
    p_claim = sum(w * r for w, r in zip(weights, rates))
    p_young_given_claim = weights[0] * rates[0] / p_claim
    assert isclose(p_claim, 0.07, abs_tol=1e-12)
    assert isclose(p_young_given_claim, 3 / 7, abs_tol=1e-12)

    weights3 = [0.50, 0.30, 0.20]
    rates3 = [0.04, 0.10, 0.20]
    p_claim3 = sum(w * r for w, r in zip(weights3, rates3))
    posterior = [w * r / p_claim3 for w, r in zip(weights3, rates3)]
    assert isclose(p_claim3, 0.09, abs_tol=1e-12)
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(posterior, [2/9, 1/3, 4/9]))
    assert isclose(sum(posterior), 1, abs_tol=1e-12)


def test_a2_s01_at_least_one_claim_and_lab_code():
    p_any = 1 - (1 - 0.05) ** 10
    assert isclose(p_any, 0.4012630607616215, abs_tol=1e-12)
    assert p_any <= 10 * 0.05

    session = yaml.safe_load((ROOT / "contenus/a2/s01.yaml").read_text(encoding="utf-8"))
    app = session["fiche"]["applications_labs"]["applications"][0]
    block = next(item for item in app["procedure"] if "weights = [0.50" in item)
    fence = chr(96) * 3
    code = block.split(fence + "python", 1)[1].split(fence, 1)[0].strip()
    namespace = {}
    exec(compile(code, "a2_s01_reference_lab.py", "exec"), namespace)
    assert isclose(namespace["p_claim"], 0.09, abs_tol=1e-12)
    assert isclose(namespace["p_any"], p_any, abs_tol=1e-12)
