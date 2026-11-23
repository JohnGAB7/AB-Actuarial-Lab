# Audit initial du dépôt — phase 0

> **Statut : audit statique préliminaire, non exhaustif.**  
> Base examinée : `main`, commit `506d107ca7ee97479996e932d44f8034c426dd05`.  
> Date : 2026-11-23.  
> Aucun fichier applicatif ni aucune donnée n'ont été modifiés dans cet audit.

## 1. Synthèse

Le dépôt possède déjà une base cohérente et utile : contenus YAML séparés de l'interface, génération statique Python, exercices à compléter, tests de calcul, site responsive, rendu mathématique, éditeur Python, progression locale et synchronisation Supabase facultative.

La bonne stratégie est de **consolider l'architecture existante**, pas de la remplacer. L'état actuel est celui d'un prototype pédagogique fonctionnel en évolution, et non encore d'une plateforme prête pour une ouverture internationale à grande échelle.

### Périmètre observé

- Instructions et gouvernance : `CLAUDE.md`, `README.md`.
- Architecture : `contenus/parcours.yaml`, `tools/construire.py`, `site/`.
- Exemples de contenu : `contenus/a1/s01.yaml`, `contenus/a3/s01.yaml`, `contenus/a3/s02.yaml`.
- Qualité : `tests/`, workflows GitHub Actions.
- Comptes et données : `site/assets/compte.js`, `docs/SUPABASE.md`, `supabase/migrations/001_progression.sql`.
- Confidentialité : `.gitignore`, `suivi/README.md`, `a-produire/README.md`.

## 2. Constats et priorités

### P0 — Exécution du code apprenant : isolation et disponibilité

**Preuve observée :** `site/assets/seance.js` charge Pyodide dans la page et exécute le code saisi avec `py.runPython(value(), { globals: ns })`. L'exécution se fait dans le fil principal du navigateur, sans limite de temps visible.

**Risques :**
- une boucle infinie ou un calcul non borné peut bloquer l'interface ;
- Pyodide ne doit pas être considéré comme une frontière de sécurité isolant le code du contexte navigateur ;
- le pont JavaScript de Pyodide et le stockage local doivent être traités comme des surfaces sensibles, d'autant que `compte.js` conserve une session Supabase dans le stockage du navigateur.

**Recommandation bloquante avant ouverture publique :**
1. déplacer l'exécution dans un Web Worker dédié ou un contexte isolé équivalent ;
2. ne transmettre à l'environnement d'exécution aucun jeton, session, donnée de compte ou accès au DOM ;
3. imposer un délai maximal, une limite mémoire raisonnable et une procédure d'arrêt ;
4. tester explicitement les boucles infinies, erreurs, imports, tentatives d'accès au navigateur et interruptions ;
5. documenter clairement les limites résiduelles : un bac à sable côté client n'est pas un environnement d'exécution hostile équivalent à un conteneur serveur durci.

Aucun changement d'exécution n'est proposé dans cette PR d'audit : ce chantier doit être conçu et testé isolément.

### P1 — Validation des contenus YAML trop permissive

**Preuve observée :** `verifier_seance()` dans `tools/construire.py` contrôle les types d'étapes, l'index des réponses et une partie des explications de quiz. Il ne vérifie pas encore systématiquement les champs requis de chaque type, l'unicité des identifiants, les références du plan, les chemins d'exercices, les structures de tableaux, les clés de calcul ni les expressions de tests.

**Risque :** un contenu partiellement mal formé peut passer la validation puis provoquer une erreur pendant la génération ou l'affichage.

**Recommandation :**
- définir un schéma explicite par type d'étape ;
- vérifier l'unicité des IDs et la cohérence `parcours.yaml` ↔ fichiers YAML ↔ exercices ;
- contrôler les chemins relatifs et les fichiers référencés ;
- ajouter des tests négatifs avec des contenus volontairement invalides ;
- conserver les contrôles de calcul indépendants déjà présents.

### P1 — Progression et maîtrise ne sont pas encore séparées

**Preuve observée :** `render()` marque automatiquement les étapes de type vidéo et rappel comme terminées lorsqu'elles sont affichées ; les quiz, calculs et exercices de code sont validés par leurs interactions.

**Risque :** le pourcentage de progression peut être interprété comme une mesure de maîtrise alors qu'il combine consultation et réussite de contrôles différents.

**Recommandation :**
- conserver la progression de navigation, utile à l'apprenant ;
- distinguer à terme « consulté », « exercice réussi » et « maîtrise évaluée » ;
- ne jamais transformer automatiquement une visite ou un score ponctuel en compétence acquise ;
- réserver le statut « maîtrisé » à un critère défini, explicite et réévaluable.

### P1 — Couverture de tests centrée sur Python et génération

**Preuve observée :** les tests vérifient des chiffres de séances, des règles de dépôt, quelques règles de configuration Supabase et la présence de RLS. Les workflows exécutent pytest et la génération du site.

