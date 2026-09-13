import Link from "next/link";
import { AlertTriangle, FileCheck2 } from "lucide-react";

import { Pagination } from "@/components/pagination";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  PAYMENT_METHOD_LABELS,
  PAYMENT_STATUS_LABELS,
  PAYMENT_STATUS_VARIANTS,
  formatAmount,
  formatDate,
} from "@/lib/format";
import type { Payment } from "@/types/api";

interface PaymentListProps {
  payments: Payment[];
  total: number;
  pageSize: number;
  currentPage: number;
  /** Masque la colonne du locataire quand la liste est filtrée sur un bail. */
  hideTenantColumn?: boolean;
}

export function PaymentList({
  payments,
  total,
  pageSize,
  currentPage,
  hideTenantColumn = false,
}: PaymentListProps) {
  if (payments.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-sm text-muted-foreground">
          Aucun paiement ne correspond à cette recherche.
        </p>
      </Card>
    );
  }

  const lastPage = Math.max(Math.ceil(total / pageSize), 1);

  return (
    <div className="space-y-4">
      {/* Telephone et tablette */}
      <ul className="grid gap-3 sm:grid-cols-2 lg:hidden">
        {payments.map((payment) => (
          <li key={payment.id}>
            <PaymentCard payment={payment} hideTenant={hideTenantColumn} />
          </li>
        ))}
      </ul>

      {/* Ordinateur */}
      <Card className="hidden lg:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Échéance</TableHead>
              {hideTenantColumn ? null : <TableHead>Locataire</TableHead>}
              <TableHead>Période</TableHead>
              <TableHead>Montant</TableHead>
              <TableHead>Mode</TableHead>
              <TableHead>Encaissé le</TableHead>
              <TableHead>Statut</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {payments.map((payment) => (
              <TableRow key={payment.id}>
                <TableCell className="whitespace-nowrap">
                  <Link
                    href={`/paiements/${payment.id}`}
                    className="font-medium hover:underline"
                  >
                    {formatDate(payment.due_date)}
                  </Link>
                </TableCell>
                {hideTenantColumn ? null : (
                  <TableCell>
                    {payment.lease?.tenant_name ?? "-"}
                    {payment.lease?.property ? (
                      <p className="text-xs text-muted-foreground">
                        {payment.lease.property.title}
                      </p>
                    ) : null}
                  </TableCell>
                )}
                <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
                  {formatDate(payment.period_start)} au {formatDate(payment.period_end)}
                </TableCell>
                <TableCell className="font-medium">{formatAmount(payment.amount)}</TableCell>
                <TableCell className="text-sm">
                  {PAYMENT_METHOD_LABELS[payment.payment_method]}
                  {payment.reference_number ? (
                    <p className="text-xs text-muted-foreground">{payment.reference_number}</p>
                  ) : null}
                </TableCell>
                <TableCell className="whitespace-nowrap text-sm">
                  {payment.paid_at ? formatDate(payment.paid_at) : "-"}
                </TableCell>
                <TableCell>
                  <StatusCell payment={payment} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {lastPage > 1 ? (
        <Pagination basePath="/paiements" currentPage={currentPage} lastPage={lastPage} />
      ) : null}
    </div>
  );
}

function StatusCell({ payment }: { payment: Payment }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <Badge variant={PAYMENT_STATUS_VARIANTS[payment.status]}>
        {PAYMENT_STATUS_LABELS[payment.status]}
      </Badge>
      {payment.is_overdue ? (
        <span
          className="inline-flex items-center gap-1 text-xs font-medium text-destructive"
          title="L'échéance est passée et le loyer n'est pas encaissé"
        >
          <AlertTriangle className="h-3.5 w-3.5" />
          Échéance passée
        </span>
      ) : null}
      {payment.receipt_generated ? (
        <FileCheck2 className="h-4 w-4 text-muted-foreground" aria-label="Quittance générée" />
      ) : null}
    </div>
  );
}

function PaymentCard({ payment, hideTenant }: { payment: Payment; hideTenant: boolean }) {
  return (
    <Link
      href={`/paiements/${payment.id}`}
      className="flex h-full flex-col gap-1 rounded-lg border bg-card p-3 transition-colors hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="line-clamp-2 font-medium leading-snug">
          {hideTenant ? formatDate(payment.due_date) : (payment.lease?.tenant_name ?? "-")}
        </p>
        <Badge variant={PAYMENT_STATUS_VARIANTS[payment.status]} className="shrink-0">
          {PAYMENT_STATUS_LABELS[payment.status]}
        </Badge>
      </div>

      <p className="line-clamp-1 text-xs text-muted-foreground">
        {formatDate(payment.period_start)} au {formatDate(payment.period_end)}
      </p>

      <p className="mt-auto text-sm font-semibold">{formatAmount(payment.amount)}</p>
      <p className="text-xs text-muted-foreground">
        {PAYMENT_METHOD_LABELS[payment.payment_method]}
        {payment.paid_at ? ` · encaissé le ${formatDate(payment.paid_at)}` : ""}
      </p>

      {payment.is_overdue ? (
        <p className="inline-flex items-center gap-1 text-xs font-medium text-destructive">
          <AlertTriangle className="h-3.5 w-3.5" />
          Échéance passée
        </p>
      ) : null}
    </Link>
  );
}
