import { Suspense } from "react";

import { LoginForm } from "@/components/layout/login-form";

export const metadata = { title: "Connexion, AdeImmo" };

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-muted/40 px-4 py-12">
      <div className="w-full max-w-sm space-y-6">
        <div className="space-y-1 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">AdeImmo</h1>
          <p className="text-sm text-muted-foreground">Gestion immobilière de l&apos;agence</p>
        </div>
        <Suspense>
          <LoginForm />
        </Suspense>
      </div>
    </main>
  );
}
