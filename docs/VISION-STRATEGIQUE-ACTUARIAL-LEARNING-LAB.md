# Vision stratégique — Parcours Actuariel

> **Actuarial Learning Lab — Learn. Model. Practice.**

## 1. Décision d'orientation

Faire évoluer progressivement `parcours-actuariel` vers une plateforme internationale d'apprentissage, de pratique et de développement des compétences actuarielles.

Le projet poursuit deux objectifs indissociables :

1. **Développement personnel de JG :** approfondir réellement les fondements mathématiques, statistiques, actuariels, informatiques et professionnels, jusqu'à pouvoir construire, expliquer et défendre des modèles et des analyses.
2. **Valeur collective :** transformer les connaissances consolidées en ressources fiables, accessibles et utiles aux étudiants, enseignants et professionnels de l'actuariat.

La plateforme ne doit être ni une simple bibliothèque de cours, ni une vitrine, ni un LMS généraliste. Sa proposition de valeur est : **apprendre l'actuariat en comprenant les mathématiques, en expérimentant les modèles et en résolvant des problèmes professionnels.**

## 2. Positionnement dans l'écosystème

Préserver une complémentarité nette avec ACTU-BASICS :

| ACTU-BASICS | Parcours Actuariel |
|---|---|
| Vulgarisation et découverte | Formation approfondie |
| Vidéos pédagogiques | Cursus structuré |
| Intuition et premières notions | Maîtrise mathématique et actuarielle |
| Fiches de synthèse | Exercices, laboratoires et études de cas |
| Donner envie d'apprendre | Apprendre, pratiquer et démontrer ses compétences |

Les deux projets peuvent partager des contenus consolidés et des éléments de marque, mais leurs missions et niveaux pédagogiques restent distincts. Le circuit de production déjà documenté dans `docs/ACTU-BASICS.md` doit être préservé.

## 3. Les piliers de la plateforme

### 3.1 Cursus actuariel de référence

Structurer le cursus en trois profondeurs :
- **Core :** connaissances fondamentales communes.
- **Advanced :** approfondissements mathématiques et actuariels.
- **Professional :** méthodes et applications du métier.

Domaines à couvrir progressivement :
- mathématiques financières ;
- probabilités, processus stochastiques et statistique ;
- assurance vie, mortalité et longévité ;
- assurance non-vie, tarification et provisionnement ;
- retraite DB/DC et IAS 19 ;
- ALM et gestion actif-passif ;
- finance, risque, solvabilité, IFRS 17 et ORSA ;
- Data Science et Machine Learning appliqués à l'assurance ;
- Python, R, SQL, Excel et VBA appliqués à l'actuariat.

Cartographier les référentiels pertinents (SOA, IFoA, ICA et cursus universitaires), sans revendiquer d'accréditation ou d'équivalence officielle. Séparer les connaissances actuarielles transversales des règles propres à chaque juridiction et dater les références réglementaires.

### 3.2 Laboratoires actuariels interactifs

Faire passer les notions de la formule à l'expérimentation :
- mortalité, survie, tables et espérance de vie ;
- rentes, valeurs actuelles et provisions ;
- fréquence, sévérité et tarification GLM/GAM/GBM ;
- provisionnement et triangles de développement ;
- duration, convexité, courbes de taux et ALM ;
- sensibilités, scénarios et simulations.

L'apprenant doit pouvoir modifier des paramètres, visualiser les effets et interpréter les résultats. Les visualisations doivent servir la compréhension, pas la décoration.

### 3.3 Programmation et calcul scientifique

Développer progressivement des exercices pratiques en Python, R et SQL. Ajouter des parcours guidés, squelettes à compléter, débogage, tests, mini-projets et projets intégrateurs.

Conserver la règle pédagogique existante : les exercices remis à l'apprenant restent des squelettes à résoudre lui-même ; ne pas y intégrer les solutions. Toute exécution de code soumis doit être isolée, limitée en ressources et sécurisée. Évaluer Pyodide/WebR et l'exécution distante seulement après analyse des besoins, des risques et des coûts.

