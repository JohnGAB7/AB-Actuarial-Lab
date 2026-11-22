"""Corrigé indépendant, utilisé seulement pour vérifier que les tests et les contenus sont justes.
Ne pas l'ouvrir avant d'avoir fait l'exercice."""
K, S, G, C, OMEGA = 1000450.59, 0.999106875782, 0.999549614043, 1.103798111448, 116


def l(x):
    return K * S**x * G ** (C**x)


def curtate_life_expectancy(x):
    return sum(l(x + k) for k in range(1, OMEGA - x + 1)) / l(x)
