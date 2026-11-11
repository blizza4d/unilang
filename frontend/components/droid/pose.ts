import { DroidPose, DroidState } from "./types";

interface LegKeyframe {
  phase: number; // 0 to 1
  thigh: number; // degrees
  shin: number;  // degrees
  pitch: number; // degrees
  lift: number;  // units
}

const LEG_KEYFRAMES: readonly LegKeyframe[] = [
  { phase: 0.0,   thigh: 24,  shin: 4,  pitch: -12, lift: 0 },
  { phase: 0.125, thigh: 14,  shin: 10, pitch: 0,   lift: 0 },
  { phase: 0.25,  thigh: 0,   shin: 2,  pitch: 0,   lift: 0 },
  { phase: 0.375, thigh: -18, shin: 6,  pitch: 12,  lift: 0 },
  { phase: 0.5,   thigh: -26, shin: 28, pitch: 18,  lift: 2 },
  { phase: 0.625, thigh: -8,  shin: 38, pitch: 6,   lift: 6 },
  { phase: 0.75,  thigh: 10,  shin: 22, pitch: -4,  lift: 4 },
  { phase: 0.875, thigh: 22,  shin: 8,  pitch: -10, lift: 1 },
  { phase: 1.0,   thigh: 24,  shin: 4,  pitch: -12, lift: 0 },
];

const BOB_KEYFRAMES: readonly { phase: number; bob: number }[] = [
  { phase: 0.0,   bob: 1.7 },
  { phase: 0.125, bob: 1.7 },
  { phase: 0.25,  bob: -1.8 },
  { phase: 0.375, bob: -0.2 },
  { phase: 0.5,   bob: 1.7 },
  { phase: 0.625, bob: 1.7 },
  { phase: 0.75,  bob: -1.8 },
  { phase: 0.875, bob: -0.2 },
  { phase: 1.0,   bob: 1.7 },
];

function smoothStep(t: number): number {
  return t * t * (3 - 2 * t);
}

function interpolateLeg(normalizedPhase: number): { thigh: number; shin: number; pitch: number; lift: number } {
  const p = ((normalizedPhase % 1) + 1) % 1;

  for (let i = 0; i < LEG_KEYFRAMES.length - 1; i++) {
    const k1 = LEG_KEYFRAMES[i];
    const k2 = LEG_KEYFRAMES[i + 1];
    if (k1 && k2 && p >= k1.phase && p <= k2.phase) {
      const segSpan = k2.phase - k1.phase;
      const t = segSpan > 0 ? (p - k1.phase) / segSpan : 0;
      const factor = smoothStep(t);
      return {
        thigh: k1.thigh + (k2.thigh - k1.thigh) * factor,
        shin: k1.shin + (k2.shin - k1.shin) * factor,
        pitch: k1.pitch + (k2.pitch - k1.pitch) * factor,
        lift: k1.lift + (k2.lift - k1.lift) * factor,
      };
    }
  }
  return { thigh: 24, shin: 4, pitch: -12, lift: 0 };
}

function interpolateBob(p: number): number {
  const norm = ((p % 1) + 1) % 1;
  for (let i = 0; i < BOB_KEYFRAMES.length - 1; i++) {
    const k1 = BOB_KEYFRAMES[i];
    const k2 = BOB_KEYFRAMES[i + 1];
    if (k1 && k2 && norm >= k1.phase && norm <= k2.phase) {
      const span = k2.phase - k1.phase;
      const t = span > 0 ? (norm - k1.phase) / span : 0;
      return k1.bob + (k2.bob - k1.bob) * smoothStep(t);
    }
  }
  return 1.7;
}

