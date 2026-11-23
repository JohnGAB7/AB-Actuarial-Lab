"""Tests for the optional self-contained lesson reference-sheet schema."""
from copy import deepcopy

from tools.validation_contenus import verifier_fiche, verifier_seance


def _valid_fiche():
    return {
        "statut": "prete",
        "vue_ensemble": {
            "question": "How does compound interest work?",
            "pourquoi": "It values cash flows over time.",
            "objectifs": ["Calculate an accumulation factor."],
            "prerequis": ["Basic algebra."],
            "carte": ["Rates", "Discounting", "Annuities"],
            "duree_minutes": 30,
        },
        "cours_complet": {"sections": [{
            "titre": "Effective annual rate",
            "contenu": "A unit capital grows to (1+i)^t after t years.",
            "formules": [{"formule": r"\text{AV} = C(1+i)^t",
                          "explication": "The accumulation factor is applied t times."}],
        }]},
        "methodes": {"methodes": [{
            "titre": "Discount a future cash flow",
            "quand_utiliser": "When a payment is valued before its due date.",
            "etapes": ["Identify the rate and time basis.", "Divide by (1+i)^t."],
            "controles": ["Check that present value is below future value for i > 0."],
            "erreurs": ["Mixing an annual rate with a monthly period count."],
        }]},
        "exemples_guides": {"exemples": [{
            "titre": "Discount one payment",
            "enonce": "Find the present value of 1,000 due in two years at 5%.",
            "raisonnement": ["Set C=1,000, i=0.05 and t=2.", "Compute 1,000/(1.05)^2."],
            "resultat": "907.03 monetary units.",
            "interpretation": "The amount today is lower than the future payment.",
            "controles": ["Re-accumulate 907.03 for two years."],
        }]},
        "exercices_corriges": {"exercices": [{
            "titre": "Two-year discounting", "niveau": "fondamental",
            "enonce": "Discount 500 due in two years at 4%.",
            "corrige": ["v=1/1.04.", "PV=500v^2=462.28."],
            "feedback": "A larger positive rate lowers the present value.",
        }]},
        "applications_labs": {"applications": [{
            "titre": "Present value of a benefit cash flow",
            "contexte": "A pension plan values a deterministic future benefit.",
            "objectif": "Reproduce a discounted cash-flow calculation.",
            "outils": ["excel", "python"],
            "entrees": ["Payment amount", "Annual effective rate", "Payment date"],
            "hypotheses": ["The rate is constant over the horizon."],
            "procedure": ["Convert the payment date into years.", "Apply the discount factor."],
            "sorties": ["Present value per payment."],
            "validation": ["Compare Excel and Python outputs."],
            "limites": ["No uncertainty in the payment or discount rate."],
        }]},
        "synthese_references": {
            "memo": ["PV is the sum of discounted cash flows."],
            "glossaire": [{"terme_fr": "Valeur actuelle", "terme_en": "Present value",
                           "definition": "Value at the valuation date of future cash flows."}],
            "maitrise": ["I can explain the rate-period convention.", "I can discount a dated cash flow."],
            "liens": [{"titre": "Next session", "cible": "a1/s02#annuites"}],
            "references": [{"titre": "Theory of Interest",
                            "detail": "Reference for compound interest and annuities.",
                            "annee": 2006}],
        },
    }


def _session(fiche):
    return {
        "id": "a1/s01", "module": "a1", "titre": "Intérêt composé",
        "en": "Compound interest", "duree": 30,
        "etapes": [{"type": "video", "titre": "Introduction", "minutes": 1, "texte": "Intro."}],
        "fiche": fiche,
    }


def test_ready_reference_sheet_accepts_all_seven_substantive_tabs():
    assert verifier_fiche(_valid_fiche(), session_id="a1/s01") == []
    assert verifier_seance(_session(_valid_fiche()), session_id="a1/s01") == []


