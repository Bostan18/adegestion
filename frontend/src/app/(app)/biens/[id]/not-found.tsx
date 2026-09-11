import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function PropertyNotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <h1 className="text-xl font-semibold">Bien introuvable</h1>
      <p className="text-sm text-muted-foreground">
        Ce bien a peut-être été supprimé ou l&apos;adresse est incorrecte.
      </p>
      <Button asChild>
        <Link href="/biens">Retour aux biens</Link>
      </Button>
    </div>
  );
}
