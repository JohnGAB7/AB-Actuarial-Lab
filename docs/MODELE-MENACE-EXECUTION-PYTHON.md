# Modèle de menace — exécution Python des apprenants

- **Statut :** modèle de menace mis à jour pour l'architecture iframe sandboxée proposée dans la PR #25. Cette architecture crée une origine opaque et ferme le réseau après le chargement de Pyodide ; elle reste une isolation côté navigateur, pas une sandbox OS/serveur avec quota mémoire dur.
- **Date :** 2026-11-23.
- **Périmètre :** exécution du code Python saisi dans les séances du site Parcours Actuariel.
- **Base examinée :** branche `security/worker-network-capability-hardening`, qui remplace le Worker historique par une iframe sandboxée ; PR #25 ouverte, non fusionnée.

## 1. Résumé exécutif

La branche de la PR #25 remplace le Worker de même origine par une iframe `srcdoc` portant uniquement `sandbox="allow-scripts"` (sans `allow-same-origin`). Son origine est opaque : le code Python ne peut pas lire le DOM ni le stockage de l'application par accès direct. Pyodide 0.27.7 est chargé depuis un chemin CDN épinglé sous une CSP temporaire ; dès son initialisation, une seconde CSP additive bloque les scripts, les connexions réseau, les workers, les images, les formulaires et les autres ressources. La page transmet le code et les tests via un `MessagePort` dédié et supprime l'iframe après 10 secondes d'exécution, ou immédiatement via « Arrêter ».

Le test Playwright vise le squelette, une solution, une boucle infinie, l'arrêt, l'origine opaque, l'inaccessibilité du DOM/stockage parent, le refus réseau après bootstrap et le rejet d'un code trop long. Cette conception sépare les privilèges applicatifs bien plus fortement que le Worker de même origine. Elle ne fournit toutefois ni quota mémoire dur, ni isolation de processus garantie, ni protection contre une vulnérabilité navigateur ou une dépendance Pyodide compromise.

## 2. Périmètre et éléments observés

### 2.1 Flux d'exécution actuel

1. Le navigateur charge `site/assets/seance.js` dans le contexte applicatif.
2. Au clic sur « Lancer les tests », la page crée une iframe `srcdoc` avec `sandbox="allow-scripts"`, sans `allow-same-origin`, sans permissions supplémentaires et avec `referrerpolicy="no-referrer"`.
3. L'iframe charge Pyodide 0.27.7 depuis le répertoire CDN épinglé. La CSP initiale autorise uniquement ce bootstrap et les fichiers nécessaires à l'initialisation.
4. Dès que `loadPyodide` est terminé, l'iframe ajoute une seconde CSP qui ferme les connexions réseau et les chargements de ressources/scripts.
5. La page transfère un `MessagePort` dédié ; seuls l'identifiant, le code, les expressions de test et les résultats bornés y circulent. Le code apprenant et les tests s'exécutent dans le même runtime et le même dictionnaire Python.
6. La page valide strictement la forme, le nombre et la taille des résultats. Le timeout de 10 secondes ou le bouton « Arrêter » supprime l'iframe et son contexte d'exécution ; le chargement dispose de 60 secondes.
7. Le code est conservé dans le stockage de la page principale et peut être synchronisé avec Supabase si l'apprenant est connecté ; aucun jeton, session ou donnée de compte n'est transmis à l'iframe.

### 2.2 Actifs à protéger

| Actif | Emplacement / exposition observée | Impact en cas de compromission |
|---|---|---|
| Session d'authentification Supabase | `localStorage`, clé de forme `sb-<ref>-auth-token` | Prise de contrôle de la session de l'apprenant |
| Données de progression | `localStorage` et, si connecté, table `public.progression` | Lecture, altération ou suppression des données du compte |
| Code Python de l'apprenant | `localStorage` ; synchronisé au compte si connecté | Atteinte à la confidentialité et à l'intégrité du travail |
| Interface de la séance | DOM du document | Altération de l'interface, hameçonnage local, tromperie sur les résultats |
| Disponibilité du navigateur | Fil principal, mémoire et ressources du navigateur | Gel de la page, consommation excessive de ressources |
| Clé Supabase publishable | `assets/config.js`, publique par conception | Ce n'est pas un secret ; les autorisations doivent être garanties par RLS et privilèges |
| Expressions de test et contenus pédagogiques | JSON intégré à la page, généré depuis YAML | Altération des résultats si le contexte de test peut être manipulé |

