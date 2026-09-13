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
import { LEASE_STATUSES, LEASE_STATUS_LABELS, PROPERTY_TYPE_LABELS } from "@/lib/format";
import type { Lease, LeaseInput, LeaseStatus, PropertyListItem } from "@/types/api";

interface LeaseFormProps {
  /** Bail existant en mode edition, absent en mode creation. */
  lease?: Lease;
  /** Biens selectionnables. Le bien d'un bail existant n'est plus modifiable. */
  properties: PropertyListItem[];
  /** Bien pre-selectionne quand on cree un bail depuis une fiche de bien. */
  defaultPropertyId?: string;
}

function initialState(
  lease: Lease | undefined,
  properties: PropertyListItem[],
  defaultPropertyId?: string
): LeaseInput {
  return {
    property_id: lease?.property_id ?? defaultPropertyId ?? properties[0]?.id ?? "",
    tenant_name: lease?.tenant_name ?? "",
    tenant_contact: lease?.tenant_contact ?? "",
    start_date: lease?.start_date ?? new Date().toISOString().slice(0, 10),
    end_date: lease?.end_date ?? "",
    rent_amount: lease?.rent_amount ?? "",
    deposit_amount: lease?.deposit_amount ?? "",
    status: lease?.status ?? "actif",
  };
}

export function LeaseForm({ lease, properties, defaultPropertyId }: LeaseFormProps) {
  const router = useRouter();
  const [form, setForm] = useState<LeaseInput>(() =>
    initialState(lease, properties, defaultPropertyId)
  );
  const [isPending, setIsPending] = useState(false);

  const isEdit = Boolean(lease);

  function update<K extends keyof LeaseInput>(key: K, value: LeaseInput[K]) {
    setForm((previous) => ({ ...previous, [key]: value }));
  }

  function prefillRentFromProperty(propertyId: string) {
    update("property_id", propertyId);
    // Le loyer du bien sert de proposition, l'agent reste libre de l'ajuster.
    const selected = properties.find((property) => property.id === propertyId);
    if (selected && !form.rent_amount) {
      update("rent_amount", selected.rent_amount);
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsPending(true);

    const payload = {
      ...form,
      tenant_contact: form.tenant_contact ? form.tenant_contact : null,
      end_date: form.end_date ? form.end_date : null,
      deposit_amount: form.deposit_amount ? form.deposit_amount : null,
    };
    // Le bien rattache n'est pas modifiable apres coup.
    if (isEdit) {
      delete (payload as Partial<LeaseInput>).property_id;
    }

    try {
      const saved = await apiFetch<Lease>(
        isEdit ? `/api/v1/leases/${lease!.id}` : "/api/v1/leases",
        { method: isEdit ? "PATCH" : "POST", body: JSON.stringify(payload) }
      );
      toast.success(isEdit ? "Bail mis à jour." : "Bail créé.");
      router.push(`/baux/${saved.id}`);
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
          Aucun bien enregistré. Créez d&apos;abord un bien pour pouvoir y rattacher un bail.
        </p>
      </Card>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Bien loué</CardTitle>
          {isEdit ? (
            <CardDescription>
              Le bien rattaché à un bail ne peut plus être changé.
            </CardDescription>
          ) : null}
        </CardHeader>
        <CardContent>
          {isEdit ? (
            <p className="font-medium">{lease?.property?.title ?? "-"}</p>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="property">Bien</Label>
              <Select value={form.property_id} onValueChange={prefillRentFromProperty}>
                <SelectTrigger id="property">
                  <SelectValue placeholder="Choisir un bien" />
                </SelectTrigger>
                <SelectContent>
                  {properties.map((property) => (
                    <SelectItem key={property.id} value={property.id}>
                      {property.title} ({PROPERTY_TYPE_LABELS[property.type]}, {property.city})
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
          <CardTitle>Locataire</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="tenant">Nom</Label>
            <Input
              id="tenant"
              required
              minLength={2}
              value={form.tenant_name}
              onChange={(event) => update("tenant_name", event.target.value)}
              placeholder="Koffi N'Guessan"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="tenantContact">Contact</Label>
            <Input
              id="tenantContact"
              value={form.tenant_contact ?? ""}
              onChange={(event) => update("tenant_contact", event.target.value)}
              placeholder="+225 07 00 00 00 00"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Conditions</CardTitle>
          <CardDescription>
            Laissez la date de fin vide pour un bail sans terme fixe.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="startDate">Début</Label>
            <Input
              id="startDate"
              type="date"
              required
              value={form.start_date}
              onChange={(event) => update("start_date", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="endDate">Fin</Label>
            <Input
              id="endDate"
              type="date"
              min={form.start_date || undefined}
              value={form.end_date ?? ""}
              onChange={(event) => update("end_date", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="rent">Loyer mensuel (FCFA)</Label>
            <Input
              id="rent"
              type="number"
              min={0}
              step="1"
              required
              value={form.rent_amount}
              onChange={(event) => update("rent_amount", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="deposit">Dépôt de garantie (FCFA)</Label>
            <Input
              id="deposit"
              type="number"
              min={0}
              step="1"
              value={form.deposit_amount ?? ""}
              onChange={(event) => update("deposit_amount", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="status">Statut</Label>
            <Select
              value={form.status}
              onValueChange={(value) => update("status", value as LeaseStatus)}
            >
              <SelectTrigger id="status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LEASE_STATUSES.map((status) => (
                  <SelectItem key={status} value={status}>
                    {LEASE_STATUS_LABELS[status]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Un bail actif passe le bien en « loué ». Le terminer ou le résilier le remet en
              « disponible ».
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={() => router.back()}>
          Annuler
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {isEdit ? "Enregistrer" : "Créer le bail"}
        </Button>
      </div>
    </form>
  );
}
