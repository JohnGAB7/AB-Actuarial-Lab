# Une séance, deux usages : le site et la vidéo Actu-Basics

## Le constat

Ce parcours suit les modules A1 à A8 du Parcours Actuariat d'Actu-Basics (v3). Écrire deux fois la même matière serait du travail perdu :
chaque module maîtrisé ici devient une fiche et une vidéo Actu-Basics.

## Le principe

La séance YAML de ce dépôt devient la **matière première** de la fiche de conception Actu-Basics :

| Séance (ce dépôt) | Fiche Actu-Basics (`contenus/conception`, puis `contenus/fiches`) |
|---|---|
| `actu_basics.accroche_fr`, `accroche_en` | scène `accroche` |
| `rappel.blocs` (paragraphes) | scènes `texte` et `etapes`, voix off FR et EN |
| `rappel.blocs` (formules) | scènes `formule` |
| `rappel.blocs` (graphique) | scène `courbe` |
| `calcul` (données, champs, solution) | scènes `exercice` et `correction`, avec leurs `verifier` |
| `vocabulaire` | mots-clés de l'édition EN, légende et hashtags |
| `quiz` | questions des extraits verticaux TikTok et Shorts |

Le niveau diffère : la vidéo vise un débutant, la séance va jusqu'au niveau des examens. La vidéo prend donc le premier tiers de la séance
(intuition, exemple chiffré, exercice simple), et la séance garde la suite (forme continue, code, lien avec IAS 19).

## Le gain

- Les chiffres sont recalculés une fois, ici, par `tests/test_contenus.py`, puis repris tels quels dans la fiche.
- Les termes anglais et les phrases B1-B2 servent à la fois à l'édition EN de la vidéo et à ton anglais.
- Préparer une vidéo te fait réviser la séance : expliquer une notion est le meilleur contrôle de compréhension.

## Le circuit, sans rien changer aux règles d'Actu-Basics

1. La séance est écrite et fusionnée ici, après ton accord.
2. Une proposition de fiche de conception est ouverte dans Actu-Basics, en PR, avec le lien vers la séance.
3. Circuit habituel d'Actu-Basics : Claude structure, ChatGPT relit, JG valide, puis le moteur rend la vidéo.
4. Une fois publiée, la vidéo apparaît dans l'étape 1 de la séance.

Un script d'export YAML vers fiche de conception pourra venir quand trois ou quatre séances auront montré que la correspondance est stable.
