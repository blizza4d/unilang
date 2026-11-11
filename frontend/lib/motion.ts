import { Variants, Transition } from "framer-motion";

export const DURATIONS = {
  instant: 0.09,
  fast: 0.15,
  base: 0.24,
  slow: 0.4,
  ambient: 2.4,
} as const;

export const EASINGS = {
  easeOut: [0.22, 1, 0.36, 1] as [number, number, number, number],
  easeInOut: [0.65, 0, 0.35, 1] as [number, number, number, number],
  springSoft: [0.34, 1.3, 0.64, 1] as [number, number, number, number],
} as const;

export const DEFAULT_TRANSITION: Transition = {
  duration: DURATIONS.base,
  ease: EASINGS.easeOut,
};

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: DURATIONS.fast, ease: EASINGS.easeOut } },
  exit: { opacity: 0, transition: { duration: DURATIONS.fast, ease: EASINGS.easeInOut } },
};

export const fadeUp: Variants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: DURATIONS.base, ease: EASINGS.easeOut } },
  exit: { opacity: 0, y: -4, transition: { duration: DURATIONS.fast, ease: EASINGS.easeInOut } },
};

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.96 },
  animate: { opacity: 1, scale: 1, transition: { duration: DURATIONS.base, ease: EASINGS.easeOut } },
  exit: { opacity: 0, scale: 0.96, transition: { duration: DURATIONS.fast, ease: EASINGS.easeInOut } },
};

export const staggerParent: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.04,
      delayChildren: 0.02,
    },
  },
};

export const staggerChild: Variants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: DURATIONS.fast, ease: EASINGS.easeOut } },
};
