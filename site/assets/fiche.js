/* Accessible, bilingual renderer for the optional self-contained reference sheet. */
(() => {
  "use strict";
  const source = document.getElementById("seance");
  if (!source) return;
  let data;
  try { data = JSON.parse(source.textContent); } catch { return; }
  const sheet = data.fiche;
  if (!sheet || sheet.statut !== "prete") return;

  const lang = document.documentElement.lang === "en" ? "en" : "fr";
  const copy = lang === "en" ? {
    modeSteps:"Guided pathway", modeSheet:"Self-contained sheet", kicker:"REFERENCE SHEET",
    notice:"Editorial prototype. The structure and examples are technically checked; an independent actuarial review and learner testing have not yet been completed.",
    tabs:["Overview","Complete course","Methods","Worked examples","Solved exercises","Applications & labs","Summary & references"],
    question:"Guiding question", why:"Why it matters", objectives:"Learning objectives", prerequisites:"Prerequisites",
    map:"Learning map", duration:"Estimated study time", formulas:"Key formula", when:"When to use",
    steps:"Procedure", checks:"Consistency checks", errors:"Common mistakes", statement:"Problem",
    reasoning:"Reasoning", result:"Result", interpretation:"Interpretation", inputs:"Inputs",
    assumptions:"Assumptions", procedure:"Procedure", outputs:"Outputs", validation:"Validation",
    limits:"Limitations", memo:"Key takeaways", glossary:"Bilingual glossary", mastery:"Mastery checklist",
    references:"Annotated references", tools:"Tools", context:"Context", goal:"Goal",
    feedback:"Learning feedback", solution:"Worked solution", completed:"Items reviewed"
  } : {
    modeSteps:"Parcours guidé", modeSheet:"Fiche autonome", kicker:"FICHE DE RÉFÉRENCE",
    notice:"Prototype éditorial. La structure et les exemples sont vérifiés techniquement ; une revue actuarielle indépendante et des tests auprès d'apprenants restent à effectuer.",
    tabs:["Vue d'ensemble","Cours complet","Méthodes","Exemples guidés","Exercices corrigés","Applications & labs","Synthèse & références"],
    question:"Question directrice", why:"Pourquoi c'est important", objectives:"Objectifs d'apprentissage", prerequisites:"Prérequis",
    map:"Carte des notions", duration:"Temps estimé", formulas:"Formule essentielle", when:"Quand l'utiliser",
    steps:"Procédure", checks:"Contrôles de cohérence", errors:"Erreurs fréquentes", statement:"Énoncé",
    reasoning:"Raisonnement", result:"Résultat", interpretation:"Interprétation", inputs:"Entrées",
    assumptions:"Hypothèses", procedure:"Procédure", outputs:"Sorties", validation:"Validation",
    limits:"Limites", memo:"À retenir", glossary:"Glossaire bilingue", mastery:"Checklist de maîtrise",
    references:"Références annotées", tools:"Outils", context:"Contexte", goal:"Objectif",
    feedback:"Retour pédagogique", solution:"Corrigé détaillé", completed:"Éléments relus"
  };
  const $ = (selector, root=document) => root.querySelector(selector);
  const make = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };
  const list = (items, ordered=false) => {
    const node = document.createElement(ordered ? "ol" : "ul");
    (items || []).forEach(item => {
      const source = typeof item === "string" ? item.trim() : "";
      const lines = source.split(/\r?\n/);
      const fenced = lines.length >= 3 && lines[0].startsWith("```") && lines[lines.length - 1] === "```";
      if (fenced) {
        const entry = make("li","reference-code-item");
        const pre = make("pre","reference-code");
        pre.append(make("code","",lines.slice(1,-1).join("\n")));
        entry.append(pre);
        node.append(entry);
      } else {
        node.append(make("li","",item));
      }
    });
    return node;
  };
  const block = (title, content) => {
    const node = make("section","reference-block");
    if (title) node.append(make("h3","",title));
    if (content) node.append(content);
    return node;
  };
  // Materialize common bare mathematical notation in prose, while preserving explicit TeX.
  const inlineNotation = (value) => {
    const pattern = /\b[A-Za-z]\([^()]{1,24}\)\^[A-Za-z0-9]+|\b[A-Za-z]_[A-Za-z0-9]+|\b[A-Za-z0-9)\]}]\^[A-Za-z0-9]+|\b[A-Za-z]\([^()]{1,24}\)/g;
    return String(value ?? "").split(/(\$[^$]*\$|\\\([^)]*\\\))/g).map((part,index) => {
      if (index % 2 === 1) return part;
      return part.replace(pattern, (match) => "$" + match + "$");
    }).join("");
  };
  const paragraph = (text) => make("p","",inlineNotation(text));

