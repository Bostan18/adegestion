import Image from "next/image";
import Link from "next/link";
import { ImageOff } from "lucide-react";

import { PropertyPagination } from "@/components/properties/property-pagination";
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
  PROPERTY_STATUS_LABELS,
  PROPERTY_STATUS_VARIANTS,
  PROPERTY_TYPE_LABELS,
  formatAmount,
  formatSurface,
} from "@/lib/format";
import { cn } from "@/lib/utils";
import type { PropertyListItem } from "@/types/api";

interface PropertyTableProps {
  properties: PropertyListItem[];
  total: number;
  pageSize: number;
  currentPage: number;
}

/**
 * Liste des biens, en deux rendus selon la largeur de l'ecran.
 *
 * Le tableau a sept colonnes n'est lisible qu'a partir d'un grand ecran : sur
 * un telephone, le loyer et le statut sortaient du cadre et demandaient un
 * defilement horizontal. En dessous de `lg`, on affiche donc des cartes ou ces
 * deux informations restent visibles d'un coup d'oeil.
 */
export function PropertyTable({ properties, total, pageSize, currentPage }: PropertyTableProps) {
  if (properties.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-sm text-muted-foreground">
          Aucun bien ne correspond à cette recherche.
        </p>
      </Card>
    );
  }

  const lastPage = Math.max(Math.ceil(total / pageSize), 1);

  return (
    <div className="space-y-4">
      {/* Telephone et tablette */}
      <ul className="grid gap-3 sm:grid-cols-2 lg:hidden">
        {properties.map((property) => (
          <li key={property.id}>
            <PropertyCard property={property} />
          </li>
        ))}
      </ul>

      {/* Ordinateur */}
      <Card className="hidden lg:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[84px]">Photo</TableHead>
              <TableHead>Bien</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Ville</TableHead>
              <TableHead>Surface</TableHead>
              <TableHead>Loyer</TableHead>
              <TableHead>Statut</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {properties.map((property) => (
              <TableRow key={property.id}>
                <TableCell>
                  <CoverPhoto property={property} className="h-12 w-16" sizes="64px" />
                </TableCell>
                <TableCell>
                  <Link href={`/biens/${property.id}`} className="font-medium hover:underline">
                    {property.title}
                  </Link>
                  <p className="text-xs text-muted-foreground">{property.address}</p>
                </TableCell>
                <TableCell>{PROPERTY_TYPE_LABELS[property.type]}</TableCell>
                <TableCell>{property.city}</TableCell>
                <TableCell>{formatSurface(property.surface_m2)}</TableCell>
                <TableCell className="font-medium">{formatAmount(property.rent_amount)}</TableCell>
                <TableCell>
                  <Badge variant={PROPERTY_STATUS_VARIANTS[property.status]}>
                    {PROPERTY_STATUS_LABELS[property.status]}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {lastPage > 1 ? (
        <PropertyPagination currentPage={currentPage} lastPage={lastPage} />
      ) : null}
    </div>
  );
}

/** Carte cliquable, rendu des petits et moyens ecrans. */
function PropertyCard({ property }: { property: PropertyListItem }) {
  const details = [
    PROPERTY_TYPE_LABELS[property.type],
    property.city,
    property.surface_m2 ? formatSurface(property.surface_m2) : null,
  ].filter(Boolean);

  return (
    <Link
      href={`/biens/${property.id}`}
      className="flex h-full gap-3 rounded-lg border bg-card p-3 transition-colors hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
    >
      <CoverPhoto
        property={property}
        className="h-[76px] w-[76px] shrink-0 sm:h-20 sm:w-20"
        sizes="80px"
      />

      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <div className="flex items-start justify-between gap-2">
          <p className="line-clamp-2 font-medium leading-snug">{property.title}</p>
          <Badge variant={PROPERTY_STATUS_VARIANTS[property.status]} className="shrink-0">
            {PROPERTY_STATUS_LABELS[property.status]}
          </Badge>
        </div>

        <p className="line-clamp-1 text-xs text-muted-foreground">{property.address}</p>

        <p className="mt-auto text-sm font-semibold">{formatAmount(property.rent_amount)}</p>
        <p className="text-xs text-muted-foreground">{details.join(" · ")}</p>
      </div>
    </Link>
  );
}

function CoverPhoto({
  property,
  className,
  sizes,
}: {
  property: PropertyListItem;
  className?: string;
  sizes: string;
}) {
  return (
    <div className={cn("relative overflow-hidden rounded-md bg-muted", className)}>
      {property.cover_url ? (
        <Image src={property.cover_url} alt="" fill sizes={sizes} className="object-cover" />
      ) : (
        <div className="flex h-full items-center justify-center">
          <ImageOff className="h-4 w-4 text-muted-foreground" />
        </div>
      )}
    </div>
  );
}
