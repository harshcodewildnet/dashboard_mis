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
    
    # Auto-detect if running in Docker or locally and adjust data path
    data_path = config["excel_loader"]["smb_share"]
    if not os.path.exists(data_path):
        # Try alternative paths
        alternatives = [
            "/app/data",  # Docker mount
            str(Path(__file__).resolve().parent.parent.parent / "data"),  # Local relative
        ]
        for alt_path in alternatives:
            if os.path.exists(alt_path):
                config["excel_loader"]["smb_share"] = alt_path
                break
    
    return config
