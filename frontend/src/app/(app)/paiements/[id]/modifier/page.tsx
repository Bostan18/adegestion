import { notFound, redirect } from "next/navigation";

import { PaymentForm } from "@/components/payments/payment-form";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import { canAccessPayments } from "@/lib/format";
import type { Payment, User } from "@/types/api";

export const metadata = { title: "Modifier un paiement, AdeImmo" };

export default async function EditPaymentPage({ params }: { params: { id: string } }) {
  const user = await serverFetch<User>("/api/v1/me");

  if (!canAccessPayments(user.role)) {
    redirect("/biens");
  }

  let payment: Payment;
  try {
    payment = await serverFetch<Payment>(`/api/v1/payments/${params.id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Modifier le paiement</h1>
      <PaymentForm payment={payment} leases={[]} />
    </div>
  );
}
