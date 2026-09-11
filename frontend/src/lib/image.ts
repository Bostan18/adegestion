"use client";

/**
 * Compression des photos avant envoi au Storage Supabase.
 *
 * Les photos prises au telephone pesent souvent plusieurs mega-octets pour un
 * affichage qui n'en demande pas le dixieme. On redimensionne et on reencode
 * dans le navigateur : le Storage reste leger et l'upload passe mieux sur une
 * connexion mobile.
 */

export interface CompressionOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  mimeType?: "image/webp" | "image/jpeg";
}

export interface CompressedImage {
  blob: Blob;
  filename: string;
  originalSize: number;
  compressedSize: number;
}

const DEFAULTS: Required<CompressionOptions> = {
  maxWidth: 1600,
  maxHeight: 1600,
  quality: 0.8,
  mimeType: "image/webp",
};

export const MAX_UPLOAD_SIZE = 5 * 1024 * 1024; // 5 Mo, aligne sur le bucket
export const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/avif"];

function computeSize(
  width: number,
  height: number,
  maxWidth: number,
  maxHeight: number
): { width: number; height: number } {
  const ratio = Math.min(maxWidth / width, maxHeight / height, 1);
  return { width: Math.round(width * ratio), height: Math.round(height * ratio) };
}

function replaceExtension(filename: string, mimeType: string): string {
  const extension = mimeType === "image/webp" ? "webp" : "jpg";
  const base = filename.replace(/\.[^.]+$/, "") || "photo";
  return `${base}.${extension}`;
}

export async function compressImage(
  file: File,
  options: CompressionOptions = {}
): Promise<CompressedImage> {
  const settings = { ...DEFAULTS, ...options };

  const bitmap = await createImageBitmap(file);
  const { width, height } = computeSize(
    bitmap.width,
    bitmap.height,
    settings.maxWidth,
    settings.maxHeight
  );

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;

  const context = canvas.getContext("2d");
  if (!context) {
    bitmap.close();
    throw new Error("La compression de l'image a echoue.");
  }

  context.drawImage(bitmap, 0, 0, width, height);
  bitmap.close();

  const blob = await new Promise<Blob | null>((resolve) =>
    canvas.toBlob(resolve, settings.mimeType, settings.quality)
  );

  // Si le navigateur ne sait pas encoder dans ce format, ou si le resultat est
  // plus lourd que l'original, on garde le fichier d'origine.
  if (!blob || blob.size >= file.size) {
    return {
      blob: file,
      filename: file.name,
      originalSize: file.size,
      compressedSize: file.size,
    };
  }

  return {
    blob,
    filename: replaceExtension(file.name, settings.mimeType),
    originalSize: file.size,
    compressedSize: blob.size,
  };
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} Ko`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
}