Le modèle ne considère pas la clé publishable comme un secret. En revanche, une session utilisateur et les données associées sont sensibles.

### 2.3 Frontières de confiance

- **Code applicatif de la page :** scripts de l'interface, navigation, compte et synchronisation, sur l'origine principale.
- **Contexte Python :** iframe sandboxée à origine opaque ; elle peut accéder à son propre document, mais pas au DOM ou au stockage de l'origine principale.
- **Code apprenant :** entrée arbitraire, exécutée dans l'iframe ; il doit être traité comme non fiable.
- **Contenu YAML et tests :** contenu versionné et relu dans le dépôt ; les tests sont transmis à l'iframe mais ne constituent pas une preuve inviolable de compétence.
- **Services distants :** CDN Pyodide, GitHub Pages et API Supabase.
- **Navigateur et système de l'utilisateur :** environnement hors du contrôle du site ; le site ne peut pas garantir l'absence d'extensions malveillantes, de navigateur compromis ou d'outils de développement.

## 3. Acteurs et hypothèses

### Acteurs

1. **Apprenant ordinaire :** exécute un code erroné, lent ou involontairement coûteux.
2. **Apprenant curieux ou malveillant :** essaie volontairement d'accéder aux API JavaScript, au DOM, au stockage, au réseau ou de falsifier les résultats.
3. **Auteur de contenu compromis ou erreur éditoriale :** introduit une valeur YAML inattendue qui atteint un rendu HTML ou une expression de test.
4. **Dépendance ou CDN compromis :** fournit un script ou un paquet modifié.
5. **Attaquant externe :** tente d'exploiter une faille du site ou d'obtenir les données d'un compte.

### Hypothèses

- Le code apprenant est arbitraire et ne peut pas être rendu fiable par une liste noire de mots Python.
- Le site est une application statique ; aucune isolation serveur de type conteneur n'est actuellement observée.
- Les comptes sont facultatifs ; la progression locale doit continuer à fonctionner sans compte.
- Le code apprenant ne doit jamais recevoir la session Supabase, une clé secrète, un accès DOM ou une fonction privilégiée de l'application.
- Les tests de séance servent actuellement à donner un retour pédagogique. Ils ne constituent pas une preuve inviolable de compétence ou de certification.
- Le modèle vise d'abord à réduire les risques liés au code exécuté dans le navigateur. Il ne protège pas l'appareil de l'utilisateur contre un navigateur ou une extension déjà compromis.

## 4. Menaces principales

| ID | Scénario | Impact | Priorité | Contrôle requis |
|---|---|---|---|---|
| T1 | Boucle infinie ou calcul non borné dans le fil principal | Interface bloquée, page inutilisable | Critique | Exécution hors du fil principal, délai dur, terminaison du contexte |
| T2 | Code Python accède à `js.window`, `document` ou au DOM via Pyodide | Lecture/altération de l'interface et accès aux données du document | Critique | Ne jamais exécuter le code dans le contexte de la page ; frontière isolée |
| T3 | Code lit le stockage local ou la session Supabase | Vol de session et accès aux données du compte | Critique | Aucun accès au stockage ou secret depuis le contexte d'exécution ; isolation testée |
| T4 | Code envoie des données vers un serveur tiers | Exfiltration de code, données ou informations accessibles | Élevée | Politique réseau restrictive ; aucune permission réseau par défaut |
| T5 | Code provoque une allocation mémoire ou une sortie gigantesque | Onglet ou processus navigateur instable | Élevée | Limites d'entrée/sortie, délai, terminaison ; documenter l'absence de quota mémoire portable |
| T6 | Code charge des paquets ou scripts distants | Exécution de code supplémentaire, dépendance à la chaîne d'approvisionnement | Élevée | Paquets préautorisés et versionnés ; pas d'installation arbitraire |
| T7 | Code modifie les fonctions ou objets utilisés par les tests | Faux positifs et résultats pédagogiques falsifiés | Élevée | Isoler l'exécution des tests de l'espace mutable de l'apprenant ; ne pas traiter le résultat comme une attestation |
| T8 | Messages Worker/iframe forgés, énormes ou mal formés | Injection, crash ou confusion d'état dans l'interface | Moyenne | Schéma strict, validation, limites de taille, identifiant de requête et source vérifiée |
| T9 | Dépendance Pyodide/CDN compromise | Exécution de code malveillant dans le contexte d'exécution | Élevée | Versions épinglées, dépendances maîtrisées, intégrité lorsque possible, plan de mise à jour |
| T10 | Contenu YAML utilise du HTML actif via `innerHTML` | XSS dans le contexte applicatif | Élevée | Échapper par défaut, liste blanche HTML, sanitisation et tests ; chantier distinct mais lié |

