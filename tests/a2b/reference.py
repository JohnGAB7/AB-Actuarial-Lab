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


# Session a2b/s03
def mean_ci(xs, q):
    m, s2 = sample_mean_var(xs)
    half = q * math.sqrt(s2 / len(xs))
    return m - half, m + half


def proportion_ci(k, n, z=1.96):
    p = k / n
    half = z * math.sqrt(p * (1 - p) / n)
    return p - half, p + half


def sample_size(p, margin, z=1.96):
    return math.ceil(z * z * p * (1 - p) / margin**2)


# Session a2b/s04
def poisson_expected(n, lam, kmax):
    probs = [math.exp(-lam) * lam**k / math.factorial(k) for k in range(kmax)]
    return [n * p for p in probs] + [n * (1 - sum(probs))]


def chi_square(observed, expected):
    return sum((o - e) ** 2 / e for o, e in zip(observed, expected))


def ks_statistic(xs, cdf):
    xs = sorted(xs)
    n = len(xs)
    return max(max((i + 1) / n - cdf(x), cdf(x) - i / n) for i, x in enumerate(xs))
