"""Construit le site statique dans _site/ à partir de contenus/*.yaml.

    python tools/construire.py            # écrit _site/
    python tools/construire.py --verifier # vérifie seulement les contenus

Le contenu (YAML) est séparé de la présentation (site/gabarits, site/assets).
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from pathlib import Path
from string import Template

import yaml

RACINE = Path(__file__).resolve().parents[1]
CONTENUS = RACINE / "contenus"
SITE = RACINE / "site"
SORTIE = RACINE / "_site"
TYPES = {"video", "rappel", "quiz", "calcul", "code", "vocabulaire"}


def charger_parcours() -> dict:
    return yaml.safe_load((CONTENUS / "parcours.yaml").read_text(encoding="utf-8"))


def charger_seance(sid: str) -> dict:
    return yaml.safe_load((CONTENUS / f"{sid}.yaml").read_text(encoding="utf-8"))


def verifier_seance(s: dict) -> list[str]:
    erreurs = []
    for i, e in enumerate(s.get("etapes", []), 1):
        if e.get("type") not in TYPES:
            erreurs.append(f"{s['id']} étape {i} : type inconnu {e.get('type')!r}")
        if e.get("type") == "quiz":
            for q in e["questions"]:
                if not 0 <= q["reponse"] < len(q["options"]):
                    erreurs.append(f"{s['id']} : réponse hors des options pour « {q['q']} »")
                p = q.get("pourquoi")
                if not isinstance(p, dict) or not all(p.get(k) for k in ("rappel", "formule", "exemple")):
                    erreurs.append(f"{s['id']} : explication sans rappel, formule et exemple pour « {q['q']} »")
    return erreurs


def seances(parcours: dict):
    for dom in parcours["domaines"]:
        for m in dom["modules"]:
            for sid in m.get("seances", []):
                yield dom, m, sid


e = html.escape
ICONE_COMPTE = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="8" r="4" fill="none" '
                'stroke="currentColor" stroke-width="1.7"/><path d="M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6" fill="none" '
                'stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>')


def entete(parcours: dict, base: str, actif: str = "") -> str:
    """Global header: brand, domain menu (inline on wide screens, a sheet on phones), account."""
    liens = "".join(
        f'<a href="{base}{d["id"]}/index.html"{" aria-current=\"page\"" if d["id"] == actif else ""}>{e(d["titre"])}</a>'
        for d in parcours["domaines"])
    return (
        f'<header class="nav gutter"><div class="nav-in">'
        f'<a class="brand" href="{base}index.html">Parcours <b>actuariel</b></a>'
        f'<nav class="nav-links" aria-label="Domaines">{liens}</nav>'
        f'<details class="nav-menu"><summary aria-label="Menu des domaines"><span></span><span></span></summary>'
        f'<nav class="nav-sheet" aria-label="Domaines">{liens}</nav></details>'
        f'<a class="acct" href="{base}compte/index.html" aria-label="Mon compte">{ICONE_COMPTE}</a>'
        f'</div></header>')


def pied(parcours: dict, base: str) -> str:
    liens = "".join(f'<a href="{base}{d["id"]}/index.html">{e(d["titre"])}</a>' for d in parcours["domaines"])
    return (
        f'<footer class="pied gutter"><div class="pied-in">'
        f'<div class="pied-col"><a class="brand" href="{base}index.html">Parcours <b>actuariel</b></a>'
        f'<p>Contenus rédigés pour ce site, sans reprise de supports de cours. Données fictives ou paramètres publics, avec leur source.</p></div>'
        f'<nav class="pied-col" aria-label="Domaines"><span class="eyebrow">Domaines</span>{liens}</nav>'
        f'<nav class="pied-col" aria-label="Compte"><span class="eyebrow">Compte</span>'
        f'<a href="{base}compte/index.html">Mon compte</a><a href="{base}compte/index.html#confidentialite">Confidentialité</a>'
        f'<a href="https://github.com/JohnGAB7/parcours-actuariel">Code source</a></nav>'
        f'</div></footer>')


def plan_json(parcours: dict, etapes: dict) -> str:
    """Course order with step counts, read by navigation.js to show progress and the "resume" target."""
    plan = [{"d": dom["id"], "m": m["id"], "s": sid, "n": etapes[sid][0], "t": etapes[sid][1]} for dom, m, sid in seances(parcours)]
    return json.dumps(plan, ensure_ascii=False).replace("</", "<\\/")


def statut_module(m: dict) -> str:
    n = len(m.get("seances", []))
    return f'{n} séance{"s" if n > 1 else ""}' if n else "À venir"


def page_accueil(parcours: dict, titres: dict) -> str:
    cartes = []
    for k, d in enumerate(parcours["domaines"], 1):
        n = sum(len(m.get("seances", [])) for m in d["modules"])
        etat = f'{n} séance{"s" if n > 1 else ""} · {len(d["modules"])} modules' if n else f'{len(d["modules"])} modules · bientôt'
        cartes.append(
            f'<a class="dom{"" if n else " futur"}" href="{d["id"]}/index.html" data-domaine="{d["id"]}">'
            f'<span class="dom-n mono">{k:02d}</span>'
            f'<span class="dom-t">{e(d["titre"])}</span><span class="dom-en">{e(d["en"])}</span>'
            f'<span class="dom-a">{e(d["accroche"])}</span>'
            f'<span class="dom-f"><span class="dom-s">{etat}</span><span class="barre" aria-hidden="true"><i></i></span></span></a>')
    premiere = next(seances(parcours))[2]
    return (
        f'<section class="hero"><div class="hero-in gutter">'
        f'<span class="eyebrow">Fondamentaux · Vie · Retraite · Non-vie · ALM · Risque</span>'
        f'<h1>Remettre la théorie <em>au travail.</em></h1>'
        f'<p>{e(parcours["sous_titre"])} Un rappel court, des questions, un calcul à la main, puis ton propre code Python. Les termes anglais à chaque étape.</p>'
        f'<div class="hero-cta"><a class="cta" href="{premiere}/index.html" data-reprendre>Commencer : {e(titres[premiere])} →</a>'
        f'<a class="cta-2" href="compte/index.html">{ICONE_COMPTE}Mon compte</a></div>'
        f'</div></section>'
        f'<main class="home gutter">'
        f'<div class="home-head"><span class="eyebrow">Les domaines</span><h2>Sept domaines, une séance de 25 minutes à la fois.</h2>'
        f'<p class="lead">Commence par les fondamentaux, puis suis l\'ordre conseillé. Les domaines marqués « bientôt » se rempliront au fil du parcours.</p></div>'
        f'<div class="doms">{"".join(cartes)}</div></main>')


def page_domaine(parcours: dict, d: dict, k: int) -> str:
    lignes = []
    for m in d["modules"]:
        corps = (f'<span class="mod-t">{e(m["titre"])}</span><span class="mod-en">{e(m["en"])}</span>')
        if m.get("seances"):
            lignes.append(f'<li><a class="mod" href="../{m["id"]}/index.html" data-module="{m["id"]}"><span class="mod-c">{corps}</span>'
                          f'<span class="mod-s"><span class="mod-n">{statut_module(m)}</span><span class="barre" aria-hidden="true"><i></i></span></span></a></li>')
        else:
            lignes.append(f'<li><span class="mod futur"><span class="mod-c">{corps}</span><span class="mod-s"><span class="mod-n">À venir</span></span></span></li>')
    autres = parcours["domaines"]
    suivant = autres[k] if k < len(autres) else None
    lien_suivant = (f'<a class="suite" href="../{suivant["id"]}/index.html"><span class="eyebrow">Domaine suivant</span>'
                    f'<span>{e(suivant["titre"])} →</span></a>') if suivant else ""
    return (
        f'<main class="page gutter">'
        f'<nav class="fil" aria-label="Fil d\'Ariane"><a href="../index.html">Accueil</a><span>/</span><span>{e(d["titre"])}</span></nav>'
        f'<div class="page-head"><span class="eyebrow mono">Domaine {k:02d}</span><h1>{e(d["titre"])}</h1>'
        f'<p class="en">{e(d["en"])}</p><p class="lead">{e(d["accroche"])}</p></div>'
        f'<ol class="mods-l">{"".join(lignes)}</ol>{lien_suivant}</main>')


def page_module(d: dict, m: dict, infos: dict) -> str:
    lignes = []
    for j, sid in enumerate(m["seances"], 1):
        s = infos[sid]
        lignes.append(
            f'<li><a class="sea" href="../{sid}/index.html" data-seance="{sid}">'
            f'<span class="sea-n mono">{j:02d}</span>'
            f'<span class="sea-c"><span class="sea-t">{e(s["titre"])}</span><span class="sea-en">{e(s["en"])}</span></span>'
            f'<span class="sea-s"><span class="sea-d">{s["duree"]} min · {len(s["etapes"])} étapes</span>'
            f'<span class="barre" aria-hidden="true"><i></i></span><span class="sea-x" data-etat>Commencer</span></span></a></li>')
    return (
        f'<main class="page gutter">'
        f'<nav class="fil" aria-label="Fil d\'Ariane"><a href="../index.html">Accueil</a><span>/</span>'
        f'<a href="../{d["id"]}/index.html">{e(d["titre"])}</a><span>/</span><span>{e(m["titre"].split(" · ")[0])}</span></nav>'
        f'<div class="page-head"><span class="eyebrow">Module</span><h1>{e(m["titre"].split(" · ", 1)[-1])}</h1>'
        f'<p class="en">{e(m["en"])}</p></div>'
        f'<ol class="seas">{"".join(lignes)}</ol></main>')


def config_supabase(env=None) -> dict:
    """Public Supabase settings, from the SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY variables (GitHub Actions).

    Only the project URL and the publishable key may reach the browser. A secret or service_role key stops the build.
    """
    env = os.environ if env is None else env
    url, cle = env.get("SUPABASE_URL", "").strip(), env.get("SUPABASE_PUBLISHABLE_KEY", "").strip()
    if not url and not cle:
        return {}
    if not re.fullmatch(r"https://[a-z0-9]{20}\.supabase\.co", url):
        sys.exit("SUPABASE_URL doit être de la forme https://<ref>.supabase.co")
    if cle.startswith("sb_secret_") or "service_role" in cle or not cle.startswith("sb_publishable_"):
        sys.exit("SUPABASE_PUBLISHABLE_KEY doit être la clé publique sb_publishable_…, jamais une clé secrète.")
    return {"url": url, "key": cle}


def construire() -> None:
    parcours = charger_parcours()
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    shutil.copytree(SITE / "assets", SORTIE / "assets")
    shutil.copytree(SITE / "vendor", SORTIE / "assets" / "vendor")
    (SORTIE / "assets" / "config.js").write_text(
        "window.PA_CONFIG = " + json.dumps(config_supabase()) + ";\n", encoding="utf-8")
    g_seance = Template((SITE / "gabarits" / "seance.html").read_text(encoding="utf-8"))
    g_page = Template((SITE / "gabarits" / "page.html").read_text(encoding="utf-8"))
    erreurs, infos = [], {}
    for dom, m, sid in seances(parcours):
        s = charger_seance(sid)
        erreurs += verifier_seance(s)
        infos[sid] = s
        profondeur = "../" * (sid.count("/") + 1)
        donnees = dict(s, accueil=profondeur + "index.html", module_url=profondeur + m["id"] + "/index.html",
                       module_titre=m["titre"], domaine_titre=dom["titre"])
        page = g_seance.substitute(titre=e(s["titre"]), base=profondeur, accueil=donnees["accueil"],
                                   donnees=json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/"))
        cible = SORTIE / sid / "index.html"
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(page, encoding="utf-8")
    if erreurs:
        sys.exit("\n".join(erreurs))
    plan = plan_json(parcours, {sid: (len(s["etapes"]), s["titre"]) for sid, s in infos.items()})
    titres = {sid: s["titre"] for sid, s in infos.items()}

    def ecrire(chemin: str, base: str, titre: str, description: str, contenu: str, actif: str = "", classe: str = "") -> None:
        cible = SORTIE / chemin / "index.html" if chemin else SORTIE / "index.html"
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(g_page.substitute(
            titre=e(titre), description=e(description), base=base, classe=classe, plan=plan,
            entete=entete(parcours, base, actif), contenu=contenu, pied=pied(parcours, base)), encoding="utf-8")

    ecrire("", "", parcours["titre"], parcours["sous_titre"], page_accueil(parcours, titres), classe="accueil")
    for k, d in enumerate(parcours["domaines"], 1):
        ecrire(d["id"], "../", f'{d["titre"]} · {parcours["titre"]}', d["accroche"], page_domaine(parcours, d, k), actif=d["id"])
        for m in d["modules"]:
            if m.get("seances"):
                ecrire(m["id"], "../", f'{m["titre"]} · {parcours["titre"]}', m["en"], page_module(d, m, infos), actif=d["id"])
    compte = (SITE / "gabarits" / "compte.html").read_text(encoding="utf-8")
    ecrire("compte", "../", f'Mon compte · {parcours["titre"]}', "Compte facultatif pour retrouver ta progression partout.", compte)
    (SORTIE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Site construit dans {SORTIE}")


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        p = charger_parcours()
        errs = [e for _, _, sid in seances(p) for e in verifier_seance(charger_seance(sid))]
        sys.exit("\n".join(errs) if errs else 0)
    construire()
