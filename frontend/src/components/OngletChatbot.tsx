import { ArrowUp, FileText, Sparkles, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { Citation, MessageChatbot } from "../api/types";

interface Props {
  messages: MessageChatbot[];
  chargement: boolean;
  envoiEnCours: boolean;
  erreur: string | null;
  nombreDocuments: number;
  onEnvoyer: (question: string) => void;
  onOuvrirApercuCitation: (citation: Citation) => void;
}

/** Nom de fichier court (sans le chemin de dossier issu d'un zip éclaté), pour les pastilles de citation. */
function nomCourtDocument(nom: string): string {
  return nom.split("/").pop() || nom;
}

function BulleReponse({
  message,
  onOuvrirApercuCitation,
}: {
  message: Pick<MessageChatbot, "contenu" | "citations" | "score_confiance">;
  onOuvrirApercuCitation: (citation: Citation) => void;
}) {
  return (
    <div className="bulle-chatbot bulle-chatbot--assistant">
      <p className={message.contenu ? undefined : "texte-discret"}>
        {message.contenu ?? "Information non trouvée dans les documents."}
      </p>

      {message.contenu && (message.citations.length > 0 || message.score_confiance !== null) && (
        <div className="bloc-reponse-ia__meta">
          {message.citations.length > 0 && (
            <ul className="liste-citations">
              {message.citations.map((citation) => (
                <li key={citation.chunk_id}>
                  <button
                    type="button"
                    className="pastille-citation"
                    onClick={() => onOuvrirApercuCitation(citation)}
                    title={citation.document_nom}
                  >
                    <FileText size={10} className="pastille-citation__icone" />
                    <span className="pastille-citation__label">
                      {nomCourtDocument(citation.document_nom)}
                      {citation.page_debut && ` — p.${citation.page_debut}`}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {message.score_confiance !== null && (
            <span
              className={`pastille-confiance pastille-confiance--${
                message.score_confiance >= 0.7 ? "elevee" : "faible"
              }`}
              title={`${Math.round(message.score_confiance * 100)}% de confiance`}
            >
              <span className="pastille-confiance__point" />
              Confiance {message.score_confiance >= 0.7 ? "élevée" : "faible"}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

/** Onglet "Chatbot" de la fiche AO : question libre sur les documents, avec mémoire de conversation. */
export function OngletChatbot({
  messages,
  chargement,
  envoiEnCours,
  erreur,
  nombreDocuments,
  onEnvoyer,
  onOuvrirApercuCitation,
}: Props) {
  const [question, setQuestion] = useState("");
  const finDuFil = useRef<HTMLDivElement>(null);

  useEffect(() => {
    finDuFil.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, envoiEnCours]);

  function envoyer(evenement: React.FormEvent) {
    evenement.preventDefault();
    const texte = question.trim();
    if (!texte || envoiEnCours) return;
    onEnvoyer(texte);
    setQuestion("");
  }

  return (
    <div className="carte carte--chatbot">
      <div className="chatbot-entete">
        <div className="chatbot-entete__icone">
          <Sparkles size={17} />
        </div>
        <div>
          <p className="chatbot-entete__titre">Mauricette</p>
          <p className="chatbot-entete__sous-titre">
            Interroge les {nombreDocuments} pièce{nombreDocuments > 1 ? "s" : ""} de ce dossier
          </p>
        </div>
      </div>

      <div className="chatbot-fil">
        {chargement ? (
          <p className="texte-discret">Chargement...</p>
        ) : (
          <>
            <div className="ligne-chatbot ligne-chatbot--assistant">
              <div className="avatar-chatbot avatar-chatbot--assistant">
                <Sparkles size={14} />
              </div>
              <div className="bulle-chatbot bulle-chatbot--assistant">
                <p>
                  Bonjour 👋 J'ai analysé les {nombreDocuments} pièce{nombreDocuments > 1 ? "s" : ""} de
                  cet AO. Pose-moi une question sur son contenu.
                </p>
              </div>
            </div>

            {messages.map((message) =>
              message.role === "utilisateur" ? (
                <div key={message.id} className="ligne-chatbot ligne-chatbot--utilisateur">
                  <div className="avatar-chatbot avatar-chatbot--utilisateur">
                    <User size={14} />
                  </div>
                  <div className="bulle-chatbot bulle-chatbot--utilisateur">
                    <p>{message.contenu}</p>
                  </div>
                </div>
              ) : (
                <div key={message.id} className="ligne-chatbot ligne-chatbot--assistant">
                  <div className="avatar-chatbot avatar-chatbot--assistant">
                    <Sparkles size={14} />
                  </div>
                  <BulleReponse message={message} onOuvrirApercuCitation={onOuvrirApercuCitation} />
                </div>
              ),
            )}
          </>
        )}
        {envoiEnCours && (
          <div className="ligne-chatbot ligne-chatbot--assistant">
            <div className="avatar-chatbot avatar-chatbot--assistant">
              <Sparkles size={14} />
            </div>
            <div className="bulle-chatbot bulle-chatbot--assistant">
              <p className="texte-discret">En train d'écrire...</p>
            </div>
          </div>
        )}
        <div ref={finDuFil} />
      </div>

      {erreur && <p className="message-erreur chatbot-erreur">{erreur}</p>}

      <form className="chatbot-zone-saisie" onSubmit={envoyer}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              envoyer(e);
            }
          }}
          placeholder="Pose une question sur cet AO..."
          rows={1}
          disabled={envoiEnCours}
        />
        <button type="submit" disabled={envoiEnCours || !question.trim()} aria-label="Envoyer">
          <ArrowUp size={16} />
        </button>
      </form>
    </div>
  );
}