export function poseAt(p: number, state: DroidState = "walk", timeSeconds: number = 0): DroidPose {
  if (state === "walk") {
    const frontLeg = interpolateLeg(p);
    const backLeg = interpolateLeg(p + 0.5);
    const bodyBob = interpolateBob(p);

    // Opposite arm swing
    const frontArmAngle = -frontLeg.thigh * 0.9;
    const backArmAngle = -backLeg.thigh * 0.9;

    const torsoTwist = Math.sin(p * 2 * Math.PI) * 2.5;
    const headPitch = -torsoTwist * 0.6;
    const antennaAngle = Math.sin((p - 0.12) * 2 * Math.PI) * 5.0;

    const shadowScaleX = 1.0 - (bodyBob < 0 ? Math.abs(bodyBob) * 0.04 : 0);
    const shadowOpacity = 0.40 - (bodyBob < 0 ? Math.abs(bodyBob) * 0.05 : 0);

    return {
      bodyBobY: bodyBob,
      torsoTwist,
      headPitch,
      headBobY: bodyBob * 0.85,
      eyeWidth: 1.0,
      eyeHeight: 1.0,
      antennaAngle,
      bulbScale: 1.0,
      frontThighAngle: frontLeg.thigh,
      frontShinFlex: frontLeg.shin,
      frontFootPitch: frontLeg.pitch,
      frontFootLiftY: frontLeg.lift,
      frontArmAngle,
      backThighAngle: backLeg.thigh,
      backShinFlex: backLeg.shin,
      backFootPitch: backLeg.pitch,
      backFootLiftY: backLeg.lift,
      backArmAngle,
      shadowScaleX,
      shadowOpacity,
    };
  }

  // Non-walking States
  const t = timeSeconds;

  if (state === "idle") {
    const breath = Math.sin(t * 1.96) * 1.2;
    // Occasional blink
    const isBlinking = t % 5.0 < 0.15;
    return {
      bodyBobY: breath,
      torsoTwist: 0,
      headPitch: Math.sin(t * 0.6) * 1.5,
      headBobY: breath * 0.7,
      eyeWidth: 1.0,
      eyeHeight: isBlinking ? 0.2 : 1.0,
      antennaAngle: Math.sin(t * 1.2) * 1.8,
      bulbScale: 1.0,
      frontThighAngle: 0,
      frontShinFlex: 0,
      frontFootPitch: 0,
      frontFootLiftY: 0,
      frontArmAngle: 4 + Math.sin(t * 1.96) * 1.5,
      backThighAngle: 0,
      backShinFlex: 0,
      backFootPitch: 0,
      backFootLiftY: 0,
      backArmAngle: 4 - Math.sin(t * 1.96) * 1.5,
      shadowScaleX: 1.0,
      shadowOpacity: 0.40,
    };
  }

  if (state === "scan") {
    const sweep = Math.sin(t * 2.8) * 14;
    return {
      bodyBobY: 0.5,
      torsoTwist: sweep * 0.2,
      headPitch: sweep,
      headBobY: 0,
      eyeWidth: 1.1,
      eyeHeight: 1.1,
      antennaAngle: -sweep * 0.3,
      bulbScale: 1.15,
      frontThighAngle: 0,
      frontShinFlex: 0,
      frontFootPitch: 0,
      frontFootLiftY: 0,
      frontArmAngle: 6,
      backThighAngle: 0,
      backShinFlex: 0,
      backFootPitch: 0,
      backFootLiftY: 0,
      backArmAngle: 6,
      shadowScaleX: 1.0,
      shadowOpacity: 0.42,
    };
  }

  if (state === "think") {
    return {
      bodyBobY: 0,
      torsoTwist: -2,
      headPitch: 7,
      headBobY: 0,
      eyeWidth: 0.9,
      eyeHeight: 0.75,
      antennaAngle: 6 + Math.sin(t * 4.0) * 2.5,
      bulbScale: 1.0 + Math.sin(t * 4.0) * 0.2,
      frontThighAngle: 0,
      frontShinFlex: 0,
      frontFootPitch: 0,
      frontFootLiftY: 0,
      frontArmAngle: -72, // Hand up to temple
      backThighAngle: 0,
      backShinFlex: 0,
      backFootPitch: 0,
      backFootLiftY: 0,
      backArmAngle: 6,
      shadowScaleX: 1.0,
      shadowOpacity: 0.40,
    };
  }

  if (state === "celebrate") {
    const hopProgress = ((t * 2.0) % 1);
    const hopY = -Math.sin(hopProgress * Math.PI) * 9.0;
    return {
      bodyBobY: hopY,
      torsoTwist: 0,
      headPitch: -4,
      headBobY: hopY,
      eyeWidth: 1.15,
      eyeHeight: 1.2,
      antennaAngle: Math.sin(t * 12.0) * 8.0,
      bulbScale: 1.3,
      frontThighAngle: 4,
      frontShinFlex: 8,
      frontFootPitch: -6,
      frontFootLiftY: Math.max(0, -hopY * 0.4),
      frontArmAngle: -65, // Arms raised high
      backThighAngle: -4,
      backShinFlex: 8,
      backFootPitch: -6,
      backFootLiftY: Math.max(0, -hopY * 0.4),
      backArmAngle: -65,
      shadowScaleX: Math.max(0.65, 1.0 + hopY * 0.04),
      shadowOpacity: Math.max(0.18, 0.40 + hopY * 0.03),
    };
  }

  if (state === "alert") {
    const sway = Math.sin(t * 6.0) * 2.5;
    return {
      bodyBobY: 0,
      torsoTwist: sway,
      headPitch: sway * 0.8,
      headBobY: 0,
      eyeWidth: 1.2,
      eyeHeight: 1.25,
      antennaAngle: sway * 2.0,
      bulbScale: 1.25,
      frontThighAngle: 0,
      frontShinFlex: 0,
      frontFootPitch: 0,
      frontFootLiftY: 0,
      frontArmAngle: 12,
      backThighAngle: 0,
      backShinFlex: 0,
      backFootPitch: 0,
      backFootLiftY: 0,
      backArmAngle: 12,
      shadowScaleX: 1.0,
      shadowOpacity: 0.40,
    };
  }

  if (state === "error") {
    return {
      bodyBobY: 2.0,
      torsoTwist: 0,
      headPitch: -8, // Drooped head
      headBobY: 2.5,
      eyeWidth: 0.8,
      eyeHeight: 0.5,
      antennaAngle: -6,
      bulbScale: 0.85,
      frontThighAngle: 0,
      frontShinFlex: 0,
      frontFootPitch: 0,
      frontFootLiftY: 0,
      frontArmAngle: 2,
      backThighAngle: 0,
      backShinFlex: 0,
      backFootPitch: 0,
      backFootLiftY: 0,
      backArmAngle: 2,
      shadowScaleX: 1.05,
      shadowOpacity: 0.42,
    };
  }

  if (state === "sleep") {
    const slowBreath = Math.sin(t * 1.2) * 0.8;
    return {
      bodyBobY: 3.5 + slowBreath,
      torsoTwist: 0,
      headPitch: -6,
      headBobY: 4.0 + slowBreath,
      eyeWidth: 0.8,
      eyeHeight: 0.15, // Eyes closed
      antennaAngle: -4,
      bulbScale: 0.7,
      frontThighAngle: 4,
      frontShinFlex: 8,
      frontFootPitch: 0,
      frontFootLiftY: 0,
      frontArmAngle: 2,
      backThighAngle: 4,
      backShinFlex: 8,
      backFootPitch: 0,
      backFootLiftY: 0,
      backArmAngle: 2,
      shadowScaleX: 1.08,
      shadowOpacity: 0.44,
    };
  }

  // Boot transition default
  return {
    bodyBobY: 1.0,
    torsoTwist: 0,
    headPitch: 0,
    headBobY: 1.0,
    eyeWidth: 1.0,
    eyeHeight: 0.7,
    antennaAngle: 0,
    bulbScale: 1.0,
    frontThighAngle: 0,
    frontShinFlex: 0,
    frontFootPitch: 0,
    frontFootLiftY: 0,
    frontArmAngle: 4,
    backThighAngle: 0,
    backShinFlex: 0,
    backFootPitch: 0,
    backFootLiftY: 0,
    backArmAngle: 4,
    shadowScaleX: 1.0,
    shadowOpacity: 0.40,
  };
}
