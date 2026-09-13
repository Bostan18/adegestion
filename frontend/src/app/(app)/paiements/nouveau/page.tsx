import { redirect } from "next/navigation";

import { PaymentForm } from "@/components/payments/payment-form";
import { serverFetch } from "@/lib/api/server";
import { canAccessPayments } from "@/lib/format";
import type { Lease, Page, User } from "@/types/api";

export const metadata = { title: "Nouveau paiement, AdeImmo" };

export default async function NewPaymentPage({
  searchParams,
}: {
  searchParams: { bail?: string };
}) {
  const user = await serverFetch<User>("/api/v1/me");

  if (!canAccessPayments(user.role)) {
    redirect("/biens");
  }

  // Les baux actifs d'abord, ce sont eux qui generent des loyers.
  const leases = await serverFetch<Page<Lease>>("/api/v1/leases?limit=100");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Enregistrer un paiement</h1>
        <p className="text-sm text-muted-foreground">
          Un chèque doit porter son numéro, pour pouvoir tracer un éventuel rejet.
        </p>
      </div>
      <PaymentForm leases={leases.items} defaultLeaseId={searchParams.bail} />
    </div>
  );
}
