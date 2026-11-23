# Gouvernance de la contribution multi-agents et feuille de route

- **Date :** 23 novembre 2026
- **Projet :** Parcours Actuariel — Actuarial Learning Lab
- **Dépôt :** `JohnGAB7/parcours-actuariel`
- **Statut :** proposition opérationnelle soumise à revue croisée ; ne modifie pas les règles de fusion ou de publication sans décision du propriétaire du projet.

## 1. Principes de collaboration

ChatGPT et Claude sont deux contributeurs techniques autonomes. Ils peuvent chacun analyser, proposer, implémenter, tester, documenter et ouvrir des pull requests. Aucun agent n'a besoin d'une approbation préalable de l'autre pour réaliser une correction ciblée dans son périmètre.

1. **Responsabilité claire :** chaque PR et chaque chantier a un responsable principal identifiable.
2. **Revue croisée :** l'autre agent examine le résultat, notamment les risques, régressions, tests et cohérence architecturale.
3. **Droit de correction :** l'auteur traite les remarques pertinentes ; il peut expliquer pourquoi une suggestion ne convient pas, avec des éléments vérifiables.
4. **Désaccord transparent :** aucun désaccord technique significatif ne doit être masqué ou résolu par une modification silencieuse de la portée. Les options, conséquences et recommandations sont présentées au propriétaire du projet.
5. **Traçabilité :** le code, les tests et les changements techniques restent dans GitHub ; Notion conserve les décisions, arbitrages et la continuité.

## 2. Répartition des responsabilités

### Propriétaire du projet

- Définit les objectifs, les priorités et le niveau de risque acceptable.
- Arbitre les désaccords non résolus et les changements de direction.
- Autorise explicitement les fusions vers `main`, les publications sensibles, les migrations risquées et les changements ayant un impact majeur sur les utilisateurs ou les données.
- N'a pas à valider chaque détail d'implémentation ni chaque correction locale réversible.

### ChatGPT — responsable technique plateforme et qualité

- Prend en charge l'audit technique, la sécurité du runtime, la validation des contenus, la sécurité du rendu, les tests automatisés et la qualité des mécanismes de progression.
- Implémente directement les corrections proportionnées dans des branches dédiées.
- Examine les PR de Claude et vérifie les preuves de tests, les dépendances de branches et les conséquences sur la production.
- Documente les limites et évite de présenter un test automatisé comme une certification de sécurité ou de qualité pédagogique.

### Claude — responsable de contribution curriculum et expérience bilingue

- Poursuit les chantiers qu'il a initiés, notamment le Worker Python, les tests RLS et le site bilingue, jusqu'à leur stabilisation.
- Prend en charge la cohérence du parcours pédagogique, la couverture des compétences, les contenus bilingues, les références et les validations éditoriales/scientifiques.
- Peut également implémenter des changements techniques lorsqu'il en est responsable ou qu'un besoin est identifié.
- Examine les PR de ChatGPT et signale les risques ou incompatibilités avec l'architecture.

### Responsabilité partagée

- Les deux agents peuvent proposer des améliorations dans tous les domaines.
- Un responsable principal est désigné pour éviter les modifications simultanées des mêmes fichiers.
- La revue de l'auteur ne remplace jamais la revue indépendante.
- Une revue `COMMENTED` n'est pas une approbation formelle ; les réserves doivent être traitées ou explicitement acceptées.

## 3. État des PR au 23 novembre 2026

| PR | Responsable principal | Sujet | État / dépendance |
|---|---|---|---|
| #11 | Claude | Exécution Python dans un Web Worker | Ouverte ; cible `main` |
| #12 | Claude | Tests RLS PostgreSQL dans GitHub Actions | Ouverte ; cible `main` ; indépendante |
| #13 | Claude | Site bilingue FR/EN | Ouverte ; cible la branche de #11 ; dépend de #11 |
| #14 | ChatGPT | Validation stricte des contenus YAML | Fusionnée dans `main` |
| #15 | ChatGPT | Modèle de menace Python | Fusionnée dans `main` |
| #16 | ChatGPT | Protection des signes, exposants, unités et identifiants numériques traduits | Fusionnée dans la branche de #13 |

