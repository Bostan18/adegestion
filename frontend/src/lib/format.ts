import type {
  LeaseStatus,
  PaymentMethod,
  PaymentStatus,
  PropertyStatus,
  PropertyType,
  UserRole,
} from "@/types/api";

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

type BadgeVariant = "default" | "secondary" | "destructive" | "outline" | "success" | "warning";

export const PROPERTY_STATUS_VARIANTS: Record<PropertyStatus, BadgeVariant> = {
  disponible: "success",
  loue: "default",
  en_travaux: "warning",
  indisponible: "secondary",
};

export const LEASE_STATUS_LABELS: Record<LeaseStatus, string> = {
  actif: "Actif",
  termine: "Terminé",
  resilie: "Résilié",
};

export const LEASE_STATUS_VARIANTS: Record<LeaseStatus, BadgeVariant> = {
  actif: "success",
  termine: "secondary",
  resilie: "destructive",
};

export const LEASE_STATUSES = Object.keys(LEASE_STATUS_LABELS) as LeaseStatus[];

export const PAYMENT_METHOD_LABELS: Record<PaymentMethod, string> = {
  especes: "Espèces",
  virement_bancaire: "Virement bancaire",
  cheque: "Chèque",
  mobile_money_orange: "Orange Money",
  mobile_money_mtn: "MTN Mobile Money",
  mobile_money_moov: "Moov Money",
  wave: "Wave",
};

export const PAYMENT_STATUS_LABELS: Record<PaymentStatus, string> = {
  paye: "Payé",
  en_attente: "En attente",
  en_retard: "En retard",
  rejete: "Rejeté",
};

export const PAYMENT_STATUS_VARIANTS: Record<PaymentStatus, BadgeVariant> = {
  paye: "success",
  en_attente: "warning",
  en_retard: "destructive",
  rejete: "destructive",
};

export const PAYMENT_METHODS = Object.keys(PAYMENT_METHOD_LABELS) as PaymentMethod[];
export const PAYMENT_STATUSES = Object.keys(PAYMENT_STATUS_LABELS) as PaymentStatus[];

/** Seul le chèque impose une référence, pour pouvoir tracer un rejet. */
export function isReferenceRequired(method: PaymentMethod): boolean {
  return method === "cheque";
}

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  admin: "Administrateur",
  agent: "Agent",
  comptable: "Comptable",
};

/** Periode d'un bail, la fin restant ouverte tant qu'aucun terme n'est fixe. */
export function formatPeriod(start: string, end: string | null): string {
  return end ? `${formatDate(start)} au ${formatDate(end)}` : `depuis le ${formatDate(start)}`;
}

export const PROPERTY_TYPES = Object.keys(PROPERTY_TYPE_LABELS) as PropertyType[];
export const PROPERTY_STATUSES = Object.keys(PROPERTY_STATUS_LABELS) as PropertyStatus[];

/** Seuls l'admin et l'agent modifient les biens (voir docs/ARCHITECTURE.md). */
export function canManageProperties(role: UserRole | undefined): boolean {
  return role === "admin" || role === "agent";
}

export function canDeleteProperties(role: UserRole | undefined): boolean {
  return role === "admin";
}

/** Les baux suivent exactement le meme RBAC que les biens. */
export const canManageLeases = canManageProperties;
export const canDeleteLeases = canDeleteProperties;

/**
 * Les paiements sont plus restreints : l'agent n'y accède pas du tout, même en
 * lecture (voir docs/ARCHITECTURE.md).
 */
export function canAccessPayments(role: UserRole | undefined): boolean {
  return role === "admin" || role === "comptable";
}

export function canDeletePayments(role: UserRole | undefined): boolean {
  return role === "admin";
}
