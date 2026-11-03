import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        app: "#0A0A0A",
        panel: "#141414",
        subtle: "rgba(255, 255, 255, 0.08)",
        muted: "#888888",
        bright: "#FDFBF7",
        "accent-amber": "#F59E0B",
        "accent-green": "#8EA48C",
        "accent-red": "#D26A5C",
        accent: {
          amber: "#F59E0B",
          green: "#8EA48C",
          red: "#D26A5C",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      borderRadius: {
        xl2: "14px",
      },
      boxShadow: {
        "glow-green": "0 0 24px 0 rgba(142, 164, 140, 0.15)",
        "glow-amber": "0 0 24px 0 rgba(245, 158, 11, 0.15)",
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateY(0%)" },
          "100%": { transform: "translateY(100%)" },
        },
        "amber-pulse": {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "0.8" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        scan: "scan 2.4s linear infinite",
        "amber-pulse": "amber-pulse 1.6s ease-in-out infinite",
        "fade-up": "fade-up 0.3s ease-out",
      },
    },
  },
  plugins: [],
};

export default config;
