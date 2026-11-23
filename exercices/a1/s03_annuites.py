"""Module A1, session 3: perpetuities and varying annuities. Write the body of each function yourself.

Run the tests: python -m pytest tests/a1/test_s03_annuites.py
A "skipped" test means the function is not written yet.
"""

def accumulated_value(n, i):
    """s_n: value at time n of n payments of 1, at the end of years 1 .. n."""
    raise NotImplementedError

def increasing_annuity(n, i):
    """(Ia)_n: payments 1, 2, ..., n at the end of years 1 .. n."""
    raise NotImplementedError

def decreasing_annuity(n, i):
    """(Da)_n: payments n, n-1, ..., 1 at the end of years 1 .. n."""
    raise NotImplementedError

def geometric_annuity(n, i, g):
    """First payment 1 at time 1, then growing by g a year; n payments in all."""
    raise NotImplementedError
