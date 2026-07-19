/**
 * Client HTTP minimal vers l'API Mauricette.
 * Centralise l'URL de base et la gestion des erreurs pour tous les appels API.
 */

const URL_BASE_API: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

/** Erreur levée quand l'API répond avec un statut HTTP non 2xx. */
export class ErreurApi extends Error {
  constructor(
    public readonly statut: number,
    message: string,
  ) {
    super(message);
    this.name = "ErreurApi";
  }
}

async function traiterReponse<T>(reponse: Response): Promise<T> {
  if (!reponse.ok) {
    const corps = await reponse.json().catch(() => null);
    const message = corps?.detail ?? `Erreur HTTP ${reponse.status}`;
    throw new ErreurApi(reponse.status, message);
  }
  return reponse.json() as Promise<T>;
}

export async function requeteJson<T>(chemin: string, options?: RequestInit): Promise<T> {
  const reponse = await fetch(`${URL_BASE_API}${chemin}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  return traiterReponse<T>(reponse);
}

export async function requeteFormulaire<T>(chemin: string, corps: FormData): Promise<T> {
  const reponse = await fetch(`${URL_BASE_API}${chemin}`, { method: "POST", body: corps });
  return traiterReponse<T>(reponse);
}
