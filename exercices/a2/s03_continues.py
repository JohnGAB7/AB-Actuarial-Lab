"""Module A2, session 3: claim size, continuous distributions. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2/test_s03_continues.py
A "skipped" test means the function is not written yet.
"""

import math

def normal_cdf(z):
    """Phi(z), the standard normal distribution function (use math.erf)."""
    raise NotImplementedError

def exp_quantile(p, theta):
    """Quantile of order p of an exponential distribution with mean theta."""
    raise NotImplementedError

def lognormal_survival(x, mu, sigma):
    """P(X > x) when ln X ~ Normal(mu, sigma**2)."""
    raise NotImplementedError

def pareto_survival(x, alpha, theta):
    """P(X > x) for a Pareto (Lomax) distribution: (theta / (theta + x)) ** alpha."""
    raise NotImplementedError
