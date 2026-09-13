import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { AlertTriangle, ArrowLeft, FileCheck2 } from "lucide-react";

import { DeletePaymentButton } from "@/components/payments/delete-payment-button";
import { ReceiptButton } from "@/components/payments/receipt-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import {
  PAYMENT_METHOD_LABELS,
  PAYMENT_STATUS_LABELS,
  PAYMENT_STATUS_VARIANTS,
  canAccessPayments,
  canDeletePayments,
  formatAmount,
  formatDate,
} from "@/lib/format";
import type { Payment, User } from "@/types/api";

async function loadPayment(id: string): Promise<Payment> {
  try {
    return await serverFetch<Payment>(`/api/v1/payments/${id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
}

export default async function PaymentDetailPage({ params }: { params: { id: string } }) {
  const user = await serverFetch<User>("/api/v1/me");

  if (!canAccessPayments(user.role)) {
    redirect("/biens");
  }

  const payment = await loadPayment(params.id);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <Button variant="ghost" size="sm" asChild className="-ml-3">
            <Link href="/paiements">
              <ArrowLeft className="h-4 w-4" />
              Retour aux paiements
            </Link>
          </Button>
          <h1 className="text-2xl font-semibold tracking-tight">
            {formatAmount(payment.amount)}
          </h1>
          <p className="text-sm text-muted-foreground">
            {payment.lease?.tenant_name ?? "-"}, période du{" "}
            {formatDate(payment.period_start)} au {formatDate(payment.period_end)}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={PAYMENT_STATUS_VARIANTS[payment.status]}>
            {PAYMENT_STATUS_LABELS[payment.status]}
          </Badge>
          <ReceiptButton paymentId={payment.id} disabled={payment.status !== "paye"} />
          <Button variant="outline" asChild>
            <Link href={`/paiements/${payment.id}/modifier`}>Modifier</Link>
          </Button>
          {canDeletePayments(user.role) ? (
            <DeletePaymentButton
              paymentId={payment.id}
              label={`${formatAmount(payment.amount)} du ${formatDate(payment.due_date)}`}
            />
          ) : null}
        </div>
      </div>

      {payment.is_overdue ? (
        <Card className="border-destructive/40 bg-destructive/5">
          <CardContent className="flex items-center gap-3 p-4">
            <AlertTriangle className="h-5 w-5 shrink-0 text-destructive" />
            <p className="text-sm">
              L&apos;échéance du {formatDate(payment.due_date)} est passée et ce loyer n&apos;est
              pas encaissé.
            </p>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Encaissement</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3 text-sm">
              <Row label="Montant" value={formatAmount(payment.amount)} />
              <Row
                label="Mode de paiement"
                value={PAYMENT_METHOD_LABELS[payment.payment_method]}
              />
              <Row label="Référence" value={payment.reference_number ?? "-"} />
              <Row label="Échéance" value={formatDate(payment.due_date)} />
              <Row
                label="Encaissé le"
                value={payment.paid_at ? formatDate(payment.paid_at) : "Pas encore encaissé"}
              />
              <Row label="Enregistré le" value={formatDate(payment.created_at)} />
            </dl>

            {payment.receipt_generated ? (
              <p className="mt-4 inline-flex items-center gap-2 text-sm text-muted-foreground">
                <FileCheck2 className="h-4 w-4" />
                Une quittance a déjà été générée pour ce paiement.
              </p>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Bail réglé</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="font-medium">{payment.lease?.tenant_name ?? "-"}</p>
              {payment.lease?.property ? (
                <p className="text-sm text-muted-foreground">{payment.lease.property.title}</p>
              ) : null}
            </div>
            <div className="flex flex-wrap gap-2">
              {payment.lease ? (
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/baux/${payment.lease.id}`}>Voir le bail</Link>
                </Button>
              ) : null}
              {payment.lease?.property ? (
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/biens/${payment.lease.property.id}`}>Voir le bien</Link>
                </Button>
              ) : null}
            </div>
          </CardContent>
        </Card>
      </div>
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
