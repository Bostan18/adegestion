import type { PropertyStatus, PropertyType, UserRole } from "@/types/api";

const currencyFormatter = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: "XOF",
  maximumFractionDigits: 0,
});

const dateFormatter = new Intl.DateTimeFormat("fr-FR", {
  day: "2-digit",
  month: "long",
  year: "numeric",
});

/** Montant en francs CFA. L'API renvoie les montants sous forme de chaine. */
export function formatAmount(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "-";
  const amount = typeof value === "string" ? Number(value) : value;
  return Number.isNaN(amount) ? "-" : currencyFormatter.format(amount);
}

export function formatSurface(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "-";
  const surface = typeof value === "string" ? Number(value) : value;
  return Number.isNaN(surface) ? "-" : `${surface.toLocaleString("fr-FR")} m²`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "-" : dateFormatter.format(date);
}

export const PROPERTY_TYPE_LABELS: Record<PropertyType, string> = {
  appartement: "Appartement",
  villa: "Villa",
  terrain: "Terrain",
  bureau: "Bureau",
  commerce: "Commerce",
};

export const PROPERTY_STATUS_LABELS: Record<PropertyStatus, string> = {
  disponible: "Disponible",
  loue: "Loué",
  en_travaux: "En travaux",
  indisponible: "Indisponible",
};

export const PROPERTY_STATUS_VARIANTS: Record<
  PropertyStatus,
  "default" | "secondary" | "destructive" | "outline" | "success" | "warning"
> = {
  disponible: "success",
  loue: "default",
  en_travaux: "warning",
  indisponible: "secondary",
};

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  admin: "Administrateur",
  agent: "Agent",
  comptable: "Comptable",
};

export const PROPERTY_TYPES = Object.keys(PROPERTY_TYPE_LABELS) as PropertyType[];
export const PROPERTY_STATUSES = Object.keys(PROPERTY_STATUS_LABELS) as PropertyStatus[];

/** Seuls l'admin et l'agent modifient les biens (voir docs/ARCHITECTURE.md). */
export function canManageProperties(role: UserRole | undefined): boolean {
  return role === "admin" || role === "agent";
}

export function canDeleteProperties(role: UserRole | undefined): boolean {
  return role === "admin";
}
