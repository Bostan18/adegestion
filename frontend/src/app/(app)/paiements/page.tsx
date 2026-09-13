import Link from "next/link";
import { redirect } from "next/navigation";
import { Plus } from "lucide-react";

import { PaymentFilters } from "@/components/payments/payment-filters";
import { PaymentList } from "@/components/payments/payment-list";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { serverFetch } from "@/lib/api/server";
import { canAccessPayments, formatAmount } from "@/lib/format";
import type { PaymentPage, User } from "@/types/api";

export const metadata = { title: "Paiements, AdeImmo" };

const PAGE_SIZE = 20;

interface PageProps {
  searchParams: {
    q?: string;
    status?: string;
    method?: string;
    due_from?: string;
    due_to?: string;
    page?: string;
  };
}

export default async function PaymentsPage({ searchParams }: PageProps) {
  const user = await serverFetch<User>("/api/v1/me");

  // L'agent n'a aucun acces aux paiements, pas meme en lecture.
  if (!canAccessPayments(user.role)) {
    redirect("/biens");
  }

  const currentPage = Math.max(Number(searchParams.page ?? "1"), 1);
  const params = new URLSearchParams();
  for (const key of ["q", "status", "method", "due_from", "due_to"] as const) {
    if (searchParams[key]) params.set(key, searchParams[key]!);
  }
  params.set("limit", String(PAGE_SIZE));
  params.set("offset", String((currentPage - 1) * PAGE_SIZE));

  const payments = await serverFetch<PaymentPage>(`/api/v1/payments?${params.toString()}`);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Paiements</h1>
          <p className="text-sm text-muted-foreground">
            {payments.total} paiement{payments.total > 1 ? "s" : ""} sur la sélection
          </p>
        </div>

        <Button asChild>
          <Link href="/paiements/nouveau">
            <Plus className="h-4 w-4" />
            Enregistrer un paiement
          </Link>
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <TotalCard label="Encaissé" value={payments.totals.encaisse} />
        <TotalCard label="Attendu" value={payments.totals.attendu} muted />
      </div>

      <PaymentFilters />

      <PaymentList
        payments={payments.items}
        total={payments.total}
        pageSize={PAGE_SIZE}
        currentPage={currentPage}
      />
    </div>
  );
}

function TotalCard({
  label,
  value,
  muted = false,
}: {
  label: string;
  value: string;
  muted?: boolean;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <p className="text-sm text-muted-foreground">{label}</p>
        <p
          className={
            muted ? "text-2xl font-semibold text-muted-foreground" : "text-2xl font-semibold"
          }
        >
          {formatAmount(value)}
        </p>
      </CardContent>
    </Card>
  );
}
