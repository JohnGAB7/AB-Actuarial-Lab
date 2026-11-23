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
    for bloc in parcours["blocs"]:
        for m in bloc["modules"]:
            for sid in m.get("seances", []):
                yield bloc, m, sid


def blocs_html(parcours: dict) -> str:
    out = []
    for b in parcours["blocs"]:
        lignes = []
        for m in b["modules"]:
            t = f'<span class="t">{html.escape(m["titre"])}<small>{html.escape(m["en"])}</small></span>'
            if m.get("seances"):
                lien = f'{m["seances"][0]}/index.html'
                lignes.append(f'<li><a href="{lien}">{t}<span class="s">Commencer →</span></a></li>')
            else:
                lignes.append(f'<li><span>{t}<span class="s">à venir</span></span></li>')
        out.append(
            f'<section class="bloc"><div class="bloc-h"><h3>{html.escape(b["titre"])}</h3>'
            f'<span>{html.escape(b["periode"])} · <i>{html.escape(b["en"])}</i></span></div>'
            f'<ul class="mods">{"".join(lignes)}</ul></section>'
        )
    return "".join(out)


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
    (SORTIE / "compte").mkdir()
    shutil.copy(SITE / "gabarits" / "compte.html", SORTIE / "compte" / "index.html")
    g_seance = Template((SITE / "gabarits" / "seance.html").read_text(encoding="utf-8"))
    g_accueil = Template((SITE / "gabarits" / "accueil.html").read_text(encoding="utf-8"))
    erreurs, premiere = [], None
    for bloc, m, sid in seances(parcours):
        s = charger_seance(sid)
        erreurs += verifier_seance(s)
        premiere = premiere or (sid, s["titre"])
        profondeur = "../" * (sid.count("/") + 1)
        s["accueil"] = profondeur + "index.html"
        s["module_titre"] = m["titre"]
        donnees = json.dumps(s, ensure_ascii=False).replace("</", "<\\/")
        page = g_seance.substitute(titre=html.escape(s["titre"]), base=profondeur, donnees=donnees, accueil=s["accueil"])
        cible = SORTIE / sid / "index.html"
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(page, encoding="utf-8")
    if erreurs:
        sys.exit("\n".join(erreurs))
    SORTIE.mkdir(exist_ok=True)
    (SORTIE / "index.html").write_text(
        g_accueil.substitute(
            sous_titre=html.escape(parcours["sous_titre"]), blocs=blocs_html(parcours),
            reprendre=f"{premiere[0]}/index.html", reprendre_titre=html.escape(premiere[1]),
        ),
        encoding="utf-8",
    )
    (SORTIE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Site construit dans {SORTIE}")


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        p = charger_parcours()
        errs = [e for _, _, sid in seances(p) for e in verifier_seance(charger_seance(sid))]
        sys.exit("\n".join(errs) if errs else 0)
    construire()
