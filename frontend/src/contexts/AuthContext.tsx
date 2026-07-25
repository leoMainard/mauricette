import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { deconnecter as appelDeconnexion, obtenirUtilisateurCourant } from "../api/authApi";
import type { Utilisateur } from "../api/types";

interface ValeurAuthContext {
  utilisateur: Utilisateur | null;
  chargement: boolean;
  rafraichir: () => Promise<void>;
  deconnecter: () => Promise<void>;
}

const AuthContext = createContext<ValeurAuthContext | null>(null);

/** Fournit l'utilisateur connecté (ou `null`) à toute l'application, hydraté au montage. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [utilisateur, setUtilisateur] = useState<Utilisateur | null>(null);
  const [chargement, setChargement] = useState(true);

  const rafraichir = useCallback(async () => {
    try {
      const resultat = await obtenirUtilisateurCourant();
      setUtilisateur(resultat);
    } catch {
      setUtilisateur(null);
    } finally {
      setChargement(false);
    }
  }, []);

  useEffect(() => {
    rafraichir();
  }, [rafraichir]);

  async function deconnecter() {
    await appelDeconnexion();
    setUtilisateur(null);
  }

  return (
    <AuthContext.Provider value={{ utilisateur, chargement, rafraichir, deconnecter }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): ValeurAuthContext {
  const contexte = useContext(AuthContext);
  if (!contexte) {
    throw new Error("useAuth doit être utilisé à l'intérieur d'un <AuthProvider>.");
  }
  return contexte;
}
