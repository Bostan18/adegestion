import Link from "next/link";
import { AlertTriangle } from "lucide-react";

import { Pagination } from "@/components/pagination";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  TICKET_PRIORITY_LABELS,
  TICKET_PRIORITY_VARIANTS,
  TICKET_STATUS_LABELS,
  TICKET_STATUS_VARIANTS,
  formatAmount,
  formatDate,
} from "@/lib/format";
import type { Ticket } from "@/types/api";

interface TicketListProps {
  tickets: Ticket[];
  total: number;
  pageSize: number;
  currentPage: number;
  /** Masque la colonne du bien quand la liste est déjà filtrée sur un bien. */
  hidePropertyColumn?: boolean;
}

export function TicketList({
  tickets,
  total,
  pageSize,
  currentPage,
  hidePropertyColumn = false,
}: TicketListProps) {
  if (tickets.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-sm text-muted-foreground">
          Aucun ticket ne correspond à cette recherche.
        </p>
      </Card>
    );
  }

  const lastPage = Math.max(Math.ceil(total / pageSize), 1);

  return (
    <div className="space-y-4">
      {/* Téléphone et tablette */}
      <ul className="grid gap-3 sm:grid-cols-2 lg:hidden">
        {tickets.map((ticket) => (
          <li key={ticket.id}>
            <TicketCard ticket={ticket} hideProperty={hidePropertyColumn} />
          </li>
        ))}
      </ul>

      {/* Ordinateur */}
      <Card className="hidden lg:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Intitulé</TableHead>
              {hidePropertyColumn ? null : <TableHead>Bien</TableHead>}
              <TableHead>Priorité</TableHead>
              <TableHead>Prestataire</TableHead>
              <TableHead>Coût</TableHead>
              <TableHead>Déclaré le</TableHead>
              <TableHead>Statut</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tickets.map((ticket) => (
              <TableRow key={ticket.id}>
                <TableCell>
                  <Link
                    href={`/maintenance/${ticket.id}`}
                    className="font-medium hover:underline"
                  >
                    {ticket.title}
                  </Link>
                </TableCell>
                {hidePropertyColumn ? null : (
                  <TableCell>
                    {ticket.property ? (
                      <Link
                        href={`/biens/${ticket.property.id}`}
                        className="text-sm hover:underline"
                      >
                        {ticket.property.title}
                      </Link>
                    ) : (
                      "-"
                    )}
                  </TableCell>
                )}
                <TableCell>
                  <Badge variant={TICKET_PRIORITY_VARIANTS[ticket.priority]}>
                    {ticket.priority === "urgente" ? (
                      <AlertTriangle className="mr-1 h-3 w-3" />
                    ) : null}
                    {TICKET_PRIORITY_LABELS[ticket.priority]}
                  </Badge>
                </TableCell>
                <TableCell className="text-sm">{ticket.contractor?.name ?? "-"}</TableCell>
                <TableCell className="whitespace-nowrap text-sm">
                  {formatAmount(ticket.actual_cost ?? ticket.estimated_cost)}
                  {ticket.actual_cost === null && ticket.estimated_cost ? (
                    <span className="text-muted-foreground"> (devis)</span>
                  ) : null}
                </TableCell>
                <TableCell className="whitespace-nowrap text-sm">
                  {formatDate(ticket.created_at)}
                </TableCell>
                <TableCell>
                  <Badge variant={TICKET_STATUS_VARIANTS[ticket.status]}>
                    {TICKET_STATUS_LABELS[ticket.status]}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {lastPage > 1 ? (
        <Pagination basePath="/maintenance" currentPage={currentPage} lastPage={lastPage} />
      ) : null}
    </div>
  );
}

function TicketCard({ ticket, hideProperty }: { ticket: Ticket; hideProperty: boolean }) {
  const cost = ticket.actual_cost ?? ticket.estimated_cost;

  return (
    <Link
      href={`/maintenance/${ticket.id}`}
      className="flex h-full flex-col gap-1 rounded-lg border bg-card p-3 transition-colors hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="line-clamp-2 font-medium leading-snug">{ticket.title}</p>
        <Badge variant={TICKET_STATUS_VARIANTS[ticket.status]} className="shrink-0">
          {TICKET_STATUS_LABELS[ticket.status]}
        </Badge>
      </div>

      {!hideProperty && ticket.property ? (
        <p className="line-clamp-1 text-xs text-muted-foreground">{ticket.property.title}</p>
      ) : null}

      <div className="mt-auto flex flex-wrap items-center gap-2 pt-1">
        <Badge variant={TICKET_PRIORITY_VARIANTS[ticket.priority]}>
          {TICKET_PRIORITY_LABELS[ticket.priority]}
        </Badge>
        {cost ? <span className="text-sm font-semibold">{formatAmount(cost)}</span> : null}
      </div>
      <p className="text-xs text-muted-foreground">
        {ticket.contractor?.name ?? "Aucun prestataire"} · {formatDate(ticket.created_at)}
      </p>
    </Link>
  );
}
