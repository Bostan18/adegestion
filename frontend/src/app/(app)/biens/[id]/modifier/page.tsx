import { notFound, redirect } from "next/navigation";

import { PropertyForm } from "@/components/properties/property-form";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import { canManageProperties } from "@/lib/format";
import type { Property, User } from "@/types/api";

export const metadata = { title: "Modifier un bien, AdeImmo" };

export default async function EditPropertyPage({ params }: { params: { id: string } }) {
  const user = await serverFetch<User>("/api/v1/me");

  if (!canManageProperties(user.role)) {
    redirect(`/biens/${params.id}`);
  }

  let property: Property;
  try {
    property = await serverFetch<Property>(`/api/v1/properties/${params.id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Modifier le bien</h1>
      <PropertyForm property={property} />
    </div>
  );
}
