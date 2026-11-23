"""Module A1, session 2: nominal rates and monthly payments. Write the body of each function yourself.

Run the tests: python -m pytest tests/a1/test_s02_taux.py
A "skipped" test means the function is not written yet.
"""

def nominal_rate(i, m):
    """i^(m): the nominal rate convertible m times a year, equivalent to the effective rate i."""
    raise NotImplementedError

def effective_rate(i_m, m):
    """The annual effective rate equivalent to the nominal rate i_m convertible m times a year."""
    raise NotImplementedError

def annuity_mthly(n, i, m, due=False):
    """Present value of 1 a year for n years, paid in m instalments of 1/m (in arrears, or in advance if due)."""
    raise NotImplementedError