Au dernier contrôle, les workflows `tests` et `site` étaient verts sur les derniers commits de #11, #12 et #13. Cela ne vaut ni approbation indépendante finale ni autorisation de fusion. La branche de #13 dépend de #11 ; conserver cet ordre et vérifier à nouveau les statuts, les bases et les checks avant toute fusion.

Les fusions précédentes vers `main` ont déclenché automatiquement le workflow GitHub Pages. Toute fusion future vers `main` doit donc être considérée comme susceptible de publier le site.

## 4. Feuille de route et attribution des prochains chantiers

Les priorités prolongent l'audit initial. Elles doivent être menées par étapes, sans lancer plusieurs refontes concurrentes.

### Étape 0 — Stabiliser les PR déjà ouvertes

**Responsable : Claude. Revue : ChatGPT.**

- #11 : finaliser la revue du Worker, ses tests navigateur et la description honnête de ses limites.
- #12 : confirmer la couverture RLS, les tentatives anonymes d'écriture, les contrôles de propriété et la suppression en cascade.
- #13 : finaliser le contrôle des traductions, des formules, des valeurs numériques, de la navigation et des pages bilingues ; conserver sa dépendance à #11.
- ChatGPT effectue une revue de suivi sur les changements finaux et signale les réserves restantes.

**Critère de sortie :** chaque PR a un périmètre clair, une CI verte sur son dernier commit, aucune remarque bloquante non traitée et une dépendance de branche cohérente. La décision de fusion reste au propriétaire du projet.

### Étape 1 — Sécurité et robustesse de l'exécution Python (P0)

**Responsable : ChatGPT. Revue : Claude.**

Après stabilisation de #11, conduire un audit ciblé du Worker réel et compléter les tests sur :

- accès au réseau (`fetch`, WebSocket, imports distants) et au stockage (IndexedDB) ;
- imports Python et capacités du pont JavaScript Pyodide ;
- validation et taille des messages, taille du code et des sorties, nombre de tests ;
- timeout, arrêt, redémarrage, navigation pendant l'exécution et erreurs de chargement ;
- isolation des tests et limites de fiabilité des résultats côté client ;
- comportement sur les navigateurs effectivement supportés.

Le Worker réduit l'accès direct au DOM et au stockage de la page et protège le fil principal, mais ne doit pas être décrit comme une sandbox complète. Si le produit doit exécuter du code fourni par des tiers ou partagé entre apprenants, réévaluer une iframe sandboxée à origine opaque ou une origine dédiée. Ne pas ajouter de backend d'exécution distante sans besoin produit et analyse opérationnelle.

**Critère de sortie :** modèle de menace actualisé, tests adversariaux reproductibles, limites résiduelles documentées et décision explicite sur le niveau de menace couvert.

### Étape 2 — Compléter l'intégration du validateur YAML (P1)

**Responsable : ChatGPT. Revue : Claude.**

Traiter les améliorations non bloquantes relevées lors de la revue de #14 :

- faire du validateur une source unique appelée par les tests et par la génération/commande de construction ;
- détecter les clés inconnues et les champs incohérents par type d'étape ;
- contrôler les références au plan, les overlays anglais et les relations entre modules/séances ;
- prévoir les types de contenu futurs sans relâcher la validation des types existants.

Ajouter des tests négatifs et vérifier que les contenus actuels restent compatibles. Éviter de changer le format YAML sans nécessité démontrée.

**Critère de sortie :** une commande de validation reproductible dans le flux de construction, des erreurs explicites et des tests couvrant les cas invalides.

### Étape 3 — Sécurité du rendu des contenus (P1/P2)

