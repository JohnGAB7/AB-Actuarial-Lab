"""Module A1, session 5: bonds and the yield curve. Write the body of each function yourself.

Run the tests: python -m pytest tests/a1/test_s05_obligations.py
A "skipped" test means the function is not written yet.
"""

def bond_price(face, coupon_rate, n, y):
    """Price of a bond paying coupon_rate * face at the end of years 1 .. n, then face, at yield y."""
    raise NotImplementedError

def price_from_spot(cash_flows, spot):
    """Price of {time: amount} using spot rates: spot[t - 1] is the rate for time t."""
    raise NotImplementedError

def forward_rates(spot):
    """One-year forward rates [f(0,1), f(1,2), ...] implied by the spot rates."""
    raise NotImplementedError
