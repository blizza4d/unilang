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
        app: "var(--bg-app)",
        panel: "var(--bg-panel)",
        elevated: "var(--bg-elevated)",
        subtle: "var(--border-subtle)",
        strong: "var(--border-strong)",
        bright: "var(--text-bright)",
        body: "var(--text-body)",
        muted: "var(--text-muted)",
        faint: "var(--text-faint)",
        accent: {
          amber: "var(--accent-amber)",
          green: "var(--accent-green)",
          red: "var(--accent-red)",
          info: "var(--accent-info)",
          cyan: "var(--accent-cyan)",
        },
        droid: {
          body: "var(--droid-body)",
          shade: "var(--droid-body-shade)",
          panel: "var(--droid-panel)",
          visor: "var(--droid-visor)",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "14px",
        xl: "20px",
        xl2: "14px",
      },
      boxShadow: {
        "glow-green": "var(--glow-green)",
        "glow-amber": "var(--glow-amber)",
        "glow-red": "var(--glow-red)",
        "glow-cyan": "var(--glow-cyan)",
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
