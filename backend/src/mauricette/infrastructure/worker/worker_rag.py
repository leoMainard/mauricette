"""Point d'entrée du worker RAG : boucle de traitement des tâches asynchrones.

Lancement : `uv run python -m mauricette.infrastructure.worker.worker_rag` (depuis `backend/`).
Aucune dépendance à Celery/Redis : la file d'attente est portée par la table
`tache_traitement` en PostgreSQL, réclamée via `SELECT ... FOR UPDATE SKIP LOCKED`.
"""

from __future__ import annotations

import logging
import time

from mauricette.config.parametres import Parametres, obtenir_parametres
from mauricette.domaine.entites.enums import TypeTache
from mauricette.domaine.exceptions import ErreurTraitementDefinitive, ErreurTraitementTransitoire
from mauricette.infrastructure.persistence.postgres.base import GestionnaireSessions, creer_fabrique_sessions
from mauricette.infrastructure.persistence.postgres.tache_traitement_repository_sql import (
    TacheTraitementRepositorySQL,
)
from mauricette.infrastructure.worker.fabrique_worker import (
    construire_adaptateurs,
    construire_gestionnaires_par_type,
)

logger = logging.getLogger("mauricette.worker_rag")

TYPES_TACHES_GEREES = [
    TypeTache.EXTRACTION_DOCUMENT,
    TypeTache.DECOUPAGE_DOCUMENT,
    TypeTache.EMBEDDING_DOCUMENT,
    TypeTache.REGENERATION_REPONSES_AO,
]


def executer_boucle(parametres: Parametres) -> None:
    """Boucle principale du worker : réclame et exécute les tâches une par une, indéfiniment."""
    gestionnaire_sessions = GestionnaireSessions(parametres)
    fabrique_sessions = creer_fabrique_sessions(gestionnaire_sessions.moteur)
    adaptateurs = construire_adaptateurs(parametres)
    logger.info("Worker RAG démarré (intervalle de sondage : %.1fs).", parametres.rag_worker_intervalle_secondes)

    while True:
        session = fabrique_sessions()
        try:
            tache = TacheTraitementRepositorySQL(session).reclamer_tache_suivante(TYPES_TACHES_GEREES)
        finally:
            session.close()

        if tache is None:
            time.sleep(parametres.rag_worker_intervalle_secondes)
            continue

        logger.info("Tâche réclamée : %s (%s, tentative %d)", tache.id, tache.type_tache, tache.tentatives)

        session = fabrique_sessions()
        try:
            depot_taches = TacheTraitementRepositorySQL(session)
            gestionnaires = construire_gestionnaires_par_type(session, adaptateurs, parametres)
            try:
                gestionnaires[tache.type_tache](tache.reference_id)
                depot_taches.marquer_reussie(tache.id)
                logger.info("Tâche réussie : %s", tache.id)
            except ErreurTraitementTransitoire as erreur:
                if tache.tentatives >= parametres.rag_nombre_max_tentatives_tache:
                    depot_taches.marquer_echouee(tache.id, str(erreur))
                    logger.warning(
                        "Tâche %s en échec définitif après %d tentatives : %s",
                        tache.id,
                        tache.tentatives,
                        erreur,
                    )
                else:
                    depot_taches.remettre_en_attente(
                        tache.id, str(erreur), parametres.rag_delai_avant_nouvelle_tentative_secondes
                    )
                    logger.warning("Tâche %s remise en attente (erreur transitoire) : %s", tache.id, erreur)
            except ErreurTraitementDefinitive as erreur:
                depot_taches.marquer_echouee(tache.id, str(erreur))
                logger.warning("Tâche %s en échec définitif : %s", tache.id, erreur)
            except Exception as erreur:  # filet de sécurité : ne jamais interrompre la boucle
                depot_taches.marquer_echouee(tache.id, str(erreur))
                logger.exception("Tâche %s en échec inattendu", tache.id)
        finally:
            session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    executer_boucle(obtenir_parametres())
