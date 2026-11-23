# A2b · Statistique pour l'assurance (Statistics for insurance)

- Séances sources : `contenus/a2b/s01.yaml`, `contenus/a2b/s02.yaml`, `contenus/a2b/s03.yaml`, `contenus/a2b/s04.yaml`
- Statut : commandé par JG le 23/11/2026, une fois la partie Fondamentaux du site terminée (décision de JG : des vidéos seulement pour les parties finalisées).
- Références : Hogg, McKean et Craig, Introduction to Mathematical Statistics, chap. 4 et 6 ; Klugman, Panjer et Willmot, Loss Models, chap. 12 à 16 (citées, jamais reproduites)

**Commande.** Une vidéo longue 16:9 par séance, complète, illustrée par des faits réels et animée, avec les mêmes chiffres que la séance, en français et en anglais, avec sous-titres. Puis des vidéos verticales de moins de 3 minutes, une par notion. Fil rouge : le contrat d'assurance vie de clients fictifs de JG's Holding, construit d'une vidéo à l'autre. Les séances déjà couvertes par une vidéo longue sont signalées et ne sont pas à refaire.

## 1. Notions

### A2b/S01 · Estimer une loi de sinistres : la méthode des moments (Estimating a claim distribution: the method of moments)

L'actuaire n'observe jamais la loi des sinistres, seulement un échantillon (sample). Un estimateur (estimator) transforme cet échantillon en valeur d'un paramètre. On le juge par son biais (bias), sa variance et leur combinaison, l'erreur quadratique moyenne (mean squared error).

$$
\begin{gathered}
\text{EQM}(\hat{\theta}) = E\big[(\hat{\theta} - \theta)^2\big] = \operatorname{Var}(\hat{\theta}) + \text{biais}(\hat{\theta})^2 \\[6pt]
\bar{X} = \frac{1}{n}\sum X_i \qquad s^2 = \frac{1}{n-1}\sum (X_i - \bar{X})^2 \qquad \operatorname{se}(\bar{X}) = \frac{s}{\sqrt{n}}
\end{gathered}
$$

La méthode des moments (method of moments) égale les moments de la loi à ceux de l'échantillon. Pour la loi gamma (gamma distribution), de moyenne $\alpha\theta$ et de variance $\alpha\theta^2$, on obtient deux équations et deux inconnues.

$$
\alpha\,\theta = \bar{x}, \quad \alpha\,\theta^2 = \hat{\sigma}^2 \;\Rightarrow\; \hat{\theta} = \frac{\hat{\sigma}^2}{\bar{x}}, \quad \hat{\alpha} = \frac{\bar{x}^2}{\hat{\sigma}^2}
$$

Par convention, la méthode des moments utilise la variance empirique divisée par $n$, notée $\hat{\sigma}^2$. Elle est simple et donne de bons points de départ, mais elle est souvent moins précise que le maximum de vraisemblance, surtout pour les lois à queue épaisse.

En pratique : Avec peu de sinistres, l'erreur type est grande. C'est l'idée de la crédibilité : ne pas se fier entièrement à l'expérience d'un petit portefeuille.

### A2b/S02 · Le maximum de vraisemblance (Maximum likelihood)

Le maximum de vraisemblance (maximum likelihood) choisit la valeur du paramètre qui rend les données observées les plus probables. On maximise la log-vraisemblance (log-likelihood) en annulant sa dérivée, le score (score).

$$
\begin{gathered}
\ell(\theta) = \sum_{i=1}^{n} \ln f(x_i; \theta) \qquad \ell'(\hat{\theta}) = 0 \\[6pt]
\text{Poisson : } \hat{\lambda} = \bar{x} \qquad \text{exponentielle : } \hat{\theta} = \bar{x} \qquad \text{Pareto, } \theta \text{ connu : } \hat{\alpha} = \frac{n}{\sum \ln(1 + x_i/\theta)}
\end{gathered}
$$

Pour un grand échantillon, le MLE est presque sans biais et suit à peu près une loi normale. Sa variance est l'inverse de l'information de Fisher (Fisher information) $I(\theta) = -E[\ell''(\theta)]$. Pour la Poisson, $I(\lambda) = n/\lambda$, donc $\operatorname{se}(\hat{\lambda}) = \sqrt{\hat{\lambda}/n}$.

La propriété d'invariance (invariance property) donne directement le MLE de toute grandeur dérivée : probabilité de zéro sinistre, quantile, prime pure. Il suffit de remplacer le paramètre par son estimation.

