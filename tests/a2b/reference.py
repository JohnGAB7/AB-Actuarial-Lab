"""Independent solutions, used only to check that the tests and contents are right.
Do not open before doing the exercise."""
import math


# Session a2b/s01
def sample_mean_var(xs):
    n = len(xs)
    m = sum(xs) / n
    return m, sum((x - m) ** 2 for x in xs) / (n - 1)


def standard_error(xs):
    return math.sqrt(sample_mean_var(xs)[1] / len(xs))


def gamma_moments(xs):
    n = len(xs)
    m, s2 = sample_mean_var(xs)
    var_n = s2 * (n - 1) / n
    return m * m / var_n, var_n / m


# Session a2b/s02
def poisson_mle(counts):
    return sum(counts) / len(counts)


def exponential_loglik(xs, theta):
    return -len(xs) * math.log(theta) - sum(xs) / theta


def pareto_alpha_mle(xs, theta):
    return len(xs) / sum(math.log(1 + x / theta) for x in xs)
