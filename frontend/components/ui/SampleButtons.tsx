"use client";

import React, { useState } from "react";
import { FileText, AlertCircle, Globe, Loader2 } from "lucide-react";

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
  icon: React.ReactNode;
  badge: string;
  badgeColor: string;
}

export function SampleButtons({ onSelectSample, disabled = false }: SampleButtonsProps): React.JSX.Element {
  const [loadingSample, setLoadingSample] = useState<string | null>(null);

  const presets: SamplePreset[] = [
    {
      id: "en_clean",
      name: "Standard Invoice",
      subtitle: "Clean English (USD) • 100% Match",
      path: "/samples/sample_en_clean.pdf",
      filename: "sample_en_clean.pdf",
      icon: <FileText className="w-3.5 h-3.5 text-cyan-400" />,
      badge: "Clean",
      badgeColor: "bg-cyan-500/10 text-cyan-300 border-cyan-500/20",
    },
    {
      id: "de_math_error",
      name: "Math Discrepancy",
      subtitle: "Arithmetic Mismatch • Discrepancy Caught",
      path: "/samples/sample_de_math_error.pdf",
      filename: "sample_de_math_error.pdf",
      icon: <AlertCircle className="w-3.5 h-3.5 text-amber-400" />,
      badge: "Math Warning",
      badgeColor: "bg-amber-500/10 text-amber-300 border-amber-500/20",
    },
    {
      id: "hi_gst",
      name: "Hindi GST Invoice",
      subtitle: "Dual GST (CGST/SGST) • Multilingual",
      path: "/samples/sample_hi_gst.pdf",
      filename: "sample_hi_gst.pdf",
      icon: <Globe className="w-3.5 h-3.5 text-emerald-400" />,
      badge: "Multilingual",
      badgeColor: "bg-emerald-500/10 text-emerald-300 border-emerald-500/20",
    },
  ];

  const handleLoadPreset = async (preset: SamplePreset) => {
    if (disabled || loadingSample) return;
    setLoadingSample(preset.id);
    try {
      const response = await fetch(preset.path);
      if (!response.ok) {
        throw new Error(`Failed to load ${preset.filename}`);
      }
      const blob = await response.blob();
      const file = new File([blob], preset.filename, { type: "application/pdf" });
      onSelectSample(file);
    } catch (err) {
      console.error("[SampleButtons] Failed to fetch sample:", err);
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div className="w-full max-w-xl mt-4 flex flex-col items-center gap-2 select-none" data-testid="sample-buttons-container">
      <div className="flex items-center gap-2 text-xs text-zinc-400">
        <span className="h-px w-8 bg-zinc-800" />
        <span>or test immediately with a bundled sample</span>
        <span className="h-px w-8 bg-zinc-800" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 w-full">
        {presets.map((preset) => {
          const isLoading = loadingSample === preset.id;
          return (
            <button
              key={preset.id}
              type="button"
              disabled={disabled || Boolean(loadingSample)}
              onClick={() => handleLoadPreset(preset)}
              className="flex flex-col items-start p-2.5 rounded-xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/20 transition-all text-left group disabled:opacity-50 disabled:pointer-events-none"
              title={`Load ${preset.name}`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <div className="flex items-center gap-1.5">
                  {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400" /> : preset.icon}
                  <span className="text-xs font-semibold text-zinc-200 group-hover:text-white transition-colors">
                    {preset.name}
                  </span>
                </div>
                <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${preset.badgeColor}`}>
                  {preset.badge}
                </span>
              </div>
              <span className="text-[10px] text-zinc-400 line-clamp-1">
                {preset.subtitle}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
