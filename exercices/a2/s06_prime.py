"""Module A2, session 6: pure premium, deductible and gross premium. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2/test_s06_prime.py
A "skipped" test means the function is not written yet.
"""

import math

def pure_premium_deductible(freq, sev, d):
    """Pure premium with a deductible d; sev is a dict {amount: probability}."""
    raise NotImplementedError

def exp_excess_mean(theta, d):
    """E[(X - d)+] for an exponential claim with mean theta."""
    raise NotImplementedError

def gross_premium(pure, risk_loading, expense_ratio):
    """Gross premium: pure * (1 + risk_loading) / (1 - expense_ratio)."""
    raise NotImplementedError
