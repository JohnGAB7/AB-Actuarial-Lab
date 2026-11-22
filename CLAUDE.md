# Règles du dépôt parcours-actuariel

- Dépôt **public**. Les supports de cours de JG sont protégés : ne jamais les committer, ni les citer, ni les paraphraser de près. Les rappels sont rédigés de zéro.
- Supports de cours et CV de JG : **jamais sur un dépôt GitHub**, public ou privé. Ils restent dans la bibliothèque du projet. Règle non négociable.
- Sur ce dépôt, seulement les notes et le code de JG. Aucune donnée personnelle (coordonnées, employeur, projets de vie). Aucun secret, aucun jeton.
- Ossature : modules A1 à A8 du Parcours Actuariat d'Actu-Basics (v3). Les approfondissements au-delà sont marqués « + ».
- Données : fictives ou paramètres publics, avec leur source.
- Rien n'est fusionné ni publié sans l'accord explicite de JG. Tout passe par une branche et une PR.
- Réponses et contenus en français, termes techniques aussi en anglais. Code, docstrings et commits en anglais.
- L'apprentissage passe par JG : les exercices de code restent des squelettes (`raise NotImplementedError`). Ne jamais écrire la solution dans `exercices/`. Le corrigé vit dans `tests/` et sert seulement à vérifier les tests.
- Chaque chiffre d'une séance est recalculé dans `tests/test_contenus.py`.
- Calculs lourds : sur GitHub Actions.
- Design : une étape par écran, pas de page surchargée. Couleurs et polices dans `site/assets/style.css` uniquement.
