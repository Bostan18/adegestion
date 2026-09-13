import Link from "next/link";
import { Plus } from "lucide-react";

import { LeaseFilters } from "@/components/leases/lease-filters";
import { LeaseList } from "@/components/leases/lease-list";
import { Button } from "@/components/ui/button";
import { serverFetch } from "@/lib/api/server";
import { canManageLeases } from "@/lib/format";
import type { Lease, Page, User } from "@/types/api";

export const metadata = { title: "Baux, AdeImmo" };

const PAGE_SIZE = 20;

interface PageProps {
  searchParams: { q?: string; status?: string; page?: string };
}

export default async function LeasesPage({ searchParams }: PageProps) {
  const currentPage = Math.max(Number(searchParams.page ?? "1"), 1);

  const params = new URLSearchParams();
  if (searchParams.q) params.set("q", searchParams.q);
  if (searchParams.status) params.set("status", searchParams.status);
  params.set("limit", String(PAGE_SIZE));
  params.set("offset", String((currentPage - 1) * PAGE_SIZE));

  const [user, leases] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    serverFetch<Page<Lease>>(`/api/v1/leases?${params.toString()}`),
  ]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Baux</h1>
          <p className="text-sm text-muted-foreground">
            {leases.total} {leases.total > 1 ? "baux enregistrés" : "bail enregistré"}
          </p>
        </div>

        {canManageLeases(user.role) ? (
          <Button asChild>
            <Link href="/baux/nouveau">
              <Plus className="h-4 w-4" />
              Ajouter un bail
            </Link>
          </Button>
        ) : null}
      </div>

      <LeaseFilters />

      <LeaseList
        leases={leases.items}
        total={leases.total}
        pageSize={PAGE_SIZE}
        currentPage={currentPage}
      />
    </div>
  );
}