### 3.4 Études de cas professionnelles

Créer une bibliothèque de missions actuarielle fondées sur des données fictives ou publiques, avec sources et dictionnaires de variables.

Chaque cas suit un cycle complet :
1. contexte métier et mission ;
2. données et qualité des données ;
3. analyse exploratoire ;
4. fondements mathématiques ;
5. modélisation et implémentation ;
6. validation, limites et interprétation ;
7. rapport actuariel ;
8. recommandations professionnelles.

Priorités possibles : assurance automobile/voyage, régimes de retraite DB/DC, IAS 19, tarification, provisionnement, ALM et capital/risque. Ces travaux doivent aussi construire progressivement le portfolio de compétences de JG.

### 3.5 Progression fondée sur la maîtrise

Faire évoluer la progression au-delà d'une simple case « terminé ». À terme :
- diagnostic initial ;
- carte de compétences ;
- prérequis explicites ;
- évaluations de compréhension, raisonnement, calcul, programmation et application ;
- répétition espacée et consolidation ;
- examens blancs ;
- portfolio de projets et historique des acquis.

Ne pas confondre points, temps passé ou progression déclarée avec maîtrise démontrée.

### 3.6 Ressources scientifiques traçables

Chaque ressource importante doit documenter :
- références bibliographiques et institutionnelles ;
- définitions, hypothèses et conditions d'application ;
- conventions et choix de modélisation ;
- limites, approximations et juridiction concernée ;
- date, version et statut de validation.

Distinguer explicitement : contenu rédigé, contenu consolidé, vérification mathématique, tests techniques, revue humaine indépendante et test auprès d'apprenants.

### 3.7 Internationalisation

Prévoir une architecture multilingue, en commençant par le français et l'anglais. Construire un glossaire bilingue cohérent et adapter les cas et références aux juridictions concernées. Ne pas se contenter de traductions littérales lorsque les pratiques ou les cadres réglementaires diffèrent.

### 3.8 Communauté — à terme

Après validation de la valeur pédagogique du produit, envisager le partage de projets, les défis actuariels, les contributions pédagogiques et les échanges entre apprenants. Ne pas commencer par construire un réseau social : la qualité du contenu et des outils passe d'abord.

## 4. Protocole qualité non négociable

Pour chaque ressource, distinguer les contrôles suivants :
1. revue mathématique : formules, démonstrations, hypothèses et conditions ;
2. revue actuarielle : cohérence métier et référentiels pertinents ;
3. recalcul indépendant des exemples en Python et/ou R ;
4. tests logiciels : tests unitaires, cas limites, propriétés et non-régression ;
5. revue pédagogique : prérequis, progression, clarté et pièges ;
6. revue humaine indépendante, lorsqu'un expert compétent est disponible ;
7. expérimentation auprès d'apprenants, lorsque possible.

La réussite des tests automatisés ne vaut ni validation académique, ni revue actuarielle indépendante, ni preuve d'efficacité pédagogique. Ne jamais afficher un statut qui n'a pas été effectivement obtenu.

## 5. Principes d'architecture et d'exploitation

Ne pas lancer de réécriture globale. Auditer puis faire évoluer les composants existants :
- contenus structurés et schémas de validation ;
- moteur de génération Python ;
- interface responsive et accessible ;
- rendu mathématique et visualisations spécialisées ;
- exercices exécutables dans un environnement sûr ;
- Supabase pour les comptes et la progression, avec RLS ;
- tests automatisés et CI GitHub Actions.

Avant une ouverture à grande échelle, auditer l'authentification, la délivrabilité des e-mails, les politiques RLS, les sauvegardes, l'export/suppression des données, la conformité RGPD, les performances et les coûts d'exploitation. La configuration actuelle documentée pour quelques utilisateurs ne doit pas être considérée comme prête pour une montée en charge.

