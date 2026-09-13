"""Logique métier des éditeurs — séance 4, partie 6."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.depots import editeurs as depot
from app.exceptions import EditeurIntrouvable, ErreurMetier
from app.modeles.jeux import EditeurEntree
from app.tables.editeurs import Editeur


def lister(session: Session, saut: int = 0, limite: int = 50) -> tuple[list[Editeur], int]:
    return depot.lister(session, saut, limite), depot.compter(session)


def trouver(session: Session, editeur_id: int) -> Editeur:
    e = depot.par_id(session, editeur_id)
    if e is None:
        raise EditeurIntrouvable(editeur_id)
    return e


def jeux_de(session: Session, editeur_id: int):
    e = depot.par_id_avec_jeux(session, editeur_id)
    if e is None:
        raise EditeurIntrouvable(editeur_id)
    return e.jeux


def creer(session: Session, entree: EditeurEntree) -> Editeur:
    e = Editeur(**entree.model_dump())
    try:
        return depot.enregistrer(session, e)
    except IntegrityError:
        session.rollback()
        raise ErreurMetier(
            "EDITEUR_DEJA_EXISTANT", f"L'éditeur '{entree.nom}' existe déjà", 409
        ) from None


def supprimer(session: Session, editeur_id: int) -> None:
    depot.supprimer(session, trouver(session, editeur_id))
