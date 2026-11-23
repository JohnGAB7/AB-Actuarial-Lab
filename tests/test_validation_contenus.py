"""Regression tests for strict course-content validation."""
from tools.validation_contenus import verifier_depot, verifier_parcours, verifier_seance


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
