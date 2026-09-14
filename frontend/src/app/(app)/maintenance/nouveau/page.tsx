import { TicketForm } from "@/components/maintenance/ticket-form";
import { serverFetch } from "@/lib/api/server";
import { canHandleTickets } from "@/lib/format";
import type { Contractor, Page, PropertyListItem, User } from "@/types/api";

export const metadata = { title: "Nouveau ticket, AdeImmo" };

export default async function NewTicketPage({
  searchParams,
}: {
  searchParams: { bien?: string };
}) {
  // Aucune garde de rôle ici : les trois rôles déclarent un ticket.
  const [user, properties, contractors] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    serverFetch<Page<PropertyListItem>>("/api/v1/properties?limit=100"),
    serverFetch<Page<Contractor>>("/api/v1/contractors?is_active=true&limit=100"),
  ]);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Déclarer un ticket</h1>
        <p className="text-sm text-muted-foreground">
          Décrivez ce que le locataire a signalé. L&apos;intervention se renseigne ensuite.
        </p>
      </div>
      <TicketForm
        properties={properties.items}
        contractors={contractors.items}
        defaultPropertyId={searchParams.bien}
        canHandle={canHandleTickets(user.role)}
      />
    </div>
  );
}
