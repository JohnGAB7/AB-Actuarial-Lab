"""Numerical and bilingual checks for the A2/S02 reference sheet."""
from math import isclose, exp
from pathlib import Path
import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction

ROOT = Path(__file__).resolve().parents[2]


def test_a2_s02_reference_sheet_is_complete_and_bilingual():
    fr = charger_seance("a2/s02", "fr")
    en = charger_seance("a2/s02", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2/s02.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "brouillon"
    assert len(fr["fiche"]["cours_complet"]["sections"]) == 7
    assert len(fr["fiche"]["methodes"]["methodes"]) == 3
    assert len(fr["fiche"]["exemples_guides"]["exemples"]) == 3
    assert len(fr["fiche"]["exercices_corriges"]["exercices"]) == 3
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2/s02")
    assert en["fiche"]["cours_complet"]["sections"][0]["titre"] == "1. Discrete random variable and probability mass function"


def test_a2_s02_binomial_poisson_and_moments_reconcile():
    n, p = 20, 0.05
    p0 = (1-p)**n
    p1 = n*p*(1-p)**(n-1)
    p_any = 1-p0
    lam=n*p
    q0=exp(-lam)
    q1=lam*exp(-lam)
    q_any=1-q0
    assert isclose(p0, 0.3584859224085422, abs_tol=1e-12)
    assert isclose(p1, 0.3773536025353072, abs_tol=1e-12)
    assert isclose(p_any, 0.6415140775914578, abs_tol=1e-12)
    assert isclose(q0, 0.36787944117144233, abs_tol=1e-12)
    assert isclose(q1, 0.36787944117144233, abs_tol=1e-12)
    assert isclose(q_any, 0.6321205588285577, abs_tol=1e-12)
    assert abs(p_any-q_any) < 0.01

    lam2=0.3
    tail2=1-exp(-lam2)*(1+lam2)
    assert isclose(tail2, 0.03693631311376675, abs_tol=1e-12)
    mean=0.7*0+0.2*1+0.1*2
    second=0.7*0+0.2*1+0.1*4
    variance=second-mean**2
    assert isclose(mean,0.4,abs_tol=1e-12)
    assert isclose(variance,0.44,abs_tol=1e-12)
    assert isclose(500**2*variance,110000,abs_tol=1e-12)


def test_a2_s02_reference_lab_code_executes():
    session=yaml.safe_load((ROOT/"contenus/a2/s02.yaml").read_text(encoding="utf-8"))
    app=session["fiche"]["applications_labs"]["applications"][0]
    code_block=next(item for item in app["procedure"] if "binom_p0" in item)
    fence=chr(96)*3
    code=code_block.split(fence+"python",1)[1].split(fence,1)[0].strip()
    namespace={}
    exec(compile(code,"a2_s02_reference_lab.py","exec"),namespace)
    assert isclose(namespace["binom_any"],0.6415140775914578,abs_tol=1e-6)
    assert isclose(namespace["pois_any"],0.6321205588285577,abs_tol=1e-6)
