"use client";

import React, { useState, useRef, useEffect } from "react";
import { Download, FileJson, FileSpreadsheet, FileText, Table, Loader2 } from "lucide-react";
import { downloadExport } from "@/lib/download";
import { useDocumentStore } from "@/store/useDocumentStore";

export function ExportMenu(): React.JSX.Element {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [exportingFormat, setExportingFormat] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const extractedData = useDocumentStore((state) => state.extractedData);
  const file = useDocumentStore((state) => state.file);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleExport = async (format: "json" | "csv" | "xlsx" | "pdf") => {
    if (!extractedData) return;
    setExportingFormat(format);
    try {
      await downloadExport(extractedData, format, file?.name || "invoice_export");
      setIsOpen(false);
    } catch (err) {
      console.error("Export error:", err);
      alert(`Export failed: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setExportingFormat(null);
    }
  };

  const options = [
    {
      format: "json" as const,
      label: "Export JSON",
      description: "Complete schema & confidence scores",
      icon: FileJson,
    },
    {
      format: "csv" as const,
      label: "Export CSV (ZIP)",
      description: "Header & line-items CSV with UTF-8 BOM",
      icon: Table,
    },
    {
      format: "xlsx" as const,
      label: "Export Excel (XLSX)",
      description: "Styled workbook with native formulas",
      icon: FileSpreadsheet,
    },
    {
      format: "pdf" as const,
      label: "Audit Report (PDF)",
      description: "Official printable audit certification",
      icon: FileText,
    },
  ];

  return (
    <div className="relative inline-block text-left" ref={menuRef}>
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        disabled={!extractedData || exportingFormat !== null}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-[#1e222d] hover:bg-[#282d3c] border border-[#2e3444] text-zinc-200 transition-colors disabled:opacity-40"
      >
        {exportingFormat ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
        ) : (
          <Download className="w-3.5 h-3.5 text-cyan-400" />
        )}
        <span>Export</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 rounded-xl bg-[#12141c] border border-[#252a38] shadow-2xl z-50 p-1.5 focus:outline-none">
          <div className="text-[10px] font-mono font-medium text-zinc-500 uppercase tracking-wider px-2 py-1">
            Enterprise Export Suite
          </div>
          {options.map((opt) => {
            const Icon = opt.icon;
            const isCurrent = exportingFormat === opt.format;

            return (
              <button
                key={opt.format}
                type="button"
                onClick={() => handleExport(opt.format)}
                disabled={exportingFormat !== null}
                className="w-full flex items-start gap-2.5 px-2.5 py-2 rounded-lg text-left hover:bg-zinc-800/60 transition-colors group"
              >
                <div className="p-1.5 rounded-md bg-zinc-800/80 group-hover:bg-cyan-500/20 text-zinc-400 group-hover:text-cyan-400 transition-colors mt-0.5">
                  {isCurrent ? (
                    <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                  ) : (
                    <Icon className="w-4 h-4" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-medium text-zinc-200 group-hover:text-white">
                    {opt.label}
                  </div>
                  <div className="text-[11px] text-zinc-500 leading-tight">
                    {opt.description}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
