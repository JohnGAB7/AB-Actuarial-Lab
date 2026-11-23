# Actuarial Learning Lab by ACTU-BASICS

Version française : **Laboratoire d’apprentissage actuariel par ACTU-BASICS**.

Un espace bilingue pour explorer l’actuariat par des explications, des expériences interactives, des calculs guidés et des laboratoires de modélisation. La plateforme reprend les logos officiels ACTU-BASICS sans les redessiner ni les modifier.

Parcours personnel de remise à niveau en actuariat : diagnostic, plan, notes, exercices et suivi de progression.
L'ossature suit les modules A1 à A8 du « Parcours Actuariat » d'Actu-Basics (`docs/actuariat/PARCOURS-ACTUARIAT-v3.md`) ;
chaque module maîtrisé devient ensuite une fiche et une vidéo Actu-Basics.
Chaque séance dure environ 25 minutes et s'affiche **une étape à la fois** :

1. **Vidéo** : l'intuition, avec l'épisode Actu-Basics du thème quand il existe.
2. **Rappel** : la théorie essentielle, rédigée pour ce site.
3. **Vérifie** : quelques questions de compréhension.
4. **À la main** : un calcul guidé, vérifié à la saisie.
5. **À toi de coder** : une fonction Python à écrire soi-même, testée dans le navigateur (Pyodide) et sur GitHub Actions.
6. **Vocabulary** : les termes anglais, avec une phrase d'entretien.

## Organisation

| Dossier | Rôle |
|---|---|
| `contenus/` | Une séance = un fichier YAML (texte, questions, calculs, tests, vocabulaire). `parcours.yaml` donne le plan. |
| `site/` | Gabarits HTML, style et script. Aucun contenu pédagogique ici. |
| `tools/construire.py` | Construit `_site/` à partir des contenus. |
| `exercices/` | Squelettes de code à compléter par JG. |
| `tests/` | Tests des exercices, corrigé de contrôle et vérification des chiffres des séances. |
| `a-produire/` | Un fichier par module maîtrisé : la matière que le projet Actu-Basics transforme en fiche et en vidéo. |
| `suivi/` | Diagnostic, plan, notes et progression : seulement mes notes, jamais de support de cours ni de CV. |
| `docs/ACTU-BASICS.md` | Comment une séance alimente aussi une vidéo Actu-Basics. |

## Utiliser

```bash
python -m pip install -r requirements.txt
python -m pytest                      # « skipped » : exercice pas encore écrit
python tools/construire.py            # site dans _site/, à ouvrir dans un navigateur
```

Publication : GitHub Pages, après fusion sur `main` (workflow `site`). À activer une fois dans Settings > Pages > Source = « GitHub Actions ».

## Règles

Voir [`CLAUDE.md`](CLAUDE.md). En bref : dépôt public, aucun support de cours, aucun CV ni donnée personnelle, aucun secret, rien de fusionné sans accord de JG.
