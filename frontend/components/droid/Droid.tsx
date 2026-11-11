"use client";

import React, { useCallback, useRef } from "react";
import { DroidFacing, DroidGlow, DroidPose, DroidProps, DroidState } from "./types";
import { useWalkCycle } from "./useWalkCycle";

const GLOW_COLORS: Record<DroidGlow, { primary: string; halo: string }> = {
  info: { primary: "#9AA7B5", halo: "rgba(154, 167, 181, 0.45)" },
  green: { primary: "#8EA48C", halo: "rgba(142, 164, 140, 0.55)" },
  amber: { primary: "#F59E0B", halo: "rgba(245, 158, 11, 0.55)" },
  red: { primary: "#D26A5C", halo: "rgba(210, 106, 92, 0.55)" },
  cyan: { primary: "#22D3EE", halo: "rgba(34, 211, 238, 0.55)" },
};

export const Droid: React.FC<DroidProps> = ({
  state = "idle",
  facing = "right",
  size = 64,
  speed = 1,
  glow = "cyan",
  paused = false,
  className = "",
}) => {
  // DOM element refs for 60fps transform writes without React re-renders
  const shadowRef = useRef<SVGEllipseElement | null>(null);
  const rootBodyRef = useRef<SVGGElement | null>(null);
  const torsoRef = useRef<SVGGElement | null>(null);
  const headRef = useRef<SVGGElement | null>(null);
  const antennaRef = useRef<SVGGElement | null>(null);
  const bulbRef = useRef<SVGCircleElement | null>(null);
  const eyesRef = useRef<SVGGElement | null>(null);

  const frontThighRef = useRef<SVGGElement | null>(null);
  const frontShinRef = useRef<SVGGElement | null>(null);
  const frontFootRef = useRef<SVGGElement | null>(null);
  const frontArmRef = useRef<SVGGElement | null>(null);

  const backThighRef = useRef<SVGGElement | null>(null);
  const backShinRef = useRef<SVGGElement | null>(null);
  const backFootRef = useRef<SVGGElement | null>(null);
  const backArmRef = useRef<SVGGElement | null>(null);

  const onPoseUpdate = useCallback((pose: DroidPose) => {
    // 1. Ground Shadow
    if (shadowRef.current) {
      shadowRef.current.setAttribute("rx", `${28 * pose.shadowScaleX}`);
      shadowRef.current.setAttribute("opacity", `${pose.shadowOpacity}`);
    }

    // 2. Torso Vertical Bob & Twist
    if (rootBodyRef.current) {
      rootBodyRef.current.setAttribute("transform", `translate(0, ${pose.bodyBobY.toFixed(2)})`);
    }
    if (torsoRef.current) {
      torsoRef.current.setAttribute(
        "transform",
        `rotate(${pose.torsoTwist.toFixed(2)}, 60, 80)`
      );
    }

    // 3. Head & Antenna Follow-through
    if (headRef.current) {
      headRef.current.setAttribute(
        "transform",
        `translate(0, ${(pose.headBobY - pose.bodyBobY).toFixed(2)}) rotate(${pose.headPitch.toFixed(2)}, 60, 48)`
      );
    }
    if (antennaRef.current) {
      antennaRef.current.setAttribute(
        "transform",
        `rotate(${pose.antennaAngle.toFixed(2)}, 60, 32)`
      );
    }
    if (bulbRef.current) {
      bulbRef.current.setAttribute("transform", `scale(${pose.bulbScale.toFixed(2)})`);
    }
    if (eyesRef.current) {
      eyesRef.current.setAttribute(
        "transform",
        `scale(${pose.eyeWidth.toFixed(2)}, ${pose.eyeHeight.toFixed(2)})`
      );
    }

    // 4. Front Leg Kinematics (Hip: 68, 96; Knee: 68, 110; Ankle: 68, 124)
    if (frontThighRef.current) {
      frontThighRef.current.setAttribute(
        "transform",
        `rotate(${pose.frontThighAngle.toFixed(2)}, 68, 96)`
      );
    }
    if (frontShinRef.current) {
      frontShinRef.current.setAttribute(
        "transform",
        `rotate(${pose.frontShinFlex.toFixed(2)}, 68, 110)`
      );
    }
    if (frontFootRef.current) {
      frontFootRef.current.setAttribute(
        "transform",
        `translate(0, ${(-pose.frontFootLiftY).toFixed(2)}) rotate(${pose.frontFootPitch.toFixed(2)}, 68, 124)`
      );
    }
    if (frontArmRef.current) {
      frontArmRef.current.setAttribute(
        "transform",
        `rotate(${pose.frontArmAngle.toFixed(2)}, 68, 70)`
      );
    }

    // 5. Back Leg Kinematics (Hip: 52, 96; Knee: 52, 110; Ankle: 52, 124)
    if (backThighRef.current) {
      backThighRef.current.setAttribute(
        "transform",
        `rotate(${pose.backThighAngle.toFixed(2)}, 52, 96)`
      );
    }
    if (backShinRef.current) {
      backShinRef.current.setAttribute(
        "transform",
        `rotate(${pose.backShinFlex.toFixed(2)}, 52, 110)`
      );
    }
    if (backFootRef.current) {
      backFootRef.current.setAttribute(
        "transform",
        `translate(0, ${(-pose.backFootLiftY).toFixed(2)}) rotate(${pose.backFootPitch.toFixed(2)}, 52, 124)`
      );
    }
    if (backArmRef.current) {
      backArmRef.current.setAttribute(
        "transform",
        `rotate(${pose.backArmAngle.toFixed(2)}, 52, 70)`
      );
    }
  }, []);

  useWalkCycle({
    state,
    speed,
    paused,
    onPoseUpdate,
  });

  const glowColors = GLOW_COLORS[glow] || GLOW_COLORS.cyan;
  const isFlipped = facing === "left";
  const renderWidth = Math.round((size * 120) / 140);

  return (
    <svg
      role="img"
      aria-hidden="true"
      viewBox="0 0 120 140"
      width={renderWidth}
      height={size}
      className={`overflow-visible select-none pointer-events-none ${className}`}
      style={{ willChange: paused ? "auto" : "transform" }}
    >
      <defs>
        {/* Soft Radial Bulb Glow */}
        <filter id="droid-glow-filter" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Linear metallic gradient for head & torso */}
        <linearGradient id="body-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="var(--droid-body, #E9E4D8)" />
          <stop offset="100%" stopColor="var(--droid-body-shade, #CFC9BA)" />
        </linearGradient>

        <linearGradient id="shade-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#C4BEAF" />
          <stop offset="100%" stopColor="#ADA799" />
        </linearGradient>
      </defs>

      {/* 1. Ground Shadow (Always centered, never flipped) */}
      <ellipse
        ref={shadowRef}
        cx="60"
        cy="128"
        rx="28"
        ry="5"
        fill="#000000"
        opacity="0.4"
      />

      {/* Facing container */}
      <g transform={isFlipped ? "scale(-1, 1) translate(-120, 0)" : undefined}>
        {/* BACK ARM */}
        <g ref={backArmRef} id="arm-back">
          <rect
            x="48"
            y="68"
            width="8"
            height="22"
            rx="4"
            fill="url(#shade-gradient)"
            stroke="rgba(0,0,0,0.3)"
            strokeWidth="1"
          />
        </g>

        {/* BACK LEG */}
        <g id="leg-back">
          <g ref={backThighRef} id="thigh-back">
            <rect
              x="48"
              y="94"
              width="8"
              height="18"
              rx="4"
              fill="url(#shade-gradient)"
              stroke="rgba(0,0,0,0.3)"
              strokeWidth="1"
            />
            <g ref={backShinRef} id="shin-back">
              <rect
                x="48"
                y="108"
                width="8"
                height="18"
                rx="4"
                fill="url(#shade-gradient)"
                stroke="rgba(0,0,0,0.3)"
                strokeWidth="1"
              />
              <g ref={backFootRef} id="foot-back">
                <path
                  d="M 44 124 L 60 124 A 3 3 0 0 1 63 127 L 63 128 L 41 128 L 41 127 A 3 3 0 0 1 44 124 Z"
                  fill="#787368"
                  stroke="rgba(0,0,0,0.3)"
                  strokeWidth="1"
                />
              </g>
            </g>
          </g>
        </g>

        {/* ROOT BODY (Torso + Head + Antenna) */}
        <g ref={rootBodyRef} id="root-body">
          {/* TORSO */}
          <g ref={torsoRef} id="torso">
            {/* Main torso chassis */}
            <rect
              x="42"
              y="62"
              width="36"
              height="36"
              rx="8"
              fill="url(#body-gradient)"
              stroke="rgba(0,0,0,0.35)"
              strokeWidth="1.2"
            />
            {/* Dark technical chest plate */}
            <rect
              x="48"
              y="68"
              width="24"
              height="20"
              rx="4"
              fill="var(--droid-panel, #2A2A2A)"
            />
            {/* Power Core LED dot */}
            <circle
              cx="60"
              cy="78"
              r="3"
              fill={glowColors.primary}
              filter="url(#droid-glow-filter)"
            />
          </g>

          {/* HEAD & ANTENNA */}
          <g ref={headRef} id="head">
            {/* Antenna */}
            <g ref={antennaRef} id="antenna-stem">
              <rect x="58.5" y="18" width="3" height="15" rx="1.5" fill="#757065" />
              <g transform="translate(60, 16)">
                <circle
                  ref={bulbRef}
                  cx="0"
                  cy="0"
                  r="4.5"
                  fill={glowColors.primary}
                  filter="url(#droid-glow-filter)"
                />
              </g>
            </g>

            {/* Head Dome */}
            <rect
              x="36"
              y="32"
              width="48"
              height="32"
              rx="10"
              fill="url(#body-gradient)"
              stroke="rgba(0,0,0,0.35)"
              strokeWidth="1.2"
            />

            {/* Dark Visor Strip */}
            <rect
              x="40"
              y="42"
              width="40"
              height="14"
              rx="4"
              fill="var(--droid-visor, #0F1412)"
            />

            {/* Eyes / Visor Display */}
            <g ref={eyesRef} id="eyes" transform-origin="60 49">
              <rect
                x="44"
                y="46"
                width="12"
                height="6"
                rx="3"
                fill={glowColors.primary}
                filter="url(#droid-glow-filter)"
              />
              <rect
                x="64"
                y="46"
                width="12"
                height="6"
                rx="3"
                fill={glowColors.primary}
                filter="url(#droid-glow-filter)"
              />
            </g>
          </g>
        </g>

        {/* FRONT LEG */}
        <g id="leg-front">
          <g ref={frontThighRef} id="thigh-front">
            <rect
              x="64"
              y="94"
              width="8"
              height="18"
              rx="4"
              fill="url(#body-gradient)"
              stroke="rgba(0,0,0,0.35)"
              strokeWidth="1"
            />
            <g ref={frontShinRef} id="shin-front">
              <rect
                x="64"
                y="108"
                width="8"
                height="18"
                rx="4"
                fill="url(#body-gradient)"
                stroke="rgba(0,0,0,0.35)"
                strokeWidth="1"
              />
              <g ref={frontFootRef} id="foot-front">
                <path
                  d="M 60 124 L 76 124 A 3 3 0 0 1 79 127 L 79 128 L 57 128 L 57 127 A 3 3 0 0 1 60 124 Z"
                  fill="#545048"
                  stroke="rgba(0,0,0,0.35)"
                  strokeWidth="1"
                />
              </g>
            </g>
          </g>
        </g>

        {/* FRONT ARM */}
        <g ref={frontArmRef} id="arm-front">
          <rect
            x="64"
            y="68"
            width="8"
            height="22"
            rx="4"
            fill="url(#body-gradient)"
            stroke="rgba(0,0,0,0.35)"
            strokeWidth="1.2"
          />
        </g>
      </g>
    </svg>
  );
};

export default Droid;
