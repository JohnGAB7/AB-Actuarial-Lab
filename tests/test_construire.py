"""Regression tests for the canonical validation/build boundary."""

import pytest

import tools.construire as builder


def test_build_rejects_invalid_content_before_removing_previous_site(tmp_path, monkeypatch):
    output = tmp_path / "_site"
    output.mkdir()
    marker = output / "previous-build.txt"
    marker.write_text("last successful build", encoding="utf-8")

    monkeypatch.setattr(builder, "SORTIE", output)
    monkeypatch.setattr(builder, "verifier_depot", lambda: ["invalid session fixture"])

    with pytest.raises(SystemExit, match="invalid session fixture"):
        builder.construire()

    assert marker.read_text(encoding="utf-8") == "last successful build"


def test_verifier_cli_uses_the_canonical_validator(monkeypatch, capsys):
    errors = ["parcours.yaml: invalid fixture"]
    monkeypatch.setattr(builder, "verifier_depot", lambda: errors)
    monkeypatch.setattr(
        builder,
        "construire",
        lambda: pytest.fail("the validation-only command must not build the site"),
    )

    assert builder.main(["--verifier"]) == 1
    assert "parcours.yaml: invalid fixture" in capsys.readouterr().err


def test_verifier_cli_reports_success_when_canonical_validator_passes(monkeypatch, capsys):
    monkeypatch.setattr(builder, "verifier_depot", lambda: [])

    assert builder.main(["--verifier"]) == 0
    assert "structurally valid" in capsys.readouterr().out


def test_english_pages_write_formula_numbers_the_english_way():
    assert builder.nombres_tex_en(r"\frac{1\,881{,}25^2}{1\,527\,460{,}94}") == r"\frac{1{,}881.25^2}{1{,}527{,}460.94}"
    assert builder.nombres_tex_en(r"f_{1,\,2} = 0{,}05 \quad \theta\,e^{-d/\theta}") == r"f_{1,\,2} = 0.05 \quad \theta\,e^{-d/\theta}"
    s = builder.charger_seance("a2/s01", "en")
    formules = [q["pourquoi"].get("formule", "") for e in s["etapes"] if e["type"] == "quiz" for q in e["questions"]]
    assert not any("{,}" in f for f in formules if "0" in f and "." not in f)
    assert any("0.2 \\times 0.15" in f for f in formules)
