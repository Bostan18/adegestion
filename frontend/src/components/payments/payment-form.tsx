"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiFetch } from "@/lib/api/client";
import {
  PAYMENT_METHODS,
  PAYMENT_METHOD_LABELS,
  PAYMENT_STATUSES,
  PAYMENT_STATUS_LABELS,
  isReferenceRequired,
} from "@/lib/format";
import type { Lease, Payment, PaymentInput, PaymentMethod, PaymentStatus } from "@/types/api";

interface PaymentFormProps {
  /** Paiement existant en mode edition, absent en mode creation. */
  payment?: Payment;
  /** Baux selectionnables. Le bail d'un paiement existant n'est plus modifiable. */
  leases: Lease[];
  defaultLeaseId?: string;
}

function initialState(
  payment: Payment | undefined,
  leases: Lease[],
  defaultLeaseId?: string
): PaymentInput {
  const today = new Date().toISOString().slice(0, 10);
  return {
    lease_id: payment?.lease_id ?? defaultLeaseId ?? leases[0]?.id ?? "",
    amount: payment?.amount ?? "",
    payment_method: payment?.payment_method ?? "especes",
    reference_number: payment?.reference_number ?? "",
    period_start: payment?.period_start ?? today,
    period_end: payment?.period_end ?? today,
    due_date: payment?.due_date ?? today,
    paid_at: payment?.paid_at ?? today,
    status: payment?.status ?? "paye",
  };
}

export function PaymentForm({ payment, leases, defaultLeaseId }: PaymentFormProps) {
  const router = useRouter();
  const [form, setForm] = useState<PaymentInput>(() =>
    initialState(payment, leases, defaultLeaseId)
  );
  const [isPending, setIsPending] = useState(false);

  const isEdit = Boolean(payment);
  const referenceRequired = isReferenceRequired(form.payment_method);
  // L'API refuse une date d'encaissement sur un paiement en attente.
  const acceptsPaidAt = form.status !== "en_attente";

  function update<K extends keyof PaymentInput>(key: K, value: PaymentInput[K]) {
    setForm((previous) => ({ ...previous, [key]: value }));
  }

  function changeLease(leaseId: string) {
    update("lease_id", leaseId);
    // Le loyer du bail sert de proposition, le comptable reste libre.
    const selected = leases.find((lease) => lease.id === leaseId);
    if (selected && !form.amount) {
      update("amount", selected.rent_amount);
    }
  }

  function changeStatus(status: PaymentStatus) {
    setForm((previous) => ({
      ...previous,
      status,
      // Un paiement en attente ne porte pas de date d'encaissement.
      paid_at: status === "en_attente" ? "" : previous.paid_at || previous.due_date,
    }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsPending(true);

    const payload = {
      ...form,
      reference_number: form.reference_number ? form.reference_number : null,
      paid_at: form.paid_at ? form.paid_at : null,
    };
    if (isEdit) {
      delete (payload as Partial<PaymentInput>).lease_id;
    }

    try {
      const saved = await apiFetch<Payment>(
        isEdit ? `/api/v1/payments/${payment!.id}` : "/api/v1/payments",
        { method: isEdit ? "PATCH" : "POST", body: JSON.stringify(payload) }
      );
      toast.success(isEdit ? "Paiement mis à jour." : "Paiement enregistré.");
      router.push(`/paiements/${saved.id}`);
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Enregistrement impossible.");
    } finally {
      setIsPending(false);
    }
  }

  if (!isEdit && leases.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-sm text-muted-foreground">
          Aucun bail enregistré. Créez d&apos;abord un bail pour pouvoir y rattacher un paiement.
        </p>
      </Card>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Bail réglé</CardTitle>
          {isEdit ? (
            <CardDescription>
              Le bail rattaché à un paiement ne peut plus être changé.
            </CardDescription>
          ) : null}
        </CardHeader>
        <CardContent>
          {isEdit ? (
            <p className="font-medium">
              {payment?.lease?.tenant_name ?? "-"}
              {payment?.lease?.property ? (
                <span className="text-muted-foreground">
                  {" "}
                  · {payment.lease.property.title}
                </span>
              ) : null}
            </p>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="lease">Bail</Label>
              <Select value={form.lease_id} onValueChange={changeLease}>
                <SelectTrigger id="lease">
                  <SelectValue placeholder="Choisir un bail" />
                </SelectTrigger>
                <SelectContent>
                  {leases.map((lease) => (
                    <SelectItem key={lease.id} value={lease.id}>
                      {lease.tenant_name}
                      {lease.property ? ` (${lease.property.title})` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Période réglée</CardTitle>
          <CardDescription>
            L&apos;échéance est la date à laquelle le loyer était dû.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="periodStart">Du</Label>
            <Input
              id="periodStart"
              type="date"
              required
              value={form.period_start}
              onChange={(event) => update("period_start", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="periodEnd">Au</Label>
            <Input
              id="periodEnd"
              type="date"
              required
              min={form.period_start || undefined}
              value={form.period_end}
              onChange={(event) => update("period_end", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="dueDate">Échéance</Label>
            <Input
              id="dueDate"
              type="date"
              required
              value={form.due_date}
              onChange={(event) => update("due_date", event.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Encaissement</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="amount">Montant (FCFA)</Label>
            <Input
              id="amount"
              type="number"
              min={0}
              step="1"
              required
              value={form.amount}
              onChange={(event) => update("amount", event.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="status">Statut</Label>
            <Select value={form.status} onValueChange={(v) => changeStatus(v as PaymentStatus)}>
              <SelectTrigger id="status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PAYMENT_STATUSES.map((status) => (
                  <SelectItem key={status} value={status}>
                    {PAYMENT_STATUS_LABELS[status]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="method">Mode de paiement</Label>
            <Select
              value={form.payment_method}
              onValueChange={(value) => update("payment_method", value as PaymentMethod)}
            >
              <SelectTrigger id="method">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PAYMENT_METHODS.map((method) => (
                  <SelectItem key={method} value={method}>
                    {PAYMENT_METHOD_LABELS[method]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="reference">
              Référence{referenceRequired ? "" : " (facultative)"}
            </Label>
            <Input
              id="reference"
              required={referenceRequired}
              value={form.reference_number ?? ""}
              onChange={(event) => update("reference_number", event.target.value)}
              placeholder={referenceRequired ? "Numéro du chèque" : "Numéro de transaction"}
            />
            {referenceRequired ? (
              <p className="text-xs text-muted-foreground">
                Obligatoire pour un chèque, afin de pouvoir tracer un rejet.
              </p>
            ) : null}
          </div>

          <div className="space-y-2">
            <Label htmlFor="paidAt">Date d&apos;encaissement</Label>
            <Input
              id="paidAt"
              type="date"
              required={form.status === "paye"}
              disabled={!acceptsPaidAt}
              value={form.paid_at ?? ""}
              onChange={(event) => update("paid_at", event.target.value)}
            />
            {!acceptsPaidAt ? (
              <p className="text-xs text-muted-foreground">
                Un paiement en attente n&apos;a pas encore de date d&apos;encaissement.
              </p>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={() => router.back()}>
          Annuler
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {isEdit ? "Enregistrer" : "Enregistrer le paiement"}
        </Button>
      </div>
    </form>
  );
}
