export function triggerFileDownload(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export async function downloadExport(
  data: unknown,
  format: "json" | "csv" | "xlsx" | "pdf",
  filename: string = "invoice"
): Promise<void> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const baseName = filename.replace(/\.[^/.]+$/, "");

  const response = await fetch(
    `${baseUrl}/api/v1/export/direct?format=${format}&filename=${encodeURIComponent(
      baseName
    )}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  const blob = await response.blob();
  const ext = format === "json" ? "json" : format === "csv" ? "csv" : format === "xlsx" ? "xlsx" : "pdf";
  triggerFileDownload(blob, `${baseName}.${ext}`);
}
