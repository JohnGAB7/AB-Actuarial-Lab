"""Regression tests for strict course-content validation."""
import yaml

import tools.validation_contenus as validation
from tools.validation_contenus import (
    fusionner_overlay,
    verifier_depot,
    verifier_overlay_traduction,
    verifier_parcours,
    verifier_seance,
)


def valid_session():
    return {
        "id": "a1/s01",
        "module": "a1",
        "titre": "Session title",
        "en": "Session title",
        "duree": 25,
        "etapes": [
            {
                "type": "video",
                "titre": "Introduction",
                "minutes": 3,
                "texte": "A short introduction.",
            }
        ],
    }


def test_existing_course_plan_and_sessions_are_valid():
    assert verifier_depot() == []


def test_session_requires_core_metadata_and_a_nonempty_step_list():
    session = valid_session()
    del session["titre"]
    session["etapes"] = []
    errors = verifier_seance(session, session_id="fixture")
    assert any("titre" in error for error in errors)
    assert any("etapes" in error for error in errors)


def test_quiz_rejects_an_answer_index_outside_the_options():
    session = valid_session()
    session["etapes"] = [
        {
            "type": "quiz",
            "titre": "Check",
            "minutes": 2,
            "intro": "Choose one answer.",
            "questions": [
                {
                    "q": "Question?",
                    "options": ["A", "B"],
                    "reponse": 2,
                    "pourquoi": {
                        "rappel": "Recall.",
                        "formule": "x = 1",
                        "exemple": "Example.",
                    },
                }
            ],
        }
    ]
    errors = verifier_seance(session, session_id="fixture")
    assert any("index d'option existant" in error for error in errors)


def test_calculation_rejects_table_rows_with_inconsistent_width():
    session = valid_session()
    session["etapes"] = [
        {
            "type": "calcul",
            "titre": "Calculation",
            "minutes": 5,
            "intro": "Calculate the result.",
            "donnees": {"entetes": ["x", "y"], "lignes": [["1"]]},
            "champs": [
                {"cle": "result", "libelle": "Result", "valeur": 1.0, "tolerance": 0.01}
            ],
            "solution": "The result is one.",
        }
    ]
    errors = verifier_seance(session, session_id="fixture")
    assert any("autant de cellules" in error for error in errors)


def test_code_step_rejects_paths_outside_the_exercise_directory():
    session = valid_session()
    session["etapes"] = [
        {
            "type": "code",
            "titre": "Python",
            "minutes": 5,
            "intro": "Write code.",
            "fichier": "exercices/../../private.py",
            "depart": "pass",
            "tests": [{"nom": "test", "expr": "True"}],
        }
    ]
    errors = verifier_seance(session, session_id="fixture")
    assert any("chemin relatif sûr" in error for error in errors)


def test_plan_identifiers_match_progress_storage_format():
    plan = {
        "titre": "Course",
        "sous_titre": "Subtitle",
        "sous_titre_en": "Subtitle",
        "domaines": [
            {
                "id": "foundations_core",
                "titre": "Foundations",
                "en": "Foundations",
                "accroche": "Introduction",
                "accroche_en": "Introduction",
                "modules": [
                    {"id": "a1_core", "titre": "Module", "en": "Module", "seances": []}
                ],
            }
        ],
    }

    errors = verifier_parcours(plan)

    assert any("identifiant de domaine invalide" in error for error in errors)
    assert any("identifiant de module invalide" in error for error in errors)


def test_plan_requires_english_home_and_domain_copy_for_bilingual_build():
    plan = {
        "titre": "Course",
        "sous_titre": "Subtitle",
        "domaines": [
            {
                "id": "foundations",
                "titre": "Foundations",
                "en": "Foundations",
                "accroche": "Introduction",
                "modules": [
                    {"id": "a1", "titre": "Module", "en": "Module", "seances": []}
                ],
            }
        ],
    }

    errors = verifier_parcours(plan)

    assert any("sous_titre_en" in error for error in errors)
    assert any("accroche_en" in error for error in errors)


def test_session_identifiers_match_progress_storage_format():
    session = valid_session()
    session["id"] = "a1/session_1"

    errors = verifier_seance(session, session_id="fixture")

    assert any("format domaine/seance" in error for error in errors)


