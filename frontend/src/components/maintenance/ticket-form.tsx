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
  TICKET_PRIORITIES,
  TICKET_PRIORITY_LABELS,
  TICKET_STATUSES,
  TICKET_STATUS_LABELS,
  acceptsActualCost,
} from "@/lib/format";
import type {
  Contractor,
  PropertyListItem,
  Ticket,
  TicketInput,
  TicketPriority,
  TicketStatus,
} from "@/types/api";

const NONE = "aucun";

interface TicketFormProps {
  ticket?: Ticket;
  properties: PropertyListItem[];
  contractors: Contractor[];
  defaultPropertyId?: string;
  /** Le comptable déclare un ticket mais ne peut pas le traiter. */
  canHandle: boolean;
}

function initialState(
  ticket: Ticket | undefined,
  properties: PropertyListItem[],
  defaultPropertyId?: string
): TicketInput {
  return {
    property_id: ticket?.property_id ?? defaultPropertyId ?? properties[0]?.id ?? "",
    title: ticket?.title ?? "",
    description: ticket?.description ?? "",
    priority: ticket?.priority ?? "moyenne",
    status: ticket?.status ?? "ouvert",
    contractor_id: ticket?.contractor_id ?? null,
    estimated_cost: ticket?.estimated_cost ?? "",
    actual_cost: ticket?.actual_cost ?? "",
    billed_to_owner: ticket?.billed_to_owner ?? false,
  };
}

export function TicketForm({
  ticket,
  properties,
  contractors,
  defaultPropertyId,
  canHandle,
}: TicketFormProps) {
  const router = useRouter();
  const [form, setForm] = useState<TicketInput>(() =>
    initialState(ticket, properties, defaultPropertyId)
  );
  const [isPending, setIsPending] = useState(false);

  const isEdit = Boolean(ticket);
  const costAccepted = acceptsActualCost(form.status);

  function update<K extends keyof TicketInput>(key: K, value: TicketInput[K]) {
    setForm((previous) => ({ ...previous, [key]: value }));
  }

  function changeStatus(status: TicketStatus) {
    setForm((previous) => ({
      ...previous,
      status,
      // L'API refuse un coût réel tant que l'intervention n'est pas terminée.
      actual_cost: acceptsActualCost(status) ? previous.actual_cost : "",
    }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsPending(true);

    const payload = {
      ...form,
      description: form.description ? form.description : null,
      contractor_id: form.contractor_id ? form.contractor_id : null,
      estimated_cost: form.estimated_cost ? form.estimated_cost : null,
      actual_cost: form.actual_cost ? form.actual_cost : null,
    };
    if (isEdit) {
      delete (payload as Partial<TicketInput>).property_id;
    }

    try {
      const saved = await apiFetch<Ticket>(
        isEdit ? `/api/v1/maintenance/${ticket!.id}` : "/api/v1/maintenance",
        { method: isEdit ? "PATCH" : "POST", body: JSON.stringify(payload) }
      );
      toast.success(isEdit ? "Ticket mis à jour." : "Ticket déclaré.");
      router.push(`/maintenance/${saved.id}`);
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Enregistrement impossible.");
    } finally {
      setIsPending(false);
    }
  }

  if (!isEdit && properties.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-sm text-muted-foreground">
          Aucun bien enregistré. Créez d&apos;abord un bien pour pouvoir y rattacher un ticket.
        </p>
      </Card>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Signalement</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="property">Bien concerné</Label>
            {isEdit ? (
              <p className="font-medium">{ticket?.property?.title ?? "-"}</p>
            ) : (
              <Select
                value={form.property_id}
                onValueChange={(value) => update("property_id", value)}
              >
                <SelectTrigger id="property">
                  <SelectValue placeholder="Choisir un bien" />
                </SelectTrigger>
                <SelectContent>
                  {properties.map((property) => (
                    <SelectItem key={property.id} value={property.id}>
                      {property.title} ({property.city})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="title">Intitulé</Label>
            <Input
              id="title"
              required
              minLength={2}
              value={form.title}
              onChange={(event) => update("title", event.target.value)}
              placeholder="Fuite sous l'évier de la cuisine"
            />
          </div>

          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              rows={4}
              className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              value={form.description ?? ""}
              onChange={(event) => update("description", event.target.value)}
              placeholder="Ce que le locataire a signalé, ce qui a été constaté."
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="priority">Priorité</Label>
            <Select
              value={form.priority}
              onValueChange={(value) => update("priority", value as TicketPriority)}
            >
              <SelectTrigger id="priority">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TICKET_PRIORITIES.map((priority) => (
                  <SelectItem key={priority} value={priority}>
                    {TICKET_PRIORITY_LABELS[priority]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="status">Statut</Label>
            <Select
              value={form.status}
              onValueChange={(value) => changeStatus(value as TicketStatus)}
              disabled={!canHandle}
            >
              <SelectTrigger id="status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TICKET_STATUSES.map((status) => (
                  <SelectItem key={status} value={status}>
                    {TICKET_STATUS_LABELS[status]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {!canHandle ? (
              <p className="text-xs text-muted-foreground">
                Vous pouvez déclarer un ticket, son traitement revient à un agent.
              </p>
            ) : null}
          </div>
        </CardContent>
      </Card>

      {canHandle ? (
        <Card>
          <CardHeader>
            <CardTitle>Intervention</CardTitle>
            <CardDescription>
              Le coût réel ne se saisit qu&apos;une fois le ticket résolu ou fermé.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="contractor">Prestataire</Label>
              <Select
                value={form.contractor_id ?? NONE}
                onValueChange={(value) =>
                  update("contractor_id", value === NONE ? null : value)
                }
              >
                <SelectTrigger id="contractor">
                  <SelectValue placeholder="Aucun prestataire" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={NONE}>Aucun prestataire</SelectItem>
                  {contractors.map((contractor) => (
                    <SelectItem key={contractor.id} value={contractor.id}>
                      {contractor.name}
                      {contractor.trade ? ` (${contractor.trade})` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="estimated">Coût estimé (FCFA)</Label>
              <Input
                id="estimated"
                type="number"
                min={0}
                step="1"
                value={form.estimated_cost ?? ""}
                onChange={(event) => update("estimated_cost", event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="actual">Coût réel (FCFA)</Label>
              <Input
                id="actual"
                type="number"
                min={0}
                step="1"
                disabled={!costAccepted}
                value={form.actual_cost ?? ""}
                onChange={(event) => update("actual_cost", event.target.value)}
              />
              {!costAccepted ? (
                <p className="text-xs text-muted-foreground">
                  Disponible une fois le ticket résolu ou fermé.
                </p>
              ) : null}
            </div>

            <div className="flex items-center gap-2 sm:col-span-2">
              <input
                id="billed"
                type="checkbox"
                className="h-4 w-4 rounded border-input"
                checked={form.billed_to_owner}
                onChange={(event) => update("billed_to_owner", event.target.checked)}
              />
              <Label htmlFor="billed" className="font-normal">
                Refacturé au propriétaire
              </Label>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={() => router.back()}>
          Annuler
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {isEdit ? "Enregistrer" : "Déclarer le ticket"}
        </Button>
      </div>
    </form>
  );
}
