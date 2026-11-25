# Schéma des contenus YAML

Ce document décrit le schéma actuellement utilisé par le parcours. Le validateur Python est l'implémentation exécutable de référence : toute extension de contenu doit mettre à jour ce document, le validateur et ses tests dans le même changement.

## Plan — `contenus/parcours.yaml`

- Racine : `titre`, `sous_titre`, `sous_titre_en`, `domaines` (les trois textes sont requis pour le site bilingue).
- Domaine : `id`, `titre`, `en`, `accroche`, `accroche_en`, `modules` (tous les textes sont requis pour le site bilingue).
- Identifiants de domaines et de modules : segments de chemin de 1 à 40 caractères, minuscules ASCII, chiffres et tirets ; ils ne peuvent contenir ni slash, ni point, ni attribut HTML. Les identifiants de séance suivent `domaine/sNN` (domaine de 2 à 20 caractères, suffixe `s` et deux chiffres), conformément au format consommé par le client et la table de progression.
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
| `video` | `texte`, `media` (facultatif) |
| `rappel` | `blocs` |
| `quiz` | `intro`, `questions` |
| `calcul` | `intro`, `donnees`, `champs`, `solution` |
| `code` | `intro`, `fichier`, `depart`, `tests` |
| `vocabulaire` | `intro`, `cartes` |

Structures imbriquées :
- Média d'une vidéo : `media.fr` et `media.en`, chacun `src` (`videos/<nom>.mp4`) et `sous_titres` (facultatif, `videos/<nom>.vtt`), chemins relatifs à `site/assets/`. Les fichiers doivent exister. Sans `media`, le site affiche « Vidéo en préparation ».
- Bloc de rappel : un ou plusieurs de `p`, `formule`, `note`, `interactif`, `sources`.
- Source : `titre`, `detail`, `url` (facultatif).
- Question de quiz : `q`, `options`, `reponse`, `pourquoi`.
- Explication : `rappel`, `formule`, `exemple`, `piege` (facultatif).
- Données de calcul : `entetes`, `lignes`.
- Champ de résultat : `cle`, `libelle`, `valeur`, `tolerance`.
- Test de code : `nom`, `expr`.
- Carte de vocabulaire : liste de trois textes (terme français, équivalent anglais, phrase d'exemple).

Les clés non listées sont refusées par le validateur. Les champs optionnels restent optionnels ; une clé inconnue n'est pas assimilée à un champ optionnel.

## Fiche de référence autonome — champ facultatif fiche

Une séance peut porter une fiche de référence indépendante de la séquence pédagogique historique etapes. Le champ reste facultatif pendant la migration progressive.

- fiche.statut est requis et vaut brouillon ou prete.
- Une fiche brouillon peut ne contenir que les onglets réellement commencés. Les sections présentes doivent néanmoins respecter leur structure.
- Une fiche prete doit contenir les sept sections ci-dessous, chacune avec un contenu substantiel et des listes non vides. Le statut est éditorial : le validateur vérifie la structure, pas la vérité scientifique ni la qualité pédagogique.
- Les clés de contenu sont strictement contrôlées. Les formules conservent leur structure mathématique dans l'overlay anglais ; seuls leurs libellés \text{...} peuvent être traduits. Les outils, niveaux, références internes, années et termes bilingues du glossaire sont des valeurs protégées.

| Section | Structure attendue |
| --- | --- |
| vue_ensemble | question, pourquoi, objectifs[], prerequis[], carte[], duree_minutes |
| cours_complet | sections[] avec titre, contenu, et éventuellement formules[] (formule, explication) |
| methodes | methodes[] avec titre, quand_utiliser, etapes[], controles[], erreurs[] |
| exemples_guides | exemples[] avec titre, enonce, raisonnement[], resultat, interpretation, controles[] |
| exercices_corriges | exercices[] avec titre, niveau, enonce, corrige[], feedback |
| applications_labs | applications[] avec contexte, objectif, outils, entrées, hypothèses, procédure, sorties, validation et limites |
| synthese_references | memo[], glossaire[] (terme_fr, terme_en, definition), maitrise[], references[] annotées et liens[] internes facultatifs |

Les niveaux d'exercice sont fondamental, intermediaire ou avance. Les outils reconnus sont excel, vba, python, r et sans-code. Une référence interne doit respecter le format domaine/sNN, éventuellement suivi d'une ancre. À ce stade, le validateur contrôle la forme et la sûreté du chemin ; il ne certifie pas encore l'existence de la cible.

Le modèle est conçu pour une migration séance par séance. Il ne modifie ni les étapes existantes, ni leur progression, ni le rendu actuel. Les onglets de l'interface seront introduits dans un lot ultérieur après stabilisation du contrat de contenu.

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


## Prototype éditorial A1/S02

La séance A1/S02 (« Taux nominaux et paiements mensuels ») est le second prototype de migration progressive. Sa fiche couvre les conventions nominal/effectif, les conversions d'intérêt et d'escompte, la limite continue, les annuités fractionnées et la dérivation par somme géométrique. Elle contient méthodes, exemples, exercices corrigés et laboratoire Excel/Python. La parité FR/EN est contrôlée par le validateur d'overlay ; les tests de contenu vérifient les sept onglets, le code reproductible et la structure. Comme pour A1/S01, le statut `prete` est structurel et ne remplace pas une revue actuarielle indépendante ou un test auprès d'apprenants.
