import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listerAppelsOffre } from "../api/appelsOffreApi";
import { ErreurApi } from "../api/client";
import type { AppelOffreAvecStatistiques, StatutAppelOffre } from "../api/types";

const LIBELLES_STATUT: Record<StatutAppelOffre, string> = {
  brouillon: "Brouillon",
  en_cours: "En cours",
  traite: "Traité",
  archive: "Archivé",
};

function formaterTaille(octets: number): string {
  if (octets < 1024) return `${octets} o`;
  if (octets < 1024 * 1024) return `${(octets / 1024).toFixed(1)} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1)} Mo`;
}

function formaterDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

/** Page d'accueil : liste des Appels d'Offres, avec recherche par nom. */
export function PageListeAppelsOffre() {
  const [terme, setTerme] = useState("");
  const [appelsOffre, setAppelsOffre] = useState<AppelOffreAvecStatistiques[]>([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);

  useEffect(() => {
    let annule = false;
    setChargement(true);

    const delai = setTimeout(async () => {
      try {
        const resultats = await listerAppelsOffre(terme);
        if (!annule) setAppelsOffre(resultats);
      } catch (e) {
        if (!annule) setErreur(e instanceof ErreurApi ? e.message : "Erreur de chargement");
      } finally {
        if (!annule) setChargement(false);
      }
    }, 300);

    return () => {
      annule = true;
      clearTimeout(delai);
    };
  }, [terme]);

  return (
    <div className="page">
      <header className="entete">
        <h1>Mauricette</h1>
        <p className="texte-discret">
          Dépose ton Appel d'Offres, et laisse Mauricette t'aider à y voir clair.
        </p>
      </header>

      <main className="contenu">
        <div className="carte carte--resume">
          <input
            type="search"
            value={terme}
            onChange={(e) => setTerme(e.target.value)}
            placeholder="Rechercher un Appel d'Offres par nom..."
            aria-label="Rechercher un Appel d'Offres par nom"
          />
          <Link to="/appels-offre/nouveau">
            <button type="button">Nouvel Appel d'Offres</button>
          </Link>
        </div>

        {erreur && <p className="message-erreur">{erreur}</p>}

        {chargement ? (
          <p className="texte-discret">Chargement...</p>
        ) : appelsOffre.length === 0 ? (
          <p className="texte-discret">
            {terme ? "Aucun Appel d'Offres ne correspond à cette recherche." : "Aucun Appel d'Offres pour le moment."}
          </p>
        ) : (
          <table className="table-documents">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Statut</th>
                <th>Créé par</th>
                <th>Créé le</th>
                <th>Documents</th>
                <th>Taille</th>
              </tr>
            </thead>
            <tbody>
              {appelsOffre.map(({ appel_offre, nombre_documents, taille_totale_octets }) => (
                <tr key={appel_offre.id}>
                  <td>
                    <Link to={`/appels-offre/${appel_offre.id}`}>{appel_offre.nom}</Link>
                  </td>
                  <td>
                    <span className={`badge badge--${appel_offre.statut}`}>
                      {LIBELLES_STATUT[appel_offre.statut]}
                    </span>
                  </td>
                  <td>{appel_offre.cree_par}</td>
                  <td>{formaterDate(appel_offre.date_creation)}</td>
                  <td>{nombre_documents}</td>
                  <td>{formaterTaille(taille_totale_octets)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </main>
    </div>
  );
}
