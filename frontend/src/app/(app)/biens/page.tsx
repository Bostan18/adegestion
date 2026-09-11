import Link from "next/link";
import { Plus } from "lucide-react";

import { PropertyFilters } from "@/components/properties/property-filters";
import { PropertyTable } from "@/components/properties/property-table";
import { Button } from "@/components/ui/button";
import { serverFetch } from "@/lib/api/server";
import { canManageProperties } from "@/lib/format";
import type { Page, PropertyListItem, User } from "@/types/api";

export const metadata = { title: "Biens, AdeImmo" };

const PAGE_SIZE = 20;

interface PageProps {
  searchParams: {
    q?: string;
    status?: string;
    type?: string;
    city?: string;
    page?: string;
  };
}

function buildQuery(searchParams: PageProps["searchParams"], offset: number): string {
  const params = new URLSearchParams();
  if (searchParams.q) params.set("q", searchParams.q);
  if (searchParams.status) params.set("status", searchParams.status);
  if (searchParams.type) params.set("type", searchParams.type);
  if (searchParams.city) params.set("city", searchParams.city);
  params.set("limit", String(PAGE_SIZE));
  params.set("offset", String(offset));
  return params.toString();
}

export default async function PropertiesPage({ searchParams }: PageProps) {
  const currentPage = Math.max(Number(searchParams.page ?? "1"), 1);
  const offset = (currentPage - 1) * PAGE_SIZE;

  const [user, properties] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    serverFetch<Page<PropertyListItem>>(`/api/v1/properties?${buildQuery(searchParams, offset)}`),
  ]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Biens</h1>
          <p className="text-sm text-muted-foreground">
            {properties.total} bien{properties.total > 1 ? "s" : ""} au portefeuille
          </p>
        </div>

        {canManageProperties(user.role) ? (
          <Button asChild>
            <Link href="/biens/nouveau">
              <Plus className="h-4 w-4" />
              Ajouter un bien
            </Link>
          </Button>
        ) : null}
      </div>

      <PropertyFilters />

      <PropertyTable
        properties={properties.items}
        total={properties.total}
        pageSize={PAGE_SIZE}
        currentPage={currentPage}
      />
    </div>
  );
}
