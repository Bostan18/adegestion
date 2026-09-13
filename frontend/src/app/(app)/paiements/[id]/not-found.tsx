import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function PaymentNotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <h1 className="text-xl font-semibold">Paiement introuvable</h1>
      <p className="text-sm text-muted-foreground">
        Ce paiement a peut-être été supprimé ou l&apos;adresse est incorrecte.
      </p>
      <Button asChild>
        <Link href="/paiements">Retour aux paiements</Link>
      </Button>
    </div>
  );
}
