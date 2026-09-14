import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Building2, CheckCircle2, Wrench } from "lucide-react";

import { DeleteTicketButton } from "@/components/maintenance/delete-ticket-button";
import { TicketPhotos } from "@/components/maintenance/ticket-photos";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import {
  TICKET_PRIORITY_LABELS,
  TICKET_PRIORITY_VARIANTS,
  TICKET_STATUS_LABELS,
  TICKET_STATUS_VARIANTS,
  canDeleteTickets,
  canHandleTickets,
  formatAmount,
  formatCostOverrun,
  formatDate,
} from "@/lib/format";
import type { Ticket, User } from "@/types/api";

async function loadTicket(id: string): Promise<Ticket> {
  try {
    return await serverFetch<Ticket>(`/api/v1/maintenance/${id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
}

export default async function TicketDetailPage({ params }: { params: { id: string } }) {
  const [user, ticket] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    loadTicket(params.id),
  ]);

  const canHandle = canHandleTickets(user.role);
  const overrun = formatCostOverrun(ticket.cost_overrun);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <Button variant="ghost" size="sm" asChild className="-ml-3">
            <Link href="/maintenance">
              <ArrowLeft className="h-4 w-4" />
              Retour à la maintenance
            </Link>
          </Button>
          <h1 className="text-2xl font-semibold tracking-tight">{ticket.title}</h1>
          <p className="text-sm text-muted-foreground">
            Déclaré le {formatDate(ticket.created_at)}
            {ticket.reporter ? ` par ${ticket.reporter.full_name}` : ""}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={TICKET_PRIORITY_VARIANTS[ticket.priority]}>
            {TICKET_PRIORITY_LABELS[ticket.priority]}
          </Badge>
          <Badge variant={TICKET_STATUS_VARIANTS[ticket.status]}>
            {TICKET_STATUS_LABELS[ticket.status]}
          </Badge>
          {canHandle ? (
            <Button variant="outline" asChild>
              <Link href={`/maintenance/${ticket.id}/modifier`}>Traiter</Link>
            </Button>
          ) : null}
          {canDeleteTickets(user.role) ? (
            <DeleteTicketButton ticketId={ticket.id} title={ticket.title} />
          ) : null}
        </div>
      </div>

      {ticket.resolved_at ? (
        <Card className="border-emerald-500/40 bg-emerald-50/60">
          <CardContent className="flex items-center gap-3 p-4">
            <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" />
            <p className="text-sm">
              Intervention terminée le {formatDate(ticket.resolved_at)}.
            </p>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Signalement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {ticket.description ? (
              <p className="whitespace-pre-line text-sm">{ticket.description}</p>
            ) : (
              <p className="text-sm text-muted-foreground">Aucune description.</p>
            )}

            {ticket.property ? (
              <div className="flex items-start gap-3 border-t pt-4">
                <Building2 className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
                <div>
                  <p className="font-medium">{ticket.property.title}</p>
                  <p className="text-sm text-muted-foreground">{ticket.property.city}</p>
                  <Button variant="outline" size="sm" asChild className="mt-2">
                    <Link href={`/biens/${ticket.property.id}`}>Voir la fiche du bien</Link>
                  </Button>
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Intervention</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3 text-sm">
              <Row
                label="Prestataire"
                value={
                  ticket.contractor
                    ? `${ticket.contractor.name}${
                        ticket.contractor.trade ? ` (${ticket.contractor.trade})` : ""
                      }`
                    : "Aucun"
                }
              />
              {ticket.contractor?.contact ? (
                <Row label="Contact" value={ticket.contractor.contact} />
              ) : null}
              <Row label="Coût estimé" value={formatAmount(ticket.estimated_cost)} />
              <Row label="Coût réel" value={formatAmount(ticket.actual_cost)} />
              {overrun ? <Row label="Écart au devis" value={overrun} /> : null}
              <Row
                label="Refacturé au propriétaire"
                value={ticket.billed_to_owner ? "Oui" : "Non"}
              />
            </dl>

            {ticket.contractor ? (
              <p className="mt-4 inline-flex items-center gap-2 text-xs text-muted-foreground">
                <Wrench className="h-3.5 w-3.5" />
                <Link
                  href={`/maintenance?contractor_id=${ticket.contractor.id}`}
                  className="hover:underline"
                >
                  Voir ses autres interventions
                </Link>
              </p>
            ) : null}
          </CardContent>
        </Card>
      </div>

      <TicketPhotos ticketId={ticket.id} photos={ticket.photos} canManage={canHandle} />
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b pb-2 last:border-0">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}
