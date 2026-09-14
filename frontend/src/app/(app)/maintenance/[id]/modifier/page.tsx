import { notFound, redirect } from "next/navigation";

import { TicketForm } from "@/components/maintenance/ticket-form";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import { canHandleTickets } from "@/lib/format";
import type { Contractor, Page, Ticket, User } from "@/types/api";

export const metadata = { title: "Modifier un ticket, AdeImmo" };

export default async function EditTicketPage({ params }: { params: { id: string } }) {
  const user = await serverFetch<User>("/api/v1/me");

  // Déclarer n'est pas traiter : le comptable ne modifie pas un ticket.
  if (!canHandleTickets(user.role)) {
    redirect(`/maintenance/${params.id}`);
  }

  let ticket: Ticket;
  try {
    ticket = await serverFetch<Ticket>(`/api/v1/maintenance/${params.id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  const contractors = await serverFetch<Page<Contractor>>(
    "/api/v1/contractors?is_active=true&limit=100"
  );

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Traiter le ticket</h1>
      <TicketForm ticket={ticket} properties={[]} contractors={contractors.items} canHandle />
    </div>
  );
}
