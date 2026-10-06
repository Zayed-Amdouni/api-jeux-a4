"""Tests de la configuration — issue #8."""

import pytest

from app.config import Configuration

DEUX_ORIGINES = ["http://a.test", "http://b.test"]


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        # La forme livrée par `.env.example`.
        ("http://a.test,http://b.test", DEUX_ORIGINES),
        # La forme utilisée par les `.env` de l'équipe.
        ('["http://a.test", "http://b.test"]', DEUX_ORIGINES),
        # Les espaces autour des virgules ne doivent pas se retrouver dans la liste.
        ("http://a.test , http://b.test", DEUX_ORIGINES),
    ],
)
def test_origines_autorisees_accepte_les_deux_formes(monkeypatch, valeur, attendu):
    """Le validateur promet d'accepter « A,B autant qu'une liste JSON ».

    Sans ce test, seule la forme JSON fonctionnait : `pydantic-settings` tentait
    un décodage JSON dans la source, avant le validateur.
    """
    monkeypatch.setenv("ORIGINES_AUTORISEES", valeur)

    assert Configuration().origines_autorisees == attendu
