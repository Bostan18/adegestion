"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";

import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/client";

export function SignOutButton() {
  const router = useRouter();

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.replace("/connexion");
    router.refresh();
  }

  return (
    <Button variant="ghost" size="icon" onClick={handleSignOut} aria-label="Se déconnecter">
      <LogOut className="h-4 w-4" />
    </Button>
  );
}
