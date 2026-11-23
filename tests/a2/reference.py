"""Independent solutions, used only to check that the tests and contents are right.
Do not open before doing the exercise."""
import math


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


# Session a2/s03
def normal_cdf(z):
    import math
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def exp_quantile(p, theta):
    import math
    return -theta * math.log(1 - p)


def lognormal_survival(x, mu, sigma):
    import math
    return 1 - normal_cdf((math.log(x) - mu) / sigma)


def pareto_survival(x, alpha, theta):
    return (theta / (theta + x)) ** alpha
