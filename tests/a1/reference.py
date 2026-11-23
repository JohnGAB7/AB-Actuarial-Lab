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
