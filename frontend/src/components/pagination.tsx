"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";

/** Pagination qui conserve les filtres actifs dans l'URL. */
export function Pagination({
  basePath,
  currentPage,
  lastPage,
}: {
  basePath: string;
  currentPage: number;
  lastPage: number;
}) {
  const searchParams = useSearchParams();

  function hrefForPage(page: number): string {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(page));
    return `${basePath}?${params.toString()}`;
  }

  const isFirst = currentPage <= 1;
  const isLast = currentPage >= lastPage;

  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-muted-foreground">
        Page {currentPage} sur {lastPage}
      </p>
      <div className="flex gap-2">
        {isFirst ? (
          <Button variant="outline" size="sm" disabled>
            Précédent
          </Button>
        ) : (
          <Button variant="outline" size="sm" asChild>
            <Link href={hrefForPage(currentPage - 1)}>Précédent</Link>
          </Button>
        )}
        {isLast ? (
          <Button variant="outline" size="sm" disabled>
            Suivant
          </Button>
        ) : (
          <Button variant="outline" size="sm" asChild>
            <Link href={hrefForPage(currentPage + 1)}>Suivant</Link>
          </Button>
        )}
      </div>
    </div>
  );
}
