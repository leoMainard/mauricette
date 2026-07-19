import { Check, Layers, ListChecks, Pencil, Plus, Trash2, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ErreurApi } from "../api/client";
import {
  changerActivationQuestion,
  creerQuestionReferentiel,
  creerSection,
  modifierQuestionReferentiel,
  modifierReferentiel,
  obtenirReferentiel,
  supprimerQuestionReferentiel,
  supprimerReferentiel,
} from "../api/referentielApi";
import type {
  ContenuQuestionReferentiel,
  ContenuReferentiel,
  DetailReferentiel,
  FormatReponse,
  QuestionReferentiel,
} from "../api/types";
import { Interrupteur } from "../components/Interrupteur";
import { Layout } from "../components/Layout";
import { LIBELLES_FORMAT_REPONSE, OPTIONS_FORMAT_REPONSE } from "../constantesReferentiel";

const CONTENU_QUESTION_VIDE: ContenuQuestionReferentiel = {
  question: "",
  format_reponse: "texte_libre",
  aide_extraction: "",
  obligatoire: false,
};

/** Page de détail d'un référentiel : KPI, filtres par section, questions, édition. */
export function PageDetailReferentiel() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [detail, setDetail] = useState<DetailReferentiel | null>(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  const [enEditionEntete, setEnEditionEntete] = useState(false);
  const [contenuEntete, setContenuEntete] = useState<ContenuReferentiel | null>(null);
  const [enregistrementEnteteEnCours, setEnregistrementEnteteEnCours] = useState(false);
  const [suppressionReferentielEnCours, setSuppressionReferentielEnCours] = useState(false);

  const [sectionFiltree, setSectionFiltree] = useState<string | null>(null);

  const [sectionFormOuvert, setSectionFormOuvert] = useState(false);
  const [nomNouvelleSection, setNomNouvelleSection] = useState("");
  const [creationSectionEnCours, setCreationSectionEnCours] = useState(false);

  const [questionFormOuvert, setQuestionFormOuvert] = useState(false);
  const [sectionCible, setSectionCible] = useState<string>("");
  const [contenuNouvelleQuestion, setContenuNouvelleQuestion] =
    useState<ContenuQuestionReferentiel>(CONTENU_QUESTION_VIDE);
  const [creationQuestionEnCours, setCreationQuestionEnCours] = useState(false);

  const [questionEnEditionId, setQuestionEnEditionId] = useState<string | null>(null);
  const [contenuEditionQuestion, setContenuEditionQuestion] =
    useState<ContenuQuestionReferentiel>(CONTENU_QUESTION_VIDE);
  const [actionQuestionEnCoursId, setActionQuestionEnCoursId] = useState<string | null>(null);

  async function recharger() {
    if (!id) return;
    try {
      const resultat = await obtenirReferentiel(id);
      setDetail(resultat);
      if (!sectionCible && resultat.sections.length > 0) {
        setSectionCible(resultat.sections[0].section.id);
      }
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement");
    } finally {
      setChargement(false);
    }
  }

  useEffect(() => {
    recharger();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const questionsActivesTotal = useMemo(
    () => detail?.sections.flatMap((s) => s.questions).filter((q) => q.actif).length ?? 0,
    [detail],
  );

  function ouvrirEditionEntete() {
    if (!detail) return;
    setContenuEntete({
      nom: detail.referentiel.nom,
      description: detail.referentiel.description ?? "",
      actif_par_defaut: detail.referentiel.actif_par_defaut,
    });
    setEnEditionEntete(true);
  }

  async function enregistrerEntete() {
    if (!id || !contenuEntete) return;
    setEnregistrementEnteteEnCours(true);
    try {
      await modifierReferentiel(id, contenuEntete);
      await recharger();
      setEnEditionEntete(false);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de l'enregistrement.");
    } finally {
      setEnregistrementEnteteEnCours(false);
    }
  }

  async function supprimerLeReferentiel() {
    if (!id) return;
    setSuppressionReferentielEnCours(true);
    try {
      await supprimerReferentiel(id);
      navigate("/referentiels");
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la suppression.");
      setSuppressionReferentielEnCours(false);
    }
  }

  async function creerNouvelleSection(evenement: React.FormEvent) {
    evenement.preventDefault();
    if (!id || !nomNouvelleSection.trim()) return;
    setCreationSectionEnCours(true);
    try {
      const section = await creerSection(id, nomNouvelleSection.trim());
      await recharger();
      setSectionCible(section.id);
      setNomNouvelleSection("");
      setSectionFormOuvert(false);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la création de la section.");
    } finally {
      setCreationSectionEnCours(false);
    }
  }

  async function creerNouvelleQuestion(evenement: React.FormEvent) {
    evenement.preventDefault();
    if (!sectionCible) return;
    setCreationQuestionEnCours(true);
    try {
      await creerQuestionReferentiel(sectionCible, contenuNouvelleQuestion);
      await recharger();
      setContenuNouvelleQuestion(CONTENU_QUESTION_VIDE);
      setQuestionFormOuvert(false);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la création de la question.");
    } finally {
      setCreationQuestionEnCours(false);
    }
  }

  function ouvrirEditionQuestion(question: QuestionReferentiel) {
    setContenuEditionQuestion({
      question: question.question,
      format_reponse: question.format_reponse,
      aide_extraction: question.aide_extraction ?? "",
      obligatoire: question.obligatoire,
    });
    setQuestionEnEditionId(question.id);
  }

  async function enregistrerEditionQuestion(questionId: string) {
    setActionQuestionEnCoursId(questionId);
    try {
      await modifierQuestionReferentiel(questionId, contenuEditionQuestion);
      await recharger();
      setQuestionEnEditionId(null);
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de l'enregistrement.");
    } finally {
      setActionQuestionEnCoursId(null);
    }
  }

  async function basculerActivationQuestion(question: QuestionReferentiel) {
    setActionQuestionEnCoursId(question.id);
    try {
      await changerActivationQuestion(question.id, !question.actif);
      await recharger();
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors du changement de statut.");
    } finally {
      setActionQuestionEnCoursId(null);
    }
  }

  async function supprimerLaQuestion(questionId: string) {
    setActionQuestionEnCoursId(questionId);
    try {
      await supprimerQuestionReferentiel(questionId);
      await recharger();
    } catch (e) {
      setErreur(e instanceof ErreurApi ? e.message : "Erreur lors de la suppression.");
    } finally {
      setActionQuestionEnCoursId(null);
    }
  }

  if (chargement) {
    return (
      <Layout>
        <p className="texte-discret">Chargement...</p>
      </Layout>
    );
  }

  if (!detail) {
    return (
      <Layout>
        <p className="message-erreur">{erreur ?? "Référentiel introuvable."}</p>
        <Link to="/referentiels">Retour aux référentiels</Link>
      </Layout>
    );
  }

  const sectionsAffichees = sectionFiltree
    ? detail.sections.filter((s) => s.section.id === sectionFiltree)
    : detail.sections;

  return (
    <Layout
      barreSuperieure={
        <Link to="/referentiels" className="lien-retour">
          ← Retour aux référentiels
        </Link>
      }
    >
      {erreur && <p className="message-erreur">{erreur}</p>}

      <div className="carte">
        {enEditionEntete && contenuEntete ? (
          <>
            <label htmlFor="entete-nom">Nom</label>
            <input
              id="entete-nom"
              type="text"
              value={contenuEntete.nom}
              onChange={(e) => setContenuEntete({ ...contenuEntete, nom: e.target.value })}
              disabled={enregistrementEnteteEnCours}
            />
            <label htmlFor="entete-description">Description</label>
            <input
              id="entete-description"
              type="text"
              value={contenuEntete.description ?? ""}
              onChange={(e) => setContenuEntete({ ...contenuEntete, description: e.target.value })}
              disabled={enregistrementEnteteEnCours}
            />
            <div className="ligne-interrupteur">
              <Interrupteur
                coche={contenuEntete.actif_par_defaut}
                onChange={(v) => setContenuEntete({ ...contenuEntete, actif_par_defaut: v })}
                disabled={enregistrementEnteteEnCours}
                libelle="Appliquer par défaut à chaque nouvel AO"
              />
              <span>Appliquer par défaut à chaque nouvel AO</span>
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                className="bouton-icone bouton-icone--valider"
                onClick={enregistrerEntete}
                disabled={enregistrementEnteteEnCours || !contenuEntete.nom.trim()}
                title="Enregistrer"
                aria-label="Enregistrer"
              >
                <Check size={17} />
              </button>
              <button
                type="button"
                className="bouton-icone bouton-icone--annuler"
                onClick={() => setEnEditionEntete(false)}
                disabled={enregistrementEnteteEnCours}
                title="Annuler"
                aria-label="Annuler"
              >
                <X size={17} />
              </button>
            </div>
          </>
        ) : (
          <div className="carte--resume">
            <div>
              <h2>{detail.referentiel.nom}</h2>
              {detail.referentiel.description && (
                <p className="texte-discret">{detail.referentiel.description}</p>
              )}
              {detail.referentiel.actif_par_defaut && (
                <span className="badge badge--actif" style={{ marginTop: "6px" }}>
                  <span className="badge__point" aria-hidden="true" />
                  Appliqué par défaut
                </span>
              )}
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                className="bouton-icone"
                onClick={ouvrirEditionEntete}
                title="Modifier"
                aria-label="Modifier le référentiel"
              >
                <Pencil size={16} />
              </button>
              <button
                type="button"
                className="bouton-icone bouton-icone--annuler"
                onClick={supprimerLeReferentiel}
                disabled={suppressionReferentielEnCours}
                title="Supprimer le référentiel"
                aria-label="Supprimer le référentiel"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="grille-kpi">
        <div className="carte-kpi">
          <ListChecks size={18} className="carte-kpi__icone" />
          <div>
            <div className="carte-kpi__libelle">Questions actives</div>
            <div className="carte-kpi__valeur">{questionsActivesTotal}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <Layers size={18} className="carte-kpi__icone" />
          <div>
            <div className="carte-kpi__libelle">Catégories</div>
            <div className="carte-kpi__valeur">{detail.sections.length}</div>
          </div>
        </div>
        <div className="carte-kpi">
          <Layers size={18} className="carte-kpi__icone" />
          <div>
            <div className="carte-kpi__libelle">AO concernés</div>
            <div className="carte-kpi__valeur">{detail.nombre_ao_concernes}</div>
          </div>
        </div>
      </div>

      <div className="barre-actions-referentiel">
        <div className="pastilles-filtre">
          <button
            type="button"
            className={`pastille-filtre${sectionFiltree === null ? " pastille-filtre--active" : ""}`}
            onClick={() => setSectionFiltree(null)}
          >
            Toutes {detail.sections.reduce((total, s) => total + s.questions.length, 0)}
          </button>
          {detail.sections.map(({ section, questions }) => (
            <button
              key={section.id}
              type="button"
              className={`pastille-filtre${sectionFiltree === section.id ? " pastille-filtre--active" : ""}`}
              onClick={() => setSectionFiltree(section.id)}
            >
              {section.nom} {questions.length}
            </button>
          ))}
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          {!sectionFormOuvert && (
            <button type="button" className="bouton-fantome" onClick={() => setSectionFormOuvert(true)}>
              + Section
            </button>
          )}
          {detail.sections.length > 0 && !questionFormOuvert && (
            <button type="button" onClick={() => setQuestionFormOuvert(true)}>
              <Plus size={16} style={{ marginRight: "4px" }} />
              Ajouter une question
            </button>
          )}
        </div>
      </div>

      {sectionFormOuvert && (
        <form onSubmit={creerNouvelleSection} className="carte carte--formulaire-inline">
          <label htmlFor="nom-section">Nom de la nouvelle section</label>
          <input
            id="nom-section"
            type="text"
            value={nomNouvelleSection}
            onChange={(e) => setNomNouvelleSection(e.target.value)}
            placeholder="ex : Franchises"
            required
            disabled={creationSectionEnCours}
            autoFocus
          />
          <div style={{ display: "flex", gap: "8px" }}>
            <button type="submit" disabled={creationSectionEnCours || !nomNouvelleSection.trim()}>
              ✓ Enregistrer
            </button>
            <button
              type="button"
              className="bouton-fantome"
              onClick={() => {
                setSectionFormOuvert(false);
                setNomNouvelleSection("");
              }}
              disabled={creationSectionEnCours}
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      {questionFormOuvert && (
        <form onSubmit={creerNouvelleQuestion} className="carte carte--formulaire-inline">
          <h2>+ Nouvelle question</h2>

          <label htmlFor="nouvelle-question">Intitulé de la question</label>
          <input
            id="nouvelle-question"
            type="text"
            value={contenuNouvelleQuestion.question}
            onChange={(e) => setContenuNouvelleQuestion((p) => ({ ...p, question: e.target.value }))}
            placeholder="ex : Quelles garanties sont demandées ?"
            required
            disabled={creationQuestionEnCours}
            autoFocus
          />

          <label htmlFor="nouvelle-aide">Aide à l'extraction</label>
          <input
            id="nouvelle-aide"
            type="text"
            value={contenuNouvelleQuestion.aide_extraction ?? ""}
            onChange={(e) => setContenuNouvelleQuestion((p) => ({ ...p, aide_extraction: e.target.value }))}
            placeholder="Précisez ce que le modèle doit chercher dans les documents..."
            disabled={creationQuestionEnCours}
          />

          <div className="ligne-deux-colonnes">
            <div>
              <label htmlFor="nouvelle-categorie">Catégorie</label>
              <select
                id="nouvelle-categorie"
                value={sectionCible}
                onChange={(e) => setSectionCible(e.target.value)}
                disabled={creationQuestionEnCours}
              >
                {detail.sections.map(({ section }) => (
                  <option key={section.id} value={section.id}>
                    {section.nom}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="nouveau-format">Type de réponse</label>
              <select
                id="nouveau-format"
                value={contenuNouvelleQuestion.format_reponse}
                onChange={(e) =>
                  setContenuNouvelleQuestion((p) => ({
                    ...p,
                    format_reponse: e.target.value as FormatReponse,
                  }))
                }
                disabled={creationQuestionEnCours}
              >
                {OPTIONS_FORMAT_REPONSE.map((option) => (
                  <option key={option} value={option}>
                    {LIBELLES_FORMAT_REPONSE[option]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="ligne-interrupteur">
            <Interrupteur
              coche={contenuNouvelleQuestion.obligatoire}
              onChange={(v) => setContenuNouvelleQuestion((p) => ({ ...p, obligatoire: v }))}
              disabled={creationQuestionEnCours}
              libelle="Question obligatoire"
            />
            <span>Question obligatoire</span>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
            <button
              type="button"
              className="bouton-fantome"
              onClick={() => {
                setQuestionFormOuvert(false);
                setContenuNouvelleQuestion(CONTENU_QUESTION_VIDE);
              }}
              disabled={creationQuestionEnCours}
            >
              Annuler
            </button>
            <button type="submit" disabled={creationQuestionEnCours || !contenuNouvelleQuestion.question.trim()}>
              ✓ Enregistrer
            </button>
          </div>
        </form>
      )}

      {detail.sections.length === 0 ? (
        <p className="texte-discret">
          Aucune section pour le moment. Crée une section pour pouvoir y ajouter des questions.
        </p>
      ) : (
        sectionsAffichees.map(({ section, questions }) => (
          <div key={section.id} className="groupe-section">
            <h3 className="groupe-section__titre">
              {section.nom} <span className="texte-discret">{questions.length}</span>
            </h3>
            {questions.length === 0 ? (
              <p className="texte-discret">Aucune question dans cette section.</p>
            ) : (
              <ul className="liste-questions-referentiel">
                {questions.map((question) => (
                  <li key={question.id} className="question-item">
                    {questionEnEditionId === question.id ? (
                      <div className="question-item__edition">
                        <label htmlFor={`edit-q-${question.id}`}>Intitulé</label>
                        <input
                          id={`edit-q-${question.id}`}
                          type="text"
                          value={contenuEditionQuestion.question}
                          onChange={(e) =>
                            setContenuEditionQuestion((p) => ({ ...p, question: e.target.value }))
                          }
                          disabled={actionQuestionEnCoursId === question.id}
                        />
                        <label htmlFor={`edit-aide-${question.id}`}>Aide à l'extraction</label>
                        <input
                          id={`edit-aide-${question.id}`}
                          type="text"
                          value={contenuEditionQuestion.aide_extraction ?? ""}
                          onChange={(e) =>
                            setContenuEditionQuestion((p) => ({ ...p, aide_extraction: e.target.value }))
                          }
                          disabled={actionQuestionEnCoursId === question.id}
                        />
                        <div className="ligne-deux-colonnes">
                          <div>
                            <label htmlFor={`edit-format-${question.id}`}>Type de réponse</label>
                            <select
                              id={`edit-format-${question.id}`}
                              value={contenuEditionQuestion.format_reponse}
                              onChange={(e) =>
                                setContenuEditionQuestion((p) => ({
                                  ...p,
                                  format_reponse: e.target.value as FormatReponse,
                                }))
                              }
                              disabled={actionQuestionEnCoursId === question.id}
                            >
                              {OPTIONS_FORMAT_REPONSE.map((option) => (
                                <option key={option} value={option}>
                                  {LIBELLES_FORMAT_REPONSE[option]}
                                </option>
                              ))}
                            </select>
                          </div>
                          <div className="ligne-interrupteur" style={{ marginTop: "22px" }}>
                            <Interrupteur
                              coche={contenuEditionQuestion.obligatoire}
                              onChange={(v) =>
                                setContenuEditionQuestion((p) => ({ ...p, obligatoire: v }))
                              }
                              disabled={actionQuestionEnCoursId === question.id}
                              libelle="Question obligatoire"
                            />
                            <span>Obligatoire</span>
                          </div>
                        </div>
                        <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
                          <button
                            type="button"
                            className="bouton-fantome"
                            onClick={() => setQuestionEnEditionId(null)}
                            disabled={actionQuestionEnCoursId === question.id}
                          >
                            Annuler
                          </button>
                          <button
                            type="button"
                            onClick={() => enregistrerEditionQuestion(question.id)}
                            disabled={
                              actionQuestionEnCoursId === question.id || !contenuEditionQuestion.question.trim()
                            }
                          >
                            ✓ Enregistrer
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="question-item__contenu">
                          <div className="question-item__titre">
                            {question.question}
                            {question.obligatoire && <span className="badge badge--en_erreur">Obligatoire</span>}
                          </div>
                          {question.aide_extraction && (
                            <p className="texte-discret">{question.aide_extraction}</p>
                          )}
                          <span className="badge">{LIBELLES_FORMAT_REPONSE[question.format_reponse]}</span>
                        </div>
                        <div className="question-item__actions">
                          <button
                            type="button"
                            className="bouton-icone"
                            onClick={() => ouvrirEditionQuestion(question)}
                            title="Modifier"
                            aria-label={`Modifier ${question.question}`}
                          >
                            <Pencil size={15} />
                          </button>
                          <button
                            type="button"
                            className="bouton-icone bouton-icone--annuler"
                            onClick={() => supprimerLaQuestion(question.id)}
                            disabled={actionQuestionEnCoursId === question.id}
                            title="Supprimer"
                            aria-label={`Supprimer ${question.question}`}
                          >
                            <Trash2 size={15} />
                          </button>
                          <Interrupteur
                            coche={question.actif}
                            onChange={() => basculerActivationQuestion(question)}
                            disabled={actionQuestionEnCoursId === question.id}
                            libelle={question.actif ? "Désactiver la question" : "Activer la question"}
                          />
                        </div>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))
      )}
    </Layout>
  );
}
