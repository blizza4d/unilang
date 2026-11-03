import { useState, useCallback } from "react";

export interface ViewerState {
  zoom: number;
  rotation: number;
  pan: { x: number; y: number };
  currentPage: number;
  totalPages: number;
}

export function useViewerState(initialTotalPages: number = 1) {
  const [zoom, setZoom] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(initialTotalPages);

  const zoomIn = useCallback(() => {
    setZoom((z) => Math.min(Number((z + 0.15).toFixed(2)), 3.0));
  }, []);

  const zoomOut = useCallback(() => {
    setZoom((z) => Math.max(Number((z - 0.15).toFixed(2)), 0.4));
  }, []);

  const resetView = useCallback(() => {
    setZoom(1.0);
    setRotation(0);
    setPan({ x: 0, y: 0 });
  }, []);

  const rotateClockwise = useCallback(() => {
    setRotation((r) => (r + 90) % 360);
  }, []);

  const nextPage = useCallback(() => {
    setCurrentPage((p) => Math.min(p + 1, totalPages));
  }, [totalPages]);

  const prevPage = useCallback(() => {
    setCurrentPage((p) => Math.max(p - 1, 1));
  }, []);

  const goToPage = useCallback(
    (page: number) => {
      if (page >= 1 && page <= totalPages) {
        setCurrentPage(page);
      }
    },
    [totalPages]
  );

  return {
    zoom,
    setZoom,
    rotation,
    pan,
    setPan,
    currentPage,
    setCurrentPage,
    totalPages,
    setTotalPages,
    zoomIn,
    zoomOut,
    resetView,
    rotateClockwise,
    nextPage,
    prevPage,
    goToPage,
  };
}
