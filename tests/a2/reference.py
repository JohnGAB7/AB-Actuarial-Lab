"""Independent solutions, used only to check that the tests and contents are right.
Do not open before doing the exercise."""


# Session a2/s01
def total_probability(priors, likelihoods):
    return sum(p * l for p, l in zip(priors, likelihoods))


def posterior(priors, likelihoods):
    total = total_probability(priors, likelihoods)
    return [p * l / total for p, l in zip(priors, likelihoods)]


def prob_at_least_one(p, n):
    return 1 - (1 - p) ** n


# Session a2/s02
def poisson_pmf(k, lam):
    import math
    return math.exp(-lam) * lam**k / math.factorial(k)


def binomial_pmf(k, n, p):
    import math
    return math.comb(n, k) * p**k * (1 - p) ** (n - k)


def mean_variance(pmf):
    m = sum(x * q for x, q in pmf.items())
    return m, sum(x * x * q for x, q in pmf.items()) - m * m
