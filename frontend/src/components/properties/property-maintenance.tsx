import Link from "next/link";
import { Plus } from "lucide-react";

import { TicketList } from "@/components/maintenance/ticket-list";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Ticket } from "@/types/api";

/** Tickets de maintenance d'un bien, affiches sur sa fiche. */
export function PropertyMaintenance({
  propertyId,
  tickets,
  total,
}: {
  propertyId: string;
  tickets: Ticket[];
  total: number;
}) {
  const open = tickets.filter((ticket) => ticket.is_open).length;

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle>Maintenance</CardTitle>
          <p className="text-sm text-muted-foreground">
            {open > 0 ? `${open} ticket${open > 1 ? "s" : ""} à traiter` : "Aucun ticket ouvert"}
          </p>
        </div>
        {/* Les trois rôles peuvent déclarer un ticket. */}
        <Button variant="secondary" size="sm" asChild>
          <Link href={`/maintenance/nouveau?bien=${propertyId}`}>
            <Plus className="h-4 w-4" />
            Déclarer
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {tickets.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            Aucun ticket pour ce bien.
          </p>
        ) : (
          <TicketList
            tickets={tickets}
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
