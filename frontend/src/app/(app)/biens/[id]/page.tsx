import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";

import { DeletePropertyButton } from "@/components/properties/delete-property-button";
import { PropertyLeases } from "@/components/properties/property-leases";
import { PropertyMaintenance } from "@/components/properties/property-maintenance";
import { PropertyPhotos } from "@/components/properties/property-photos";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ApiError } from "@/lib/api/errors";
import { serverFetch } from "@/lib/api/server";
import {
  PROPERTY_STATUS_LABELS,
  PROPERTY_STATUS_VARIANTS,
  PROPERTY_TYPE_LABELS,
  canDeleteProperties,
  canManageProperties,
  formatAmount,
  formatDate,
  formatSurface,
} from "@/lib/format";
import type { Lease, Page, Property, Ticket, User } from "@/types/api";

interface PageProps {
  params: { id: string };
}

async function loadProperty(id: string): Promise<Property> {
  try {
    return await serverFetch<Property>(`/api/v1/properties/${id}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
}

export default async function PropertyDetailPage({ params }: PageProps) {
  const [user, property, leases, tickets] = await Promise.all([
    serverFetch<User>("/api/v1/me"),
    loadProperty(params.id),
    serverFetch<Page<Lease>>(`/api/v1/leases?property_id=${params.id}&limit=50`),
    serverFetch<Page<Ticket>>(`/api/v1/maintenance?property_id=${params.id}&limit=50`),
  ]);

  const canManage = canManageProperties(user.role);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <Button variant="ghost" size="sm" asChild className="-ml-3">
            <Link href="/biens">
              <ArrowLeft className="h-4 w-4" />
              Retour aux biens
            </Link>
          </Button>
          <h1 className="text-2xl font-semibold tracking-tight">{property.title}</h1>
          <p className="text-sm text-muted-foreground">
            {property.address}, {property.city}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={PROPERTY_STATUS_VARIANTS[property.status]}>
            {PROPERTY_STATUS_LABELS[property.status]}
          </Badge>
          {canManage ? (
            <Button variant="outline" asChild>
              <Link href={`/biens/${property.id}/modifier`}>Modifier</Link>
            </Button>
          ) : null}
          {canDeleteProperties(user.role) ? (
            <DeletePropertyButton propertyId={property.id} propertyTitle={property.title} />
          ) : null}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Caractéristiques</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3 text-sm">
              <Row label="Type" value={PROPERTY_TYPE_LABELS[property.type]} />
              <Row label="Surface" value={formatSurface(property.surface_m2)} />
              <Row label="Loyer mensuel" value={formatAmount(property.rent_amount)} />
              <Row label="Ville" value={property.city} />
              <Row label="Propriétaire" value={property.owner_name ?? "-"} />
              <Row label="Contact" value={property.owner_contact ?? "-"} />
              <Row label="Ajouté le" value={formatDate(property.created_at)} />
            </dl>
          </CardContent>
        </Card>

        <div className="space-y-6 lg:col-span-2">
          <PropertyPhotos
            propertyId={property.id}
            photos={property.photos}
            canManage={canManage}
          />

          <PropertyLeases
            propertyId={property.id}
            leases={leases.items}
            total={leases.total}
            canManage={canManage}
          />

          <PropertyMaintenance
            propertyId={property.id}
            tickets={tickets.items}
            total={tickets.total}
          />
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b pb-2 last:border-0">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}
