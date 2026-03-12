import { createTheme } from "@mantine/core";

export const theme = createTheme({
  fontFamily: "'Inter', 'Space Grotesk', 'DM Sans', system-ui, -apple-system, sans-serif",
  primaryColor: "indigo",
  primaryShade: 6,
  defaultRadius: "lg",
  white: "#ffffff",
  black: "#0f172a",
  colors: {
    indigo: [
      "#eef2ff",
      "#e0e7ff",
      "#c7d2fe",
      "#a5b4fc",
      "#818cf8",
      "#6366f1",
      "#4f46e5", // Shade 6
      "#4338ca",
      "#3730a3",
      "#1e1b4b"
    ],
    slate: [
      "#f8fafc",
      "#f1f5f9",
      "#e2e8f0",
      "#cbd5e1",
      "#94a3b8",
      "#64748b",
      "#475569",
      "#334155",
      "#1e293b",
      "#0f172a"
    ]
  },
  shadows: {
    xs: "0 1px 2px rgba(0, 0, 0, 0.05)",
    sm: "0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)",
    md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
  },
  headings: {
    fontFamily: "'Inter', 'Space Grotesk', system-ui, sans-serif",
    fontWeight: "700"
  },
  components: {
    Paper: {
      defaultProps: {
        shadow: "sm",
        withBorder: true
      }
    },
    Button: {
      styles: {
        root: {
          transition: "transform 150ms ease, box-shadow 150ms ease"
        }
      }
    }
  }
});
