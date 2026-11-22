"""Tests de l'exercice de la séance a3/s01. Les mêmes tests tournent dans le site (Pyodide)."""
import pytest
import yaml
from pathlib import Path

from exercices.a3 import s01_survie as ex
from tests.a3 import reference as ref

SEANCE = yaml.safe_load((Path(__file__).resolve().parents[2] / "contenus/a3/s01.yaml").read_text(encoding="utf-8"))
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
