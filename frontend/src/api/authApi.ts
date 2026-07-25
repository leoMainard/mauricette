/**
 * Fonctions d'accès à l'API pour l'authentification et le profil utilisateur.
 */

import { requeteJson } from "./client";
import type { Utilisateur } from "./types";

export async function inscrire(email: string, motDePasse: string, nom: string): Promise<Utilisateur> {
  return requeteJson<Utilisateur>("/auth/inscription", {
    method: "POST",
    body: JSON.stringify({ email, mot_de_passe: motDePasse, nom }),
  });
}

export async function connecter(email: string, motDePasse: string): Promise<Utilisateur> {
  return requeteJson<Utilisateur>("/auth/connexion", {
    method: "POST",
    body: JSON.stringify({ email, mot_de_passe: motDePasse }),
  });
}

export async function deconnecter(): Promise<void> {
  return requeteJson<void>("/auth/deconnexion", { method: "POST" });
}

export async function obtenirUtilisateurCourant(): Promise<Utilisateur> {
  return requeteJson<Utilisateur>("/auth/moi");
}

export async function modifierProfil(nom: string, email: string): Promise<Utilisateur> {
  return requeteJson<Utilisateur>("/auth/profil", {
    method: "PATCH",
    body: JSON.stringify({ nom, email }),
  });
}

export async function changerMotDePasse(
  ancienMotDePasse: string,
  nouveauMotDePasse: string,
): Promise<void> {
  return requeteJson<void>("/auth/mot-de-passe", {
    method: "PATCH",
    body: JSON.stringify({
      ancien_mot_de_passe: ancienMotDePasse,
      nouveau_mot_de_passe: nouveauMotDePasse,
    }),
  });
}
