"use client";

import React from "react";
import { DroidGlow } from "./types";

interface DroidSpriteProps {
  size?: number;
  glow?: DroidGlow;
  className?: string;
}

const GLOW_COLOR_MAP: Record<DroidGlow, string> = {
  info: "#9AA7B5",
  green: "#8EA48C",
  amber: "#F59E0B",
  red: "#D26A5C",
  cyan: "#22D3EE",
};

export const DroidSprite: React.FC<DroidSpriteProps> = ({
  size = 24,
  glow = "cyan",
  className = "",
}) => {
  const eyeColor = GLOW_COLOR_MAP[glow] || GLOW_COLOR_MAP.cyan;

  return (
    <svg
      role="img"
      aria-hidden="true"
      viewBox="0 0 32 32"
      width={size}
      height={size}
      className={`shrink-0 select-none pointer-events-none ${className}`}
    >
      {/* Antenna */}
      <line x1="16" y1="2" x2="16" y2="7" stroke="#757065" strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="16" cy="3" r="2" fill={eyeColor} />

      {/* Head Chassis */}
      <rect x="6" y="8" width="20" height="15" rx="4" fill="#E9E4D8" stroke="rgba(0,0,0,0.3)" strokeWidth="1" />

      {/* Visor */}
      <rect x="8" y="12" width="16" height="7" rx="2" fill="#0F1412" />

      {/* Dual Eyes */}
      <rect x="10" y="14" width="4" height="3" rx="1.5" fill={eyeColor} />
      <rect x="18" y="14" width="4" height="3" rx="1.5" fill={eyeColor} />

      {/* Neck & Shoulders */}
      <rect x="11" y="23" width="10" height="4" rx="1" fill="#2A2A2A" />
      <circle cx="16" cy="25" r="1" fill={eyeColor} />
    </svg>
  );
};

export default DroidSprite;
