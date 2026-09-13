"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Search, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LEASE_STATUSES, LEASE_STATUS_LABELS } from "@/lib/format";

const ALL = "tous";

export function LeaseFilters() {
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
    router.push(`/baux?${params.toString()}`);
  }

  const hasFilters = ["q", "status"].some((key) => searchParams.get(key));

  return (
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

      <Select
        value={searchParams.get("status") ?? ALL}
        onValueChange={(value) => applyFilter("status", value)}
      >
        <SelectTrigger className="w-[170px]" aria-label="Filtrer par statut">
          <SelectValue placeholder="Statut" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ALL}>Tous les statuts</SelectItem>
          {LEASE_STATUSES.map((status) => (
            <SelectItem key={status} value={status}>
              {LEASE_STATUS_LABELS[status]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button type="submit" variant="secondary">
        Filtrer
      </Button>

      {hasFilters ? (
        <Button
          type="button"
          variant="ghost"
          onClick={() => {
            setSearch("");
            router.push("/baux");
          }}
        >
          <X className="h-4 w-4" />
          Réinitialiser
        </Button>
      ) : null}
    </form>
  );
}
