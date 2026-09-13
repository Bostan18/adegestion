import Link from "next/link";
import { Plus } from "lucide-react";

import { LeaseList } from "@/components/leases/lease-list";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Lease } from "@/types/api";

/** Baux rattaches a un bien, affiches sur sa fiche. */
export function PropertyLeases({
  propertyId,
  leases,
  total,
  canManage,
}: {
  propertyId: string;
  leases: Lease[];
  total: number;
  canManage: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle>Baux</CardTitle>
        {canManage ? (
          <Button variant="secondary" size="sm" asChild>
            <Link href={`/baux/nouveau?bien=${propertyId}`}>
              <Plus className="h-4 w-4" />
              Ajouter
            </Link>
          </Button>
        ) : null}
      </CardHeader>
      <CardContent>
        {leases.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            Aucun bail pour ce bien.
          </p>
        ) : (
          <LeaseList
            leases={leases}
            total={total}
            pageSize={total || 1}
            currentPage={1}
            hidePropertyColumn
          />
        )}
      </CardContent>
    </Card>
  );
}
