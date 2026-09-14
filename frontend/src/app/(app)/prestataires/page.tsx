import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { ContractorManager } from "@/components/maintenance/contractor-manager";
import { Button } from "@/components/ui/button";
import { serverFetch } from "@/lib/api/server";
import { canDeleteTickets, canHandleTickets } from "@/lib/format";
import type { Contractor, Page, User } from "@/types/api";

export const metadata = { title: "Prestataires, AdeImmo" };

export default async function ContractorsPage() {
  const [user, contractors] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    serverFetch<Page<Contractor>>("/api/v1/contractors?limit=100"),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <Button variant="ghost" size="sm" asChild className="-ml-3">
          <Link href="/maintenance">
            <ArrowLeft className="h-4 w-4" />
            Retour à la maintenance
          </Link>
        </Button>
        <h1 className="text-2xl font-semibold tracking-tight">Prestataires</h1>
        <p className="text-sm text-muted-foreground">
          Les artisans et entreprises qui interviennent sur les biens de l&apos;agence.
        </p>
      </div>

      <ContractorManager
        contractors={contractors.items}
        canManage={canHandleTickets(user.role)}
        canDelete={canDeleteTickets(user.role)}
      />
    </div>
  );
}
