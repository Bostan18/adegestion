import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function TicketNotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <h1 className="text-xl font-semibold">Ticket introuvable</h1>
      <p className="text-sm text-muted-foreground">
        Ce ticket a peut-être été supprimé ou l&apos;adresse est incorrecte.
      </p>
      <Button asChild>
        <Link href="/maintenance">Retour à la maintenance</Link>
      </Button>
    </div>
  );
}
