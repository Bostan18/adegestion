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
import {
  TICKET_PRIORITIES,
  TICKET_PRIORITY_LABELS,
  TICKET_STATUSES,
  TICKET_STATUS_LABELS,
} from "@/lib/format";

const ALL = "tous";
const FILTER_KEYS = ["q", "status", "priority", "open_only"];

export function TicketFilters() {
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
    router.push(`/maintenance?${params.toString()}`);
  }

  const openOnly = searchParams.get("open_only") === "true";
  const hasFilters = FILTER_KEYS.some((key) => searchParams.get(key));

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
          placeholder="Rechercher un intitulé"
          className="pl-9"
          aria-label="Rechercher un ticket"
        />
      </div>

      <div className="flex w-full gap-3 sm:w-auto">
        <Select
          value={searchParams.get("status") ?? ALL}
          onValueChange={(value) => applyFilter("status", value)}
        >
          <SelectTrigger className="flex-1 sm:w-[170px]" aria-label="Filtrer par statut">
            <SelectValue placeholder="Statut" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>Tous les statuts</SelectItem>
            {TICKET_STATUSES.map((status) => (
              <SelectItem key={status} value={status}>
                {TICKET_STATUS_LABELS[status]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={searchParams.get("priority") ?? ALL}
          onValueChange={(value) => applyFilter("priority", value)}
        >
          <SelectTrigger className="flex-1 sm:w-[170px]" aria-label="Filtrer par priorité">
            <SelectValue placeholder="Priorité" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL}>Toutes priorités</SelectItem>
            {TICKET_PRIORITIES.map((priority) => (
              <SelectItem key={priority} value={priority}>
                {TICKET_PRIORITY_LABELS[priority]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button
        type="button"
        variant={openOnly ? "default" : "outline"}
        onClick={() => applyFilter("open_only", openOnly ? null : "true")}
      >
        À traiter
      </Button>

      <Button type="submit" variant="secondary">
        Filtrer
      </Button>

      {hasFilters ? (
        <Button
          type="button"
          variant="ghost"
          onClick={() => {
            setSearch("");
            router.push("/maintenance");
          }}
        >
          <X className="h-4 w-4" />
          Réinitialiser
        </Button>
      ) : null}
    </form>
  );
}
