"""Module A2, session 4: pooling and the law of large numbers. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2/test_s04_mutualisation.py
A "skipped" test means the function is not written yet.
"""

import math
import random

def sd_of_mean(sigma, n):
    """Standard deviation of the average of n independent costs with standard deviation sigma."""
    raise NotImplementedError

def prob_mean_exceeds(threshold, mu, sigma, n):
    """Normal approximation of P(mean cost > threshold) for n independent policies."""
    raise NotImplementedError

def simulate_mean_cost(n, p, claim, seed=1):
    """Simulate one portfolio of n policies (claim with probability p) and return the average cost."""
    raise NotImplementedError
