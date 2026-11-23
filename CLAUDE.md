# Règles du dépôt AB-Actuarial-Lab

- Dépôt **public**. Les supports de cours de JG sont protégés : ne jamais les committer, ni les citer, ni les paraphraser de près. Les rappels sont rédigés de zéro.
- Supports de cours et CV de JG : **jamais sur un dépôt GitHub**, public ou privé. Ils restent dans la bibliothèque du projet. Règle non négociable.
- Sur ce dépôt, seulement les notes et le code de JG. Aucune donnée personnelle (coordonnées, employeur, projets de vie). Aucun secret, aucun jeton.
- Ossature : modules A1 à A8 du Parcours Actuariat d'Actu-Basics (v3), rangés en domaines (Fondamentaux, Vie, Retraite, Non-vie, ALM, Risque, Outils) dans `contenus/parcours.yaml`. Les approfondissements au-delà sont marqués « + ».
- Quand un module est maîtrisé par JG, déposer `a-produire/<module>.md` (notions, exercices corrigés, pièges, vocabulaire anglais, pour la vidéo) à partir de `a-produire/_modele.md`. Actu-Basics s'en sert pour la fiche et la vidéo.
- Données : fictives ou paramètres publics, avec leur source.
- Tout passe par une branche et une PR. Deux agents travaillent sur ce dépôt, Claude et ChatGPT, avec le même rôle (JG, 23 novembre 2026) :
  - chacun relit les PR de l'autre et prévient JG de toute amélioration ou de tout changement qui ne cadre pas ;
  - corrections et nouvelles séances : fusionnées après relecture croisée et tests verts ;
  - vision, structure du site, comptes et tout ce qui touche aux données : seulement avec le « oui » explicite de JG.
- Site bilingue : français à la racine, anglais sous `en/`, comme Actu-Basics.
- Réponses et contenus en français, termes techniques aussi en anglais. Code, docstrings et commits en anglais.
- L'apprentissage passe par JG : les exercices de code restent des squelettes (`raise NotImplementedError`). Ne jamais écrire la solution dans `exercices/`. Le corrigé vit dans `tests/` et sert seulement à vérifier les tests.
- Chaque chiffre d'une séance est recalculé dans `tests/test_contenus.py`.
- Calculs lourds : sur GitHub Actions.
- Design : une étape par écran, pas de page surchargée. Couleurs et polices dans `site/assets/style.css` uniquement.
- Comptes (Supabase) : seule la clé publique `sb_publishable_…` atteint le navigateur, via les variables Actions `SUPABASE_URL` et `SUPABASE_PUBLISHABLE_KEY`. Jamais de clé secrète ni `service_role`. Toute table a la RLS. Voir `docs/SUPABASE.md`.
