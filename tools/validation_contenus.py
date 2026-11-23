"""Validate the course plan and YAML sessions before they reach the site generator.

Run with: python -m tools.validation_contenus
The validator is deliberately additive: it keeps the existing YAML format and
reports malformed structures without rewriting or normalizing course content.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "contenus"
SESSION_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*/[a-z0-9][a-z0-9_-]*$")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _positive_number(value: Any) -> bool:
    return _number(value) and value > 0


def _unknown_keys(mapping: dict, allowed: set[str], label: str) -> list[str]:
    """Report schema keys that are not recognized at this mapping level."""
    return [
        f"{label}: clé inconnue {key!r}."
        for key in sorted(set(mapping) - allowed)
    ]


def _safe_session_path(session_id: Any) -> Path | None:
    if not isinstance(session_id, str) or not SESSION_ID.fullmatch(session_id):
        return None
    path = (CONTENT_DIR / f"{session_id}.yaml").resolve()
    return path if path.is_relative_to(CONTENT_DIR.resolve()) else None


def _safe_exercise_path(value: Any) -> Path | None:
    if not _text(value) or "\\" in value:
        return None
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != ("exercices",):
        return None
    path = (ROOT / relative).resolve()
    exercise_root = (ROOT / "exercices").resolve()
    return path if path.is_relative_to(exercise_root) else None



# Fields whose meaning is not linguistic and must remain in the French source.
# "formule" is the sole exception: only its \text{...} labels may be translated.
NON_TRADUISIBLES = {
    "id", "module", "en", "actu_basics", "type", "minutes", "duree", "table", "taux",
    "reponse", "valeur", "tolerance", "cle", "expr", "fichier", "depart", "interactif",
    "url", "cartes", "statut", "formule",
}


def _nombres_texte(texte: str, langue: str) -> list[str]:
    """Extract numeric tokens while normalizing French/English separators.

    Signs, exponents, percentages and per-mille units remain part of each token.
    """
    value = texte.replace("{,}", ",")
    value = re.sub(r"\\\\,\\s*(?=\\\\?[%‰])", " ", value)
    value = re.sub(r"(?<=\\d)(?:\\\\,|\\\\ |\\u202f|\\u00a0| )(?=\\d{3}\\b)", "", value)
    if langue == "fr":
        value = re.sub(r"(?<=\\d),(?=\\d)", ".", value)
    else:
        value = re.sub(r"(?<=\\d),(?=\\d{3}\\b)", "", value)
    pattern = r"(?:(?<![\\w.])[+\\-−])?(?<![\\d.])\\d+(?:\\.\\d+)?(?:[eE][+\\-−]?\\d+)?(?:\\s*\\\\?[%‰])?"
    return sorted(
        token.replace("−", "-").replace(" ", "").replace(r"\\%", "%")
        for token in re.findall(pattern, value)
    )


def _formule_sans_libelles(formule: str) -> str:
    """Blank translatable LaTeX text labels while preserving mathematical structure."""
    return re.sub(r"\\\\text\\{[^{}]*\\}", r"\\\\text{}", formule)


def fusionner_overlay(base: Any, overlay: Any, chemin: str = "séance") -> Any:
    """Merge a sparse English overlay after enforcing its structural contract."""
    if isinstance(overlay, dict):
        if not isinstance(base, dict):
            raise ValueError(f"{chemin} : structure différente du français")
        merged = dict(base)
        for key, value in overlay.items():
            if key not in base:
                raise ValueError(f"{chemin}.{key} : clé absente du français")
            if key in NON_TRADUISIBLES and key != "formule":
                raise ValueError(f"{chemin}.{key} : ce champ reste dans le fichier français")
            if key == "formule":
                if not isinstance(base[key], str) or not isinstance(value, str):
                    raise ValueError(f"{chemin}.{key} : la formule doit rester un texte")
                if _formule_sans_libelles(value) != _formule_sans_libelles(base[key]):
                    raise ValueError(f"{chemin}.{key} : une formule ne peut changer que ses \\\\text{{…}}")
                merged[key] = value
            else:
                merged[key] = fusionner_overlay(base[key], value, f"{chemin}.{key}")
        return merged
    if isinstance(overlay, list):
        if not isinstance(base, list) or len(base) != len(overlay):
            raise ValueError(f"{chemin} : liste de longueur différente du français")
        return [
            fusionner_overlay(original, translated, f"{chemin}[{index}]")
            for index, (original, translated) in enumerate(zip(base, overlay))
        ]
    if type(overlay) is not type(base):
        raise ValueError(f"{chemin} : type différent du français")
    if isinstance(overlay, str):
        if base.strip() and not overlay.strip():
            raise ValueError(f"{chemin} : texte vide")
        if _nombres_texte(overlay, "en") != _nombres_texte(base, "fr"):
            raise ValueError(
                f"{chemin} : chiffres différents du français "
                f"({_nombres_texte(base, 'fr')} ≠ {_nombres_texte(overlay, 'en')})"
            )
    return overlay


def _contient_texte_a_traduire(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            _contient_texte_a_traduire(child)
            for key, child in value.items()
            if key not in NON_TRADUISIBLES
        )
    if isinstance(value, list):
        return any(_contient_texte_a_traduire(child) for child in value)
    if isinstance(value, str):
        without_markup = re.sub(r"\\$[^$]*\\$|<[^>]+>", "", value)
        return bool(re.search(r"[a-zà-ÿ]{4,}", without_markup))
    return False


def verifier_overlay_traduction(
    session: Any, overlay: Any, *, session_id: str = "<inconnue>"
) -> list[str]:
    """Validate an English overlay and report translatable French text it omits."""
    if not isinstance(overlay, dict):
        return [f"{session_id} : l'overlay anglais doit être un objet YAML (mapping)."]
    try:
        fusionner_overlay(session, overlay, session_id)
    except (TypeError, ValueError) as exc:
        return [str(exc)]

    missing: list[str] = []

    def inspect(original: Any, translated: Any, path: str) -> None:
        if isinstance(original, dict):
            if not isinstance(translated, dict):
                if _contient_texte_a_traduire(original):
                    missing.append(path)
                return
            for key, value in original.items():
                if key in NON_TRADUISIBLES:
                    continue
                if key not in translated:
                    if _contient_texte_a_traduire(value):
                        missing.append(f"{path}.{key}")
                else:
                    inspect(value, translated[key], f"{path}.{key}")
        elif isinstance(original, list):
            if not isinstance(translated, list) or len(original) != len(translated):
                return  # The structural error is already reported by fusionner_overlay.
            for index, (left, right) in enumerate(zip(original, translated)):
                inspect(left, right, f"{path}[{index}]")

    inspect(session, overlay, session_id)
    return [f"{path} : texte non traduit" for path in missing]

def verifier_seance(session: Any, *, session_id: str = "<inconnue>") -> list[str]:
    """Return all structural errors found in one session mapping."""
    errors: list[str] = []
    if not isinstance(session, dict):
        return [f"{session_id}: la séance doit être un objet YAML (mapping)."]

    errors.extend(_unknown_keys(
        session,
        {"id", "module", "titre", "en", "duree", "taux", "table", "actu_basics", "etapes"},
        session_id,
    ))
    table = session.get("table")
    if table is not None:
        if not isinstance(table, dict):
            errors.append(f"{session_id}: « table » doit être un objet YAML.")
        else:
            errors.extend(_unknown_keys(table, {"nom", "k", "s", "g", "c", "omega"}, f"{session_id}.table"))
    actu_basics = session.get("actu_basics")
    if actu_basics is not None:
        if not isinstance(actu_basics, dict):
            errors.append(f"{session_id}: « actu_basics » doit être un objet YAML.")
        else:
            errors.extend(_unknown_keys(
                actu_basics, {"episode", "statut", "accroche_fr", "accroche_en"}, f"{session_id}.actu_basics"
            ))

    for key in ("id", "module", "titre", "en", "duree", "etapes"):
        if key not in session:
            errors.append(f"{session_id}: champ requis manquant « {key} ».")

    if not _text(session.get("id")):
        errors.append(f"{session_id}: « id » doit être un texte non vide.")
    elif SESSION_ID.fullmatch(session["id"]) is None:
        errors.append(f"{session_id}: « id » doit suivre le format domaine/seance.")
    if not _text(session.get("module")):
        errors.append(f"{session_id}: « module » doit être un texte non vide.")
    elif _text(session.get("id")) and session["id"].split("/", 1)[0] != session["module"]:
        errors.append(f"{session_id}: « module » ne correspond pas au préfixe de « id ».")
    for key in ("titre", "en"):
        if not _text(session.get(key)):
            errors.append(f"{session_id}: « {key} » doit être un texte non vide.")
    if not _positive_number(session.get("duree")):
        errors.append(f"{session_id}: « duree » doit être un nombre strictement positif.")

    steps = session.get("etapes")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{session_id}: « etapes » doit être une liste non vide.")
        return errors

    for index, step in enumerate(steps, 1):
        label = f"{session_id}, étape {index}"
        if not isinstance(step, dict):
            errors.append(f"{label}: chaque étape doit être un objet YAML.")
            continue

        step_type = step.get("type")
        if not isinstance(step_type, str) or step_type not in {"video", "rappel", "quiz", "calcul", "code", "vocabulaire"}:
            errors.append(f"{label}: type d'étape inconnu {step_type!r}.")
            continue
        step_keys = {
            "video": {"type", "titre", "minutes", "texte"},
            "rappel": {"type", "titre", "minutes", "blocs"},
            "quiz": {"type", "titre", "minutes", "intro", "questions"},
            "calcul": {"type", "titre", "minutes", "intro", "donnees", "champs", "solution"},
            "code": {"type", "titre", "minutes", "intro", "fichier", "depart", "tests"},
            "vocabulaire": {"type", "titre", "minutes", "intro", "cartes"},
        }[step_type]
        errors.extend(_unknown_keys(step, step_keys, label))
        if not _text(step.get("titre")):
            errors.append(f"{label}: « titre » doit être un texte non vide.")
        if not _positive_number(step.get("minutes")):
            errors.append(f"{label}: « minutes » doit être un nombre strictement positif.")

        if step_type == "video":
            if not _text(step.get("texte")):
                errors.append(f"{label}: « texte » est requis pour une vidéo.")

        elif step_type == "rappel":
            blocks = step.get("blocs")
            if not isinstance(blocks, list) or not blocks:
                errors.append(f"{label}: « blocs » doit être une liste non vide.")
                continue
            for block_index, block in enumerate(blocks, 1):
                block_label = f"{label}, bloc {block_index}"
                if not isinstance(block, dict):
                    errors.append(f"{block_label}: le bloc doit être un objet YAML.")
                    continue
                errors.extend(_unknown_keys(
                    block, {"p", "formule", "note", "interactif", "sources"}, block_label
                ))
                recognized = {"p", "formule", "note", "interactif", "sources"}
                if not recognized.intersection(block):
                    errors.append(f"{block_label}: aucun champ de contenu reconnu.")
                for key in ("p", "formule", "note", "interactif"):
                    if key in block and not _text(block[key]):
                        errors.append(f"{block_label}: « {key} » doit être un texte non vide.")
                if "sources" in block:
                    sources = block["sources"]
                    if not isinstance(sources, list):
                        errors.append(f"{block_label}: « sources » doit être une liste.")
                    else:
                        for source_index, source in enumerate(sources, 1):
                            source_label = f"{block_label}, source {source_index}"
                            if not isinstance(source, dict):
                                errors.append(f"{source_label}: la source doit être un objet YAML.")
                                continue
                            errors.extend(_unknown_keys(source, {"titre", "detail", "url"}, source_label))
                            if not _text(source.get("titre")) or not _text(source.get("detail")):
                                errors.append(f"{source_label}: « titre » et « detail » sont requis.")
                            elif "url" in source and not _text(source["url"]):
                                errors.append(f"{source_label}: « url » doit être un texte non vide.")

        elif step_type == "quiz":
            if not _text(step.get("intro")):
                errors.append(f"{label}: « intro » est requis pour un quiz.")
            questions = step.get("questions")
            if not isinstance(questions, list) or not questions:
                errors.append(f"{label}: « questions » doit être une liste non vide.")
                continue
            for question_index, question in enumerate(questions, 1):
                question_label = f"{label}, question {question_index}"
                if not isinstance(question, dict):
                    errors.append(f"{question_label}: la question doit être un objet YAML.")
                    continue
                errors.extend(_unknown_keys(question, {"q", "options", "reponse", "pourquoi"}, question_label))
                if not _text(question.get("q")):
                    errors.append(f"{question_label}: « q » doit être un texte non vide.")
                options = question.get("options")
                if not isinstance(options, list) or len(options) < 2 or not all(_text(option) for option in options):
                    errors.append(f"{question_label}: « options » doit contenir au moins deux textes non vides.")
                answer = question.get("reponse")
                if not isinstance(answer, int) or isinstance(answer, bool) or not isinstance(options, list) or not 0 <= answer < len(options):
                    errors.append(f"{question_label}: « reponse » doit désigner un index d'option existant.")
                explanation = question.get("pourquoi")
                if not isinstance(explanation, dict) or not all(_text(explanation.get(key)) for key in ("rappel", "formule", "exemple")):
                    errors.append(f"{question_label}: « pourquoi » doit contenir rappel, formule et exemple.")
                else:
                    errors.extend(_unknown_keys(
                        explanation, {"rappel", "formule", "exemple", "piege"}, f"{question_label}.pourquoi"
                    ))

        elif step_type == "calcul":
            if not _text(step.get("intro")):
                errors.append(f"{label}: « intro » est requis pour un calcul.")
            data = step.get("donnees")
            if not isinstance(data, dict):
                errors.append(f"{label}: « donnees » doit être un objet YAML.")
            else:
                errors.extend(_unknown_keys(data, {"entetes", "lignes"}, f"{label}.donnees"))
                headers, rows = data.get("entetes"), data.get("lignes")
                if not isinstance(headers, list) or not headers or not all(_text(item) for item in headers):
                    errors.append(f"{label}: « donnees.entetes » doit être une liste de textes non vides.")
                if not isinstance(rows, list) or not rows:
                    errors.append(f"{label}: « donnees.lignes » doit être une liste non vide.")
                elif isinstance(headers, list):
                    for row_index, row in enumerate(rows, 1):
                        if not isinstance(row, list) or len(row) != len(headers):
                            errors.append(f"{label}: la ligne {row_index} doit avoir autant de cellules que d'en-têtes.")
            fields = step.get("champs")
            if not isinstance(fields, list) or not fields:
                errors.append(f"{label}: « champs » doit être une liste non vide.")
            else:
                seen_keys: set[str] = set()
                for field_index, field in enumerate(fields, 1):
                    field_label = f"{label}, champ {field_index}"
                    if not isinstance(field, dict):
                        errors.append(f"{field_label}: le champ doit être un objet YAML.")
                        continue
                    errors.extend(_unknown_keys(
                        field, {"cle", "libelle", "valeur", "tolerance"}, field_label
                    ))
                    key = field.get("cle")
                    if not _text(key) or key in seen_keys:
                        errors.append(f"{field_label}: « cle » doit être un texte non vide et unique.")
                    else:
                        seen_keys.add(key)
                    if not _text(field.get("libelle")):
                        errors.append(f"{field_label}: « libelle » doit être un texte non vide.")
                    if not _number(field.get("valeur")):
                        errors.append(f"{field_label}: « valeur » doit être un nombre fini.")
                    tolerance = field.get("tolerance")
                    if not _number(tolerance) or tolerance < 0:
                        errors.append(f"{field_label}: « tolerance » doit être un nombre fini positif ou nul.")
            if not _text(step.get("solution")):
                errors.append(f"{label}: « solution » doit être un texte non vide.")

        elif step_type == "code":
            if not _text(step.get("intro")):
                errors.append(f"{label}: « intro » est requis pour un exercice de code.")
            if not _text(step.get("depart")):
                errors.append(f"{label}: « depart » doit être un texte non vide.")
            exercise = _safe_exercise_path(step.get("fichier"))
            if exercise is None:
                errors.append(f"{label}: « fichier » doit être un chemin relatif sûr sous exercices/.")
            elif not exercise.is_file():
                errors.append(f"{label}: fichier d'exercice introuvable : {step['fichier']!r}.")
            tests = step.get("tests")
            if not isinstance(tests, list) or not tests:
                errors.append(f"{label}: « tests » doit être une liste non vide.")
            else:
                for test_index, test in enumerate(tests, 1):
                    test_label = f"{label}, test {test_index}"
                    if not isinstance(test, dict):
                        errors.append(f"{test_label}: le test doit être un objet YAML.")
                        continue
                    errors.extend(_unknown_keys(test, {"nom", "expr"}, test_label))
                    if not _text(test.get("nom")) or not _text(test.get("expr")):
                        errors.append(f"{test_label}: « nom » et « expr » sont requis.")

        elif step_type == "vocabulaire":
            if not _text(step.get("intro")):
                errors.append(f"{label}: « intro » est requis pour le vocabulaire.")
            cards = step.get("cartes")
            if not isinstance(cards, list) or not cards:
                errors.append(f"{label}: « cartes » doit être une liste non vide.")
            else:
                for card_index, card in enumerate(cards, 1):
                    if not isinstance(card, list) or len(card) != 3 or not all(_text(item) for item in card):
                        errors.append(f"{label}, carte {card_index}: trois textes non vides sont requis.")

    return errors


def verifier_parcours(plan: Any) -> list[str]:
    """Validate domain/module identifiers and every plan-to-session reference."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["parcours.yaml: la racine doit être un objet YAML."]
    errors.extend(_unknown_keys(plan, {"titre", "sous_titre", "sous_titre_en", "domaines"}, "parcours.yaml"))
    for key in ("titre", "sous_titre", "domaines"):
        if key not in plan:
            errors.append(f"parcours.yaml: champ requis manquant « {key} ».")
    for key in ("titre", "sous_titre"):
        if not _text(plan.get(key)):
            errors.append(f"parcours.yaml: « {key} » doit être un texte non vide.")

    domains = plan.get("domaines")
    if not isinstance(domains, list) or not domains:
        return errors + ["parcours.yaml: « domaines » doit être une liste non vide."]

    domain_ids: set[str] = set()
    module_ids: set[str] = set()
    session_ids: set[str] = set()
    for domain_index, domain in enumerate(domains, 1):
        label = f"parcours.yaml, domaine {domain_index}"
        if not isinstance(domain, dict):
            errors.append(f"{label}: le domaine doit être un objet YAML.")
            continue
        errors.extend(_unknown_keys(
            domain, {"id", "titre", "en", "accroche", "accroche_en", "modules"}, label
        ))
        domain_id = domain.get("id")
        if not _text(domain_id) or domain_id in domain_ids:
            errors.append(f"{label}: « id » doit être un texte non vide et unique.")
        else:
            domain_ids.add(domain_id)
        for key in ("titre", "en", "accroche"):
            if not _text(domain.get(key)):
                errors.append(f"{label}: « {key} » doit être un texte non vide.")
        modules = domain.get("modules")
        if not isinstance(modules, list):
            errors.append(f"{label}: « modules » doit être une liste.")
            continue
        for module_index, module in enumerate(modules, 1):
            module_label = f"{label}, module {module_index}"
            if not isinstance(module, dict):
                errors.append(f"{module_label}: le module doit être un objet YAML.")
                continue
            errors.extend(_unknown_keys(module, {"id", "titre", "en", "seances"}, module_label))
            module_id = module.get("id")
            if not _text(module_id) or module_id in module_ids:
                errors.append(f"{module_label}: « id » doit être un texte non vide et unique.")
            else:
                module_ids.add(module_id)
            for key in ("titre", "en"):
                if not _text(module.get(key)):
                    errors.append(f"{module_label}: « {key} » doit être un texte non vide.")
            session_refs = module.get("seances", [])
            if not isinstance(session_refs, list):
                errors.append(f"{module_label}: « seances » doit être une liste.")
                continue
            for session_id in session_refs:
                if not isinstance(session_id, str) or session_id in session_ids:
                    errors.append(f"{module_label}: référence de séance invalide ou dupliquée {session_id!r}.")
                    continue
                session_ids.add(session_id)
                path = _safe_session_path(session_id)
                if path is None:
                    errors.append(f"{module_label}: chemin de séance invalide {session_id!r}.")
                    continue
                if not path.is_file():
                    errors.append(f"{module_label}: fichier de séance introuvable {session_id!r}.")
                    continue
                try:
                    session = yaml.safe_load(path.read_text(encoding="utf-8"))
                except (OSError, yaml.YAMLError) as exc:
                    errors.append(f"{session_id}: impossible de lire le YAML ({exc}).")
                    continue
                errors.extend(verifier_seance(session, session_id=session_id))
                if isinstance(session, dict):
                    if session.get("id") != session_id:
                        errors.append(f"{session_id}: l'« id » du fichier ne correspond pas à sa référence dans le plan.")
                    if session.get("module") != module_id:
                        errors.append(f"{session_id}: le module de la séance ne correspond pas au module du plan.")
                    # The English layer is optional for French-only deployments. Once the
                    # contents/en directory exists, every referenced session must have an overlay.
                    english_path = CONTENT_DIR / "en" / f"{session_id}.yaml"
                    if (CONTENT_DIR / "en").is_dir():
                        if not english_path.is_file():
                            errors.append(
                                f"{session_id}: traduction anglaise manquante "
                                f"(contenus/en/{session_id}.yaml)."
                            )
                        else:
                            try:
                                overlay = yaml.safe_load(english_path.read_text(encoding="utf-8"))
                            except (OSError, yaml.YAMLError) as exc:
                                errors.append(f"{session_id}: impossible de lire l'overlay anglais ({exc}).")
                            else:
                                errors.extend(
                                    verifier_overlay_traduction(session, overlay, session_id=session_id)
                                )

    return errors


def verifier_depot() -> list[str]:
    """Validate the course plan and all sessions referenced by it."""
    plan_path = CONTENT_DIR / "parcours.yaml"
    try:
        plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"parcours.yaml: impossible de lire le YAML ({exc})."]
    return verifier_parcours(plan)


def main() -> int:
    errors = verifier_depot()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Course plan and referenced sessions are structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
