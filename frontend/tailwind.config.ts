import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Serious "instrument" palette — not hype-funnel green-on-black.
        ink: {
          DEFAULT: "#0E1518", // deep slate background
          raised: "#15201F", // raised surfaces / cards
          line: "#23302F", // hairline borders
        },
        parchment: {
          DEFAULT: "#E8E6DD", // primary text
          dim: "#9AA39E", // secondary text
          faint: "#5C6764", // tertiary / captions
        },
        signal: {
          DEFAULT: "#E0A84E", // restrained amber accent
          deep: "#C2872E",
        },
        // Honest data colors — used ONLY for real gains/losses, never decoration.
        gain: "#5FA88A",
        loss: "#C16A5E",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        eyebrow: "0.18em",
      },
      maxWidth: {
        readable: "68rem",
      },
    },
  },
  plugins: [],
};

export default config;
