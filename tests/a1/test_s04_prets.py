"""Tests de l'exercice de la séance a1/s04. Les mêmes tests tournent dans le site (Pyodide)."""
import pytest
import yaml
from pathlib import Path

from exercices.a1 import s04_prets as ex
from tests.a1 import reference as ref

SEANCE = yaml.safe_load((Path(__file__).resolve().parents[2] / "contenus/a1/s04.yaml").read_text(encoding="utf-8"))
TESTS = next(e for e in SEANCE["etapes"] if e["type"] == "code")["tests"]


def _evaluer(module, expr):
    return eval(expr, vars(module).copy())


@pytest.mark.parametrize("t", TESTS, ids=[t["nom"] for t in TESTS])
def test_corrige_passe_les_tests(t):
    """Garde-fou : le corrigé doit passer chaque test, sinon c'est le test qui est faux."""
    assert _evaluer(ref, t["expr"])


@pytest.mark.parametrize("t", TESTS, ids=[t["nom"] for t in TESTS])
def test_ton_code(t):
    try:
        resultat = _evaluer(ex, t["expr"])
    except NotImplementedError:
        pytest.skip("Fonction pas encore écrite : à toi de jouer.")
    assert resultat, t["nom"]


def test_reference_irr_rejects_unbracketed_cashflows():
    """Bisection must not return a boundary when no IRR is bracketed."""
    with pytest.raises(ValueError, match="IRR is not bracketed"):
        ref.irr({0: -1000, 1: -100})


def test_reference_irr_rejects_invalid_bounds():
    with pytest.raises(ValueError, match="bounds"):
        ref.irr({0: -1000, 1: 1200}, low=-1.0, high=1.0)
