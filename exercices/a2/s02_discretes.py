"""Module A2, session 2: claim counts, binomial and Poisson. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2/test_s02_discretes.py
A "skipped" test means the function is not written yet.
"""

import math

def poisson_pmf(k, lam):
    """P(N = k) for N ~ Poisson(lam)."""
    raise NotImplementedError

def binomial_pmf(k, n, p):
    """P(X = k) for X ~ Binomial(n, p)."""
    raise NotImplementedError

def mean_variance(pmf):
    """(E[X], Var(X)) for a dict {value: probability}."""
    raise NotImplementedError
