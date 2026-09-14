import Link from "next/link";
import { Building2 } from "lucide-react";

import { SignOutButton } from "@/components/layout/sign-out-button";
import { Badge } from "@/components/ui/badge";
import { USER_ROLE_LABELS, canAccessPayments } from "@/lib/format";
import type { User } from "@/types/api";

/**
 * En-tete de l'application.
 *
 * Sur telephone, la navigation passe sur une seconde ligne : logo, badge de
 * role et deconnexion occupent deja toute la largeur, et garder les liens sur
 * la meme ligne faisait deborder la page horizontalement.
 */
export function AppHeader({ user }: { user: User }) {
  const links = [
    { href: "/biens", label: "Biens" },
    { href: "/baux", label: "Baux" },
    // L'agent n'a aucun acces aux paiements, l'entree ne lui est pas proposee.
    ...(canAccessPayments(user.role) ? [{ href: "/paiements", label: "Paiements" }] : []),
    // Les trois roles ont acces a la maintenance : declarer un ticket est
    // ouvert a tous, seul le traitement est restreint.
    { href: "/maintenance", label: "Maintenance" },
  ];

  return (
    <header className="border-b bg-background">
      <div className="container flex h-16 items-center justify-between gap-3">
        <div className="flex items-center gap-6">
          <Link href="/biens" className="flex items-center gap-2 font-semibold">
            <Building2 className="h-5 w-5 text-primary" />
            AdeImmo
          </Link>
          <NavLinks links={links} className="hidden sm:flex" />
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

      <NavLinks links={links} className="container flex pb-3 sm:hidden" />
    </header>
  );
}

function NavLinks({
  links,
  className,
}: {
  links: { href: string; label: string }[];
  className: string;
}) {
  return (
    <nav className={`items-center gap-5 text-sm ${className}`}>
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className="text-muted-foreground transition hover:text-foreground"
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