Prendre en compte l'accessibilité (WCAG), le mobile, le SEO, les performances, la confidentialité et la maintenabilité dès la conception.

## 6. Principes de design

Viser une identité universitaire contemporaine, élégante et lisible. Le design doit faciliter l'apprentissage grâce aux schémas, graphiques, animations utiles, espaces de calcul et visualisations. Éviter les pages surchargées, les effets gratuits et les animations qui détournent l'attention. Préserver le principe existant : une étape par écran.

## 7. Feuille de route proposée

**Phase 0 — Audit et fondations**
- cartographier architecture, contenus, tests, UX, sécurité et déploiement ;
- identifier les acquis, lacunes, risques et dettes techniques ;
- évaluer la couverture et le niveau scientifique du cursus ;
- proposer une architecture cible argumentée ;
- définir des critères d'acceptation mesurables.

**Phase 1 — Excellence pédagogique**
- consolider les modules fondamentaux ;
- expliciter prérequis et progression ;
- appliquer le protocole qualité ;
- créer un premier parcours exemplaire.

**Phase 2 — Laboratoires et programmation**
- développer les premières visualisations interactives ;
- améliorer les exercices Python/R/SQL ;
- produire les premiers cas professionnels complets.

**Phase 3 — Expérience apprenant**
- diagnostic, compétences, évaluations, répétition espacée et portfolio.

**Phase 4 — International**
- anglais, glossaire, références et adaptations par juridiction.

**Phase 5 — Ouverture**
- revue indépendante, tests utilisateurs, documentation de contribution, communauté et montée en charge.

## 8. Parcours pilote recommandé

Ne pas développer tous les domaines simultanément. Après l'audit, choisir un parcours pilote complet et exemplaire. **Assurance vie et mortalité** est un candidat pertinent : il relie mathématiques financières, probabilités, survie, tables de mortalité, rentes, provisions, programmation et applications aux engagements de retraite.

Le parcours pilote doit démontrer le niveau de qualité attendu avant de généraliser le modèle aux autres disciplines.

## 9. Méthode de travail et gouvernance

Pour chaque évolution :
1. examiner l'existant et le besoin ;
2. formuler un résultat attendu et des critères d'acceptation ;
3. proposer une solution proportionnée ;
4. travailler sur une branche et une PR ciblée ;
5. ajouter les tests pertinents ;
6. exécuter et rapporter les vérifications ;
7. documenter les limites et les points non vérifiés.

Ne rien fusionner ni publier sans accord explicite de JG. Respecter intégralement `CLAUDE.md` : confidentialité des supports de cours et données personnelles, absence de secrets, données fictives ou publiques sourcées, exercices laissés à résoudre, règles de tests et de publication.

## 10. Première livraison demandée à Claude

**Cette PR est une orientation stratégique, pas une autorisation de lancer une refonte globale.**

La première tâche après prise en compte de cette vision est un audit documenté du dépôt, puis une proposition de roadmap priorisée avec :
- état actuel et preuves observées ;
- écarts par rapport à la vision ;
- risques scientifiques, pédagogiques et techniques ;
- dépendances et coûts/complexités ;
- quick wins et chantiers structurants ;
- critères d'acceptation par phase ;
- recommandation du parcours pilote.

Aucune fonctionnalité majeure ne doit être engagée avant cette étape et avant validation de la proposition.

---

## Principe directeur

Chaque unité doit produire deux résultats : **une compétence réellement acquise par l'apprenant et une ressource fiable qui aide quelqu'un d'autre à progresser.**

L'ambition est de construire, avec le temps, une plateforme actuarielle de référence par sa profondeur scientifique, sa qualité pédagogique, son utilité professionnelle et la confiance qu'inspirent ses ressources — non par des promesses de grandeur ou une accumulation prématurée de fonctionnalités.
