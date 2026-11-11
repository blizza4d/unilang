"use client";

import { useEffect, useRef, useState } from "react";
import { DroidFacing, DroidState } from "./types";

interface UseWalkTargetOptions {
  currentX: number;
  targetX: number;
  renderHeight?: number;
  onArrival?: () => void;
  paused?: boolean;
}

export interface WalkTargetResult {
  x: number;
  facing: DroidFacing;
  isMoving: boolean;
  cadence: number;
}

export function useWalkTarget({
  currentX,
  targetX,
  renderHeight = 64,
  onArrival,
  paused = false,
}: UseWalkTargetOptions): WalkTargetResult {
  const [posX, setPosX] = useState<number>(currentX);
  const [facing, setFacing] = useState<DroidFacing>("right");
  const [isMoving, setIsMoving] = useState<boolean>(false);
  const [cadence, setCadence] = useState<number>(1.0);

  const posRef = useRef<number>(currentX);
  posRef.current = posX;

  useEffect(() => {
    const distance = targetX - posRef.current;
    if (Math.abs(distance) < 2) {
      setIsMoving(false);
      return;
    }

    const direction: DroidFacing = distance > 0 ? "right" : "left";
    setFacing(direction);
    setIsMoving(true);

    if (paused) {
      setPosX(targetX);
      setIsMoving(false);
      onArrival?.();
      return;
    }

    // Mathematical stride: 72 SVG units/s at cadence 1.0
    // In CSS px: (72 * (renderHeight / 140)) px/s
    const pxPerSecondAtCadenceOne = 72 * (renderHeight / 140);
    const targetDurationSeconds = Math.max(1.0, Math.min(2.5, Math.abs(distance) / pxPerSecondAtCadenceOne));
    const computedCadence = Math.max(0.7, Math.min(1.4, Math.abs(distance) / (pxPerSecondAtCadenceOne * targetDurationSeconds)));
    setCadence(computedCadence);

    const actualSpeedPxPerSec = pxPerSecondAtCadenceOne * computedCadence;
    let lastTime = performance.now();
    let currentPos = posRef.current;
    let animId: number;

    const step = (now: number) => {
      const deltaSec = Math.min((now - lastTime) / 1000, 0.05);
      lastTime = now;

      const moveStep = actualSpeedPxPerSec * deltaSec;
      const remaining = targetX - currentPos;

      if (Math.abs(remaining) <= moveStep) {
        currentPos = targetX;
        setPosX(targetX);
        setIsMoving(false);
        onArrival?.();
      } else {
        currentPos += (remaining > 0 ? 1 : -1) * moveStep;
        setPosX(currentPos);
        animId = requestAnimationFrame(step);
      }
    };

    animId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animId);
  }, [targetX, renderHeight, paused, onArrival]);

  return {
    x: posX,
    facing,
    isMoving,
    cadence,
  };
}
