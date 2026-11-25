"""Numerical and bilingual checks for the A2/S04 pooling reference sheet."""
from math import isclose, sqrt, erfc
from pathlib import Path
import yaml

from tools.construire import charger_seance
from tools.validation_contenus import verifier_overlay_traduction

ROOT = Path(__file__).resolve().parents[2]


def test_a2_s04_reference_sheet_is_complete_and_bilingual():
    fr = charger_seance("a2/s04", "fr")
    en = charger_seance("a2/s04", "en")
    overlay = yaml.safe_load((ROOT / "contenus/en/a2/s04.yaml").read_text(encoding="utf-8"))
    assert fr["fiche"]["statut"] == "brouillon"
    assert len(fr["fiche"]["cours_complet"]["sections"]) == 7
    assert len(fr["fiche"]["methodes"]["methodes"]) == 3
    assert len(fr["fiche"]["exemples_guides"]["exemples"]) == 3
    assert len(fr["fiche"]["exercices_corriges"]["exercices"]) == 3
    assert not verifier_overlay_traduction(fr, overlay, session_id="a2/s04")
    assert en["fiche"]["cours_complet"]["sections"][0]["titre"] == "1. Sum and average of independent risks"


def test_a2_s04_portfolio_pooling_and_correlation_values():
    n,p,c=10000,0.01,10000
    mean_n=n*p
    var_n=n*p*(1-p)
    sd_n=sqrt(var_n)
    mean_total=mean_n*c
    sd_total=sd_n*c
    sd_average=sd_total/n
    assert isclose(mean_n,100,abs_tol=1e-12)
    assert isclose(var_n,99,abs_tol=1e-12)
    assert isclose(sd_n,sqrt(99),abs_tol=1e-12)
    assert isclose(mean_total,1_000_000,abs_tol=1e-12)
    assert isclose(sd_total,99498.743710662,abs_tol=1e-8)
    assert isclose(sd_average,9.9498743710662,abs_tol=1e-12)

    sigma,rho,n2=10000,0.05,1000
    sd_ind=sigma/sqrt(n2)
    sd_corr=sqrt(sigma**2*(1/n2+(n2-1)/n2*rho))
    floor=sigma*sqrt(rho)
    assert isclose(sd_ind,316.22776601683796,abs_tol=1e-12)
    assert isclose(sd_corr,2257.2106680591423,abs_tol=1e-9)
    assert isclose(floor,2236.06797749979,abs_tol=1e-9)
    assert sd_corr>sd_ind>floor*0.1


def test_a2_s04_clt_tail_and_lab_code_execute():
    z=(119.5-100)/sqrt(99)
    tail=0.5*erfc(z/sqrt(2))
    assert isclose(z,1.9598237397554636,abs_tol=1e-12)
    assert isclose(tail,0.02500819774282286,abs_tol=1e-12)

    session=yaml.safe_load((ROOT/"contenus/a2/s04.yaml").read_text(encoding="utf-8"))
    app=session["fiche"]["applications_labs"]["applications"][0]
    block=next(item for item in app["procedure"] if "sd_average_corr" in item)
    fence=chr(96)*3
    code=block.split(fence+"python",1)[1].split(fence,1)[0].strip()
    namespace={}
    exec(compile(code,"a2_s04_reference_lab.py","exec"),namespace)
    assert isclose(namespace["sd_average"],10_000*sqrt(0.01*0.99/10_000),abs_tol=1e-12)
    assert isclose(namespace["sd_average_corr"],10_000*sqrt(0.01*0.99*(1/10_000+9999/10_000*0.05)),abs_tol=1e-9)
