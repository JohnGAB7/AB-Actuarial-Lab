"""Module A3, séance 2 : valeurs actuelles des assurances. À toi d'écrire le corps des fonctions.

Lance les tests : python -m pytest tests/a3/test_s02_assurances.py
Un test « skipped » veut dire que la fonction n'est pas encore écrite.
"""

K, S, G, C, OMEGA = 1000450.59, 0.999106875782, 0.999549614043, 1.103798111448, 116

def l(x):
    """Number of survivors at integer age x (copy your session 1 code)."""
    raise NotImplementedError

def pure_endowment(x, n, i):
    """nE_x = v**n * l(x + n) / l(x)."""
    raise NotImplementedError

def term_insurance(x, n, i):
    """A1_{x:n} = sum over k = 0 .. n-1 of v**(k+1) * d(x+k) / l(x), paid at the end of the year of death."""
    raise NotImplementedError

def whole_life(x, i):
    """A_x: term insurance up to the end of the table (OMEGA)."""
    raise NotImplementedError