def test_plan_rejects_duplicate_session_references():
    plan = {
        "titre": "Course",
        "sous_titre": "Subtitle",
        "domaines": [
            {
                "id": "foundations",
                "titre": "Foundations",
                "en": "Foundations",
                "accroche": "Introduction",
                "modules": [
                    {"id": "a1", "titre": "Module", "en": "Module", "seances": ["a1/s01", "a1/s01"]}
                ],
            }
        ],
    }
    errors = verifier_parcours(plan)
    assert any("dupliquée" in error for error in errors)


def test_plan_rejects_unsafe_domain_and_module_path_identifiers():
    plan = {
        "titre": "Course",
        "sous_titre": "Subtitle",
        "domaines": [
            {
                "id": 'foundations" onclick="alert(1)',
                "titre": "Foundations",
                "en": "Foundations",
                "accroche": "Introduction",
                "modules": [
                    {
                        "id": "../outside",
                        "titre": "Module",
                        "en": "Module",
                        "seances": [],
                    }
                ],
            }
        ],
    }

    errors = verifier_parcours(plan)

    assert any("identifiant de domaine invalide" in error for error in errors)
    assert any("identifiant de module invalide" in error for error in errors)


def test_session_rejects_unknown_top_level_key():
    session = valid_session()
    session["tauxx"] = 0.025

    errors = verifier_seance(session, session_id="fixture")

    assert any("clé inconnue 'tauxx'" in error for error in errors)


def test_step_rejects_unknown_key():
    session = valid_session()
    session["etapes"][0]["minuts"] = 3

    errors = verifier_seance(session, session_id="fixture")

    assert any("clé inconnue 'minuts'" in error for error in errors)


def test_quiz_rejects_unknown_question_and_explanation_keys():
    session = valid_session()
    session["etapes"] = [
        {
            "type": "quiz",
            "titre": "Check",
            "minutes": 2,
            "intro": "Choose one answer.",
            "questions": [
                {
                    "q": "Question?",
                    "options": ["A", "B"],
                    "reponse": 0,
                    "reponse_correcte": 1,
                    "pourquoi": {
                        "rappel": "Recall.",
                        "formule": "x = 1",
                        "exemple": "Example.",
                        "explication": "Unexpected field.",
                    },
                }
            ],
        }
    ]

    errors = verifier_seance(session, session_id="fixture")

    assert any("clé inconnue 'reponse_correcte'" in error for error in errors)
    assert any("clé inconnue 'explication'" in error for error in errors)


def test_recall_blocks_and_sources_reject_unknown_keys():
    session = valid_session()
    session["etapes"] = [
        {
            "type": "rappel",
            "titre": "Recap",
            "minutes": 5,
            "blocs": [
                {
                    "p": "Text.",
                    "paragraphe": "Unexpected.",
                    "sources": [{"titre": "Book", "detail": "Chapter 1", "href": "https://example.org"}],
                }
            ],
        }
    ]

    errors = verifier_seance(session, session_id="fixture")

    assert any("clé inconnue 'paragraphe'" in error for error in errors)
    assert any("clé inconnue 'href'" in error for error in errors)


def test_plan_rejects_unknown_keys_at_each_level():
    plan = {
        "titre": "Course",
        "sous_titre": "Subtitle",
        "sous_titre_en": "Subtitle",
        "extra": "Unexpected",
        "domaines": [
            {
                "id": "foundations",
                "titre": "Foundations",
                "en": "Foundations",
                "accroche": "Introduction",
                "accroche_en": "Introduction",
                "extra_domain": True,
                "modules": [
                    {
                        "id": "a1",
                        "titre": "Module",
                        "en": "Module",
                        "extra_module": True,
                        "seances": [],
                    }
                ],
            }
        ],
    }

    errors = verifier_parcours(plan)

    assert any("clé inconnue 'extra'" in error for error in errors)
    assert any("clé inconnue 'extra_domain'" in error for error in errors)
    assert any("clé inconnue 'extra_module'" in error for error in errors)



