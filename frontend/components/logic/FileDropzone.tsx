"use client";

import React, { useCallback, useState } from "react";
import { useDropzone, FileRejection } from "react-dropzone";
import { motion, useReducedMotion } from "framer-motion";
import { FileText, Globe2, UploadCloud, Layers } from "lucide-react";
import { useBatchStore } from "@/store/useBatchStore";

export interface FileDropzoneProps {
  onFileAccepted: (file: File) => void;
  disabled?: boolean;
}

const MULTILINGUAL_BADGES = [
  "हिन्दी",
  "தமிழ்",
  "العربية",
  "中文",
  "日本語",
  "Deutsch",
  "Français",
  "Español",
];

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileAccepted,
  disabled = false,
}) => {
  const [rejectionMessage, setRejectionMessage] = useState<string | null>(null);
  const shouldReduceMotion = useReducedMotion();
  const startBatch = useBatchStore((state) => state.startBatch);

  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: FileRejection[]) => {
      setRejectionMessage(null);
      if (fileRejections.length > 0) {
        const firstError = fileRejections[0]?.errors[0];
        if (firstError?.code === "file-too-large") {
          setRejectionMessage("One or more files exceed the 15 MB limit.");
        } else if (firstError?.code === "file-invalid-type") {
          setRejectionMessage("Unsupported file type. Please use PDF, PNG, JPG, or WEBP.");
        } else if (firstError?.code === "too-many-files") {
          setRejectionMessage("Maximum 20 files can be uploaded per batch.");
        } else {
          setRejectionMessage(firstError?.message ?? "Invalid file upload.");
        }
        return;
      }

      const firstFile = acceptedFiles[0];
      if (acceptedFiles.length === 1 && firstFile) {
        onFileAccepted(firstFile);
      } else if (acceptedFiles.length > 1) {
        startBatch(acceptedFiles);
      }

    },
    [onFileAccepted, startBatch]
  );

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    isFocused,
  } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/webp": [".webp"],
    },
    maxFiles: 20,
    maxSize: 15 * 1024 * 1024,
    multiple: true,
    disabled,
  });

  let borderState = "border-white/10 hover:border-white/20 hover:bg-white/[0.02]";
  if (isDragReject || rejectionMessage) {
    borderState = "border-accent-red bg-accent-red/5";
  } else if (isDragActive) {
    borderState = "border-cyan-400/50 bg-cyan-950/10";
  } else if (isFocused) {
    borderState = "border-cyan-400 ring-2 ring-cyan-400/20";
  }

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-8 select-none">
      <div
        {...getRootProps()}
        tabIndex={0}
        className={`w-full max-w-xl min-h-[420px] rounded-2xl border-2 border-dashed flex flex-col items-center justify-center p-8 text-center cursor-pointer transition-all duration-200 outline-none ${borderState}`}
      >
        <input {...getInputProps()} />

        <motion.div
          animate={{ scale: isDragActive && !shouldReduceMotion ? 1.08 : 1 }}
          transition={{ duration: 0.2 }}
          className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 mb-5 text-muted"
        >
          <UploadCloud className="w-12 h-12 text-cyan-400/80" />
        </motion.div>

        <h2 className="text-lg font-semibold text-bright mb-1 tracking-tight">
          Drop invoice(s) to extract
        </h2>
        <p className="text-xs text-muted max-w-sm mb-6 leading-relaxed">
          Drop a single file or multiple invoices (up to 20). PDF, PNG, JPG or WEBP.
        </p>

        {rejectionMessage ? (
          <div className="text-xs text-rose-400 font-medium py-1 px-3 rounded-full bg-rose-500/10 border border-rose-500/20 mb-4">
            {rejectionMessage}
          </div>
        ) : (
          <div className="flex items-center gap-3 text-xs text-muted/80 mb-6">
            <span className="flex items-center gap-1">
              <FileText className="w-3.5 h-3.5" />
              Single File
            </span>
            <span className="text-zinc-600">&bull;</span>
            <span className="flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              Batch Queue Mode
            </span>
          </div>
        )}

        {/* Multilingual proof chips */}
        <div className="pt-4 border-t border-white/5 w-full flex flex-col items-center gap-2">
          <div className="flex items-center gap-1 text-[11px] uppercase tracking-wider text-muted font-medium">
            <Globe2 className="w-3 h-3 text-cyan-400" />
            <span>Multilingual Understanding Engine</span>
          </div>
          <div className="flex flex-wrap justify-center gap-1.5 max-w-md">
            {MULTILINGUAL_BADGES.map((badge) => (
              <span
                key={badge}
                className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-white/[0.04] text-muted border border-white/5"
              >
                {badge}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileDropzone;
