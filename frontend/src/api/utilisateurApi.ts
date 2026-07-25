/**
 * Fonctions d'accès à l'API pour l'administration des utilisateurs et groupes.
 */

import { requeteJson } from "./client";
import type { GroupeUtilisateur, Utilisateur } from "./types";

export async function creerGroupe(nom: string): Promise<GroupeUtilisateur> {
  return requeteJson<GroupeUtilisateur>("/groupes", {
    method: "POST",
    body: JSON.stringify({ nom }),
  });
}

export async function listerGroupes(): Promise<GroupeUtilisateur[]> {
  return requeteJson<GroupeUtilisateur[]>("/groupes");
}

export async function listerUtilisateurs(): Promise<Utilisateur[]> {
  return requeteJson<Utilisateur[]>("/utilisateurs");
}

export async function affecterGroupe(
  utilisateurId: string,
  groupeId: string | null,
): Promise<Utilisateur> {
  return requeteJson<Utilisateur>(`/utilisateurs/${utilisateurId}/groupe`, {
    method: "PATCH",
    body: JSON.stringify({ groupe_id: groupeId }),
  });
}
