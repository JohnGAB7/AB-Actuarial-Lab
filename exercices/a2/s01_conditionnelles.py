"""Module A2, session 1: conditional probability and Bayes' theorem. Write the body of each function yourself.

Run the tests: python -m pytest tests/a2/test_s01_conditionnelles.py
A "skipped" test means the function is not written yet.
"""

def total_probability(priors, likelihoods):
    """P(A) = sum of P(A | B_j) P(B_j); priors and likelihoods are lists of the same length."""
    raise NotImplementedError

def posterior(priors, likelihoods):
    """List of P(B_j | A) by Bayes' theorem."""
    raise NotImplementedError

def prob_at_least_one(p, n):
    """Probability of at least one event among n independent trials of probability p."""
    raise NotImplementedError