En pratique : Deux lois peuvent coller aux mêmes sinistres et diverger dans la queue. La Pareto, à queue épaisse (heavy tail), donne bien plus de poids aux gros sinistres que l'exponentielle : c'est ce qui compte pour la réassurance et le capital. La séance 4 compare les ajustements.

### A2b/S03 · Intervalles de confiance : quelle précision pour une fréquence ? (Confidence intervals: how precise is a claim frequency?)

Une estimation seule ne suffit pas : il faut dire à quel point on s'y fie. Un intervalle de confiance (confidence interval) encadre le paramètre avec un niveau de confiance (confidence level) donné. Sa demi-largeur s'appelle la marge d'erreur (margin of error).

$$
\begin{gathered}
\text{moyenne : } \bar{x} \pm t_{n-1;\,0{,}975}\,\frac{s}{\sqrt{n}} \qquad \text{proportion : } \hat{p} \pm 1{,}96\,\sqrt{\frac{\hat{p}(1 - \hat{p})}{n}} \\[6pt]
\text{Poisson : } \hat{\lambda} \pm 1{,}96\,\sqrt{\frac{\hat{\lambda}}{n}} \qquad \text{taille d'échantillon : } n \ge \frac{z^2\,p(1 - p)}{e^2}
\end{gathered}
$$

Ces formules reposent sur l'approximation normale : elles marchent bien pour une fréquence sur un grand portefeuille, beaucoup moins pour quelques gros sinistres à la queue épaisse. Le bootstrap (bootstrap) rééchantillonne alors les données pour obtenir l'intervalle sans hypothèse de loi.

La taille d'échantillon (sample size) se calcule à l'envers : on fixe la marge voulue $e$ et on en déduit $n$. Comme la marge décroît en $1/\sqrt{n}$, diviser la marge par 2 demande 4 fois plus de contrats.

En pratique : En tarification, un petit portefeuille a une fréquence observée très imprécise. La théorie de la crédibilité (credibility) mélange alors son expérience avec celle du marché, en proportion de sa précision.

### A2b/S04 · La loi colle-t-elle aux données ? Tests d'adéquation (Does the distribution fit the data? Goodness-of-fit tests)

Une loi ajustée reste une hypothèse. Un test d'adéquation (goodness-of-fit test) mesure l'écart entre les données et le modèle. Le khi-deux (chi-square test) compare des effectifs par classe ; le test de Kolmogorov-Smirnov (Kolmogorov-Smirnov test) compare des fonctions de répartition.

$$
\begin{gathered}
\chi^2 = \sum_{j=1}^{k} \frac{(O_j - E_j)^2}{E_j} \qquad \text{ddl} = k - 1 - p \\[6pt]
D = \max_x \big|F_n(x) - F_{\hat{\theta}}(x)\big| \qquad \text{AIC} = 2p - 2\,\ell(\hat{\theta})
\end{gathered}
$$

Pour le khi-deux, on regroupe les classes pour que chaque effectif attendu dépasse 5. Avec 2 degrés de liberté, le seuil à 5 % vaut 5,99 et la p-valeur se calcule à la main : $p = e^{-\chi^2/2}$.

Pour choisir entre plusieurs lois, on compare leur critère d'information d'Akaike (Akaike information criterion, AIC) : la plus faible valeur gagne. Il récompense la vraisemblance et pénalise le nombre de paramètres. Le QQ-plot (QQ plot) montre où la loi décroche, souvent dans la queue.

En pratique : Quand les paramètres sont estimés sur les mêmes données, les seuils usuels du test de Kolmogorov-Smirnov sont trop indulgents. Et sur quelques sinistres, aucun test ne voit la queue : le jugement de l'actuaire et les données de marché comptent autant que la p-valeur.

## 2. Exercices corrigés

### A2b/S01 · à la main

Énoncé : Même échantillon de 8 sinistres. Saisis tes résultats au centime, $\hat{\alpha}$ à 4 décimales.

| $x_1$ | $x_2$ | $x_3$ | $x_4$ | $x_5$ | $x_6$ | $x_7$ | $x_8$ |
|---|---|---|---|---|---|---|---|
| 1 200 | 800 | 3 500 | 600 | 2 100 | 950 | 1 700 | 4 200 |

Solution : $\sum (x_i - \bar{x})^2 = 12\,219\,687{,}5$, donc $s^2 = 12\,219\,687{,}5 / 7 = 1\,745\,669{,}64$ et $s = 1\,321{,}24$ € ; $s/\sqrt{8} = 467{,}13$ €. $\hat{\sigma}^2 = 12\,219\,687{,}5 / 8 = 1\,527\,460{,}94$, $\hat{\alpha} = 1\,881{,}25^2 / \hat{\sigma}^2 = 2{,}3170$ et $\hat{\theta} = \hat{\sigma}^2 / 1\,881{,}25 = 811{,}94$ €.

### A2b/S02 · à la main

Énoncé : Montants de la séance 1, Pareto avec $\theta = 2\,000$ € connu, puis exponentielle. Saisis tes résultats à 4 décimales.

| $x_1$ | $x_2$ | $x_3$ | $x_4$ | $x_5$ | $x_6$ | $x_7$ | $x_8$ |
|---|---|---|---|---|---|---|---|
| 1 200 | 800 | 3 500 | 600 | 2 100 | 950 | 1 700 | 4 200 |

Solution : $\sum \ln(1 + x_i/2\,000) = 4{,}9335$, donc $\hat{\alpha} = 8 / 4{,}9335 = 1{,}6216$ et $P(X > 5\,000) = (2\,000 / 7\,000)^{1{,}6216} = 0{,}1311$. Exponentielle : $\ell(\theta) = -n \ln \theta - \sum x_i / \theta$, maximale en $\hat{\theta} = 1\,881{,}25$, où $\ell = -8 \ln 1\,881{,}25 - 8 = -68{,}3175$.

### A2b/S03 · à la main

Énoncé : Fréquence observée sur le portefeuille, niveau de confiance de 95 % ($z = 1{,}96$). Saisis tes résultats à 4 décimales, et $n$ arrondi au-dessus pour une marge de ±1 point.

| Contrats | Sinistres |
|---|---|
| 2 000 | 120 |

Solution : $\hat{p} = 0{,}06$, $\operatorname{se} = \sqrt{0{,}06 \times 0{,}94 / 2\,000} = 0{,}0053$, donc l'intervalle est $[0{,}0496 ; 0{,}0704]$. Pour une marge de 0,01 : $n \ge 1{,}96^2 \times 0{,}0564 / 0{,}0001 = 2\,166{,}7$, soit 2 167 contrats.

### A2b/S04 · à la main

Énoncé : Les 1 000 contrats de la vérification, loi de Poisson de paramètre 0,5, classes regroupées à partir de 3. Puis le $D$ de Kolmogorov-Smirnov sur les 8 sinistres face à l'exponentielle. Saisis tes résultats à 4 décimales.

| $N = 0$ | $N = 1$ | $N = 2$ | $N \ge 3$ |
|---|---|---|---|
| 610 | 300 | 70 | 20 |

Solution : Effectifs attendus : $606{,}53$, $303{,}27$, $75{,}82$ et $1\,000 - 985{,}61 = 14{,}39$. Contributions : $0{,}0198 + 0{,}0352 + 0{,}4462 + 2{,}1892 = 2{,}6905$, p-valeur $e^{-1{,}3452} = 0{,}2605$. $D = F(600) - 0 = 1 - e^{-600/1\,881{,}25} = 0{,}2731$.

## 3. Pièges

- A2b/S01 : 1 450 € est la médiane. 15 050 € est la somme.
- A2b/S01 : 1 321,24 € est l'écart-type empirique $s$, pas la moyenne.
- A2b/S01 : 0,432 est l'inverse. Un $\alpha$ supérieur à 1 donne une densité en cloche asymétrique, moins piquée en 0 que l'exponentielle.
- A2b/S01 : Changer de convention de calcul ne rend pas les données plus informatives.
- A2b/S02 : 1,58 est $\sqrt{2{,}5}$, l'écart-type du nombre de sinistres d'une année, pas la précision de la moyenne sur 10 ans.
- A2b/S02 : 10 % est la fréquence observée (1 année sur 10) : elle ignore le modèle de Poisson.
- A2b/S02 : 0,62 est $\hat{\alpha} - 1$. 2,32 est le $\hat{\alpha}$ de la loi gamma de la séance 1 : une autre loi, un autre paramètre.
- A2b/S02 : 28,6 % est $2\,000 / 7\,000$ : la Pareto avec $\alpha = 1$ au lieu de 1,62, et pas l'exponentielle.
- A2b/S03 : [5,47 % ; 6,53 %] s'arrête à une erreur type : c'est un intervalle à 68 % seulement.
- A2b/S03 : 564 oublie $z$, et 1 106 oublie de mettre $z$ au carré.
- A2b/S03 : [966 € ; 2 797 €] prend 1,96 au lieu de 2,365, et [1 414 € ; 2 348 €] une seule erreur type.
- A2b/S03 : [−0,60 ; 5,60] utilise l'écart-type d'une seule année, $\sqrt{2{,}5}$, au lieu de l'erreur type de la moyenne sur 10 ans. Une borne négative est d'ailleurs un signal d'alerte.
- A2b/S04 : 610 est l'effectif observé. 500 confond $\lambda$ avec une probabilité.
- A2b/S04 : Le test porte sur les nombres de sinistres : les montants n'y jouent aucun rôle.
- A2b/S04 : 0,107 est l'écart au dernier point, et 0,481 l'ordre de grandeur du seuil, $1{,}36 / \sqrt{8}$.
- A2b/S04 : Un AIC plus élevé est moins bon, pas meilleur.

## 4. Vocabulaire anglais

| Français | English | Example sentence |
|---|---|---|
| Échantillon | sample | We only had a sample of 8 large claims. |
| Estimateur sans biais | unbiased estimator | The sample mean is an unbiased estimator of the expected claim. |
| Erreur type | standard error | With so few claims, the standard error is a quarter of the mean. |
| Erreur quadratique moyenne | mean squared error | A small bias can be worth it if it lowers the mean squared error. |
| Méthode des moments | method of moments | The method of moments gave starting values for the gamma fit. |
| Loi gamma | gamma distribution | Claim severity was fitted with a gamma distribution. |
| Vraisemblance | likelihood | The likelihood is the density of the data, read as a function of the parameter. |
| Log-vraisemblance | log-likelihood | We maximized the log-likelihood numerically for the lognormal. |
| Estimateur du maximum de vraisemblance | maximum likelihood estimator (MLE) | The MLE of the Poisson mean is simply the average claim count. |
| Information de Fisher | Fisher information | The Fisher information gave us the standard error of the estimate. |
| Propriété d'invariance | invariance property | By invariance, the estimated probability of no claim is exp of minus lambda hat. |
| Queue épaisse | heavy tail | A Pareto has a much heavier tail than an exponential fitted to the same claims. |
| Intervalle de confiance | confidence interval | The 95% confidence interval for the claim frequency was 5% to 7%. |
| Niveau de confiance | confidence level | Raising the confidence level to 99% widens the interval. |
| Marge d'erreur | margin of error | We needed a margin of error of one point on the frequency. |
| Loi de Student | t distribution | With only 8 claims, we used the t distribution instead of the normal. |
| Taille d'échantillon | sample size | The sample size had to quadruple to halve the margin of error. |
| Crédibilité | credibility | A small portfolio gets a low credibility weight. |
| Test d'adéquation | goodness-of-fit test | The goodness-of-fit test did not reject the Poisson model. |
| Hypothèse nulle | null hypothesis | Not rejecting the null hypothesis does not prove it. |
| Degrés de liberté | degrees of freedom | We lose one degree of freedom for each estimated parameter. |
| p-valeur | p-value | A p-value of 0.26 means such a gap is common by chance. |
| Diagramme quantile-quantile | QQ plot | The QQ plot showed the large claims above the line: a heavier tail. |
| Critère d'information d'Akaike | Akaike information criterion (AIC) | We kept the model with the lowest AIC, then checked the tail. |

## 5. Pour la vidéo

- A2b/S01 : accroche FR « Huit sinistres observés : que peut-on dire de tous les autres ? », EN “Eight claims observed: what can we say about all the others?”.
- A2b/S02 : accroche FR « Quelle valeur du paramètre rend nos sinistres les plus probables ? », EN “Which parameter value makes our claims the most likely?”.
- A2b/S03 : accroche FR « 6 % de sinistres : à un point près, ou à trois points près ? », EN “A 6% claim rate: give or take one point, or three?”.
- A2b/S04 : accroche FR « Une loi ajustée n'est pas une loi juste : comment le vérifier ? », EN “A fitted distribution is not a right one: how do we check?”.

Extraits verticaux : un par notion de la section 1, repris de la vidéo longue. Prérequis à annoncer : la séance précédente du module. Hors vidéo : les exercices de code, que l'apprenant fait seul sur le site.
