"""Adaptateur PostgreSQL du port `ChunkRepositoryPort`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from mauricette.domaine.entites.chunk import Chunk
from mauricette.domaine.ports.chunk_repository import LIMITE_RECHERCHE_PAR_DEFAUT, ChunkRepositoryPort
from mauricette.infrastructure.persistence.postgres.mappers import chunk_vers_entite, chunk_vers_modele
from mauricette.infrastructure.persistence.postgres.modeles import ChunkModele

# Recherche hybride : fusionne un classement vectoriel (similarité cosinus) et un
# classement plein texte (français) par Reciprocal Rank Fusion (RRF), plutôt que
# de sommer des scores d'échelles incompatibles (distance cosinus vs ts_rank).
# La constante 60 est la valeur usuelle de la littérature RRF (Cormack et al.).
_CONSTANTE_RRF = 60
_NOMBRE_CANDIDATS_PAR_METHODE = 30

_REQUETE_RECHERCHE_HYBRIDE = text(
    f"""
    WITH vectoriel AS (
        SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> CAST(:vecteur AS vector)) AS rang
        FROM chunk
        WHERE appel_offre_id = :appel_offre_id AND embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:vecteur AS vector)
        LIMIT :nombre_candidats
    ),
    textuel AS (
        SELECT id, ROW_NUMBER() OVER (
            ORDER BY ts_rank(contenu_tsv, plainto_tsquery('french', :texte_question)) DESC
        ) AS rang
        FROM chunk
        WHERE appel_offre_id = :appel_offre_id
          AND contenu_tsv @@ plainto_tsquery('french', :texte_question)
        ORDER BY ts_rank(contenu_tsv, plainto_tsquery('french', :texte_question)) DESC
        LIMIT :nombre_candidats
    )
    SELECT chunk.id,
           COALESCE(1.0 / ({_CONSTANTE_RRF} + vectoriel.rang), 0)
           + COALESCE(1.0 / ({_CONSTANTE_RRF} + textuel.rang), 0) AS score_combine
    FROM chunk
    LEFT JOIN vectoriel ON vectoriel.id = chunk.id
    LEFT JOIN textuel ON textuel.id = chunk.id
    WHERE chunk.appel_offre_id = :appel_offre_id
      AND (vectoriel.id IS NOT NULL OR textuel.id IS NOT NULL)
    ORDER BY score_combine DESC
    LIMIT :limite
    """
)


def _vecteur_vers_litteral_pgvector(vecteur: list[float]) -> str:
    """Sérialise un vecteur Python au format texte attendu par pgvector (`[0.1,0.2,...]`)."""
    return "[" + ",".join(repr(v) for v in vecteur) + "]"


class ChunkRepositorySQL(ChunkRepositoryPort):
    """Implémentation PostgreSQL (via pgvector) du repository des chunks."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def remplacer_pour_document(self, document_id: UUID, chunks: list[Chunk]) -> None:
        self._session.execute(delete(ChunkModele).where(ChunkModele.document_id == document_id))
        for chunk in chunks:
            self._session.add(chunk_vers_modele(chunk))
        self._session.commit()

    def mettre_a_jour_embeddings(self, embeddings_par_chunk_id: dict[UUID, list[float]]) -> None:
        for chunk_id, vecteur in embeddings_par_chunk_id.items():
            modele = self._session.get(ChunkModele, chunk_id)
            if modele is None:
                raise ValueError(f"Chunk introuvable : {chunk_id}")
            modele.embedding = vecteur
        self._session.commit()

    def lister_sans_embedding(self, document_id: UUID) -> list[Chunk]:
        requete = (
            select(ChunkModele)
            .where(ChunkModele.document_id == document_id, ChunkModele.embedding.is_(None))
            .order_by(ChunkModele.ordre)
        )
        modeles = self._session.execute(requete).scalars().all()
        return [chunk_vers_entite(modele) for modele in modeles]

    def recherche_hybride(
        self,
        appel_offre_id: UUID,
        vecteur_question: list[float],
        texte_question: str,
        limite: int = LIMITE_RECHERCHE_PAR_DEFAUT,
    ) -> list[Chunk]:
        resultats = self._session.execute(
            _REQUETE_RECHERCHE_HYBRIDE,
            {
                "appel_offre_id": str(appel_offre_id),
                "vecteur": _vecteur_vers_litteral_pgvector(vecteur_question),
                "texte_question": texte_question,
                "nombre_candidats": _NOMBRE_CANDIDATS_PAR_METHODE,
                "limite": limite,
            },
        ).all()
        if not resultats:
            return []

        ids_ordonnes = [ligne.id for ligne in resultats]
        modeles = self._session.execute(
            select(ChunkModele).where(ChunkModele.id.in_(ids_ordonnes))
        ).scalars().all()
        modeles_par_id = {modele.id: modele for modele in modeles}
        return [
            chunk_vers_entite(modeles_par_id[chunk_id])
            for chunk_id in ids_ordonnes
            if chunk_id in modeles_par_id
        ]
