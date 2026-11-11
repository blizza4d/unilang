"use client";

import React, { useState } from "react";
import {
  FileText,
  AlertCircle,
  Globe,
  Receipt,
  ShieldAlert,
  Loader2,
  Sparkles,
} from "lucide-react";

interface SampleButtonsProps {
  onSelectSample: (file: File) => void;
  disabled?: boolean;
}

interface SamplePreset {
  id: string;
  name: string;
  subtitle: string;
  path: string;
  filename: string;
  category: "featured" | "multilingual" | "edge";
  icon: React.ReactNode;
  badge: string;
  badgeColor: string;
}

export function SampleButtons({
  onSelectSample,
  disabled = false,
}: SampleButtonsProps): React.JSX.Element {
  const [loadingSample, setLoadingSample] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"all" | "featured" | "multilingual" | "edge">("all");

  const presets: SamplePreset[] = [
    {
      id: "en_clean",
      name: "Standard SaaS",
      subtitle: "Clean English (USD) • 100% Match",
      path: "/samples/sample_en_clean.pdf",
      filename: "sample_en_clean.pdf",
      category: "featured",
      icon: <FileText className="w-3.5 h-3.5 text-cyan-400" />,
      badge: "Clean Match",
      badgeColor: "bg-cyan-500/10 text-cyan-300 border-cyan-500/20",
    },
    {
      id: "de_math_error",
      name: "Math Discrepancy",
      subtitle: "EUR Comma Decimal • €500 Caught",
      path: "/samples/sample_de_math_error.pdf",
      filename: "sample_de_math_error.pdf",
      category: "featured",
      icon: <AlertCircle className="w-3.5 h-3.5 text-amber-400" />,
      badge: "Math Alert",
      badgeColor: "bg-amber-500/10 text-amber-300 border-amber-500/20",
    },
    {
      id: "hi_gst",
      name: "Hindi GST Invoice",
      subtitle: "Dual GST (CGST/SGST) • Devanagari",
      path: "/samples/sample_hi_gst.pdf",
      filename: "sample_hi_gst.pdf",
      category: "multilingual",
      icon: <Globe className="w-3.5 h-3.5 text-emerald-400" />,
      badge: "Devanagari",
      badgeColor: "bg-emerald-500/10 text-emerald-300 border-emerald-500/20",
    },
    {
      id: "ar_rtl",
      name: "Arabic Riyadh VAT",
      subtitle: "Right-to-Left Arabic • 15% VAT",
      path: "/samples/sample_ar_rtl.pdf",
      filename: "sample_ar_rtl.pdf",
      category: "multilingual",
      icon: <Globe className="w-3.5 h-3.5 text-purple-400" />,
      badge: "Arabic RTL",
      badgeColor: "bg-purple-500/10 text-purple-300 border-purple-500/20",
    },
    {
      id: "receipt_blurry",
      name: "POS Expense Receipt",
      subtitle: "Thermal Receipt • Downtown Bistro",
      path: "/samples/sample_receipt_blurry.pdf",
      filename: "sample_receipt_blurry.pdf",
      category: "edge",
      icon: <Receipt className="w-3.5 h-3.5 text-blue-400" />,
      badge: "Receipt",
      badgeColor: "bg-blue-500/10 text-blue-300 border-blue-500/20",
    },
    {
      id: "injection_test",
      name: "Prompt Injection Test",
      subtitle: "Adversarial Attack Neutralized",
      path: "/samples/sample_injection_test.pdf",
      filename: "sample_injection_test.pdf",
      category: "edge",
      icon: <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />,
      badge: "Security",
      badgeColor: "bg-rose-500/10 text-rose-300 border-rose-500/20",
    },
  ];

  const filteredPresets = presets.filter((p) => {
    if (activeTab === "all") return true;
    return p.category === activeTab;
  });

  const handleLoadPreset = async (preset: SamplePreset) => {
    if (disabled || loadingSample) return;
    setLoadingSample(preset.id);
    try {
      const response = await fetch(preset.path);
      if (!response.ok) {
        throw new Error(`Failed to load ${preset.filename}`);
      }
      const blob = await response.blob();
      const file = new File([blob], preset.filename, {
        type: "application/pdf",
      });
      onSelectSample(file);
    } catch (err) {
      console.error("[SampleButtons] Failed to fetch sample:", err);
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div
      className="w-full max-w-2xl mt-4 flex flex-col items-center gap-2.5 select-none"
      data-testid="sample-buttons-container"
    >
      <div className="flex items-center gap-2 text-xs text-zinc-400">
        <span className="h-px w-8 bg-zinc-800" />
        <span className="flex items-center gap-1.5 font-medium">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          Test immediately with a canonical sample
        </span>
        <span className="h-px w-8 bg-zinc-800" />
      </div>

      {/* Category filter tabs */}
      <div className="flex items-center gap-1 p-0.5 rounded-lg bg-zinc-900/80 border border-zinc-800/80 text-[11px] font-mono">
        <button
          type="button"
          onClick={() => setActiveTab("all")}
          className={`px-2.5 py-0.5 rounded-md transition-colors ${
            activeTab === "all"
              ? "bg-zinc-800 text-zinc-100 font-medium"
              : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          All (6)
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("featured")}
          className={`px-2.5 py-0.5 rounded-md transition-colors ${
            activeTab === "featured"
              ? "bg-zinc-800 text-zinc-100 font-medium"
              : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          Featured
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("multilingual")}
          className={`px-2.5 py-0.5 rounded-md transition-colors ${
            activeTab === "multilingual"
              ? "bg-zinc-800 text-zinc-100 font-medium"
              : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          Multilingual
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("edge")}
          className={`px-2.5 py-0.5 rounded-md transition-colors ${
            activeTab === "edge"
              ? "bg-zinc-800 text-zinc-100 font-medium"
              : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          Security & Edge
        </button>
      </div>

      {/* Sample presets grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 w-full">
        {filteredPresets.map((preset) => {
          const isLoading = loadingSample === preset.id;
          return (
            <button
              key={preset.id}
              type="button"
              disabled={disabled || Boolean(loadingSample)}
              onClick={() => handleLoadPreset(preset)}
              className="flex flex-col items-start p-2.5 rounded-xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.06] hover:border-white/20 transition-all text-left group disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98]"
              title={`Load ${preset.name} (${preset.filename})`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <div className="flex items-center gap-1.5">
                  {isLoading ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  ) : (
                    preset.icon
                  )}
                  <span className="text-xs font-semibold text-zinc-200 group-hover:text-white transition-colors truncate max-w-[110px]">
                    {preset.name}
                  </span>
                </div>
                <span
                  className={`text-[9px] font-mono px-1.5 py-0.2 rounded border shrink-0 ${preset.badgeColor}`}
                >
                  {preset.badge}
                </span>
              </div>
              <span className="text-[10px] text-zinc-400 line-clamp-1 group-hover:text-zinc-300 transition-colors">
                {preset.subtitle}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
