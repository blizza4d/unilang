"use client";

import { useEffect, useRef } from "react";
import { DroidPose, DroidState } from "./types";
import { poseAt } from "./pose";

interface UseWalkCycleOptions {
  state?: DroidState;
  speed?: number;
  paused?: boolean;
  onPoseUpdate: (pose: DroidPose) => void;
}

export function useWalkCycle({
  state = "idle",
  speed = 1,
  paused = false,
  onPoseUpdate,
}: UseWalkCycleOptions): void {
  const phaseRef = useRef<number>(0);
  const timeRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);
  const rafIdRef = useRef<number | null>(null);

  useEffect(() => {
    // If paused, immediately emit static pose and exit
    if (paused) {
      const staticPose = poseAt(phaseRef.current, state, timeRef.current);
      onPoseUpdate(staticPose);
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current);
        rafIdRef.current = null;
      }
      return;
    }

    const cycleMs = 1000 / Math.max(0.1, speed);

    const tick = (now: number) => {
      if (!lastTimeRef.current) {
        lastTimeRef.current = now;
      }

      // Clamp delta to prevent jumps after tab throttling
      const deltaMs = Math.min(now - lastTimeRef.current, 50);
      lastTimeRef.current = now;

      const deltaSeconds = deltaMs / 1000;
      timeRef.current += deltaSeconds;

      if (state === "walk") {
        phaseRef.current = (phaseRef.current + deltaMs / cycleMs) % 1;
      }

      const pose = poseAt(phaseRef.current, state, timeRef.current);
      onPoseUpdate(pose);

      rafIdRef.current = requestAnimationFrame(tick);
    };

    lastTimeRef.current = performance.now();
    rafIdRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafIdRef.current) {
        cancelAnimationFrame(rafIdRef.current);
        rafIdRef.current = null;
      }
    };
  }, [state, speed, paused, onPoseUpdate]);
}
