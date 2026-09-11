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
import type { PropertyListItem } from "@/types/api";

interface PropertyTableProps {
  properties: PropertyListItem[];
  total: number;
  pageSize: number;
  currentPage: number;
}

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
      <Card>
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
                  <div className="relative h-12 w-16 overflow-hidden rounded-md bg-muted">
                    {property.cover_url ? (
                      <Image
                        src={property.cover_url}
                        alt=""
                        fill
                        sizes="64px"
                        className="object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center">
                        <ImageOff className="h-4 w-4 text-muted-foreground" />
                      </div>
                    )}
                  </div>
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
