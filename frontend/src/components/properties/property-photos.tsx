"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { ImagePlus, Loader2, Star, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api/client";
import {
  ACCEPTED_IMAGE_TYPES,
  MAX_UPLOAD_SIZE,
  compressImage,
  formatFileSize,
} from "@/lib/image";
import { createClient } from "@/lib/supabase/client";
import type { Photo, PhotoUploadTicket } from "@/types/api";

interface PropertyPhotosProps {
  propertyId: string;
  photos: Photo[];
  canManage: boolean;
}

export function PropertyPhotos({ propertyId, photos, canManage }: PropertyPhotosProps) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [busyPhotoId, setBusyPhotoId] = useState<string | null>(null);

  async function uploadFile(file: File) {
    if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
      toast.error("Format non supporté. Utilisez JPEG, PNG, WebP ou AVIF.");
      return;
    }

    // 1. Compression dans le navigateur, avant tout transfert.
    const compressed = await compressImage(file);

    if (compressed.blob.size > MAX_UPLOAD_SIZE) {
      toast.error(
        `Image trop lourde même après compression (${formatFileSize(compressed.blob.size)}).`
      );
      return;
    }

    // 2. L'API verifie le role et renvoie un jeton d'upload signe.
    const ticket = await apiFetch<PhotoUploadTicket>(
      `/api/v1/properties/${propertyId}/photos/upload-url`,
      {
        method: "POST",
        body: JSON.stringify({
          filename: compressed.filename,
          content_type: compressed.blob.type,
        }),
      }
    );

    // 3. Envoi direct vers le Storage Supabase, sans passer par l'API.
    const supabase = createClient();
    const { error } = await supabase.storage
      .from(ticket.bucket)
      .uploadToSignedUrl(ticket.storage_path, ticket.token, compressed.blob, {
        contentType: compressed.blob.type,
      });

    if (error) {
      throw new Error("Le transfert de la photo a échoué.");
    }

    // 4. Enregistrement du chemin en base.
    await apiFetch<Photo>(`/api/v1/properties/${propertyId}/photos`, {
      method: "POST",
      body: JSON.stringify({
        storage_path: ticket.storage_path,
        is_cover: photos.length === 0,
      }),
    });

    const saved = compressed.originalSize - compressed.compressedSize;
    if (saved > 0) {
      toast.success(
        `Photo ajoutée, ${formatFileSize(compressed.originalSize)} compressés en ${formatFileSize(
          compressed.compressedSize
        )}.`
      );
    } else {
      toast.success("Photo ajoutée.");
    }
  }

  async function handleFiles(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    if (files.length === 0) return;

    setIsUploading(true);
    try {
      for (const file of files) {
        await uploadFile(file);
      }
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Ajout de la photo impossible.");
    } finally {
      setIsUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  async function setCover(photoId: string) {
    setBusyPhotoId(photoId);
    try {
      await apiFetch(`/api/v1/properties/${propertyId}/photos/${photoId}/cover`, {
        method: "PATCH",
      });
      toast.success("Photo de couverture mise à jour.");
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Action impossible.");
    } finally {
      setBusyPhotoId(null);
    }
  }

  async function deletePhoto(photoId: string) {
    setBusyPhotoId(photoId);
    try {
      await apiFetch(`/api/v1/properties/${propertyId}/photos/${photoId}`, { method: "DELETE" });
      toast.success("Photo supprimée.");
      router.refresh();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Suppression impossible.");
    } finally {
      setBusyPhotoId(null);
    }
  }

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle>Photos</CardTitle>
        {canManage ? (
          <div>
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPTED_IMAGE_TYPES.join(",")}
              multiple
              className="hidden"
              onChange={handleFiles}
            />
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={isUploading}
              onClick={() => inputRef.current?.click()}
            >
              {isUploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <ImagePlus className="h-4 w-4" />
              )}
              Ajouter
            </Button>
          </div>
        ) : null}
      </CardHeader>

      <CardContent>
        {photos.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            Aucune photo pour ce bien.
          </p>
        ) : (
          <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {photos.map((photo) => (
              <li key={photo.id} className="group relative overflow-hidden rounded-lg border">
                <div className="relative aspect-[4/3] bg-muted">
                  {photo.url ? (
                    <Image
                      src={photo.url}
                      alt=""
                      fill
                      sizes="(max-width: 640px) 50vw, 33vw"
                      className="object-cover"
                    />
                  ) : null}
                </div>

                {photo.is_cover ? (
                  <span className="absolute left-2 top-2 rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground">
                    Couverture
                  </span>
                ) : null}

                {canManage ? (
                  <div className="flex justify-end gap-1 border-t bg-background p-1.5">
                    {!photo.is_cover ? (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        disabled={busyPhotoId === photo.id}
                        onClick={() => setCover(photo.id)}
                        aria-label="Définir comme photo de couverture"
                      >
                        <Star className="h-4 w-4" />
                      </Button>
                    ) : null}
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-destructive"
                      disabled={busyPhotoId === photo.id}
                      onClick={() => deletePhoto(photo.id)}
                      aria-label="Supprimer la photo"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
