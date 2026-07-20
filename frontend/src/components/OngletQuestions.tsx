import { Check, RotateCw, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import type { DetailReferentiel, Referentiel, ReponseQuestion } from "../api/types";
import { LIBELLES_FORMAT_REPONSE } from "../constantesReferentiel";

interface Props {
  referentielsAttaches: Referentiel[];
  referentielsDisponibles: Referentiel[];
  referentielChoisi: string;
  referentielActionEnCours: boolean;
  onChangerReferentielChoisi: (id: string) => void;
  onAttacher: () => void;
  onDetacher: (referentielId: string) => void;

  chargementQuestions: boolean;
  details: DetailReferentiel[];
  reponsesParQuestion: Map<string, ReponseQuestion>;
  validationEnCoursId: string | null;
  onValider: (reponse: ReponseQuestion) => void;

  reanalyseEnCours: boolean;
  onReanalyser: () => void;
}

/** Onglet "Questions" de la fiche AO : référentiels appliqués + réponses générées par l'IA. */
export function OngletQuestions({
  referentielsAttaches,
  referentielsDisponibles,
  referentielChoisi,
  referentielActionEnCours,
  onChangerReferentielChoisi,
  onAttacher,
  onDetacher,
  chargementQuestions,
  details,
  reponsesParQuestion,
  validationEnCoursId,
  onValider,
  reanalyseEnCours,
  onReanalyser,
}: Props) {
  const questionsActivesTotal = details.reduce(
    (total, d) => total + d.sections.flatMap((s) => s.questions).filter((q) => q.actif).length,
    0,
  );
  const reponsesGenereesTotal = details.reduce(
    (total, d) =>
      total +
      d.sections
        .flatMap((s) => s.questions)
        .filter((q) => q.actif && reponsesParQuestion.get(q.id)?.contenu).length,
    0,
  );

  return (
    <>
      <div className="carte">
        <h2>Référentiels appliqués</h2>
        {referentielsAttaches.length === 0 ? (
          <p className="texte-discret">Aucun référentiel appliqué à cet AO.</p>
        ) : (
          <ul className="liste-referentiels-ao">
            {referentielsAttaches.map((referentiel) => (
              <li key={referentiel.id}>
                <Link to={`/referentiels/${referentiel.id}`}>{referentiel.nom}</Link>
                <button
                  type="button"
                  className="bouton-icone bouton-icone--annuler"
                  onClick={() => onDetacher(referentiel.id)}
                  disabled={referentielActionEnCours}
                  title="Retirer ce référentiel"
                  aria-label={`Retirer ${referentiel.nom}`}
                >
                  <Trash2 size={14} />
                </button>
              </li>
            ))}
          </ul>
        )}
        {referentielsDisponibles.length > 0 && (
          <div className="ligne-ajout-referentiel">
            <select
              value={referentielChoisi}
              onChange={(e) => onChangerReferentielChoisi(e.target.value)}
              disabled={referentielActionEnCours}
            >
              <option value="">Choisir un référentiel à ajouter...</option>
              {referentielsDisponibles.map((referentiel) => (
                <option key={referentiel.id} value={referentiel.id}>
                  {referentiel.nom}
                </option>
              ))}
            </select>
            <button type="button" onClick={onAttacher} disabled={referentielActionEnCours || !referentielChoisi}>
              Ajouter
            </button>
          </div>
        )}
      </div>

      <div className="entete-page--avec-action">
        <p className="texte-discret">
          Réponses extraites par le modèle pour cet AO. {reponsesGenereesTotal} renseignée
          {reponsesGenereesTotal > 1 ? "s" : ""} sur {questionsActivesTotal}.
        </p>
        <button
          type="button"
          className="bouton-fantome"
          onClick={onReanalyser}
          disabled={reanalyseEnCours || questionsActivesTotal === 0}
          title="Relancer une analyse complète des documents pour cet AO"
        >
          <RotateCw size={15} style={{ marginRight: "4px" }} className={reanalyseEnCours ? "icone-rotation" : undefined} />
          {reanalyseEnCours ? "Analyse en cours..." : "Ré-analyser"}
        </button>
      </div>

      {chargementQuestions ? (
        <p className="texte-discret">Chargement...</p>
      ) : details.length === 0 ? (
        <p className="texte-discret">
          Aucun référentiel n'est appliqué à cet AO. Attache un référentiel ci-dessus pour voir
          apparaître des questions ici.
        </p>
      ) : (
        details.map((detail) => (
          <div key={detail.referentiel.id} className="groupe-section">
            <h3 className="groupe-section__titre">{detail.referentiel.nom}</h3>
            {detail.sections
              .filter(({ questions }) => questions.some((q) => q.actif))
              .map(({ section, questions }) => (
                <div key={section.id} style={{ marginBottom: "16px" }}>
                  <p className="texte-discret" style={{ marginBottom: "8px" }}>
                    {section.nom}
                  </p>
                  <ul className="liste-questions-referentiel">
                    {questions
                      .filter((q) => q.actif)
                      .map((question) => {
                        const reponse = reponsesParQuestion.get(question.id);
                        return (
                          <li key={question.id} className="question-item">
                            <div className="question-item__contenu">
                              <div className="question-item__titre">
                                {question.question}
                                <span className="badge">{LIBELLES_FORMAT_REPONSE[question.format_reponse]}</span>
                              </div>

                              {!reponse ? (
                                <p className="texte-discret">Pas encore traité par l'IA.</p>
                              ) : (
                                <div className="bloc-reponse-ia">
                                  <p className={reponse.contenu ? undefined : "texte-discret"}>
                                    {reponse.contenu ?? "Information non trouvée dans les documents."}
                                  </p>

                                  {reponse.contenu && (
                                    <div className="bloc-reponse-ia__meta">
                                      {reponse.score_confiance !== null && (
                                        <span
                                          className={`badge ${
                                            reponse.score_confiance >= 0.7 ? "badge--traite" : "badge--en_attente"
                                          }`}
                                        >
                                          {Math.round(reponse.score_confiance * 100)}% de confiance
                                        </span>
                                      )}
                                      {reponse.statut === "valide_utilisateur" && (
                                        <span className="badge badge--actif">Validé</span>
                                      )}
                                    </div>
                                  )}

                                  {reponse.citations.length > 0 && (
                                    <ul className="liste-citations">
                                      {reponse.citations.map((citation) => (
                                        <li key={citation.chunk_id} className="texte-discret">
                                          {citation.document_nom}
                                          {citation.page_debut && ` · p.${citation.page_debut}`}
                                          {citation.titre_section && ` · ${citation.titre_section}`}
                                        </li>
                                      ))}
                                    </ul>
                                  )}
                                </div>
                              )}
                            </div>

                            {reponse && reponse.contenu && reponse.statut === "generee" && (
                              <div className="question-item__actions">
                                <button
                                  type="button"
                                  className="bouton-icone bouton-icone--valider"
                                  onClick={() => onValider(reponse)}
                                  disabled={validationEnCoursId === reponse.id}
                                  title="Valider cette réponse"
                                  aria-label={`Valider la réponse à ${question.question}`}
                                >
                                  <Check size={15} />
                                </button>
                              </div>
                            )}
                          </li>
                        );
                      })}
                  </ul>
                </div>
              ))}
          </div>
        ))
      )}
    </>
  );
}
