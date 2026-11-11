export type DroidState =
  | "idle"
  | "walk"
  | "scan"
  | "think"
  | "celebrate"
  | "alert"
  | "error"
  | "sleep"
  | "boot";

export type DroidFacing = "left" | "right";

export type DroidGlow = "info" | "green" | "amber" | "red" | "cyan";

export interface DroidPose {
  // Torso & Root
  bodyBobY: number;        // Vertical translation (units, negative is up)
  torsoTwist: number;      // Degrees
  // Head & Antenna
  headPitch: number;       // Degrees
  headBobY: number;        // Vertical offset lagging torso
  eyeWidth: number;        // SVG unit scale (1.0 default, 0.2 blink/sleep)
  eyeHeight: number;
  antennaAngle: number;    // Degrees
  bulbScale: number;
  // Limbs - Front
  frontThighAngle: number; // Degrees about hip
  frontShinFlex: number;   // Knee bend (degrees)
  frontFootPitch: number;  // Ankle rotation (degrees)
  frontFootLiftY: number;  // Foot vertical lift (units)
  frontArmAngle: number;   // Shoulder rotation (degrees)
  // Limbs - Back
  backThighAngle: number;
  backShinFlex: number;
  backFootPitch: number;
  backFootLiftY: number;
  backArmAngle: number;
  // Ground Shadow
  shadowScaleX: number;    // Multiplier (1.0 baseline)
  shadowOpacity: number;
}

export interface DroidProps {
  state?: DroidState;
  facing?: DroidFacing;
  size?: number;           // Rendered pixel height (default 64)
  speed?: number;          // Cadence multiplier (default 1)
  glow?: DroidGlow;        // Visor & bulb glow color
  paused?: boolean;        // Freeze motion (reduced motion, offscreen, hidden tab)
  className?: string;
}
