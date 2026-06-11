import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172026",
        mist: "#f5f7f8",
        harbor: "#0f766e",
        amberline: "#d97706",
        lotus: "#7c3aed",
        signal: "#dc2626"
      },
      borderRadius: {
        sm: "4px",
        md: "6px",
        lg: "8px"
      }
    }
  },
  plugins: []
};

export default config;
