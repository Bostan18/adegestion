import { notFound, redirect } from "next/navigation";

import { LeaseForm } from "@/components/leases/lease-form";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import { canManageLeases } from "@/lib/format";
import type { Lease, User } from "@/types/api";

export const metadata = { title: "Modifier un bail, AdeImmo" };

export default async function EditLeasePage({ params }: { params: { id: string } }) {
  const user = await serverFetch<User>("/api/v1/me");

  if (!canManageLeases(user.role)) {
    redirect(`/baux/${params.id}`);
  }

  let lease: Lease;
  try {
    lease = await serverFetch<Lease>(`/api/v1/leases/${params.id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Modifier le bail</h1>
      <LeaseForm lease={lease} properties={[]} />
    </div>
  );
}
