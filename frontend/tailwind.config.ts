import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#c9770c",
        "primary-dark": "8d550b",
        "primary-light": "#c9770c94",
        "bg-light": "#fdfcf9",
        "bg-dark": "#151022",
        "warm-50": "#fffbf6",
        "warm-100": "#fff3e5",
        "warm-200": "#fff0e0",
        "warm-300": "#fdecd9",
        "warm-400": "#f5e3cd",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      borderRadius: {
        DEFAULT: "0.375rem",
        lg: "0.625rem",
        xl: "0.875rem",
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
      boxShadow: {
        "warm-sm": "0 1px 3px rgba(137,90,246,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        "warm-md": "0 4px 16px rgba(137,90,246,0.08), 0 2px 6px rgba(0,0,0,0.04)",
        "warm-lg": "0 12px 40px rgba(137,90,246,0.12), 0 4px 12px rgba(0,0,0,0.06)",
        "warm-xl": "0 24px 64px rgba(137,90,246,0.16), 0 8px 24px rgba(0,0,0,0.08)",
        "glow": "0 0 32px rgba(137,90,246,0.25)",
      },
      animation: {
        "fade-up": "fadeUp 0.5s ease-out forwards",
        "fade-in": "fadeIn 0.4s ease-out forwards",
        "slide-in": "slideIn 0.3s ease-out forwards",
        "pulse-soft": "pulseSoft 2s ease-in-out infinite",
        "shimmer": "shimmer 1.8s infinite",
        "spin-slow": "spin 3s linear infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideIn: {
          "0%": { opacity: "0", transform: "translateX(-12px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.6" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
