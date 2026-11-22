"""Module 1, séance 1 : modèles de survie. À toi d'écrire le corps des fonctions.

Lance les tests : python -m pytest tests/a3/test_s01_survie.py
Un test « skipped » veut dire que la fonction n'est pas encore écrite.
"""

K, S, G, C, OMEGA = 1000450.59, 0.999106875782, 0.999549614043, 1.103798111448, 116

def l(x):
    """Number of survivors at integer age x, Makeham law: k * s**x * g**(c**x)."""
    raise NotImplementedError

def curtate_life_expectancy(x):
    """e_x = sum of k_p_x for k = 1 .. OMEGA - x."""
    raise NotImplementedError
