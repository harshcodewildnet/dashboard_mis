from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config(config_path: Path | None = None) -> Dict[str, Any]:
    """Load dashboard configuration from JSON.

    Priority order for data source:
    1. local_excel_path in config.json  → always use local file, skip S3
    2. LOCAL_MODE env var == 'true'     → skip S3, use smb_share folder
    3. S3_BUCKET env var               → use S3
    4. smb_share in config.json        → use local folder
    """
    path = config_path or _DEFAULT_CONFIG_PATH
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)

    excel_cfg = config.get("excel_loader", {})

    # ── Priority 1: local_excel_path in JSON → skip S3 completely ────────────
    local_path = excel_cfg.get("local_excel_path", "").strip()
    if local_path:
        excel_cfg.pop("s3_bucket", None)
        excel_cfg.pop("s3_prefix", None)
        # Resolve relative local_excel_path to absolute
        if local_path and not Path(local_path).is_absolute():
            # Join relative to the directory containing config.json
            base_dir = path.parent.parent
            resolved = base_dir / local_path
            # Check if it exists before committing to the absolute path
            if resolved.exists():
                excel_cfg["local_excel_path"] = str(resolved)
        return config

    # ── Priority 2: LOCAL_MODE env var → skip S3 completely ──────────────────
    local_mode = os.getenv("LOCAL_MODE", "").lower() in ("1", "true", "yes")
    if local_mode:
        excel_cfg.pop("s3_bucket", None)
        excel_cfg.pop("s3_prefix", None)
        # Resolve relative smb_share to absolute
        smb = excel_cfg.get("smb_share", "")
        if smb and not Path(smb).is_absolute():
            base_dir = path.parent.parent
            resolved = base_dir / smb
            if resolved.exists():
                excel_cfg["smb_share"] = str(resolved)
        return config

    # ── Priority 3 & 4: Normal mode — inject S3 if env var is non-empty ──────
    s3_bucket = os.getenv("S3_BUCKET", "").strip()
    if s3_bucket:
        excel_cfg["s3_bucket"] = s3_bucket
        excel_cfg["s3_prefix"] = os.getenv("S3_PREFIX", "")
    else:
        excel_cfg.pop("s3_bucket", None)

    # Resolve relative smb_share to absolute
    smb = excel_cfg.get("smb_share", "")
    if smb and not Path(smb).is_absolute():
        base_dir = path.parent.parent
        resolved = base_dir / smb
        if resolved.exists():
            excel_cfg["smb_share"] = str(resolved)

    return config
