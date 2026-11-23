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

Le niveau diffère : la vidéo part de zéro et couvre toute la matière de la séance, la séance va jusqu'au niveau des examens
(forme continue, code, lien avec IAS 19).

## Le gain

- Les chiffres sont recalculés une fois, ici, par `tests/test_contenus.py`, puis repris tels quels dans la fiche.
- Les termes anglais et les phrases B1-B2 servent à la fois à l'édition EN de la vidéo et à ton anglais.
- Préparer une vidéo te fait réviser la séance : expliquer une notion est le meilleur contrôle de compréhension.

## Le circuit, sans rien changer aux règles d'Actu-Basics

1. Les séances du module sont écrites ici, et JG les travaille jusqu'à maîtriser le module.
2. Un fichier `a-produire/<module>.md` est alors déposé (voir `a-produire/README.md`) : notions, exercices corrigés, pièges, vocabulaire anglais, notes pour la vidéo. C'est l'entrée du projet Actu-Basics.
3. Circuit habituel d'Actu-Basics : Claude structure, ChatGPT relit, JG valide, puis le moteur rend la vidéo.
4. La vidéo apparaît dans l'étape 1 de la séance (champ `media`, fichiers MP4 et sous-titres WebVTT dans `site/assets/videos/`). Elle est d'abord servie par le site ; une fois publiée sur YouTube, elle sera remplacée par la vidéo YouTube, pour que les vues y comptent.

Décisions de JG du 23 novembre 2026 : une **vidéo longue 16:9 par séance**, complète (toute la séance, faits réels sourcés, animations), et des **vidéos verticales de moins de 3 minutes**, une par notion, pour réviser. À partir de la deuxième vidéo, un **fil rouge** relie les vidéos : le contrat d'assurance vie de clients fictifs de JG's Holding, construit composante après composante. Les vidéos suivent les parties du site déjà finalisées, en commençant par les fondamentaux.

Un script d'export YAML vers fiche de conception pourra venir quand trois ou quatre séances auront montré que la correspondance est stable.

## Vidéos transmises par Actu-Basics

| Séance | Vidéo | Durée | Fichiers | État |
|---|---|---|---|---|
| a1/s01 | « Intérêt simple, intérêt composé et annuités certaines » / “Simple interest, compound interest and annuities” | FR 14 min 41, EN 15 min | `site/assets/videos/a1-s01-*` (MP4 et sous-titres WebVTT) | validée par JG le 23/11/2026 ; sur le site, à remplacer par YouTube à la publication |

Chapitres (FR) : 0:00 Introduction · 0:55 Taux d'intérêt et intérêt simple · 2:48 Intérêt composé · 4:54 Actualisation · 6:21 Taux d'escompte · 7:46 Taux équivalents · 9:44 Annuités certaines · 12:34 Exercice.
Source de la vidéo : fiche `contenus/fiches/2026-11-act-a1-s01-interet-et-annuites.yaml` du dépôt Actu-Basics (registre `docs/actuariat/videos-seances.yaml`). Les chiffres sont ceux de la séance (taux fictif de 2,5 %) ; les faits réels cités sont sourcés dans la fiche.

En attente côté Actu-Basics : les vidéos verticales de moins de 3 minutes tirées de cette vidéo ; une version corrigée d'un détail visuel de l'animation de l'intérêt composé. Aucune nouvelle vidéo avant que les fondamentaux du site soient finalisés.
