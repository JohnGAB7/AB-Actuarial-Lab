# Comptes apprenants (Supabase)

Le compte est facultatif. Sans compte, la progression reste dans le navigateur. Avec un compte (lien magique par e-mail), les étapes terminées et le code Python de chaque séance sont synchronisés entre appareils.

## Ce qui va dans le dépôt, et ce qui n'y va jamais

- Dans le navigateur : seulement l'URL du projet et la **clé publique** (`sb_publishable_…`). Elles sont faites pour être publiques ; la sécurité vient de la Row Level Security (RLS).
- Jamais dans le dépôt ni dans le site : la clé secrète (`sb_secret_…`), l'ancienne clé `service_role`, le mot de passe de la base. `tools/construire.py` refuse de construire le site si on lui donne autre chose qu'une clé publique, et un test vérifie qu'aucune clé secrète n'est committée.
- Les deux valeurs publiques ne sont pas écrites dans le code : elles viennent des **variables** GitHub Actions `SUPABASE_URL` et `SUPABASE_PUBLISHABLE_KEY`, lues au moment de la construction.

## Mise en place (une seule fois, par JG)

Le site utilise le projet Supabase `jg-s-learning-english-lab`, l'ancien laboratoire de Learning English, réaffecté à ce parcours (décision de JG, 23 novembre 2026). Le site principal Learning English garde son propre projet.

1. **Renommer le projet** (facultatif, conseillé). *Project Settings > General > Project name* : `parcours-actuariel`. Le nom n'apparaît pas dans le code ; il évite les confusions.
2. **Faire le tri.** Dans *Table Editor*, regarder les tables du schéma `public` laissées par le laboratoire. Si une table s'appelle déjà `progression`, me le dire avant d'aller plus loin. Les autres peuvent rester, ou être supprimées si elles ne servent plus. Dans *Authentication > Users*, les comptes de test du laboratoire peuvent être supprimés.
3. **Créer la table.** Dans *SQL Editor*, coller le contenu de `supabase/migrations/001_progression.sql` et cliquer sur *Run*.
4. **Autoriser le site.** Dans *Authentication > URL Configuration* :
   - *Site URL* : `https://johngab7.github.io/parcours-actuariel/`
   - *Redirect URLs* : ajouter `https://johngab7.github.io/parcours-actuariel/**`, et retirer les adresses du laboratoire.
5. **Donner les deux valeurs publiques au site.** Dans *Project Settings > API Keys*, copier l'URL du projet et la clé *publishable*. Puis, sur GitHub : *Settings > Secrets and variables > Actions > onglet Variables > New repository variable* :
   - `SUPABASE_URL` = `https://<ref>.supabase.co`
   - `SUPABASE_PUBLISHABLE_KEY` = `sb_publishable_…`
6. **Me prévenir.** Je fusionne la PR, le site se redéploie avec les comptes, et je vérifie la connexion.

La page de confidentialité indique un centre de données dans l'Union européenne : vérifier la région du projet dans *Project Settings > General*. Si elle est hors UE, me le dire pour corriger la page.

## Données

Table `public.progression`, une ligne par apprenant et par séance : `etapes` (étapes terminées), `code` (le code de l'exercice, 20 000 caractères au plus), `code_at`, `updated_at`. RLS : chacun ne lit et n'écrit que ses propres lignes. La fonction `supprimer_mon_compte()` permet à un apprenant d'effacer son compte ; ses lignes partent avec lui.

Fusion entre appareils : les étapes terminées sont l'union des deux côtés ; pour le code, la version modifiée le plus récemment l'emporte.

## Limite à connaître

Le service d'e-mail intégré de Supabase n'envoie que quelques e-mails par heure. Il suffit pour JG et quelques personnes. Si le site s'ouvre plus largement, il faudra brancher un fournisseur SMTP (*Authentication > Emails > SMTP Settings*).
