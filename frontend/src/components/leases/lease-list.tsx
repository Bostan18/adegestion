import Link from "next/link";

import { Pagination } from "@/components/pagination";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  LEASE_STATUS_LABELS,
  LEASE_STATUS_VARIANTS,
  formatAmount,
  formatDate,
  formatPeriod,
} from "@/lib/format";
import type { Lease } from "@/types/api";

interface LeaseListProps {
  leases: Lease[];
  total: number;
  pageSize: number;
  currentPage: number;
  /** Masque la colonne du bien quand la liste est deja filtree sur un bien. */
  hidePropertyColumn?: boolean;
}

export function LeaseList({
  leases,
  total,
  pageSize,
  currentPage,
  hidePropertyColumn = false,
}: LeaseListProps) {
  if (leases.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-sm text-muted-foreground">
          Aucun bail ne correspond à cette recherche.
        </p>
      </Card>
    );
  }

  const lastPage = Math.max(Math.ceil(total / pageSize), 1);

  return (
    <div className="space-y-4">
      {/* Telephone et tablette */}
      <ul className="grid gap-3 sm:grid-cols-2 lg:hidden">
        {leases.map((lease) => (
          <li key={lease.id}>
            <LeaseCard lease={lease} hideProperty={hidePropertyColumn} />
          </li>
        ))}
      </ul>

      {/* Ordinateur */}
      <Card className="hidden lg:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Locataire</TableHead>
              {hidePropertyColumn ? null : <TableHead>Bien</TableHead>}
              <TableHead>Période</TableHead>
              <TableHead>Loyer</TableHead>
              <TableHead>Dépôt</TableHead>
              <TableHead>Statut</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leases.map((lease) => (
              <TableRow key={lease.id}>
                <TableCell>
                  <Link href={`/baux/${lease.id}`} className="font-medium hover:underline">
                    {lease.tenant_name}
                  </Link>
                  {lease.tenant_contact ? (
                    <p className="text-xs text-muted-foreground">{lease.tenant_contact}</p>
                  ) : null}
                </TableCell>
                {hidePropertyColumn ? null : (
                  <TableCell>
                    {lease.property ? (
                      <Link
                        href={`/biens/${lease.property.id}`}
                        className="hover:underline"
                      >
                        {lease.property.title}
                      </Link>
                    ) : (
                      "-"
                    )}
                  </TableCell>
                )}
                <TableCell className="whitespace-nowrap text-sm">
                  {formatDate(lease.start_date)}
                  <span className="text-muted-foreground">
                    {lease.end_date ? ` au ${formatDate(lease.end_date)}` : " (sans terme)"}
                  </span>
                </TableCell>
                <TableCell className="font-medium">{formatAmount(lease.rent_amount)}</TableCell>
                <TableCell>{formatAmount(lease.deposit_amount)}</TableCell>
                <TableCell>
                  <Badge variant={LEASE_STATUS_VARIANTS[lease.status]}>
                    {LEASE_STATUS_LABELS[lease.status]}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {lastPage > 1 ? <Pagination basePath="/baux" currentPage={currentPage} lastPage={lastPage} /> : null}
    </div>
  );
}

function LeaseCard({ lease, hideProperty }: { lease: Lease; hideProperty: boolean }) {
  return (
    <Link
      href={`/baux/${lease.id}`}
      className="flex h-full flex-col gap-1 rounded-lg border bg-card p-3 transition-colors hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="line-clamp-2 font-medium leading-snug">{lease.tenant_name}</p>
        <Badge variant={LEASE_STATUS_VARIANTS[lease.status]} className="shrink-0">
          {LEASE_STATUS_LABELS[lease.status]}
        </Badge>
      </div>

      {!hideProperty && lease.property ? (
        <p className="line-clamp-1 text-xs text-muted-foreground">{lease.property.title}</p>
      ) : null}

      <p className="mt-auto text-sm font-semibold">{formatAmount(lease.rent_amount)}</p>
      <p className="text-xs text-muted-foreground">
        {formatPeriod(lease.start_date, lease.end_date)}
      </p>
    </Link>
  );
}