def valid_overlay_session():
    return {
        "id": "a1/s01",
        "module": "a1",
        "titre": "Intérêts composés",
        "en": "Compound interest",
        "duree": 25,
        "etapes": [
            {
                "type": "rappel",
                "titre": "Rappel",
                "minutes": 5,
                "blocs": [
                    {
                        "p": "La valeur actuelle d’un capital.",
                        "formule": r"\text{Valeur actuelle} = C(1+i)^{-n}",
                    }
                ],
            }
        ],
    }


def valid_overlay():
    return {
        "titre": "Compound interest",
        "etapes": [
            {
                "titre": "Recap",
                "blocs": [
                    {
                        "p": "The present value of a capital.",
                        "formule": r"\text{Present value} = C(1+i)^{-n}",
                    }
                ],
            }
        ],
    }


def test_overlay_accepts_text_translation_and_formula_label_translation():
    base = valid_overlay_session()
    merged = fusionner_overlay(base, valid_overlay(), "a1/s01")

    assert merged["titre"] == "Compound interest"
    assert merged["etapes"][0]["blocs"][0]["formule"] == (
        r"\text{Present value} = C(1+i)^{-n}"
    )
    assert merged["etapes"][0]["minutes"] == 5


def test_overlay_rejects_unknown_keys_and_protected_metadata():
    base = valid_overlay_session()

    assert any(
        "clé absente du français" in error
        for error in verifier_overlay_traduction(
            base, {"etapes": [{"titre": "Recap", "unexpected": "value"}]}, session_id="a1/s01"
        )
    )
    assert any(
        "reste dans le fichier français" in error
        for error in verifier_overlay_traduction(
            base, {"id": "a1/s01"}, session_id="a1/s01"
        )
    )


def test_overlay_rejects_empty_text_type_changes_and_list_length_changes():
    base = valid_overlay_session()

    assert any("texte vide" in error for error in verifier_overlay_traduction(
        base, {"titre": "   "}, session_id="a1/s01"
    ))
    assert any("type différent" in error for error in verifier_overlay_traduction(
        base, {"titre": ["not", "text"]}, session_id="a1/s01"
    ))
    assert any("longueur différente" in error for error in verifier_overlay_traduction(
        base, {"etapes": []}, session_id="a1/s01"
    ))


def test_overlay_preserves_numeric_values_sign_exponent_and_units():
    base = {"texte": "Le taux est de -2,5 % et la marge vaut 1,2e-3 ‰."}
    assert fusionner_overlay(
        base, {"texte": "The rate is -2.5% and the margin is 1.2e-3‰."}
    )["texte"]

    for translated in (
        "The rate is 2.5% and the margin is 1.2e-3‰.",
        "The rate is -2.5 and the margin is 1.2e-3‰.",
        "The rate is -2.5% and the margin is 1.2e+3‰.",
    ):
        try:
            fusionner_overlay(base, {"texte": translated})
        except ValueError as exc:
            assert "chiffres différents" in str(exc)
        else:
            raise AssertionError(f"Numeric alteration was accepted: {translated}")


def test_overlay_formula_may_only_translate_text_labels():
    base = {"formule": r"\text{Valeur} = C(1+i)^{-n}"}
    valid = {"formule": r"\text{Value} = C(1+i)^{-n}"}
    invalid = {"formule": r"\text{Value} = C(1+i)^{n}"}

    assert fusionner_overlay(base, valid)["formule"] == valid["formule"]
    try:
        fusionner_overlay(base, invalid)
    except ValueError as exc:
        assert "formule ne peut changer" in str(exc)
    else:
        raise AssertionError("Formula structure change was accepted")


