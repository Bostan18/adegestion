import Link from "next/link";
import { Building2 } from "lucide-react";

import { SignOutButton } from "@/components/layout/sign-out-button";
import { Badge } from "@/components/ui/badge";
import { USER_ROLE_LABELS } from "@/lib/format";
import type { User } from "@/types/api";

export function AppHeader({ user }: { user: User }) {
  return (
    <header className="border-b bg-background">
      <div className="container flex h-16 items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <Link href="/biens" className="flex items-center gap-2 font-semibold">
            <Building2 className="h-5 w-5 text-primary" />
            AdeImmo
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link href="/biens" className="text-muted-foreground transition hover:text-foreground">
              Biens
            </Link>
            <Link href="/baux" className="text-muted-foreground transition hover:text-foreground">
              Baux
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium leading-tight">{user.full_name}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
          <Badge variant="secondary">{USER_ROLE_LABELS[user.role]}</Badge>
          <SignOutButton />
        </div>
      </div>
    </header>
  );
}
