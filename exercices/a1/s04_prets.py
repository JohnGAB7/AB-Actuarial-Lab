"""Module A1, session 4: loans, amortization and yield rates. Write the body of each function yourself.

Run the tests: python -m pytest tests/a1/test_s04_prets.py
A "skipped" test means the function is not written yet.
"""

def level_payment(loan, n, i):
    """Level payment at the end of each year that repays the loan in n years at rate i."""
    raise NotImplementedError

def amortization_schedule(loan, n, i):
    """List of n tuples (year, interest, principal repaid, balance after payment)."""
    raise NotImplementedError

def irr(cash_flows, low=-0.99, high=1.0, tol=1e-10):
    """Rate j that makes the NPV of {time: amount} zero, by bisection on [low, high]."""
    raise NotImplementedError
