"""Cas d'usage : orchestrent le domaine via les ports, sans logique d'infrastructure."""

from mauricette.application.cas_usage.attacher_referentiel_appel_offre import (
    AttacherReferentielAAppelOffre,
    CommandeAttacherReferentiel,
)
from mauricette.application.cas_usage.changer_activation_question_referentiel import (
    ChangerActivationQuestionReferentiel,
    CommandeChangerActivationQuestion,
)
from mauricette.application.cas_usage.creer_appel_offre import (
    CommandeCreerAppelOffre,
    CreerAppelOffre,
)
from mauricette.application.cas_usage.creer_question_referentiel import (
    CommandeCreerQuestionReferentiel,
    CreerQuestionReferentiel,
)
from mauricette.application.cas_usage.creer_referentiel import (
    CommandeCreerReferentiel,
    CreerReferentiel,
)
from mauricette.application.cas_usage.creer_section_referentiel import (
    CommandeCreerSection,
    CreerSectionReferentiel,
)
from mauricette.application.cas_usage.decouper_document import (
    CommandeDecouperDocument,
    DecouperDocument,
)
from mauricette.application.cas_usage.deposer_document import (
    CommandeDeposerDocument,
    DeposerDocument,
)
from mauricette.application.cas_usage.deposer_fichier import (
    CommandeDeposerFichier,
    DeposerFichier,
    ResultatDepotFichier,
)
from mauricette.application.cas_usage.detacher_referentiel_appel_offre import (
    CommandeDetacherReferentiel,
    DetacherReferentielDeAppelOffre,
)
from mauricette.application.cas_usage.extraire_document import (
    CommandeExtraireDocument,
    ExtraireDocument,
)
from mauricette.application.cas_usage.lister_appels_offre import (
    AppelOffreAvecStatistiques,
    ListerAppelsOffre,
)
from mauricette.application.cas_usage.lister_referentiels import (
    ListerReferentiels,
    ReferentielAvecStatistiques,
)
from mauricette.application.cas_usage.lister_referentiels_appel_offre import (
    ListerReferentielsAppelOffre,
)
from mauricette.application.cas_usage.lister_reponses_appel_offre import ListerReponsesAppelOffre
from mauricette.application.cas_usage.modifier_appel_offre import (
    CommandeModifierAppelOffre,
    ModifierAppelOffre,
)
from mauricette.application.cas_usage.modifier_question_referentiel import (
    CommandeModifierQuestionReferentiel,
    ModifierQuestionReferentiel,
)
from mauricette.application.cas_usage.modifier_referentiel import (
    CommandeModifierReferentiel,
    ModifierReferentiel,
)
from mauricette.application.cas_usage.modifier_section_referentiel import (
    CommandeModifierSection,
    ModifierSectionReferentiel,
)
from mauricette.application.cas_usage.obtenir_appel_offre import (
    DetailAppelOffre,
    ObtenirAppelOffre,
)
from mauricette.application.cas_usage.obtenir_etat_traitement_appel_offre import (
    ObtenirEtatTraitementAppelOffre,
)
from mauricette.application.cas_usage.obtenir_referentiel_detail import (
    DetailReferentiel,
    ObtenirReferentielDetail,
    SectionAvecQuestions,
)
from mauricette.application.cas_usage.regenerer_reponses_appel_offre import (
    CommandeRegenererReponsesAppelOffre,
    RegenererReponsesAppelOffre,
)
from mauricette.application.cas_usage.relancer_document import (
    CommandeRelancerDocument,
    RelancerDocument,
)
from mauricette.application.cas_usage.supprimer_document import (
    CommandeSupprimerDocument,
    SupprimerDocument,
)
from mauricette.application.cas_usage.supprimer_question_referentiel import (
    SupprimerQuestionReferentiel,
)
from mauricette.application.cas_usage.supprimer_referentiel import SupprimerReferentiel
from mauricette.application.cas_usage.supprimer_section_referentiel import (
    SupprimerSectionReferentiel,
)
from mauricette.application.cas_usage.valider_reponse import (
    CommandeValiderReponse,
    ValiderReponse,
)
from mauricette.application.cas_usage.vectoriser_document import (
    CommandeVectoriserDocument,
    VectoriserDocument,
)

__all__ = [
    "AppelOffreAvecStatistiques",
    "AttacherReferentielAAppelOffre",
    "ChangerActivationQuestionReferentiel",
    "CommandeAttacherReferentiel",
    "CommandeChangerActivationQuestion",
    "CommandeCreerAppelOffre",
    "CommandeCreerQuestionReferentiel",
    "CommandeCreerReferentiel",
    "CommandeCreerSection",
    "CommandeDecouperDocument",
    "CommandeDeposerDocument",
    "CommandeDeposerFichier",
    "CommandeDetacherReferentiel",
    "CommandeExtraireDocument",
    "CommandeModifierAppelOffre",
    "CommandeModifierQuestionReferentiel",
    "CommandeModifierReferentiel",
    "CommandeModifierSection",
    "CommandeRegenererReponsesAppelOffre",
    "CommandeRelancerDocument",
    "CommandeSupprimerDocument",
    "CommandeValiderReponse",
    "CommandeVectoriserDocument",
    "CreerAppelOffre",
    "CreerQuestionReferentiel",
    "CreerReferentiel",
    "CreerSectionReferentiel",
    "DecouperDocument",
    "DeposerDocument",
    "DeposerFichier",
    "DetacherReferentielDeAppelOffre",
    "DetailAppelOffre",
    "DetailReferentiel",
    "ExtraireDocument",
    "ListerAppelsOffre",
    "ListerReferentiels",
    "ListerReferentielsAppelOffre",
    "ListerReponsesAppelOffre",
    "ModifierAppelOffre",
    "ModifierQuestionReferentiel",
    "ModifierReferentiel",
    "ModifierSectionReferentiel",
    "ObtenirAppelOffre",
    "ObtenirEtatTraitementAppelOffre",
    "ObtenirReferentielDetail",
    "ReferentielAvecStatistiques",
    "RegenererReponsesAppelOffre",
    "RelancerDocument",
    "ResultatDepotFichier",
    "SectionAvecQuestions",
    "SupprimerDocument",
    "SupprimerQuestionReferentiel",
    "SupprimerReferentiel",
    "SupprimerSectionReferentiel",
    "ValiderReponse",
    "VectoriserDocument",
]
