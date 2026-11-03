"use client";

import React, { useRef, useState } from "react";
import {
  FileText,
  Play,
  RefreshCw,
  Trash2,
} from "lucide-react";
import { FileDropzone } from "@/components/logic/FileDropzone";
import { ViewerToolbar } from "@/components/ui/ViewerToolbar";
import { PageThumbnails } from "@/components/ui/PageThumbnails";
import { PageCanvas } from "./PageCanvas";
import { formatBytes } from "@/lib/utils";
import { useDocumentStore } from "@/store/useDocumentStore";
import { useViewerState } from "@/hooks/useViewerState";
import { usePdfPages } from "@/hooks/usePdfPages";

export const DocumentViewer: React.FC = () => {
  const file = useDocumentStore((state) => state.file);
  const filePreviewUrl = useDocumentStore((state) => state.filePreviewUrl);
  const isProcessing = useDocumentStore((state) => state.isProcessing);
  const extractedData = useDocumentStore((state) => state.extractedData);
  const boundingBoxes = useDocumentStore((state) => state.boundingBoxes);
  const activeField = useDocumentStore((state) => state.activeField);
  const activePage = useDocumentStore((state) => state.activePage);
  const setActiveField = useDocumentStore((state) => state.setActiveField);
  const setActivePage = useDocumentStore((state) => state.setActivePage);
  const setFile = useDocumentStore((state) => state.setFile);
  const resetStore = useDocumentStore((state) => state.resetStore);
  const processFile = useDocumentStore((state) => state.processFile);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [showThumbnails, setShowThumbnails] = useState<boolean>(false);

  const { pages } = usePdfPages(file);

  const {
    zoom,
    rotation,
    pan,
    setPan,
    currentPage,
    setCurrentPage,
    zoomIn,
    zoomOut,
    resetView,
    rotateClockwise,
    nextPage,
    prevPage,
  } = useViewerState(Math.max(pages.length, 1));

  // Sync external activePage with viewer page
  const handlePageSelect = (page: number) => {
    setCurrentPage(page);
    setActivePage(page);
  };

  const handleFileAccepted = (acceptedFile: File) => {
    setFile(acceptedFile);
    setTimeout(() => {
      useDocumentStore.getState().processFile();
    }, 50);
  };

  if (!file || !filePreviewUrl) {
    return <FileDropzone onFileAccepted={handleFileAccepted} />;
  }

  const isPdfFile = file.type === "application/pdf" || file.name.endsWith(".pdf");
  const currentPageInfo = pages.find((p) => p.pageNumber === currentPage);
  const activeImage = !isPdfFile
    ? filePreviewUrl
    : currentPageInfo?.imageUrl;

  return (
    <div className="relative w-full h-full flex flex-col bg-[#0a0c10] overflow-hidden select-none">
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf,image/png,image/jpeg,image/webp"
        className="hidden"
        onChange={(e) => {
          const newFile = e.target.files?.[0];
          if (newFile) {
            handleFileAccepted(newFile);
          }
        }}
      />

      {/* Header Bar */}
      <header className="z-20 px-4 py-2.5 flex items-center justify-between border-b border-[#232730] bg-[#111318]/90 backdrop-blur-md">
        <div className="flex items-center gap-2.5 min-w-0 pr-2">
          <div className="p-1.5 rounded-lg bg-zinc-800/80 border border-zinc-700/60 text-cyan-400">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h2 className="text-xs font-medium text-zinc-200 truncate max-w-[200px] md:max-w-[280px]">
              {file.name}
            </h2>
            <p className="text-[11px] font-mono text-zinc-400">
              {formatBytes(file.size)} &bull; {isPdfFile ? "PDF" : "Image"}
            </p>
          </div>
        </div>

        {/* Toolbar & Action Controls */}
        <div className="flex items-center gap-2">
          <ViewerToolbar
            zoom={zoom}
            rotation={rotation}
            currentPage={currentPage}
            totalPages={Math.max(pages.length, 1)}
            showThumbnails={showThumbnails}
            onZoomIn={zoomIn}
            onZoomOut={zoomOut}
            onResetView={resetView}
            onRotate={rotateClockwise}
            onPrevPage={prevPage}
            onNextPage={nextPage}
            onToggleThumbnails={() => setShowThumbnails((prev) => !prev)}
          />

          {!extractedData && !isProcessing && (
            <button
              type="button"
              onClick={() => processFile()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-500 text-black hover:bg-cyan-400 shadow transition-all"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              Process
            </button>
          )}

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing}
            className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60 border border-zinc-800 transition-colors disabled:opacity-40"
            title="Replace document"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Replace</span>
          </button>

          <button
            type="button"
            onClick={resetStore}
            disabled={isProcessing}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors disabled:opacity-40"
            title="Clear and reset"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Workspace Body with Optional Thumbnails Drawer */}
      <div className="relative flex-1 w-full h-full flex overflow-hidden">
        <PageThumbnails
          pages={pages}
          currentPage={currentPage}
          onSelectPage={handlePageSelect}
          isOpen={showThumbnails}
        />

        <div className="relative flex-1 w-full h-full flex items-center justify-center overflow-hidden">
          {/* Scanning Beam when processing */}
          {isProcessing && (
            <div className="pointer-events-none absolute inset-x-0 h-32 bg-gradient-to-b from-transparent via-cyan-400/20 to-transparent animate-scan z-30" />
          )}

          <PageCanvas
            imageUrl={activeImage}
            pdfUrl={isPdfFile && !activeImage ? filePreviewUrl : undefined}
            currentPage={currentPage}
            zoom={zoom}
            rotation={rotation}
            pan={pan}
            boxes={boundingBoxes}
            activeField={activeField}
            onPanChange={setPan}
            onSelectField={(f) => setActiveField(f)}
            onHoverField={(f) => setActiveField(f)}
          />
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
