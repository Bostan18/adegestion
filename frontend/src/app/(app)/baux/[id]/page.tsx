import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Building2 } from "lucide-react";

import { DeleteLeaseButton } from "@/components/leases/delete-lease-button";
import { LeasePayments } from "@/components/leases/lease-payments";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import {
  LEASE_STATUS_LABELS,
  LEASE_STATUS_VARIANTS,
  PROPERTY_TYPE_LABELS,
  canAccessPayments,
  canDeleteLeases,
  canManageLeases,
  formatAmount,
  formatDate,
} from "@/lib/format";
import type { Lease, PaymentPage, User } from "@/types/api";

async function loadLease(id: string): Promise<Lease> {
  try {
    return await serverFetch<Lease>(`/api/v1/leases/${id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
}

export default async function LeaseDetailPage({ params }: { params: { id: string } }) {
  const [user, lease] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    loadLease(params.id),
  ]);

  // L'agent n'a aucun acces aux paiements, on ne les charge meme pas pour lui.
  const payments = canAccessPayments(user.role)
    ? await serverFetch<PaymentPage>(`/api/v1/payments?lease_id=${params.id}&limit=50`)
    : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <Button variant="ghost" size="sm" asChild className="-ml-3">
            <Link href="/baux">
              <ArrowLeft className="h-4 w-4" />
              Retour aux baux
            </Link>
          </Button>
          <h1 className="text-2xl font-semibold tracking-tight">{lease.tenant_name}</h1>
          {lease.tenant_contact ? (
            <p className="text-sm text-muted-foreground">{lease.tenant_contact}</p>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={LEASE_STATUS_VARIANTS[lease.status]}>
            {LEASE_STATUS_LABELS[lease.status]}
          </Badge>
          {canManageLeases(user.role) ? (
            <Button variant="outline" asChild>
              <Link href={`/baux/${lease.id}/modifier`}>Modifier</Link>
            </Button>
          ) : null}
          {canDeleteLeases(user.role) ? (
            <DeleteLeaseButton leaseId={lease.id} tenantName={lease.tenant_name} />
          ) : null}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Conditions</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3 text-sm">
              <Row label="Début" value={formatDate(lease.start_date)} />
              <Row
                label="Fin"
                value={lease.end_date ? formatDate(lease.end_date) : "Sans terme"}
              />
              <Row label="Loyer mensuel" value={formatAmount(lease.rent_amount)} />
              <Row label="Dépôt de garantie" value={formatAmount(lease.deposit_amount)} />
              <Row label="Enregistré le" value={formatDate(lease.created_at)} />
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Bien loué</CardTitle>
          </CardHeader>
          <CardContent>
            {lease.property ? (
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <Building2 className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{lease.property.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {PROPERTY_TYPE_LABELS[lease.property.type]}, {lease.property.city}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/biens/${lease.property.id}`}>Voir la fiche du bien</Link>
                </Button>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Bien introuvable.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {payments ? (
        <LeasePayments
          leaseId={lease.id}
          payments={payments.items}
          total={payments.total}
          encaisse={payments.totals.encaisse}
        />
      ) : null}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b pb-2 last:border-0">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}
