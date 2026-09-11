export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Traduit une reponse d'erreur de l'API en message affichable. */
export async function toApiError(response: Response): Promise<ApiError> {
  let message = "Une erreur est survenue.";
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") {
      message = body.detail;
    } else if (Array.isArray(body?.detail)) {
      // Erreurs de validation FastAPI.
      message = body.detail
        .map((item: { loc?: (string | number)[]; msg?: string }) => {
          const field = item.loc?.slice(1).join(".") ?? "";
          return field ? `${field} : ${item.msg}` : item.msg;
        })
        .join(", ");
    }
  } catch {
    message = response.statusText || message;
  }
  return new ApiError(message, response.status);
}