def test_draft_reference_sheet_can_be_incremental_but_explicitly_marked():
    assert verifier_fiche({"statut": "brouillon"}, session_id="a1/s01") == []
    assert verifier_fiche({
        "statut": "brouillon",
        "vue_ensemble": {
            "question": "A guiding question", "pourquoi": "A reason to learn this.",
            "objectifs": ["One objective."], "prerequis": ["One prerequisite."],
            "carte": ["One concept."], "duree_minutes": 20,
        },
    }, session_id="a1/s01") == []


def test_ready_sheet_cannot_omit_a_tab_or_publish_empty_content():
    missing_tab = _valid_fiche()
    del missing_tab["methodes"]
    assert any("methodes" in error and "doit contenir" in error
               for error in verifier_fiche(missing_tab, session_id="a1/s01"))
    empty_course = _valid_fiche()
    empty_course["cours_complet"]["sections"] = []
    assert any("sections" in error for error in verifier_fiche(empty_course, session_id="a1/s01"))


def test_reference_sheet_rejects_unknown_fields_and_unsafe_internal_links():
    unknown = _valid_fiche()
    unknown["cours_complet"]["html"] = "<script>alert(1)</script>"
    assert any("clé inconnue" in error for error in verifier_fiche(unknown, session_id="a1/s01"))
    unsafe = _valid_fiche()
    unsafe["synthese_references"]["liens"][0]["cible"] = "../../outside"
    assert any("référence interne" in error
               for error in verifier_fiche(unsafe, session_id="a1/s01"))


def test_reference_sheet_rejects_invalid_exercise_levels_and_unannotated_references():
    invalid = _valid_fiche()
    invalid["exercices_corriges"]["exercices"][0]["niveau"] = "expert"
    invalid["synthese_references"]["references"] = [{"titre": "Book", "detail": ""}]
    errors = verifier_fiche(invalid, session_id="a1/s01")
    assert any("niveau" in error for error in errors)
    assert any("titre" in error or "detail" in error for error in errors)


def test_reference_sheet_formula_structure_is_protected_in_english_overlay():
    from tools.validation_contenus import fusionner_overlay

    base = {"fiche": {"statut": "prete", "cours_complet": {"sections": [{
        "titre": "Intérêt composé", "contenu": "Un capital croît.",
        "formules": [{"formule": r"\text{VA} = C v^t",
                      "explication": "Le flux est actualisé."}],
    }]}}}
    translated = {"fiche": {"cours_complet": {"sections": [{
        "titre": "Compound interest", "contenu": "A capital grows.",
        "formules": [{"formule": r"\text{PV} = C v^t",
                      "explication": "The cash flow is discounted."}],
    }]}}}
    merged = fusionner_overlay(base, translated, "a1/s01")
    from tools.validation_contenus import verifier_overlay_traduction
    assert verifier_overlay_traduction(base, translated, session_id="a1/s01") == []
    assert merged["fiche"]["statut"] == "prete"
    assert merged["fiche"]["cours_complet"]["sections"][0]["formules"][0]["formule"] == r"\text{PV} = C v^t"

    invalid = deepcopy(translated)
    invalid["fiche"]["cours_complet"]["sections"][0]["formules"][0]["formule"] = r"\text{PV} = 2 C v^t"
    try:
        fusionner_overlay(base, invalid, "a1/s01")
    except ValueError:
        pass
    else:
        raise AssertionError("An English overlay changed the mathematical formula.")


def test_reference_sheet_rejects_malformed_types_without_raising():
    invalid_status = {"statut": []}
    assert any("statut" in error for error in verifier_fiche(invalid_status, session_id="a1/s01"))

    invalid = _valid_fiche()
    invalid["vue_ensemble"]["duree_minutes"] = float("nan")
    invalid["exercices_corriges"]["exercices"][0]["niveau"] = {}
    invalid["applications_labs"]["applications"][0]["outils"] = [{}]
    errors = verifier_fiche(invalid, session_id="a1/s01")
    assert any("duree_minutes" in error for error in errors)
    assert any("niveau" in error for error in errors)
    assert any("outils" in error for error in errors)
