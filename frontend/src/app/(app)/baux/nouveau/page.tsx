import { redirect } from "next/navigation";

import { LeaseForm } from "@/components/leases/lease-form";
import { serverFetch } from "@/lib/api/server";
import { canManageLeases } from "@/lib/format";
import type { Page, PropertyListItem, User } from "@/types/api";

export const metadata = { title: "Nouveau bail, AdeImmo" };

export default async function NewLeasePage({
  searchParams,
}: {
  searchParams: { bien?: string };
}) {
  const user = await serverFetch<User>("/api/v1/me");

  if (!canManageLeases(user.role)) {
    redirect("/baux");
  }

  // La liste des biens alimente le selecteur du formulaire.
  const properties = await serverFetch<Page<PropertyListItem>>("/api/v1/properties?limit=100");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Nouveau bail</h1>
        <p className="text-sm text-muted-foreground">
          Un bail actif ne peut pas chevaucher un autre bail actif sur le même bien.
        </p>
      </div>
      <LeaseForm properties={properties.items} defaultPropertyId={searchParams.bien} />
    </div>
  );
}
