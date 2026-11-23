"""Module A2B, session 4: goodness-of-fit tests. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2b/test_s04_adequation.py
A "skipped" test means the function is not written yet.
"""

def poisson_expected(n, lam, kmax):
    """Expected counts for 0, 1, ..., kmax - 1 claims, then one last group for kmax claims or more."""
    raise NotImplementedError

def chi_square(observed, expected):
    """Chi-square statistic: sum of (O - E)**2 / E."""
    raise NotImplementedError

def ks_statistic(xs, cdf):
    """Kolmogorov-Smirnov distance between the empirical distribution of xs and the function cdf."""
    raise NotImplementedError
