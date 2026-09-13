/** Types partages avec l'API FastAPI (backend/app/schemas). */

export type UserRole = "admin" | "agent" | "comptable";

export type PropertyType = "appartement" | "villa" | "terrain" | "bureau" | "commerce";

export type PropertyStatus = "disponible" | "loue" | "en_travaux" | "indisponible";

export type LeaseStatus = "actif" | "termine" | "resilie";

export type PaymentMethod =
  | "especes"
  | "virement_bancaire"
  | "cheque"
  | "mobile_money_orange"
  | "mobile_money_mtn"
  | "mobile_money_moov"
  | "wave";

export type PaymentStatus = "paye" | "en_attente" | "en_retard" | "rejete";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
}

export interface Photo {
  id: string;
  property_id: string;
  storage_path: string;
  is_cover: boolean;
  created_at: string;
  url: string | null;
}

export interface Property {
  id: string;
  title: string;
  type: PropertyType;
  address: string;
  city: string;
  surface_m2: string | null;
  rent_amount: string;
  status: PropertyStatus;
  owner_name: string | null;
  owner_contact: string | null;
  created_at: string;
  photos: Photo[];
}

export interface PropertyListItem extends Omit<Property, "photos"> {
  cover_url: string | null;
}

export interface PropertyInput {
  title: string;
  type: PropertyType;
  address: string;
  city: string;
  surface_m2?: string | null;
  rent_amount: string;
  status: PropertyStatus;
  owner_name?: string | null;
  owner_contact?: string | null;
}

export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface PhotoUploadTicket {
  bucket: string;
  storage_path: string;
  token: string;
  signed_url: string;
}

export interface LeasePropertySummary {
  id: string;
  title: string;
  type: PropertyType;
  city: string;
}

export interface Lease {
  id: string;
  property_id: string;
  tenant_name: string;
  tenant_contact: string | null;
  start_date: string;
  end_date: string | null;
  rent_amount: string;
  deposit_amount: string | null;
  status: LeaseStatus;
  created_at: string;
  property: LeasePropertySummary | null;
}

export interface LeaseInput {
  property_id: string;
  tenant_name: string;
  tenant_contact?: string | null;
  start_date: string;
  end_date?: string | null;
  rent_amount: string;
  deposit_amount?: string | null;
  status: LeaseStatus;
}

export interface PaymentLeaseSummary {
  id: string;
  tenant_name: string;
  property: { id: string; title: string } | null;
}

export interface Payment {
  id: string;
  lease_id: string;
  amount: string;
  payment_method: PaymentMethod;
  reference_number: string | null;
  period_start: string;
  period_end: string;
  due_date: string;
  paid_at: string | null;
  status: PaymentStatus;
  receipt_generated: boolean;
  created_at: string;
  is_overdue: boolean;
  lease: PaymentLeaseSummary | null;
}

export interface PaymentInput {
  lease_id: string;
  amount: string;
  payment_method: PaymentMethod;
  reference_number?: string | null;
  period_start: string;
  period_end: string;
  due_date: string;
  paid_at?: string | null;
  status: PaymentStatus;
}

export interface PaymentPage {
  items: Payment[];
  total: number;
  limit: number;
  offset: number;
  totals: { encaisse: string; attendu: string };
}
