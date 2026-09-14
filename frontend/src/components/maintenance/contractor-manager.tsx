"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { apiFetch } from "@/lib/api/client";
import type { Contractor, ContractorInput } from "@/types/api";

/**
 * Ecran de gestion des prestataires.
 *
 * Table de reference courte, editee au fil de l'eau : des boites de dialogue
 * plutot que des pages dediees, pour rester dans la liste pendant la saisie.
 */
export function ContractorManager({
  contractors,
  canManage,
  canDelete,
}: {
  contractors: Contractor[];
  canManage: boolean;
  canDelete: boolean;
}) {
  const [editing, setEditing] = useState<Contractor | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  return (
    <div className="space-y-4">
      {canManage ? (
        <div className="flex justify-end">
          <Button onClick={() => setIsCreating(true)}>
            <Plus className="h-4 w-4" />
            Ajouter un prestataire
          </Button>
        </div>
      ) : null}

      {contractors.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-sm text-muted-foreground">Aucun prestataire enregistré.</p>
        </Card>
      ) : (
        <>
          {/* Téléphone et tablette */}
          <ul className="grid gap-3 sm:grid-cols-2 lg:hidden">
            {contractors.map((contractor) => (
              <li key={contractor.id} className="rounded-lg border bg-card p-3">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium">{contractor.name}</p>
                  {contractor.is_active ? null : <Badge variant="secondary">Inactif</Badge>}
                </div>
                <p className="text-xs text-muted-foreground">{contractor.trade ?? "-"}</p>
                <p className="text-sm">{contractor.contact ?? "-"}</p>
                {canManage ? (
                  <div className="mt-2 flex justify-end gap-1">
                    <RowActions
                      contractor={contractor}
                      canDelete={canDelete}
                      onEdit={setEditing}
                    />
                  </div>
                ) : null}
              </li>
            ))}
          </ul>

          {/* Ordinateur */}
          <Card className="hidden lg:block">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nom</TableHead>
                  <TableHead>Métier</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead>État</TableHead>
                  {canManage ? <TableHead className="w-[100px]" /> : null}
                </TableRow>
              </TableHeader>
              <TableBody>
                {contractors.map((contractor) => (
                  <TableRow key={contractor.id}>
                    <TableCell className="font-medium">{contractor.name}</TableCell>
                    <TableCell>{contractor.trade ?? "-"}</TableCell>
                    <TableCell>{contractor.contact ?? "-"}</TableCell>
                    <TableCell className="max-w-[280px] truncate text-sm text-muted-foreground">
                      {contractor.notes ?? "-"}
                    </TableCell>
                    <TableCell>
                      <Badge variant={contractor.is_active ? "success" : "secondary"}>
                        {contractor.is_active ? "Actif" : "Inactif"}
                      </Badge>
                    </TableCell>
                    {canManage ? (
                      <TableCell>
                        <div className="flex justify-end gap-1">
                          <RowActions
                            contractor={contractor}
                            canDelete={canDelete}
                            onEdit={setEditing}
                          />
                        </div>
                      </TableCell>
                    ) : null}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </>
      )}

      <ContractorDialog
        open={isCreating}
        onOpenChange={setIsCreating}
        title="Nouveau prestataire"
      />
      <ContractorDialog
        open={editing !== null}
        onOpenChange={(open) => !open && setEditing(null)}
        title="Modifier le prestataire"
        contractor={editing ?? undefined}
      />
    </div>
  );
}

function RowActions({
  contractor,
  canDelete,
  onEdit,
}: {
  contractor: Contractor;
  canDelete: boolean;
  onEdit: (contractor: Contractor) => void;
}) {
  const router = useRouter();
  const [isPending, setIsPending] = useState(false);

  async function handleDelete() {
    setIsPending(true);
    try {
      await apiFetch(`/api/v1/contractors/${contractor.id}`, { method: "DELETE" });
      toast.success("Prestataire supprimé.");
      router.refresh();
    } catch (error) {
      // L'API refuse en 409 si le prestataire est rattaché à des tickets, et
      // le message oriente vers la désactivation.
      toast.error(error instanceof Error ? error.message : "Suppression impossible.");
    } finally {
      setIsPending(false);
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={() => onEdit(contractor)}
        aria-label={`Modifier ${contractor.name}`}
      >
        <Pencil className="h-4 w-4" />
      </Button>
      {canDelete ? (
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-destructive"
          disabled={isPending}
          onClick={handleDelete}
          aria-label={`Supprimer ${contractor.name}`}
        >
          {isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Trash2 className="h-4 w-4" />
          )}
        </Button>
      ) : null}
    </>
  );
}

function ContractorDialog({
  open,
  onOpenChange,
  title,
  contractor,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  contractor?: Contractor;
}) {
  const router = useRouter();
  const [isPending, setIsPending] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const payload: ContractorInput = {
      name: String(data.get("name") ?? ""),
      trade: String(data.get("trade") ?? "") || null,
      contact: String(data.get("contact") ?? "") || null,
      notes: String(data.get("notes") ?? "") || null,
      is_active: data.get("is_active") === "on",
    };

    setIsPending(true);
    try {
      await apiFetch(
        contractor ? `/api/v1/contractors/${contractor.id}` : "/api/v1/contractors",
        { method: contractor ? "PATCH" : "POST", body: JSON.stringify(payload) }
      );
      toast.success(contractor ? "Prestataire mis à jour." : "Prestataire ajouté.");
      onOpenChange(false);
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Enregistrement impossible.");
    } finally {
      setIsPending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>
            Un prestataire déjà intervenu se désactive plutôt qu&apos;il ne se supprime, pour
            conserver l&apos;historique.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Nom</Label>
            <Input
              id="name"
              name="name"
              required
              minLength={2}
              defaultValue={contractor?.name ?? ""}
              placeholder="Plomberie Lagune"
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="trade">Métier</Label>
              <Input
                id="trade"
                name="trade"
                defaultValue={contractor?.trade ?? ""}
                placeholder="Plombier"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="contact">Contact</Label>
              <Input
                id="contact"
                name="contact"
                defaultValue={contractor?.contact ?? ""}
                placeholder="+225 07 00 00 00 00"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Input
              id="notes"
              name="notes"
              defaultValue={contractor?.notes ?? ""}
              placeholder="Intervient rapidement sur Cocody"
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              id="is_active"
              name="is_active"
              type="checkbox"
              className="h-4 w-4 rounded border-input"
              defaultChecked={contractor?.is_active ?? true}
            />
            <Label htmlFor="is_active" className="font-normal">
              Prestataire actif
            </Label>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Annuler
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Enregistrer
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