def _write_overlay_fixture(tmp_path, monkeypatch, *, overlay=None, include_overlay=True):
    content_dir = tmp_path / "contenus"
    (content_dir / "en" / "a1").mkdir(parents=True)
    (tmp_path / "exercices").mkdir()
    plan = {
        "titre": "Parcours",
        "sous_titre": "Sous-titre",
        "sous_titre_en": "Subtitle",
        "domaines": [{
            "id": "a1",
            "titre": "Fondamentaux",
            "en": "Foundations",
            "accroche": "Introduction",
            "accroche_en": "Introduction",
            "modules": [{
                "id": "a1",
                "titre": "Module",
                "en": "Module",
                "seances": ["a1/s01"],
            }],
        }],
    }
    session = valid_session()
    session["etapes"][0]["texte"] = "Le taux est de 2,5 %."
    (content_dir / "parcours.yaml").write_text(
        yaml.safe_dump(plan, allow_unicode=True), encoding="utf-8"
    )
    (content_dir / "a1" / "s01.yaml").parent.mkdir(parents=True)
    (content_dir / "a1" / "s01.yaml").write_text(
        yaml.safe_dump(session, allow_unicode=True), encoding="utf-8"
    )
    if include_overlay:
        translated = overlay if overlay is not None else {
            "titre": "Session title",
            "etapes": [{
                "titre": "Introduction",
                "texte": "The rate is 2.5%.",
            }],
        }
        (content_dir / "en" / "a1" / "s01.yaml").write_text(
            yaml.safe_dump(translated, allow_unicode=True), encoding="utf-8"
        )
    monkeypatch.setattr(validation, "CONTENT_DIR", content_dir)
    monkeypatch.setattr(validation, "ROOT", tmp_path)
    return content_dir


def test_repository_validation_checks_english_overlays_when_enabled(tmp_path, monkeypatch):
    _write_overlay_fixture(tmp_path, monkeypatch)
    assert validation.verifier_depot() == []


def test_repository_validation_requires_overlay_for_each_referenced_session(tmp_path, monkeypatch):
    _write_overlay_fixture(tmp_path, monkeypatch, include_overlay=False)
    assert any("traduction anglaise manquante" in error for error in validation.verifier_depot())


def test_repository_validation_rejects_numeric_changes_in_english_overlay(tmp_path, monkeypatch):
    _write_overlay_fixture(
        tmp_path,
        monkeypatch,
        overlay={
            "titre": "Session title",
            "etapes": [{
                "titre": "Introduction",
                "texte": "The rate is 2.6%.",
            }],
        },
    )
    assert any("chiffres différents" in error for error in validation.verifier_depot())


def test_overlay_reports_missing_translatable_text():
    errors = verifier_overlay_traduction(
        valid_overlay_session(), {"titre": "Compound interest"}, session_id="a1/s01"
    )
    assert any("texte non traduit" in error for error in errors)


def test_video_media_requires_existing_files_for_both_languages():
    session = valid_session()
    session["etapes"][0]["media"] = {"fr": {"src": "videos/missing-fr.mp4"}}
    assert any("une vidéo par langue" in error for error in verifier_seance(session, session_id="fixture"))
    session["etapes"][0]["media"] = {
        "fr": {"src": "videos/missing-fr.mp4"},
        "en": {"src": "../secret.mp4", "sous_titres": "videos/x.srt"},
    }
    errors = verifier_seance(session, session_id="fixture")
    assert any("introuvable" in error for error in errors)
    assert sum("doit être un chemin" in error for error in errors) == 2


def test_a1_s01_video_files_are_on_the_site():
    session = yaml.safe_load((validation.CONTENT_DIR / "a1" / "s01.yaml").read_text(encoding="utf-8"))
    media = next(step["media"] for step in session["etapes"] if step["type"] == "video")
    for langue in ("fr", "en"):
        assert (validation.ASSETS_DIR / media[langue]["src"]).is_file()
        assert (validation.ASSETS_DIR / media[langue]["sous_titres"]).is_file()


def test_published_videos_need_a_youtube_id_a_language_and_a_title():
    session = valid_session()
    session["actu_basics"] = {"videos": [{"id": "uJ_eQqqQB6s", "langue": "en", "titre": "Lesson", "duree": "6:42"}]}
    assert verifier_seance(session, session_id="fixture") == []
    for bad in (
        {"id": "javascript:x", "langue": "en", "titre": "Lesson"},
        {"id": "uJ_eQqqQB6s", "langue": "de", "titre": "Lesson"},
        {"id": "uJ_eQqqQB6s", "langue": "en", "titre": ""},
        {"id": "uJ_eQqqQB6s", "langue": "en", "titre": "Lesson", "url": "https://example.com"},
    ):
        session["actu_basics"] = {"videos": [bad]}
        assert verifier_seance(session, session_id="fixture"), bad
