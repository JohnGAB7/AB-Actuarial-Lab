# Comptes apprenants (Supabase)

Le compte est facultatif. Sans compte, la progression reste dans le navigateur. Avec un compte (lien magique par e-mail), les étapes terminées et le code Python de chaque séance sont synchronisés entre appareils.

## Ce qui va dans le dépôt, et ce qui n'y va jamais

- Dans le navigateur : seulement l'URL du projet et la **clé publique** (`sb_publishable_…`). Elles sont faites pour être publiques ; la sécurité vient de la Row Level Security (RLS).
- Jamais dans le dépôt ni dans le site : la clé secrète (`sb_secret_…`), l'ancienne clé `service_role`, le mot de passe de la base. `tools/construire.py` refuse de construire le site si on lui donne autre chose qu'une clé publique, et un test vérifie qu'aucune clé secrète n'est committée.
- Les deux valeurs publiques ne sont pas écrites dans le code : elles viennent des **variables** GitHub Actions `SUPABASE_URL` et `SUPABASE_PUBLISHABLE_KEY`, lues au moment de la construction.

## Mise en place (une seule fois, par JG)

1. **Créer le projet.** Sur supabase.com, nouveau projet `parcours-actuariel`, plan gratuit, région **Europe (Frankfurt, eu-central-1)**.
2. **Créer la table.** Dans *SQL Editor*, coller le contenu de `supabase/migrations/001_progression.sql` et cliquer sur *Run*.
3. **Autoriser le site.** Dans *Authentication > URL Configuration* :
   - *Site URL* : `https://johngab7.github.io/parcours-actuariel/`
   - *Redirect URLs* : ajouter `https://johngab7.github.io/parcours-actuariel/**`
4. **Donner les deux valeurs publiques au site.** Dans *Project Settings > API Keys*, copier l'URL du projet et la clé *publishable*. Puis, sur GitHub : *Settings > Secrets and variables > Actions > onglet Variables > New repository variable* :
   - `SUPABASE_URL` = `https://<ref>.supabase.co`
   - `SUPABASE_PUBLISHABLE_KEY` = `sb_publishable_…`
5. **Relancer le déploiement.** *Actions > site > Run workflow* sur `main`.

## Données

Table `public.progression`, une ligne par apprenant et par séance : `etapes` (étapes terminées), `code` (le code de l'exercice, 20 000 caractères au plus), `code_at`, `updated_at`. RLS : chacun ne lit et n'écrit que ses propres lignes. La fonction `supprimer_mon_compte()` permet à un apprenant d'effacer son compte ; ses lignes partent avec lui.

Fusion entre appareils : les étapes terminées sont l'union des deux côtés ; pour le code, la version modifiée le plus récemment l'emporte.

## Limite à connaître

Le service d'e-mail intégré de Supabase n'envoie que quelques e-mails par heure. Il suffit pour JG et quelques personnes. Si le site s'ouvre plus largement, il faudra brancher un fournisseur SMTP (*Authentication > Emails > SMTP Settings*).