**Lacunes à couvrir progressivement :**
- tests du navigateur pour navigation, clavier, mobile et rendu ;
- tests du cycle quiz/calcul/code et de la persistance locale ;
- tests de synchronisation Supabase (fusion, conflits, déconnexion, suppression) ;
- vérification plus forte des politiques RLS, des privilèges et des cas d'accès croisé entre utilisateurs ;
- tests de sécurité et de non-régression pour l'environnement Python.

Le contrôle actuel qui cherche la présence de `ENABLE ROW LEVEL SECURITY` ne prouve pas à lui seul que les politiques et privilèges sont corrects ; la migration doit aussi faire l'objet d'une revue sémantique.

### P2 — Robustesse de l'interface et du contenu riche

**Preuve observée :** plusieurs rendus utilisent `innerHTML` pour afficher les contenus YAML (questions, explications, rappels et solutions).

**Risque :** le contenu pédagogique est actuellement une source maîtrisée par le dépôt, mais une contribution future ou une donnée externe non fiable pourrait introduire du HTML actif.

**Recommandation :**
- documenter les champs autorisés à contenir du HTML ;
- échapper par défaut les champs textuels ;
- limiter le HTML riche à une liste de balises autorisées et le sanitiser à la génération ;
- ajouter des tests avec des chaînes contenant des balises et attributs dangereux.

### P2 — Références scientifiques et statut de validation

**Constat :** les séances existantes citent des ouvrages et des référentiels, et les tests recalculent plusieurs résultats. C'est une bonne base. Toutefois, la présence d'une référence ou le succès d'un test ne vaut pas validation indépendante.

**Recommandation :** ajouter progressivement des métadonnées de traçabilité par ressource : source exacte, édition/date, hypothèses, juridiction, date de vérification et statuts séparés (rédigé, relu mathématiquement, revu actuariellement, testé techniquement, revu pédagogiquement, validé indépendamment, testé auprès d'apprenants). Ne déclarer que les statuts effectivement obtenus.

### P2 — Couverture pédagogique encore limitée

**Constat :** le plan décrit sept domaines et de nombreux modules, mais les séances actuellement référencées dans `parcours.yaml` sont concentrées sur A1 et A3. A2 et plusieurs autres domaines restent à venir.

**Recommandation :** mesurer la couverture réelle par domaine et prérequis, puis avancer par parcours complet. Le parcours Vie et mortalité est un bon pilote car il relie mathématiques financières, probabilités, survie, assurances et programmation. Ne pas ouvrir de nouveaux chantiers avant d'avoir consolidé ce pilote.

## 3. Éléments positifs à préserver

- Séparation nette entre contenu YAML et présentation.
- Génération statique simple, sans dépendance à un framework lourd.
- Exercices de code fournis comme squelettes `NotImplementedError`, conformément à la règle d'apprentissage.
- Tests de chiffres indépendants dans `tests/test_contenus.py`.
- Progression locale utilisable sans compte.
- Compte Supabase facultatif, clé publique seulement côté navigateur, RLS dans la migration et suppression de compte prévue.
- Documentation explicite de la confidentialité des supports de cours et des données personnelles.
- Design « une étape par écran », à préserver.
- Déploiement séparé de la construction sur PR et de la publication après push sur `main`.

## 4. Ordre de travail recommandé

| Ordre | Chantier | Résultat attendu |
|---|---|---|
| 1 | Sécuriser l'exécution Python | Aucun accès du code apprenant à la session/au DOM ; arrêt des exécutions non bornées |
| 2 | Renforcer la validation YAML | Toute incohérence de structure ou de référence échoue avant génération |
| 3 | Séparer progression et maîtrise | Statuts compréhensibles, non trompeurs et traçables |
| 4 | Compléter les tests navigateur et Supabase | Non-régression des parcours réels et des accès aux données |
| 5 | Renforcer traçabilité scientifique | Sources, hypothèses, limites et validation visibles |
| 6 | Consolider le pilote Vie et mortalité | Parcours cohérent, complet et relu avant généralisation |

## 5. Vérifications et limites de cet audit

- Revue statique des fichiers listés dans le périmètre.
- L'état du commit de base ne retournait pas de status checks exploitables via l'API consultée.
- L'environnement de cette session ne pouvait pas joindre `github.com` pour cloner le dépôt ; **pytest et la génération n'ont donc pas été exécutés localement**.
- Aucun test navigateur, test de charge, test d'intrusion ni revue humaine actuarielle indépendante n'a été réalisé.
- Les constats sont des constats de code et de configuration, pas une certification de sécurité ou de conformité.

## 6. Décision proposée

Poursuivre par des PR petites et indépendantes. Le premier chantier technique devrait traiter l'isolation et les limites d'exécution Python, avec tests de sécurité dédiés. En parallèle, renforcer le validateur YAML sans changer le format de contenu existant.

**Aucune migration de base de données, refonte visuelle, modification de contenu pédagogique ni publication n'est justifiée par ce seul audit.**

---
