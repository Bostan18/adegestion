"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { Download, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiDownload } from "@/lib/api/client";

/** Export CSV des paiements, sur les filtres actifs, pour le rapprochement bancaire. */
export function ExportPaymentsButton() {
  const searchParams = useSearchParams();
  const [isPending, setIsPending] = useState(false);

  async function handleExport() {
    setIsPending(true);
    const params = new URLSearchParams();
    for (const key of ["status", "method", "due_from", "due_to"]) {
      const value = searchParams.get(key);
      if (value) params.set(key, value);
    }

    try {
      await apiDownload(
        `/api/v1/payments/export?${params.toString()}`,
        {},
        "paiements.csv"
      );
      toast.success("Export téléchargé.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Export impossible.");
    } finally {
      setIsPending(false);
    }
  }

  return (
    <Button type="button" variant="outline" onClick={handleExport} disabled={isPending}>
      {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
      Exporter en CSV
    </Button>
  );
}
