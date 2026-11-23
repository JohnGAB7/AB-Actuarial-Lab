"""Module A1, séance 1 : intérêt composé et annuités certaines. À toi d'écrire le corps des fonctions.

Lance les tests : python -m pytest tests/a1/test_s01_interet.py
Un test « skipped » veut dire que la fonction n'est pas encore écrite.
"""

def discount_factor(i, t):
    """v**t = (1 + i)**(-t)."""
    raise NotImplementedError

def annuity_immediate(n, i):
    """a_n: n payments of 1, at the end of years 1 .. n."""
    raise NotImplementedError

def annuity_due(n, i):
    """a-double-dot_n: n payments of 1, at the start of years 0 .. n-1."""
    raise NotImplementedError

def present_value(cash_flows, i):
    """Present value of a dict {time: amount}."""
    raise NotImplementedError
