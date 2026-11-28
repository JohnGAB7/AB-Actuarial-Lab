"""Corrigé indépendant, utilisé seulement pour vérifier que les tests et les contenus sont justes.
Ne pas l'ouvrir avant d'avoir fait l'exercice."""


def discount_factor(i, t):
    return (1 + i) ** -t


def annuity_immediate(n, i):
    return sum(discount_factor(i, k) for k in range(1, n + 1))


def annuity_due(n, i):
    return sum(discount_factor(i, k) for k in range(n))


def present_value(cash_flows, i):
    return sum(c * discount_factor(i, t) for t, c in cash_flows.items())


# Session a1/s02
def nominal_rate(i, m):
    return m * ((1 + i) ** (1 / m) - 1)


def effective_rate(i_m, m):
    return (1 + i_m / m) ** m - 1


def annuity_mthly(n, i, m, due=False):
    v = 1 / (1 + i)
    times = [(k + (0 if due else 1)) / m for k in range(n * m)]
    return sum(v**t for t in times) / m


# Session a1/s03
def accumulated_value(n, i):
    return sum((1 + i) ** k for k in range(n))


def increasing_annuity(n, i):
    return sum(k * (1 + i) ** -k for k in range(1, n + 1))


def decreasing_annuity(n, i):
    return sum((n + 1 - k) * (1 + i) ** -k for k in range(1, n + 1))


def geometric_annuity(n, i, g):
    return sum((1 + g) ** (k - 1) * (1 + i) ** -k for k in range(1, n + 1))


# Session a1/s04
def level_payment(loan, n, i):
    if i == 0:
        return loan / n
    return loan * i / (1 - (1 + i) ** -n)


def amortization_schedule(loan, n, i):
    p, balance, rows = level_payment(loan, n, i), loan, []
    for year in range(1, n + 1):
        interest = i * balance
        balance -= p - interest
        rows.append((year, interest, p - interest, balance))
    return rows


def irr(cash_flows, low=-0.99, high=1.0, tol=1e-10):
    npv = lambda j: sum(c * (1 + j) ** -t for t, c in cash_flows.items())
    f_low = npv(low)
    while high - low > tol:
        mid = (low + high) / 2
        if (npv(mid) > 0) == (f_low > 0):
            low, f_low = mid, npv(mid)
        else:
            high = mid
    return (low + high) / 2


# Session a1/s05
def bond_price(face, coupon_rate, n, y):
    return sum(coupon_rate * face * (1 + y) ** -t for t in range(1, n + 1)) + face * (1 + y) ** -n


def price_from_spot(cash_flows, spot):
    return sum(c * (1 + spot[t - 1]) ** -t for t, c in cash_flows.items())


def forward_rates(spot):
    acc = [1.0] + [(1 + s) ** (t + 1) for t, s in enumerate(spot)]
    return [acc[t + 1] / acc[t] - 1 for t in range(len(spot))]
