"""Module A2B, session 3: confidence intervals. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2b/test_s03_intervalles.py
A "skipped" test means the function is not written yet.
"""

def mean_ci(xs, q):
    """(low, high) interval for the mean: mean -/+ q * s / sqrt(n), with s the unbiased standard deviation."""
    raise NotImplementedError

def proportion_ci(k, n, z=1.96):
    """(low, high) normal-approximation interval for a proportion with k events out of n."""
    raise NotImplementedError

def sample_size(p, margin, z=1.96):
    """Smallest whole number of policies for which z * sqrt(p * (1 - p) / n) <= margin."""
    raise NotImplementedError
