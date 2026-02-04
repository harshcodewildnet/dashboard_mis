from __future__ import annotations

import streamlit as st


_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap');

:root {
  --accent: #5bc0de;
  --accent-strong: #1f6feb;
  --card-bg: rgba(255, 255, 255, 0.04);
  --border: rgba(255, 255, 255, 0.08);
}

html, body, [class*="css"]  {
  font-family: 'Space Grotesk', 'DM Sans', system-ui, -apple-system, "Segoe UI", sans-serif;
  letter-spacing: -0.01em;
}

h1, h2, h3, h4 { font-weight: 700; letter-spacing: -0.02em; }

section.main > div { padding-top: 0.5rem; }

/* metric tweaks */
div[data-testid="stMetric"] { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 12px 16px; }
div[data-testid="stMetricValue"] { color: var(--accent); font-size: 1.4rem; font-weight: 700; }

div[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(31,111,235,0.15), rgba(13,17,23,0.6)); border-right: 1px solid var(--border); }

button[kind="secondary"] { border-radius: 999px; border: 1px solid var(--accent); color: var(--accent); }
button[kind="secondary"]:hover { border-color: var(--accent-strong); color: var(--accent-strong); }

/* cards */
.block-container { padding-top: 1.5rem; }
.css-1p05t8e, .css-1r6slb0 { background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; }

/* tables */
[data-testid="stDataFrame"] table { border-radius: 10px; }
</style>
"""


def inject_global_styles() -> None:
    """Injects a lightweight modern style layer across pages."""
    st.markdown(_STYLE, unsafe_allow_html=True)