**Responsable : ChatGPT. Revue : Claude.**

Auditer les usages de `innerHTML` et les champs issus du YAML. Échapper le texte par défaut, limiter le HTML riche à une liste blanche et ajouter des tests d'entrées hostiles. Préserver le rendu mathématique et les contenus pédagogiques légitimes.

**Critère de sortie :** les chemins de rendu sont inventoriés, les champs actifs contrôlés et les cas d'injection couverts par des tests.

### Étape 4 — Progression, maîtrise et synchronisation (P1)

**Conception du modèle : Claude. Implémentation et tests : ChatGPT. Revue croisée : réciproque.**

- Distinguer étape consultée, exercice réussi et compétence maîtrisée.
- Définir des critères de maîtrise explicites et réévaluables ; ne pas déduire la maîtrise d'une simple consultation.
- Vérifier la persistance locale sans compte, la synchronisation facultative, les conflits, la déconnexion et la reprise.
- Vérifier les règles RLS et les scénarios multi-utilisateurs.

**Critère de sortie :** états de progression compréhensibles, modèle documenté, tests navigateur et tests de synchronisation couvrant les scénarios principaux.

### Étape 5 — Qualité scientifique et couverture du curriculum (P2)

**Responsable : Claude. Appui technique : ChatGPT.**

- Cartographier les compétences, prérequis et dépendances du cursus.
- Consolider un parcours pilote cohérent, notamment Vie et mortalité.
- Associer aux notions les sources, éditions, dates, hypothèses, juridictions et limites.
- Distinguer clairement les statuts : rédigé, vérifié mathématiquement, revu actuariellement, testé techniquement, revu pédagogiquement, validé indépendamment et testé auprès d'apprenants.
- Ne pas revendiquer de revue indépendante ou de test apprenant sans preuve correspondante.

**Critère de sortie :** couverture et lacunes documentées, références traçables, statut de validation honnête et plan de revue humaine.

### Étape 6 — Validation auprès d'apprenants

**Responsable : Claude pour le protocole pédagogique ; ChatGPT pour les outils de collecte/analyse ; propriétaire pour le recrutement et les arbitrages.**

Définir un petit protocole de test : tâches, profils visés, critères d'observation, difficultés, retours et limites de l'échantillon. Les résultats ne doivent pas être présentés comme représentatifs au-delà de ce que le protocole permet.

## 5. Règles de travail pour chaque PR

Chaque PR doit contenir :
1. problème et justification ;
2. périmètre et éléments explicitement exclus ;
3. fichiers et architecture concernés ;
4. risques, hypothèses et limites ;
5. tests exécutés et résultats observés ;
6. dépendances avec d'autres PR ;
7. état de la revue croisée et réserves non résolues.

Règles opérationnelles :
- une PR = un objectif cohérent et réversible ;
- ne pas modifier simultanément les mêmes fichiers sans coordination ;
- ne pas fusionner une branche empilée avant sa base ;
- recontrôler les checks sur le dernier commit, pas sur un commit antérieur ;
- vérifier les workflows de publication déclenchés par une fusion ;
- ne pas confondre CI verte, revue indépendante, validation scientifique et test apprenant ;
- ne pas fusionner ni publier sans autorisation explicite du propriétaire du projet.

## 6. Prochaine action immédiate

1. Claude termine les PR #11, #12 et #13 et signale tout problème restant.
2. ChatGPT réalise la revue indépendante finale de ces PR.
3. Le propriétaire décide de l'ordre et autorise ou non les fusions, en tenant compte du déclenchement automatique de GitHub Pages.
4. ChatGPT prend ensuite le chantier P0 de vérification/hardening du Worker ; Claude en assure la revue.
5. Les chantiers suivants sont ouverts séquentiellement selon les critères de sortie ci-dessus.

Cette feuille de route est une proposition de travail et non une autorisation de fusion, de déploiement ou de changement majeur.
