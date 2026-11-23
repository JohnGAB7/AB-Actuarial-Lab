"""Structural validation for self-contained actuarial lesson reference sheets."""
from __future__ import annotations

import re
from typing import Any

FICHE_SECTIONS = (
    "vue_ensemble", "cours_complet", "methodes", "exemples_guides",
    "exercices_corriges", "applications_labs", "synthese_references",
)
OUTILS_FICHE = {"excel", "vba", "python", "r", "sans-code"}
NIVEAUX_FICHE = {"fondamental", "intermediaire", "avance"}
LIEN_INTERNE_FICHE = re.compile(r"^[a-z0-9][a-z0-9-]{1,19}/s[0-9]{2}(?:#[a-z0-9-]+)?$")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _unknown(mapping: dict, allowed: set[str], label: str) -> list[str]:
    return [f"{label}: clé inconnue {key!r}." for key in sorted(set(mapping) - allowed)]


def _textes(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value or not all(_text(item) for item in value):
        errors.append(f"{label}: une liste non vide de textes est requise.")


def _object(value: Any, label: str, allowed: set[str], required: tuple[str, ...], errors: list[str]) -> dict | None:
    if not isinstance(value, dict):
        errors.append(f"{label}: un objet YAML est requis.")
        return None
    errors.extend(_unknown(value, allowed, label))
    for key in required:
        if key not in value:
            errors.append(f"{label}: champ requis manquant « {key} ».")
    return value


def verifier_fiche(fiche: Any, *, session_id: str = "<inconnue>") -> list[str]:
    """Validate the optional lesson reference-sheet structure, not its scientific quality."""
    label = f"{session_id}.fiche"
    errors: list[str] = []
    root = _object(fiche, label, {"statut", *FICHE_SECTIONS}, ("statut",), errors)
    if root is None:
        return errors
    status = root.get("statut")
    if status not in {"brouillon", "prete"}:
        errors.append(f"{label}: « statut » doit valoir « brouillon » ou « prete ».")
        return errors
    if status == "prete":
        for section in FICHE_SECTIONS:
            if section not in root:
                errors.append(f"{label}: une fiche prête doit contenir l'onglet « {section} ».")

    overview = root.get("vue_ensemble")
    if overview is not None:
        part = _object(overview, f"{label}.vue_ensemble",
            {"question", "pourquoi", "objectifs", "prerequis", "carte", "duree_minutes"},
            ("question", "pourquoi", "objectifs", "prerequis", "carte", "duree_minutes"), errors)
        if part is not None:
            for key in ("question", "pourquoi"):
                if not _text(part.get(key)):
                    errors.append(f"{label}.vue_ensemble: « {key} » doit être un texte non vide.")
            for key in ("objectifs", "prerequis", "carte"):
                _textes(part.get(key), f"{label}.vue_ensemble.{key}", errors)
            duration = part.get("duree_minutes")
            if not _number(duration) or duration <= 0:
                errors.append(f"{label}.vue_ensemble: « duree_minutes » doit être strictement positif.")

    course = root.get("cours_complet")
    if course is not None:
        part = _object(course, f"{label}.cours_complet", {"sections"}, ("sections",), errors)
        if part is not None:
            sections = part.get("sections")
            if not isinstance(sections, list) or not sections:
                errors.append(f"{label}.cours_complet: « sections » doit être une liste non vide.")
            else:
                for index, section in enumerate(sections, 1):
                    where = f"{label}.cours_complet.sections[{index}]"
                    item = _object(section, where, {"titre", "contenu", "formules"}, ("titre", "contenu"), errors)
                    if item is not None:
                        for key in ("titre", "contenu"):
                            if not _text(item.get(key)):
                                errors.append(f"{where}: « {key} » doit être un texte non vide.")
                        formulas = item.get("formules", [])
                        if not isinstance(formulas, list):
                            errors.append(f"{where}: « formules » doit être une liste.")
                        else:
                            for formula_index, formula in enumerate(formulas, 1):
                                fw = f"{where}.formules[{formula_index}]"
                                fpart = _object(formula, fw, {"formule", "explication"}, ("formule", "explication"), errors)
                                if fpart is not None and not all(_text(fpart.get(key)) for key in ("formule", "explication")):
                                    errors.append(f"{fw}: formule et explication doivent être non vides.")

    methods = root.get("methodes")
    if methods is not None:
        part = _object(methods, f"{label}.methodes", {"methodes"}, ("methodes",), errors)
        if part is not None:
            values = part.get("methodes")
            if not isinstance(values, list) or not values:
                errors.append(f"{label}.methodes: au moins une méthode est requise.")
            else:
                for index, method in enumerate(values, 1):
                    where = f"{label}.methodes.methodes[{index}]"
                    item = _object(method, where, {"titre", "quand_utiliser", "etapes", "controles", "erreurs"},
                        ("titre", "quand_utiliser", "etapes", "controles", "erreurs"), errors)
                    if item is not None:
                        for key in ("titre", "quand_utiliser"):
                            if not _text(item.get(key)):
                                errors.append(f"{where}: « {key} » doit être un texte non vide.")
                        for key in ("etapes", "controles", "erreurs"):
                            _textes(item.get(key), f"{where}.{key}", errors)

    examples = root.get("exemples_guides")
    if examples is not None:
        part = _object(examples, f"{label}.exemples_guides", {"exemples"}, ("exemples",), errors)
        if part is not None:
            values = part.get("exemples")
            if not isinstance(values, list) or not values:
                errors.append(f"{label}.exemples_guides: au moins un exemple est requis.")
            else:
                for index, example in enumerate(values, 1):
                    where = f"{label}.exemples_guides.exemples[{index}]"
                    item = _object(example, where,
                        {"titre", "enonce", "raisonnement", "resultat", "interpretation", "controles"},
                        ("titre", "enonce", "raisonnement", "resultat", "interpretation", "controles"), errors)
                    if item is not None:
                        for key in ("titre", "enonce", "resultat", "interpretation"):
                            if not _text(item.get(key)):
                                errors.append(f"{where}: « {key} » doit être un texte non vide.")
                        for key in ("raisonnement", "controles"):
                            _textes(item.get(key), f"{where}.{key}", errors)

    exercises = root.get("exercices_corriges")
    if exercises is not None:
        part = _object(exercises, f"{label}.exercices_corriges", {"exercices"}, ("exercices",), errors)
        if part is not None:
            values = part.get("exercices")
            if not isinstance(values, list) or not values:
                errors.append(f"{label}.exercices_corriges: au moins un exercice est requis.")
            else:
                for index, exercise in enumerate(values, 1):
                    where = f"{label}.exercices_corriges.exercices[{index}]"
                    item = _object(exercise, where, {"titre", "niveau", "enonce", "corrige", "feedback"},
                        ("titre", "niveau", "enonce", "corrige", "feedback"), errors)
                    if item is not None:
                        for key in ("titre", "enonce", "feedback"):
                            if not _text(item.get(key)):
                                errors.append(f"{where}: « {key} » doit être un texte non vide.")
                        if item.get("niveau") not in NIVEAUX_FICHE:
                            errors.append(f"{where}: « niveau » doit être fondamental, intermediaire ou avance.")
                        _textes(item.get("corrige"), f"{where}.corrige", errors)

    applications = root.get("applications_labs")
    if applications is not None:
        part = _object(applications, f"{label}.applications_labs", {"applications"}, ("applications",), errors)
        if part is not None:
            values = part.get("applications")
            if not isinstance(values, list) or not values:
                errors.append(f"{label}.applications_labs: au moins une application est requise.")
            else:
                fields = ("entrees", "hypotheses", "procedure", "sorties", "validation", "limites")
                for index, application in enumerate(values, 1):
                    where = f"{label}.applications_labs.applications[{index}]"
                    allowed = {"titre", "contexte", "objectif", "outils", *fields}
                    item = _object(application, where, allowed, tuple(allowed), errors)
                    if item is not None:
                        for key in ("titre", "contexte", "objectif"):
                            if not _text(item.get(key)):
                                errors.append(f"{where}: « {key} » doit être un texte non vide.")
                        tools = item.get("outils")
                        if not isinstance(tools, list) or any(tool not in OUTILS_FICHE for tool in tools):
                            errors.append(f"{where}: « outils » doit être une liste d'outils reconnus.")
                        for key in fields:
                            _textes(item.get(key), f"{where}.{key}", errors)

    summary = root.get("synthese_references")
    if summary is not None:
        part = _object(summary, f"{label}.synthese_references",
            {"memo", "glossaire", "maitrise", "liens", "references"},
            ("memo", "glossaire", "maitrise", "references"), errors)
        if part is not None:
            for key in ("memo", "maitrise"):
                _textes(part.get(key), f"{label}.synthese_references.{key}", errors)
            glossary = part.get("glossaire")
            if not isinstance(glossary, list) or not glossary:
                errors.append(f"{label}.synthese_references: « glossaire » doit être une liste non vide.")
            else:
                for index, term in enumerate(glossary, 1):
                    where = f"{label}.synthese_references.glossaire[{index}]"
                    item = _object(term, where, {"terme_fr", "terme_en", "definition"},
                        ("terme_fr", "terme_en", "definition"), errors)
                    if item is not None and not all(_text(item.get(key)) for key in ("terme_fr", "terme_en", "definition")):
                        errors.append(f"{where}: les deux termes et la définition doivent être non vides.")
            links = part.get("liens", [])
            if not isinstance(links, list):
                errors.append(f"{label}.synthese_references: « liens » doit être une liste.")
            else:
                for index, link in enumerate(links, 1):
                    where = f"{label}.synthese_references.liens[{index}]"
                    item = _object(link, where, {"titre", "cible"}, ("titre", "cible"), errors)
                    if item is not None:
                        if not _text(item.get("titre")):
                            errors.append(f"{where}: « titre » doit être un texte non vide.")
                        if not isinstance(item.get("cible"), str) or not LIEN_INTERNE_FICHE.fullmatch(item["cible"]):
                            errors.append(f"{where}: « cible » doit être une référence interne domaine/sNN sûre.")
            references = part.get("references")
            if not isinstance(references, list) or not references:
                errors.append(f"{label}.synthese_references: au moins une référence annotée est requise.")
            else:
                for index, reference in enumerate(references, 1):
                    where = f"{label}.synthese_references.references[{index}]"
                    item = _object(reference, where, {"titre", "detail", "url", "annee"}, ("titre", "detail"), errors)
                    if item is not None:
                        for key in ("titre", "detail"):
                            if not _text(item.get(key)):
                                errors.append(f"{where}: « {key} » doit être un texte non vide.")
                        if "url" in item and (not _text(item["url"]) or not item["url"].startswith("https://")):
                            errors.append(f"{where}: « url » doit être une URL HTTPS.")
                        year = item.get("annee")
                        if "annee" in item and (not isinstance(year, int) or isinstance(year, bool) or not 1800 <= year <= 2200):
                            errors.append(f"{where}: « annee » doit être une année entière plausible.")
    return errors
