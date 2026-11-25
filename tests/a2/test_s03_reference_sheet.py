"""Numerical and bilingual checks for the A2/S03 continuous severity reference sheet."""
from math import isclose, exp, log, erf, sqrt
from pathlib import Path
import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction

ROOT = Path(__file__).resolve().parents[2]


def test_a2_s03_reference_sheet_is_complete_and_bilingual():
    fr = charger_seance("a2/s03", "fr")
    en = charger_seance("a2/s03", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2/s03.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "prete"
    assert len(fr["fiche"]["cours_complet"]["sections"]) == 7
    assert len(fr["fiche"]["methodes"]["methodes"]) == 3
    assert len(fr["fiche"]["exemples_guides"]["exemples"]) == 3
    assert len(fr["fiche"]["exercices_corriges"]["exercices"]) == 3
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2/s03")
    assert en["fiche"]["cours_complet"]["sections"][0]["titre"] == "1. Density, CDF and probability"


def test_a2_s03_exponential_lognormal_and_pareto_values():
    exp_surv = exp(-5000/2000)
    exp_q99 = -2000*log(0.01)
    assert isclose(exp_surv,0.0820849986238988,abs_tol=1e-12)
    assert isclose(exp_q99,9210.340371976182,abs_tol=1e-9)

    ln_mean=exp(7+1/2)
    ln_median=exp(7)
    z_ln=(log(5000)-7)/1
    ln_surv=1-0.5*(1+erf(z_ln/sqrt(2)))
    ln_q95=exp(7+1.6448536269514722)
    assert isclose(ln_mean,1808.0424144560632,abs_tol=1e-12)
    assert isclose(ln_median,1096.6331584284585,abs_tol=1e-12)
    assert isclose(ln_surv,0.064608957412716,abs_tol=1e-12)
    assert isclose(ln_q95,5680.835676010869,abs_tol=1e-9)

    par_surv=(4000/9000)**3
    par_mean=4000/(3-1)
    par_var=3*4000**2/((3-1)**2*(3-2))
    par_q99=4000*((0.01)**(-1/3)-1)
    assert isclose(par_surv,64/729,abs_tol=1e-12)
    assert isclose(par_mean,2000,abs_tol=1e-12)
    assert isclose(par_var,12000000,abs_tol=1e-12)
    assert isclose(par_q99,14566.355334451113,abs_tol=1e-9)


def test_a2_s03_reference_lab_code_executes():
    session=yaml.safe_load((ROOT/"contenus/a2/s03.yaml").read_text(encoding="utf-8"))
    app=session["fiche"]["applications_labs"]["applications"][0]
    block=next(item for item in app["procedure"] if "normal_cdf" in item)
    fence=chr(96)*3
    code=block.split(fence+"python",1)[1].split(fence,1)[0].strip()
    namespace={}
    exec(compile(code,"a2_s03_reference_lab.py","exec"),namespace)
    assert isclose(namespace["exp_surv"],0.0820849986,abs_tol=1e-8)
    assert isclose(namespace["ln_surv"],0.0646089574,abs_tol=1e-8)
    assert isclose(namespace["par_surv"],64/729,abs_tol=1e-12)
