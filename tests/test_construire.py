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
