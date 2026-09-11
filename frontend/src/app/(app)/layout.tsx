import { redirect } from "next/navigation";

import { AppHeader } from "@/components/layout/app-header";
import { serverFetch } from "@/lib/api/server";
import type { User } from "@/types/api";

/**
 * Coquille des pages authentifiees. Le profil vient de l'API, qui fait
 * autorite sur le role : le middleware verifie seulement qu'une session existe.
 */
export default async function AppLayout({ children }: { children: React.ReactNode }) {
  let currentUser: User;

  try {
    currentUser = await serverFetch<User>("/api/v1/me");
  } catch {
    redirect("/connexion");
  }

  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader user={currentUser} />
      <main className="container flex-1 py-8">{children}</main>
    </div>
  );
}