### Observations particulières

- Pyodide expose un pont JavaScript ; le fait de passer un dictionnaire Python via `globals: ns` ne constitue pas une sandbox.
- Une iframe `sandbox="allow-scripts"` sans `allow-same-origin` reçoit une origine opaque. Les accès à `parent.document`, au `localStorage` parent et au `localStorage` propre à l'origine opaque sont refusés par le navigateur ; le test Playwright exerce ces accès via le pont Pyodide.
- La CSP initiale autorise le chargement de Pyodide 0.27.7 uniquement depuis son répertoire CDN épinglé. Après initialisation, une seconde politique CSP additive est ajoutée au document de l'iframe avec `connect-src 'none'`, `script-src 'none'` et les autres directives restrictives. Le test navigateur tente un `fetch` vers un domaine externe et attend son rejet.
- Le canal applicatif est un `MessagePort` transféré, conservé dans une fermeture JavaScript et non exposé comme variable globale. La page n'utilise pas de gestionnaire `message` global pour recevoir des résultats ; elle n'accepte que les messages structurés du port associé à l'instance active.
- La sandbox interdit les popups, formulaires et navigations de premier niveau. La directive CSP `navigate-to` n'est pas uniformément prise en charge ; les navigations propres à l'iframe et les vulnérabilités du moteur restent des limites du modèle navigateur.
- Le code apprenant et les expressions de test restent dans le même runtime et le même espace de noms. Un apprenant motivé peut manipuler l'environnement d'exécution ; les résultats restent un feedback d'exercice, pas une attestation inviolable.
- Les navigateurs ne fournissent pas de quota mémoire strict, portable et fiable pour une iframe sandboxée. Le timeout supprime le contexte après 10 secondes, mais une allocation extrême peut provoquer une pression mémoire ou un crash du processus avant l'arrêt.

### CSP et contraintes propres à GitHub Pages

