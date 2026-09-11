"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  PROPERTY_STATUSES,
  PROPERTY_STATUS_LABELS,
  PROPERTY_TYPES,
  PROPERTY_TYPE_LABELS,
} from "@/lib/format";
import type { Property, PropertyInput, PropertyStatus, PropertyType } from "@/types/api";

interface PropertyFormProps {
  /** Bien existant en mode edition, absent en mode creation. */
  property?: Property;
}

function initialState(property?: Property): PropertyInput {
  return {
    title: property?.title ?? "",
    type: property?.type ?? "appartement",
    address: property?.address ?? "",
    city: property?.city ?? "",
    surface_m2: property?.surface_m2 ?? "",
    rent_amount: property?.rent_amount ?? "",
    status: property?.status ?? "disponible",
    owner_name: property?.owner_name ?? "",
    owner_contact: property?.owner_contact ?? "",
  };
}

export function PropertyForm({ property }: PropertyFormProps) {
  const router = useRouter();
  const [form, setForm] = useState<PropertyInput>(() => initialState(property));
  const [isPending, setIsPending] = useState(false);

  const isEdit = Boolean(property);

  function update<K extends keyof PropertyInput>(key: K, value: PropertyInput[K]) {
    setForm((previous) => ({ ...previous, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsPending(true);

    // Les champs optionnels vides sont envoyes a null plutot qu'en chaine vide.
    const payload: PropertyInput = {
      ...form,
      surface_m2: form.surface_m2 ? form.surface_m2 : null,
      owner_name: form.owner_name ? form.owner_name : null,
      owner_contact: form.owner_contact ? form.owner_contact : null,
    };

    try {
      const saved = await apiFetch<Property>(
        isEdit ? `/api/v1/properties/${property!.id}` : "/api/v1/properties",
        { method: isEdit ? "PATCH" : "POST", body: JSON.stringify(payload) }
      );
      toast.success(isEdit ? "Bien mis à jour." : "Bien créé.");
      router.push(`/biens/${saved.id}`);
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Enregistrement impossible.");
    } finally {
      setIsPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Informations du bien</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="title">Titre</Label>
            <Input
              id="title"
              required
              minLength={2}
              value={form.title}
              onChange={(event) => update("title", event.target.value)}
              placeholder="Villa 4 pièces à Cocody"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="type">Type</Label>
            <Select
              value={form.type}
              onValueChange={(value) => update("type", value as PropertyType)}
            >
              <SelectTrigger id="type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PROPERTY_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>
                    {PROPERTY_TYPE_LABELS[type]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="status">Statut</Label>
            <Select
              value={form.status}
              onValueChange={(value) => update("status", value as PropertyStatus)}
            >
              <SelectTrigger id="status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PROPERTY_STATUSES.map((status) => (
                  <SelectItem key={status} value={status}>
                    {PROPERTY_STATUS_LABELS[status]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="address">Adresse</Label>
            <Input
              id="address"
              required
              minLength={2}
              value={form.address}
              onChange={(event) => update("address", event.target.value)}
              placeholder="Rue des Jardins, Angré 7e tranche"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="city">Ville</Label>
            <Input
              id="city"
              required
              minLength={2}
              value={form.city}
              onChange={(event) => update("city", event.target.value)}
              placeholder="Abidjan"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="surface">Surface (m²)</Label>
            <Input
              id="surface"
              type="number"
              min={0}
              step="0.01"
              value={form.surface_m2 ?? ""}
              onChange={(event) => update("surface_m2", event.target.value)}
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
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Propriétaire</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="owner">Nom</Label>
            <Input
              id="owner"
              value={form.owner_name ?? ""}
              onChange={(event) => update("owner_name", event.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="ownerContact">Contact</Label>
            <Input
              id="ownerContact"
              value={form.owner_contact ?? ""}
              onChange={(event) => update("owner_contact", event.target.value)}
              placeholder="+225 07 00 00 00 00"
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={() => router.back()}>
          Annuler
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {isEdit ? "Enregistrer" : "Créer le bien"}
        </Button>
      </div>
    </form>
  );
}
