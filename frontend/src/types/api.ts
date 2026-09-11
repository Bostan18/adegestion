/** Types partages avec l'API FastAPI (backend/app/schemas). */

export type UserRole = "admin" | "agent" | "comptable";

export type PropertyType = "appartement" | "villa" | "terrain" | "bureau" | "commerce";

export type PropertyStatus = "disponible" | "loue" | "en_travaux" | "indisponible";

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
