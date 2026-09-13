import Link from "next/link";
import { Plus } from "lucide-react";

import { PaymentList } from "@/components/payments/payment-list";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatAmount } from "@/lib/format";
import type { Payment } from "@/types/api";

/** Paiements rattaches a un bail, affiches sur sa fiche. */
export function LeasePayments({
  leaseId,
  payments,
  total,
  encaisse,
}: {
  leaseId: string;
  payments: Payment[];
  total: number;
  encaisse: string;
}) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle>Paiements</CardTitle>
          <p className="text-sm text-muted-foreground">
            {formatAmount(encaisse)} encaissés sur ce bail
          </p>
        </div>
        <Button variant="secondary" size="sm" asChild>
          <Link href={`/paiements/nouveau?bail=${leaseId}`}>
            <Plus className="h-4 w-4" />
            Ajouter
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {payments.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            Aucun paiement enregistré pour ce bail.
          </p>
        ) : (
          <PaymentList
            payments={payments}
            total={total}
            pageSize={total || 1}
            currentPage={1}
            hideTenantColumn
          />
        )}
      </CardContent>
    </Card>
  );
}
