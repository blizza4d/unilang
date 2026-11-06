import { useState, useEffect } from "react";

export interface PageInfo {
  pageNumber: number;
  imageUrl?: string;
  width?: number;
  height?: number;
}

export function usePdfPages(file: File | null, serverPageImages: string[] = []): {
  pages: PageInfo[];
  isLoading: boolean;
  error: string | null;
} {
  const [pages, setPages] = useState<PageInfo[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!file) {
      setPages([]);
      setIsLoading(false);
      setError(null);
      return;
    }

    // If server already provided base64 or URL page images (from extended response):
    if (serverPageImages.length > 0) {
      setPages(
        serverPageImages.map((url, idx) => ({
          pageNumber: idx + 1,
          imageUrl: url,
        }))
      );
      setIsLoading(false);
      return;
    }

    // If image file, single page with object URL
    if (file.type.startsWith("image/") || /\.(png|jpe?g|webp|gif|bmp)$/i.test(file.name)) {
      const url = URL.createObjectURL(file);
      setPages([{ pageNumber: 1, imageUrl: url }]);
      setIsLoading(false);
      return () => {
        URL.revokeObjectURL(url);
      };
    }

    // If PDF file, track page number without setting raw PDF blob as imageUrl
    if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
      setPages([{ pageNumber: 1 }]);
      setIsLoading(false);
      return;
    }

    setPages([]);
  }, [file, serverPageImages]);

  return { pages, isLoading, error };
}