GitHub Pages ne permet pas de configurer librement des en-têtes HTTP de réponse. Le parent ne peut donc pas imposer une politique réseau par en-tête. L'architecture de la PR #25 utilise une iframe `srcdoc` avec l'attribut HTML `sandbox="allow-scripts"` (la restriction d'origine vient de cet attribut, pas de la CSP meta). Une CSP initiale dans le document de l'iframe autorise uniquement le bootstrap Pyodide depuis son répertoire CDN épinglé ; après `loadPyodide`, une seconde CSP meta additive ferme `connect-src`, `script-src` et les autres sources. Cette politique interne à l'iframe est différente d'une CSP meta posée sur le parent et s'applique aux requêtes émises ensuite par le contexte de l'iframe.

La CSP meta ne peut pas appliquer les directives `frame-ancestors`, `sandbox` ou `report-uri`. Elle ne fournit pas de contrôle réseau au niveau du système d'exploitation et ne protège pas contre un navigateur compromis, une faille d'implémentation ou une navigation propre à l'iframe que le moteur autoriserait. Le test Playwright doit vérifier le comportement effectif dans les navigateurs supportés ; la simple présence d'une directive CSP ne suffit pas.

## 5. Objectifs de sécurité

Toute solution future doit satisfaire les objectifs suivants :

1. **Séparation des privilèges :** le code apprenant ne peut ni lire ni modifier la session d'authentification, les données du compte, le stockage de l'application ou le DOM de la page principale.
2. **Disponibilité :** une exécution bloquée peut être arrêtée sans recharger ni bloquer durablement l'interface.
3. **Réseau par défaut fermé :** aucun accès réseau non nécessaire depuis le runtime apprenant ; toute exception doit être documentée et limitée.
4. **Entrées/sorties bornées :** taille du code, nombre de tests, durée, taille des résultats et fréquence des messages sont bornés.
5. **Intégrité de l'interface :** seules les données de résultat validées traversent le canal de communication.
6. **Résilience :** les erreurs, arrêts, timeouts, chargements interrompus et redémarrages laissent l'interface dans un état cohérent.
7. **Confidentialité :** le code et les données d'un apprenant ne sont pas partagés avec d'autres apprenants ; aucune télémétrie de code n'est ajoutée sans décision explicite.
8. **Compatibilité pédagogique :** le site reste utilisable sans compte ; les squelettes d'exercice restent à compléter par l'apprenant.
9. **Transparence :** les limites résiduelles d'une exécution côté client sont affichées dans la documentation.

## 6. Options d'architecture à évaluer

### Option A — Web Worker dédié, même origine

**Avantages :**
- déplace le calcul hors du fil principal ;
- permet l'arrêt brutal du Worker via `terminate()` ;
- retire l'accès direct au DOM, à `window` et à `localStorage` du contexte Worker ;
- préserve une architecture statique et un déploiement simple.

**Limites :**
- le Worker peut encore disposer d'API réseau et de stockage comme IndexedDB, selon le navigateur et les politiques ;
- le Worker partage l'origine du site ; ce n'est pas une frontière d'origine ;
- une limite de temps n'est pas une limite mémoire stricte ;
- la politique CSP effective des Workers doit être vérifiée avec l'hébergement réel ;
- Pyodide, ses fichiers WASM, ses imports et son modèle de chargement doivent être validés dans un Worker.

**Conclusion :** bon palier pour la disponibilité et la réduction de privilèges, mais insuffisant à lui seul pour revendiquer une exécution de code hostile fortement isolée.

### Option B — iframe sandboxée avec origine opaque ou dédiée

**Avantages :**
- peut créer une séparation de contexte plus forte entre l'interface et l'exécution ;
- l'attribut `sandbox` peut retirer des capacités puissantes ; ne pas combiner les permissions sans justification ;
- le protocole `postMessage` permet de ne transmettre que le code, les tests et les résultats explicitement nécessaires.

**Limites :**
- la gestion d'une origine opaque, des messages et de l'identité de la fenêtre est délicate ;
- le chargement Pyodide/WASM et les Workers imbriqués peuvent être affectés par les règles CSP et sandbox ;
- l'origine `null` ne doit jamais être considérée comme une authentification suffisante ; vérifier également `event.source` et un canal/nonce propre à l'instance ;
- une iframe sur la même origine avec des permissions trop larges peut annuler le bénéfice attendu.

**Conclusion :** prototype implémenté dans la PR #25. L'origine opaque, la CSP post-bootstrap et le canal privé sont vérifiés par des tests navigateur ciblés ; la solution reste une isolation côté navigateur, sans quota mémoire dur ni garantie de processus séparé.

### Option C — origine séparée dédiée au runtime

**Avantages :**
- frontière d'origine plus claire ; aucun cookie ou stockage applicatif ne devrait être partagé avec l'origine d'exécution ;
- possibilité de définir des en-têtes de sécurité et une politique réseau indépendants ;
- limite les conséquences d'une compromission du runtime sur l'application principale.

**Limites :**
- nécessite une origine et une configuration d'hébergement séparées ;
- nécessite une politique CORS et un protocole de messages soigneusement conçus ;
- augmente la complexité de déploiement et de maintenance ;
- ne remplace pas les limites de ressources ni les contrôles de dépendances.

**Conclusion :** meilleure piste à étudier pour une ouverture publique avec menace hostile, si l'hébergement permet de contrôler les en-têtes et l'isolation d'origine.

### Option D — exécution distante dans un service isolé

**Avantages :**
- permet potentiellement d'appliquer des limites CPU/mémoire, quotas, isolation OS/conteneur et filtrage réseau plus stricts ;
- ne dépend pas des ressources de l'ordinateur de l'apprenant.

**Limites :**
- exige un backend, une infrastructure d'exécution hostile, une gestion des coûts, des quotas, des abus, des données et de la disponibilité ;
- élargit fortement le périmètre opérationnel et réglementaire ;
- ne doit pas être ajouté avant d'avoir démontré qu'une solution client ne répond pas aux besoins.

**Conclusion :** ne pas retenir à ce stade sans besoin produit, budget et modèle opérationnel explicites.

## 7. Évaluation de l'architecture proposée dans la PR #25

La PR #11 avait introduit un Worker de même origine. La PR #25 remplace ce mécanisme sur sa branche par une iframe à origine opaque, avec plafonds d'entrée (50 000 caractères de code, 30 tests, 2 000 caractères par expression, 20 000 caractères cumulés), erreurs limitées à 500 caractères, timeout d'exécution de 10 secondes et timeout de chargement de 60 secondes. Le parent supprime le contexte complet à l'arrêt. La PR #25 reste ouverte et non fusionnée ; les résultats CI doivent être vérifiés sur son SHA exact avant toute conclusion.

Le modèle de menace doit distinguer deux scénarios :

- **Usage actuel envisagé :** chaque apprenant exécute son propre code, sans partage entre comptes ; la session Supabase et les données de progression restent dans le contexte principal et ne sont pas transmises à l'iframe. L'origine opaque bloque les accès DOM/stockage parent et la CSP ferme les connexions ordinaires après le bootstrap. C'est un palier client nettement plus fort, sans garantie contre toutes les navigations, vulnérabilités navigateur ou pressions mémoire.
- **Menace hostile renforcée :** partage de code tiers, confidentialité forte ou validation de compétences à valeur probante. Le navigateur ne fournit toujours pas de quota mémoire dur ni d'isolation de processus garantie. Avant ces usages, une origine dédiée avec en-têtes HTTP contrôlés ou un service d'exécution serveur isolé reste préférable.

La PR #25 est une implémentation applicative active sur sa branche, mais pas encore intégrée à `main`. Aucun déploiement ni aucune adoption ne sont présumés.

## 8. Critères d'acceptation avant adoption d'une implémentation

### Isolation et données

- [ ] Le code Python ne peut pas lire `localStorage`, la session Supabase ou les données de progression de la page.
- [ ] Le code Python ne peut pas lire ou modifier le DOM, ni appeler les fonctions privilégiées de l'application.
- [ ] Le runtime ne reçoit aucun secret ; la clé publishable reste traitée comme publique.
- [ ] Les tests démontrent les frontières d'accès dans les navigateurs supportés.

### Disponibilité et ressources

- [ ] Une boucle infinie est interrompue dans le délai défini.
- [ ] Le bouton d'arrêt fonctionne et l'interface reste réactive.
- [ ] Une exécution peut être redémarrée après timeout, exception ou arrêt.
- [ ] Les entrées, sorties, messages et nombre de tests ont des limites explicites.
- [ ] Les limites mémoire non garanties par le navigateur sont documentées.

### Réseau et dépendances

- [ ] Les appels réseau depuis le runtime sont bloqués par défaut ou strictement allowlistés.
- [ ] Les imports et paquets sont limités à un ensemble versionné et documenté.
- [ ] La politique CSP est vérifiée sur l'environnement de déploiement réel.
- [ ] Les erreurs de chargement CDN/WASM sont gérées sans bloquer la séance.

### Intégrité des tests et interface

- [ ] Les expressions de test ne peuvent pas être falsifiées simplement en modifiant l'espace de noms de l'apprenant.
- [ ] Les résultats du navigateur sont décrits comme feedback pédagogique, pas comme attestation de compétence.
- [ ] Les messages de retour sont validés, limités et affichés comme texte, pas comme HTML.
- [ ] Les tests couvrent erreurs Python, accès JavaScript, réseau, stockage, messages invalides et redémarrages.

### Compatibilité

- [ ] Le parcours fonctionne sans compte et sans synchronisation Supabase.
- [ ] Les exercices gardent leurs squelettes à compléter ; aucune solution n'est injectée dans `exercices/`.
- [ ] Les navigateurs supportés et leurs limites sont explicités.

## 9. Plan de tests de sécurité à construire

| Test | Tentative | Résultat attendu |
|---|---|---|
| TST-01 | Boucle `while True` | Timeout puis arrêt effectif ; interface réactive |
| TST-02 | Calcul CPU très long | Arrêt dans le délai ; pas de blocage du document |
| TST-03 | Allocation mémoire répétée | Arrêt/échec contrôlé autant que possible ; limites résiduelles documentées |
| TST-04 | `import js` puis accès à `document` / `window` | Accès impossible depuis le runtime isolé |
| TST-05 | Lecture de `localStorage` et clé `sb-*-auth-token` | Données inaccessibles |
| TST-06 | Lecture/écriture IndexedDB | Aucun stockage applicatif accessible ; résultat vérifié |
| TST-07 | `fetch` vers un domaine tiers | Bloqué, sauf domaine explicitement autorisé |
| TST-08 | Tentative de WebSocket/import de script distant | Bloquée ou strictement contrôlée |
| TST-09 | Modification de fonctions/builtins avant les tests | Les tests ne peuvent pas être transformés en faux succès |
| TST-10 | Message `postMessage` trop grand, inattendu ou mal formé | Rejet sans exception ni corruption d'état |
| TST-11 | Arrêt pendant le chargement de Pyodide | État cohérent ; nouvelle tentative possible |
| TST-12 | Erreur Python puis nouvelle exécution | Runtime récupérable ou recréé proprement |
| TST-13 | Navigation vers une autre séance pendant l'exécution | Ancien résultat ignoré ; aucune mise à jour du nouvel écran |
| TST-14 | Session Supabase connectée pendant les tests | Session et synchronisation inaccessibles au code apprenant |
| TST-15 | Navigateur sans Worker/WASM ou mémoire insuffisante | Message explicite et solution de repli sûre |

## 10. Questions à résoudre en revue croisée

1. Quel niveau de menace le produit souhaite-t-il couvrir : erreurs accidentelles uniquement, utilisateurs curieux, ou code délibérément hostile ?
2. Le maintien de GitHub Pages comme hébergement unique est-il une contrainte ferme, ou une origine dédiée peut-elle être envisagée ?
3. Quels navigateurs et appareils doivent être supportés, notamment mobiles ?
4. Le réseau doit-il être totalement désactivé pour les exercices, ou certains exercices auront-ils besoin de télécharger des données/paquets ?
5. Les tests côté client sont-ils uniquement un retour pédagogique, ou le produit envisage-t-il un jour une validation de compétences opposable ? Dans ce dernier cas, l'exécution client ne peut pas être considérée comme une preuve fiable.
6. Quel délai maximal est acceptable pour un exercice et quelle taille maximale de code/sortie peut être imposée sans dégrader l'expérience ?

## 11. Références techniques à consulter lors du prototype

Les références suivantes sont des points de départ, pas une preuve que l'architecture proposée est déjà conforme :

- Pyodide — documentation officielle : https://pyodide.org/en/stable/usage/webworker.html
- MDN — Web Workers : https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API
- MDN — iframe sandbox : https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#sandbox
- MDN — Content Security Policy : https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- OWASP — HTML5 Security Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html
- OWASP — Cross Site Scripting Prevention Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

## 12. Décision attendue

Cette PR propose uniquement le modèle de menace et les critères de vérification. La revue croisée a clarifié que le Worker de la PR #11 est un premier palier adapté au scénario actuel, sous réserve de ne pas le présenter comme une sandbox complète. La fusion de cette PR documentaire ne vaut ni validation de sécurité indépendante, ni autorisation d'ouverture à du code tiers ou partagé. Toute évolution vers une iframe sandboxée, une origine dédiée ou une exécution distante devra faire l'objet d'une conception et de tests distincts. Aucune fusion de code applicatif, publication ou modification de l'authentification n'est demandée ici.
