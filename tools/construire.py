"""Construit le site statique dans _site/ à partir de contenus/*.yaml.

    python tools/construire.py            # écrit _site/
    python tools/construire.py --verifier # vérifie seulement les contenus

Le contenu (YAML) est séparé de la présentation (site/gabarits, site/assets).
Site bilingue : français à la racine, anglais sous en/. Les textes anglais d'une séance vivent dans
contenus/en/<id>.yaml, qui ne contient que des textes : chiffres, réponses et tests restent dans le fichier français.
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
LANGUES = ("fr", "en")
# Keys that hold numbers, answers, tests or structure: they only live in the French file.
NON_TRADUISIBLES = {"id", "module", "type", "minutes", "duree", "table", "taux", "reponse", "valeur", "tolerance",
                    "cle", "expr", "fichier", "depart", "interactif", "url", "cartes", "statut", "formule"}


def charger_parcours() -> dict:
    return yaml.safe_load((CONTENUS / "parcours.yaml").read_text(encoding="utf-8"))


def charger_seance(sid: str, langue: str = "fr") -> dict:
    s = yaml.safe_load((CONTENUS / f"{sid}.yaml").read_text(encoding="utf-8"))
    if langue == "fr":
        return s
    return fusion(s, yaml.safe_load((CONTENUS / langue / f"{sid}.yaml").read_text(encoding="utf-8")), sid)


def nombres(texte: str, langue: str) -> list[str]:
    """Numbers in a text, written the same way whatever the language: 0,0247 and 0.0247 give 0.0247; 716 046 and 716,046 give 716046."""
    t = texte.replace("{,}", ",")
    t = re.sub(r"(?<=\d)(?:\\,|\\ |\u202f|\u00a0| )(?=\d{3}\b)", "", t)  # thousands separators: 716 046, 716\,046
    if langue == "fr":
        t = re.sub(r"(?<=\d),(?=\d)", ".", t)
    else:
        t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)
    # Keep sign, exponent and percentage/per-mille unit: comparing unsigned digit runs
    # would accept -2.5 % -> 2.5 % or 2.5 % -> 2.5, both material changes.
    motif = r"(?<![\w.])[+\-−]?\d+(?:\.\d+)?(?:[eE][+\-−]?\d+)?(?:\s*\\?[%‰])?"
    return sorted(x.replace("−", "-").replace(" ", "").replace(r"\%", "%") for x in re.findall(motif, t))


def sans_texte(formule: str) -> str:
    """A formula with its \\text{...} labels blanked: only those labels may change in a translation."""
    return re.sub(r"\\text\{[^{}]*\}", r"\\text{}", formule)


def fusion(base, trad, chemin: str):
    """Lay the translated texts over the French session.

    The translation may not add keys, change list lengths or types, touch the numeric fields, leave a text empty,
    or change a number written in a text. A formula may only change its \\text{...} labels.
    """
    if isinstance(trad, dict):
        if not isinstance(base, dict):
            raise ValueError(f"{chemin} : structure différente du français")
        sortie = dict(base)
        for k, v in trad.items():
            if k not in base:
                raise ValueError(f"{chemin}.{k} : clé absente du français")
            if k in NON_TRADUISIBLES and k != "formule":
                raise ValueError(f"{chemin}.{k} : ce champ reste dans le fichier français")
            if k == "formule" and (not isinstance(v, str) or sans_texte(v) != sans_texte(base[k])):
                raise ValueError(f"{chemin}.{k} : une formule ne peut changer que ses \\text{{…}}")
            sortie[k] = v if k == "formule" else fusion(base[k], v, f"{chemin}.{k}")
        return sortie
    if isinstance(trad, list):
        if not isinstance(base, list) or len(base) != len(trad):
            raise ValueError(f"{chemin} : liste de longueur différente du français")
        return [fusion(b, t, f"{chemin}[{i}]") for i, (b, t) in enumerate(zip(base, trad))]
    if type(trad) is not type(base):
        raise ValueError(f"{chemin} : type différent du français")
    if isinstance(trad, str):
        if base.strip() and not trad.strip():
            raise ValueError(f"{chemin} : texte vide")
        if nombres(trad, "en") != nombres(base, "fr"):
            raise ValueError(f"{chemin} : chiffres différents du français ({nombres(base, 'fr')} ≠ {nombres(trad, 'en')})")
    return trad


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


def verifier_traduction(sid: str) -> list[str]:
    """The English file must exist and give every French text with words in it (a text the overlay leaves out counts as missing)."""
    chemin = CONTENUS / "en" / f"{sid}.yaml"
    if not chemin.exists():
        return [f"{sid} : traduction anglaise manquante (contenus/en/{sid}.yaml)"]
    try:
        charger_seance(sid, "en")
    except ValueError as err:
        return [str(err)]
    fr = charger_seance(sid)
    trad = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    oublis = []

    def a_traduire(x) -> bool:
        if isinstance(x, dict):
            return any(a_traduire(v) for k, v in x.items() if k not in NON_TRADUISIBLES)
        if isinstance(x, list):
            return any(a_traduire(v) for v in x)
        return isinstance(x, str) and bool(re.search(r"[a-zà-ÿ]{4,}", re.sub(r"\$[^$]*\$|<[^>]+>", "", x)))

    def comparer(a, b, p):
        if b is None:
            if a_traduire(a):
                oublis.append(p)
        elif isinstance(a, dict):
            for k in a:
                if k not in NON_TRADUISIBLES and k not in ("actu_basics", "en"):
                    comparer(a[k], b.get(k) if isinstance(b, dict) else None, f"{p}.{k}")
        elif isinstance(a, list):
            for i, x in enumerate(a):
                comparer(x, b[i] if isinstance(b, list) else None, f"{p}[{i}]")

    comparer(fr, trad, sid)
    return [f"{o} : texte non traduit" for o in oublis]


def seances(parcours: dict):
    for dom in parcours["domaines"]:
        for m in dom["modules"]:
            for sid in m.get("seances", []):
                yield dom, m, sid


e = html.escape
ICONE_COMPTE = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="8" r="4" fill="none" '
                'stroke="currentColor" stroke-width="1.7"/><path d="M4 20c1.5-4 4.5-6 8-6s6.5 2 8 6" fill="none" '
                'stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>')

TXT = {
    "fr": {
        "domaines": "Domaines", "menu": "Menu des domaines", "compte": "Mon compte", "confid": "Confidentialité",
        "source": "Code source", "compte_t": "Compte", "accueil": "Accueil", "fil": "Fil d'Ariane",
        "pied": "Contenus rédigés pour ce site, sans reprise de supports de cours. Données fictives ou paramètres publics, avec leur source.",
        "autre": "English", "autre_court": "EN", "autre_aria": "Read this page in English",
        "seance": lambda n: f'{n} séance{"s" if n > 1 else ""}', "a_venir": "À venir", "bientot": "bientôt", "modules": "modules",
        "eyebrow": "Fondamentaux · Vie · Retraite · Non-vie · ALM · Risque",
        "h1": "Remettre la théorie <em>au travail.</em>",
        "hero": "Un rappel court, des questions, un calcul à la main, puis ton propre code Python. Les termes anglais à chaque étape.",
        "commencer": "Commencer", "les_domaines": "Les domaines", "h2": "Sept domaines, une séance de 25 minutes à la fois.",
        "lead": "Commence par les fondamentaux, puis suis l'ordre conseillé. Les domaines marqués « bientôt » se rempliront au fil du parcours.",
        "domaine": "Domaine", "suivant": "Domaine suivant", "module": "Module", "min_etapes": lambda d, n: f"{d} min · {n} étapes",
        "commencer_f": "Commencer", "progression": "Progression de la séance", "etapes": "Étapes",
        "compte_desc": "Compte facultatif pour retrouver ta progression partout.",
    },
    "en": {
        "domaines": "Domains", "menu": "Domain menu", "compte": "My account", "confid": "Privacy",
        "source": "Source code", "compte_t": "Account", "accueil": "Home", "fil": "Breadcrumbs",
        "pied": "Content written for this site, with no reuse of course materials. Fictional data or public parameters, with their source.",
        "autre": "Français", "autre_court": "FR", "autre_aria": "Lire cette page en français",
        "seance": lambda n: f'{n} session{"s" if n > 1 else ""}', "a_venir": "Coming soon", "bientot": "soon", "modules": "modules",
        "eyebrow": "Foundations · Life · Pensions · P&C · ALM · Risk",
        "h1": "Put theory <em>back to work.</em>",
        "hero": "A short recap, questions, a calculation by hand, then your own Python code. French and English terms at every step.",
        "commencer": "Start", "les_domaines": "The domains", "h2": "Seven domains, one 25-minute session at a time.",
        "lead": "Start with the foundations, then follow the suggested order. Domains marked “soon” will fill up as the path grows.",
        "domaine": "Domain", "suivant": "Next domain", "module": "Module", "min_etapes": lambda d, n: f"{d} min · {n} steps",
        "commencer_f": "Start", "progression": "Session progress", "etapes": "Steps",
        "compte_desc": "Optional account to keep your progress on every device.",
    },
}


def dom_titre(d: dict, langue: str) -> str:
    return d["titre"] if langue == "fr" else d["en"]


def dom_sous(d: dict, langue: str) -> str:
    return d["en"] if langue == "fr" else d["titre"]


def dom_accroche(d: dict, langue: str) -> str:
    return d["accroche"] if langue == "fr" else d["accroche_en"]


def mod_titre(m: dict, langue: str) -> str:
    if langue == "fr":
        return m["titre"]
    return m["titre"].split(" · ")[0] + " · " + m["en"]


def mod_sous(m: dict, langue: str) -> str:
    return m["en"] if langue == "fr" else m["titre"].split(" · ", 1)[-1]


def bascule(langue: str, autre: str) -> str:
    """FR | EN switch: the current language is marked, the other one links to the same page in that language."""
    def cote(code):
        if code == langue:
            return f'<span aria-current="true">{code.upper()}</span>'
        aria = TXT[langue]["autre_aria"]
        return f'<a href="{autre}" hreflang="{code}" lang="{code}" aria-label="{aria}" data-langue="{code}">{code.upper()}</a>'
    return f'<span class="langs" role="group" aria-label="Langue · Language">{cote("fr")}{cote("en")}</span>'


def entete(parcours: dict, racine: str, autre: str, langue: str, actif: str = "") -> str:
    """Global header: brand, domain menu (inline on wide screens, a sheet on phones), language switch, account."""
    t = TXT[langue]
    liens = "".join(
        f'<a href="{racine}{d["id"]}/index.html"{" aria-current=\"page\"" if d["id"] == actif else ""}>{e(dom_titre(d, langue))}</a>'
        for d in parcours["domaines"])
    return (
        f'<header class="nav gutter"><div class="nav-in">'
        f'<a class="brand" href="{racine}index.html">Parcours <b>actuariel</b></a>'
        f'<nav class="nav-links" aria-label="{t["domaines"]}">{liens}</nav>'
        f'<details class="nav-menu"><summary aria-label="{t["menu"]}"><span></span><span></span></summary>'
        f'<nav class="nav-sheet" aria-label="{t["domaines"]}">{liens}</nav></details>'
        f'{bascule(langue, autre)}'
        f'<a class="acct" href="{racine}compte/index.html" aria-label="{t["compte"]}">{ICONE_COMPTE}</a>'
        f'</div></header>')


def pied(parcours: dict, racine: str, autre: str, langue: str) -> str:
    t = TXT[langue]
    liens = "".join(f'<a href="{racine}{d["id"]}/index.html">{e(dom_titre(d, langue))}</a>' for d in parcours["domaines"])
    return (
        f'<footer class="pied gutter"><div class="pied-in">'
        f'<div class="pied-col"><a class="brand" href="{racine}index.html">Parcours <b>actuariel</b></a><p>{t["pied"]}</p></div>'
        f'<nav class="pied-col" aria-label="{t["domaines"]}"><span class="eyebrow">{t["domaines"]}</span>{liens}</nav>'
        f'<nav class="pied-col" aria-label="{t["compte_t"]}"><span class="eyebrow">{t["compte_t"]}</span>'
        f'<a href="{racine}compte/index.html">{t["compte"]}</a><a href="{racine}compte/index.html#confidentialite">{t["confid"]}</a>'
        f'<a href="{autre}" lang="{"en" if langue == "fr" else "fr"}">{t["autre"]}</a>'
        f'<a href="https://github.com/JohnGAB7/parcours-actuariel">{t["source"]}</a></nav>'
        f'</div></footer>')


def plan_json(parcours: dict, titres: dict) -> str:
    """Course order with step counts, read by navigation.js to show progress and the "resume" target."""
    plan = [{"d": dom["id"], "m": m["id"], "s": sid, "n": titres[sid][0], "t": titres[sid][1]} for dom, m, sid in seances(parcours)]
    return json.dumps(plan, ensure_ascii=False).replace("</", "<\\/")


def page_accueil(parcours: dict, titres: dict, langue: str) -> str:
    t = TXT[langue]
    cartes = []
    for k, d in enumerate(parcours["domaines"], 1):
        n = sum(len(m.get("seances", [])) for m in d["modules"])
        etat = f'{t["seance"](n)} · {len(d["modules"])} {t["modules"]}' if n else f'{len(d["modules"])} {t["modules"]} · {t["bientot"]}'
        cartes.append(
            f'<a class="dom{"" if n else " futur"}" href="{d["id"]}/index.html" data-domaine="{d["id"]}">'
            f'<span class="dom-n mono">{k:02d}</span>'
            f'<span class="dom-t">{e(dom_titre(d, langue))}</span><span class="dom-en">{e(dom_sous(d, langue))}</span>'
            f'<span class="dom-a">{e(dom_accroche(d, langue))}</span>'
            f'<span class="dom-f"><span class="dom-s">{etat}</span><span class="barre" aria-hidden="true"><i></i></span></span></a>')
    premiere = next(seances(parcours))[2]
    sous_titre = parcours["sous_titre"] if langue == "fr" else parcours["sous_titre_en"]
    return (
        f'<section class="hero"><div class="hero-in gutter">'
        f'<span class="eyebrow">{t["eyebrow"]}</span><h1>{t["h1"]}</h1>'
        f'<p>{e(sous_titre)} {t["hero"]}</p>'
        f'<div class="hero-cta"><a class="cta" href="{premiere}/index.html" data-reprendre>{t["commencer"]} : {e(titres[premiere][1])} →</a>'
        f'<a class="cta-2" href="compte/index.html">{ICONE_COMPTE}{t["compte"]}</a></div>'
        f'</div></section>'
        f'<main class="home gutter">'
        f'<div class="home-head"><span class="eyebrow">{t["les_domaines"]}</span><h2>{t["h2"]}</h2><p class="lead">{e(t["lead"])}</p></div>'
        f'<div class="doms">{"".join(cartes)}</div></main>').replace("Start :", "Start:")


def page_domaine(parcours: dict, d: dict, k: int, langue: str) -> str:
    t = TXT[langue]
    lignes = []
    for m in d["modules"]:
        corps = f'<span class="mod-t">{e(mod_titre(m, langue))}</span><span class="mod-en">{e(mod_sous(m, langue))}</span>'
        if m.get("seances"):
            lignes.append(f'<li><a class="mod" href="../{m["id"]}/index.html" data-module="{m["id"]}"><span class="mod-c">{corps}</span>'
                          f'<span class="mod-s"><span class="mod-n">{t["seance"](len(m["seances"]))}</span>'
                          f'<span class="barre" aria-hidden="true"><i></i></span></span></a></li>')
        else:
            lignes.append(f'<li><span class="mod futur"><span class="mod-c">{corps}</span>'
                          f'<span class="mod-s"><span class="mod-n">{t["a_venir"]}</span></span></span></li>')
    autres = parcours["domaines"]
    suivant = autres[k] if k < len(autres) else None
    lien_suivant = (f'<a class="suite" href="../{suivant["id"]}/index.html"><span class="eyebrow">{t["suivant"]}</span>'
                    f'<span>{e(dom_titre(suivant, langue))} →</span></a>') if suivant else ""
    return (
        f'<main class="page gutter">'
        f'<nav class="fil" aria-label="{e(t["fil"])}"><a href="../index.html">{t["accueil"]}</a><span>/</span><span>{e(dom_titre(d, langue))}</span></nav>'
        f'<div class="page-head"><span class="eyebrow mono">{t["domaine"]} {k:02d}</span><h1>{e(dom_titre(d, langue))}</h1>'
        f'<p class="en">{e(dom_sous(d, langue))}</p><p class="lead">{e(dom_accroche(d, langue))}</p></div>'
        f'<ol class="mods-l">{"".join(lignes)}</ol>{lien_suivant}</main>')


def page_module(d: dict, m: dict, infos: dict, langue: str) -> str:
    t = TXT[langue]
    lignes = []
    for j, sid in enumerate(m["seances"], 1):
        s = infos[sid]
        sous = s["en"] if langue == "fr" else charger_seance(sid)["titre"]
        lignes.append(
            f'<li><a class="sea" href="../{sid}/index.html" data-seance="{sid}">'
            f'<span class="sea-n mono">{j:02d}</span>'
            f'<span class="sea-c"><span class="sea-t">{e(s["titre"])}</span><span class="sea-en">{e(sous)}</span></span>'
            f'<span class="sea-s"><span class="sea-d">{t["min_etapes"](s["duree"], len(s["etapes"]))}</span>'
            f'<span class="barre" aria-hidden="true"><i></i></span><span class="sea-x" data-etat>{t["commencer_f"]}</span></span></a></li>')
    code, nom = mod_titre(m, langue).split(" · ", 1)
    return (
        f'<main class="page gutter">'
        f'<nav class="fil" aria-label="{e(t["fil"])}"><a href="../index.html">{t["accueil"]}</a><span>/</span>'
        f'<a href="../{d["id"]}/index.html">{e(dom_titre(d, langue))}</a><span>/</span><span>{e(code)}</span></nav>'
        f'<div class="page-head"><span class="eyebrow">{t["module"]}</span><h1>{e(nom)}</h1>'
        f'<p class="en">{e(mod_sous(m, langue))}</p></div>'
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


def chemins(chemin: str, langue: str) -> tuple[str, str, str]:
    """For a page at <chemin>/ in <langue>: (base to the site root for assets, root of this language, same page in the other language)."""
    parties = [p for p in chemin.split("/") if p]
    profondeur = len(parties) + (1 if langue == "en" else 0)
    base = "../" * profondeur
    racine = base + ("en/" if langue == "en" else "")
    autre = base + ("" if langue == "en" else "en/") + (chemin + "/" if chemin else "") + "index.html"
    return base, racine, autre


def construire() -> None:
    parcours = charger_parcours()
    erreurs = []
    for _, _, sid in seances(parcours):
        erreurs += verifier_seance(charger_seance(sid)) + verifier_traduction(sid)
    if erreurs:
        sys.exit("\n".join(erreurs))
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    shutil.copytree(SITE / "assets", SORTIE / "assets")
    shutil.copytree(SITE / "vendor", SORTIE / "assets" / "vendor")
    (SORTIE / "assets" / "config.js").write_text(
        "window.PA_CONFIG = " + json.dumps(config_supabase()) + ";\n", encoding="utf-8")
    g_seance = Template((SITE / "gabarits" / "seance.html").read_text(encoding="utf-8"))
    g_page = Template((SITE / "gabarits" / "page.html").read_text(encoding="utf-8"))

    for langue in LANGUES:
        t = TXT[langue]
        sortie = SORTIE if langue == "fr" else SORTIE / langue
        infos = {}
        for dom, m, sid in seances(parcours):
            s = charger_seance(sid, langue)
            infos[sid] = s
            base, racine, autre = chemins(sid, langue)
            donnees = dict(s, accueil=racine + "index.html", module_url=racine + m["id"] + "/index.html",
                           module_titre=mod_titre(m, langue), domaine_titre=dom_titre(dom, langue))
            page = g_seance.substitute(
                titre=e(s["titre"]), base=base, accueil=donnees["accueil"], lang=langue, autre=autre,
                bascule=bascule(langue, autre), alt_fr=base + sid + "/index.html", alt_en=base + "en/" + sid + "/index.html", compte=t["compte"], racine=racine,
                progression=t["progression"], etapes=t["etapes"],
                donnees=json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/"))
            cible = sortie / sid / "index.html"
            cible.parent.mkdir(parents=True, exist_ok=True)
            cible.write_text(page, encoding="utf-8")
        plan = plan_json(parcours, {sid: (len(s["etapes"]), s["titre"]) for sid, s in infos.items()})
        titres = {sid: (len(s["etapes"]), s["titre"]) for sid, s in infos.items()}

        def ecrire(chemin, titre, description, contenu, actif="", classe=""):
            base, racine, autre = chemins(chemin, langue)
            cible = (sortie / chemin / "index.html") if chemin else sortie / "index.html"
            cible.parent.mkdir(parents=True, exist_ok=True)
            cible.write_text(g_page.substitute(
                titre=e(titre), description=e(description), base=base, classe=classe, plan=plan, lang=langue,
                alt_fr=base + (chemin + "/" if chemin else "") + "index.html",
                alt_en=base + "en/" + (chemin + "/" if chemin else "") + "index.html",
                entete=entete(parcours, racine, autre, langue, actif), contenu=contenu,
                pied=pied(parcours, racine, autre, langue)), encoding="utf-8")

        nom = parcours["titre"]
        ecrire("", nom, parcours["sous_titre"] if langue == "fr" else parcours["sous_titre_en"],
               page_accueil(parcours, titres, langue), classe="accueil")
        for k, d in enumerate(parcours["domaines"], 1):
            ecrire(d["id"], f'{dom_titre(d, langue)} · {nom}', dom_accroche(d, langue), page_domaine(parcours, d, k, langue), actif=d["id"])
            for m in d["modules"]:
                if m.get("seances"):
                    ecrire(m["id"], f'{mod_titre(m, langue)} · {nom}', mod_sous(m, langue), page_module(d, m, infos, langue), actif=d["id"])
        compte = (SITE / "gabarits" / ("compte.html" if langue == "fr" else "compte.en.html")).read_text(encoding="utf-8")
        ecrire("compte", f'{t["compte"]} · {nom}', t["compte_desc"], compte)
    (SORTIE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Site construit dans {SORTIE}")


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        p = charger_parcours()
        errs = [x for _, _, sid in seances(p) for x in verifier_seance(charger_seance(sid)) + verifier_traduction(sid)]
        sys.exit("\n".join(errs) if errs else 0)
    construire()
