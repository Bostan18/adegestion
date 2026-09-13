import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function LeaseNotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <h1 className="text-xl font-semibold">Bail introuvable</h1>
      <p className="text-sm text-muted-foreground">
        Ce bail a peut-être été supprimé ou l&apos;adresse est incorrecte.
      </p>
      <Button asChild>
        <Link href="/baux">Retour aux baux</Link>
      </Button>
    </div>
  );
}
