import { createTheme } from "@mantine/core";

export const theme = createTheme({
  fontFamily: "'Space Grotesk', 'DM Sans', 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif",
  primaryColor: "indigo",
  defaultRadius: "md",
  colors: {
    indigo: ["#eef2ff", "#e0e7ff", "#c7d2fe", "#a5b4fc", "#818cf8", "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81"],
    slate: ["#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8", "#64748b", "#475569", "#334155", "#1e293b", "#0f172a"]
  },
  headings: {
    fontFamily: "'Space Grotesk', 'DM Sans', 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"
  }
});
