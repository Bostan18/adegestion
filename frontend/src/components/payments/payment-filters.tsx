"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Search, X } from "lucide-react";

import { ExportPaymentsButton } from "@/components/payments/export-payments-button";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  PAYMENT_METHODS,
  PAYMENT_METHOD_LABELS,
  PAYMENT_STATUSES,
  PAYMENT_STATUS_LABELS,
} from "@/lib/format";

const ALL = "tous";
const FILTER_KEYS = ["q", "status", "method", "due_from", "due_to"];

export function PaymentFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("q") ?? "");

  function applyFilter(key: string, value: string | null) {
    const params = new URLSearchParams(searchParams.toString());
    if (value && value !== ALL) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.delete("page");
    router.push(`/paiements?${params.toString()}`);
  }

  const hasFilters = FILTER_KEYS.some((key) => searchParams.get(key));

  return (
    <div className="space-y-3">
      <form
        className="flex flex-wrap items-center gap-3"
        onSubmit={(event) => {
          event.preventDefault();
          applyFilter("q", search.trim() || null);
        }}
      >
        <div className="relative min-w-[220px] flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Rechercher un locataire"
            className="pl-9"
            aria-label="Rechercher un locataire"
          />
        </div>

        <div className="flex w-full gap-3 sm:w-auto">
          <Select
            value={searchParams.get("status") ?? ALL}
            onValueChange={(value) => applyFilter("status", value)}
          >
            <SelectTrigger className="flex-1 sm:w-[160px]" aria-label="Filtrer par statut">
              <SelectValue placeholder="Statut" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL}>Tous les statuts</SelectItem>
              {PAYMENT_STATUSES.map((status) => (
                <SelectItem key={status} value={status}>
                  {PAYMENT_STATUS_LABELS[status]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={searchParams.get("method") ?? ALL}
            onValueChange={(value) => applyFilter("method", value)}
          >
            <SelectTrigger className="flex-1 sm:w-[180px]" aria-label="Filtrer par mode">
              <SelectValue placeholder="Mode" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL}>Tous les modes</SelectItem>
              {PAYMENT_METHODS.map((method) => (
                <SelectItem key={method} value={method}>
                  {PAYMENT_METHOD_LABELS[method]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button type="submit" variant="secondary">
          Filtrer
        </Button>
      </form>

      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <Label htmlFor="dueFrom" className="text-xs text-muted-foreground">
            Échéances du
          </Label>
          <Input
            id="dueFrom"
            type="date"
            className="w-[170px]"
            value={searchParams.get("due_from") ?? ""}
            onChange={(event) => applyFilter("due_from", event.target.value || null)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="dueTo" className="text-xs text-muted-foreground">
            au
          </Label>
          <Input
            id="dueTo"
            type="date"
            className="w-[170px]"
            value={searchParams.get("due_to") ?? ""}
            onChange={(event) => applyFilter("due_to", event.target.value || null)}
          />
        </div>

        <ExportPaymentsButton />

        {hasFilters ? (
          <Button type="button" variant="ghost" onClick={() => { setSearch(""); router.push("/paiements"); }}>
            <X className="h-4 w-4" />
            Réinitialiser
          </Button>
        ) : null}
      </div>
    </div>
  );
}
