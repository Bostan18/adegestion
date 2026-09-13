"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiDownload } from "@/lib/api/client";

/** Génère et télécharge la quittance PDF d'un paiement encaissé. */
export function ReceiptButton({
  paymentId,
  disabled,
}: {
  paymentId: string;
  disabled?: boolean;
}) {
  const router = useRouter();
  const [isPending, setIsPending] = useState(false);

  async function handleClick() {
    setIsPending(true);
    try {
      await apiDownload(
        `/api/v1/payments/${paymentId}/receipt`,
        { method: "POST" },
        "quittance.pdf"
      );
      toast.success("Quittance générée.");
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Génération impossible.");
    } finally {
      setIsPending(false);
    }
  }

  return (
    <Button type="button" variant="outline" onClick={handleClick} disabled={disabled || isPending}>
      {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
      Quittance PDF
    </Button>
  );
}
