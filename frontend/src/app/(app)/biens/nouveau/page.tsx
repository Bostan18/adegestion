import { redirect } from "next/navigation";

import { PropertyForm } from "@/components/properties/property-form";
import { serverFetch } from "@/lib/api/server";
import { canManageProperties } from "@/lib/format";
import type { User } from "@/types/api";

export const metadata = { title: "Nouveau bien, AdeImmo" };

export default async function NewPropertyPage() {
  const user = await serverFetch<User>("/api/v1/me");

  // Deuxieme garde apres celle de l'API : le comptable n'a rien a faire ici.
  if (!canManageProperties(user.role)) {
    redirect("/biens");
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Nouveau bien</h1>
        <p className="text-sm text-muted-foreground">
          Les photos s&apos;ajoutent depuis la fiche, une fois le bien créé.
        </p>
      </div>
      <PropertyForm />
    </div>
  );
}
