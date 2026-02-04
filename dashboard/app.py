from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.config import load_config
from utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from utils.ui import inject_global_styles

st.set_page_config(page_title="Tally Financial Dashboard", layout="wide")

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


@st.cache_resource(show_spinner=False)
def get_config():
    return load_config(CONFIG_PATH)


@st.cache_data(show_spinner=True)
def get_data(cache_key: tuple[str, float]):
    """Cache by (path, mtime) so updates invalidate automatically."""
    config = get_config()
    path_str, _ = cache_key
    return load_excel_at_path(Path(path_str), config["excel_loader"])


def main():
    st.title("Tally Financial Dashboard")
    st.write("Use the sidebar to navigate pages. Data loads from the latest MIS Excel in the configured share.")
    inject_global_styles()

    try:
        config = get_config()
        cache_key = latest_cache_key(config["excel_loader"])
        df, meta = get_data(cache_key)
    except ExcelLoadError as exc:
        st.error(f"Excel load failed: {exc}")
        st.info("Check network access to the UNC path and that a recent MIS Excel exists.")
        st.stop()
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)
        st.stop()

    st.subheader("Data Snapshot")
    st.write(
        f"Loaded **{meta['rows']}** rows from **{meta['sheet']}** in **{Path(meta['file_path']).name}**"
    )
    st.caption(f"Last modified: {meta['modified_at']}")
    if st.button("Refresh data", type="secondary"):
        get_data.clear()
        st.rerun()
    st.dataframe(df.head(20))


if __name__ == "__main__":
    main()
