"""Module A2, session 5: frequency, severity and aggregate loss. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2/test_s05_charge.py
A "skipped" test means the function is not written yet.
"""

def aggregate_mean_var(mean_n, var_n, mean_x, var_x):
    """(E[S], Var(S)) for S = X_1 + ... + X_N in the collective risk model."""
    raise NotImplementedError

def compound_poisson_var(lam, second_moment_x):
    """Var(S) when N ~ Poisson(lam): lam * E[X**2]."""
    raise NotImplementedError

def aggregate_pmf(freq, sev):
    """Exact distribution of S by convolution; freq and sev are dicts {value: probability}."""
    raise NotImplementedError
