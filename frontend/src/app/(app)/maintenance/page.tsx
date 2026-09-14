import Link from "next/link";
import { Plus } from "lucide-react";

import { TicketFilters } from "@/components/maintenance/ticket-filters";
import { TicketList } from "@/components/maintenance/ticket-list";
import { Button } from "@/components/ui/button";
import { serverFetch } from "@/lib/api/server";
import type { Page, Ticket, User } from "@/types/api";

export const metadata = { title: "Maintenance, AdeImmo" };

const PAGE_SIZE = 20;

interface PageProps {
  searchParams: {
    q?: string;
    status?: string;
    priority?: string;
    open_only?: string;
    page?: string;
  };
}

export default async function MaintenancePage({ searchParams }: PageProps) {
  const currentPage = Math.max(Number(searchParams.page ?? "1"), 1);

  const params = new URLSearchParams();
  for (const key of ["q", "status", "priority", "open_only"] as const) {
    if (searchParams[key]) params.set(key, searchParams[key]!);
  }
  params.set("limit", String(PAGE_SIZE));
  params.set("offset", String((currentPage - 1) * PAGE_SIZE));

  const [, tickets] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    serverFetch<Page<Ticket>>(`/api/v1/maintenance?${params.toString()}`),
  ]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Maintenance</h1>
          <p className="text-sm text-muted-foreground">
            {tickets.total} ticket{tickets.total > 1 ? "s" : ""} sur la sélection
          </p>
        </div>

        {/* Les trois rôles peuvent déclarer un ticket. */}
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" asChild>
            <Link href="/prestataires">Prestataires</Link>
          </Button>
          <Button asChild>
            <Link href="/maintenance/nouveau">
              <Plus className="h-4 w-4" />
              Déclarer un ticket
            </Link>
          </Button>
        </div>
      </div>

      <TicketFilters />

      <TicketList
        tickets={tickets.items}
        total={tickets.total}
        pageSize={PAGE_SIZE}
        currentPage={currentPage}
      />
    </div>
  );
}
