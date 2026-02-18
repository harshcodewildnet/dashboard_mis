from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config(config_path: Path | None = None) -> Dict[str, Any]:
    """Load dashboard configuration from JSON."""
    path = config_path or _DEFAULT_CONFIG_PATH
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    
    # Inject S3 environment variables if present
    s3_bucket = os.getenv("S3_BUCKET")
    if s3_bucket:
        config["excel_loader"]["s3_bucket"] = s3_bucket
        config["excel_loader"]["s3_prefix"] = os.getenv("S3_PREFIX", "")
    
    return config
