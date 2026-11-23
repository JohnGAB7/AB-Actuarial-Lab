# Schéma des contenus YAML

Ce document décrit le schéma actuellement utilisé par le parcours. Le validateur Python est l'implémentation exécutable de référence : toute extension de contenu doit mettre à jour ce document, le validateur et ses tests dans le même changement.

## Plan — `contenus/parcours.yaml`

- Racine : `titre`, `sous_titre`, `sous_titre_en`, `domaines` (les trois textes sont requis pour le site bilingue).
- Domaine : `id`, `titre`, `en`, `accroche`, `accroche_en`, `modules` (tous les textes sont requis pour le site bilingue).
- Identifiants de domaines et de modules : segments de chemin de 1 à 40 caractères, minuscules ASCII, chiffres et tirets ; ils ne peuvent contenir ni slash, ni point, ni attribut HTML.
- Module : `id`, `titre`, `en`, `seances` (facultatif ; liste de références `domaine/seance`).

## Séance — `contenus/<id>.yaml`

Champs de premier niveau :
- Obligatoires : `id`, `module`, `titre`, `en`, `duree`, `etapes`.
- Facultatifs : `taux`, `table`, `actu_basics`.

Structures facultatives :
- `table` : `nom`, `k`, `s`, `g`, `c`, `omega`.
- `actu_basics` : `episode`, `statut`, `accroche_fr`, `accroche_en`.

Chaque étape possède les champs communs `type`, `titre`, `minutes`, puis les champs propres à son type :

| Type | Champs spécifiques |
| --- | --- |
| `video` | `texte` |
| `rappel` | `blocs` |
| `quiz` | `intro`, `questions` |
| `calcul` | `intro`, `donnees`, `champs`, `solution` |
| `code` | `intro`, `fichier`, `depart`, `tests` |
| `vocabulaire` | `intro`, `cartes` |

Structures imbriquées :
- Bloc de rappel : un ou plusieurs de `p`, `formule`, `note`, `interactif`, `sources`.
- Source : `titre`, `detail`, `url` (facultatif).
- Question de quiz : `q`, `options`, `reponse`, `pourquoi`.
- Explication : `rappel`, `formule`, `exemple`, `piege` (facultatif).
- Données de calcul : `entetes`, `lignes`.
- Champ de résultat : `cle`, `libelle`, `valeur`, `tolerance`.
- Test de code : `nom`, `expr`.
- Carte de vocabulaire : liste de trois textes (terme français, équivalent anglais, phrase d'exemple).

Les clés non listées sont refusées par le validateur. Les champs optionnels restent optionnels ; une clé inconnue n'est pas assimilée à un champ optionnel.

## Contrat des overlays anglais

Les overlays sont proposés sous `contenus/en/<id>.yaml`. Les trois exemples examinés dans la PR bilingue #13 sont `a1/s01`, `a3/s01` et `a3/s02`. Ils sont actuellement dans la branche de cette PR, pas dans `main`.

Contrat observé et à conserver :
- l'overlay est un sous-ensemble de l'arbre français correspondant ; il ne crée aucune clé ;
- les listes gardent la même longueur et le même ordre ;
- les types YAML sont conservés ;
- les textes traduits ne peuvent pas être vides lorsqu'un texte français existe ;
- les nombres présents dans les textes sont comparés après normalisation des conventions FR/EN, avec signe, exposant et unité (`%`, `‰`) ;
- les formules peuvent changer uniquement leurs libellés `\\text{...}` ; leur structure mathématique reste identique ;
- les réponses de quiz, valeurs/tolérances, identifiants, tests exécutables, chemins d'exercice et paramètres actuariels restent dans le fichier français ;
- les cellules de `donnees.lignes` peuvent adapter le séparateur décimal ou de milliers, sans changer les valeurs.

Implémentation canonique :
- les champs de métadonnées `en` et `actu_basics` sont explicitement protégés contre toute surcharge ;
- `fusionner_overlay()` est l'unique fonction de fusion et de contrôle structurel des overlays ;
- `verifier_overlay_traduction()` contrôle aussi la complétude des textes traduisibles ;
- `verifier_depot()` active le contrôle bilingue lorsque le dossier `contenus/en/` existe et exige alors un overlay pour chaque séance référencée ;
- le générateur et son mode `--verifier` utilisent tous deux `verifier_depot()`. Le générateur bilingue réutilise `fusionner_overlay()` pour construire les séances anglaises ;
- les tests couvrent les clés ajoutées, les métadonnées protégées, les types, longueurs de listes, textes vides ou manquants, nombres, signes, exposants, unités et structure des formules.

## État et limites de l'inventaire

Inventaire réalisé sur les trois séances actuellement référencées par le plan de `main` et sur les trois overlays de la branche PR #13. Les futurs types de contenu ou champs métier devront être ajoutés explicitement avec leurs tests. Cet inventaire ne constitue pas une validation pédagogique ou actuarielle indépendante.
