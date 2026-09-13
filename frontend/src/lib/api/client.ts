"use client";

import { createClient } from "@/lib/supabase/client";

import { ApiError, toApiError } from "./errors";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Appelle l'API FastAPI depuis le navigateur, avec le jeton de la session. */
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    throw new ApiError("Votre session a expire, reconnectez-vous.", 401);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...init.headers,
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw await toApiError(response);
  }

  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

/**
 * Telecharge un fichier renvoye par l'API (quittance PDF, export CSV).
 *
 * Un lien simple ne conviendrait pas : l'API attend le jeton Supabase dans
 * l'en-tete Authorization, qu'un navigateur n'ajoute pas sur une navigation.
 * On recupere donc un blob puis on declenche le telechargement nous-memes.
 */
export async function apiDownload(
  path: string,
  init: RequestInit = {},
  fallbackFilename = "export"
): Promise<void> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    throw new ApiError("Votre session a expire, reconnectez-vous.", 401);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { ...init.headers, Authorization: `Bearer ${session.access_token}` },
  });

  if (!response.ok) {
    throw await toApiError(response);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filenameFromResponse(response) ?? fallbackFilename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function filenameFromResponse(response: Response): string | null {
  const disposition = response.headers.get("content-disposition");
  const match = disposition?.match(/filename="?([^"]+)"?/);
  return match ? match[1] : null;
}

export { ApiError };
