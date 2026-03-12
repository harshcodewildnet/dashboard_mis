from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd
from openpyxl import load_workbook
import boto3
import io
import os
import requests
from botocore.exceptions import NoCredentialsError

# Column aliases to resolve inconsistent headings
COLUMN_MAPPING: Dict[str, List[str]] = {
    "date": [
        "date",
        "transaction_date",
        "date_of_transaction",
        "voucher_date",
        "dt",
        "trans_date",
    ],
    "amount": [
        "amount",
        "value",
        "transaction_amount",
        "amt",
        "amount_dr",
        "amount_cr",
        "debit",
        "credit",
        "dr",
        "cr",
    ],
    "ledger": ["ledger", "account", "account_name", "ledger_name", "particulars"],
    "customer": ["customer", "vendor", "party", "customer_name", "party_name"],
    "voucher_type": ["voucher_type", "type", "transaction_type", "voucher"],
    "description": ["description", "memo", "notes", "narration"],
    "reference": ["reference", "ref", "cheque_number", "cheque", "ref_no"],
    "quantity": ["quantity", "qty", "units"],
    "item": ["item", "product", "item_name", "stock_item"],
    "cost_centre": ["cost_centre", "cost_center", "department", "project"],
    "alloc_parent_template": ["alloc_parent_template", "alloc parent template"],
    "cost_centre_parent": ["cost_centre_parent", "cost_center_parent", "parent_cost_centre", "parent_cost_center"],
    "debit": ["debit", "dr", "amount_dr"],
    "credit": ["credit", "cr", "amount_cr"],
    "primary_group": ["primary_group", "primary group", "group", "account_group"],
    "expense_ledger_group": ["expenses_ledger_group", "expense_ledger_group", "expenses ledger group", "expense ledger group"],
}

MONTH_MAP = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


class ExcelLoadError(RuntimeError):
    pass


def _ensure_directory_exists(directory: Path) -> None:
    if not directory.exists():
        raise ExcelLoadError(f"Directory not found or unreachable: {directory}")
    if not directory.is_dir():
        raise ExcelLoadError(f"Configured path is not a directory: {directory}")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to snake_case and trim whitespace."""
    df = df.copy()
    df.columns = [re.sub(r"[\s\-]+", "_", str(col).lower().strip()) for col in df.columns]
    return df


def _find_column(df: pd.DataFrame, key: str) -> Optional[str]:
    """Find a column by alias list, returning the actual column name."""
    aliases = COLUMN_MAPPING.get(key, [])
    normalized = {str(col).lower(): col for col in df.columns}
    for alias in aliases:
        if alias in normalized:
            return normalized[alias]
    return None


def _resolve_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to canonical names; raise if required are missing."""
    df = _normalize_columns(df)
    renamed: Dict[str, str] = {}
    required = ["date", "amount", "ledger"]
    optional = [
        "customer",
        "voucher_type",
        "description",
        "reference",
        "quantity",
        "item",
        "cost_centre",
        "alloc_parent_template",
        "cost_centre_parent",
        "debit",
        "credit",
        "primary_group",
        "expense_ledger_group",
    ]

    for key in required + optional:
        found = _find_column(df, key)
        if found:
            renamed[found] = key

    missing_required = [key for key in required if key not in renamed.values()]
    if missing_required:
        # Try to derive amount from debit/credit if missing amount
        if "amount" in missing_required:
            has_debit = any(alias in df.columns for alias in COLUMN_MAPPING["debit"])
            has_credit = any(alias in df.columns for alias in COLUMN_MAPPING["credit"])
            if has_debit and has_credit:
                missing_required.remove("amount")
            else:
                # Heuristic: pick first column with amount-ish name
                amt_like = next((c for c in df.columns if any(tok in c.lower() for tok in ["amt", "amount", "value", "net"])), None)
                if amt_like:
                    renamed[amt_like] = "amount"
                    missing_required = [m for m in missing_required if m != "amount"]
        if "date" in missing_required:
            # Heuristic: pick first column containing 'date'
            auto_date = next((c for c in df.columns if "date" in c.lower()), None)
            if auto_date:
                renamed[auto_date] = "date"
                missing_required = [m for m in missing_required if m != "date"]
        if missing_required:
            raise ExcelLoadError(
                f"Missing required columns: {', '.join(missing_required)}. Available: {', '.join(df.columns)}"
            )

    # Drop existing columns that would cause a collision with renamed targets
    existing_cols = set(df.columns)
    targets = set(renamed.values())
    sources = set(renamed.keys())
    
    # Columns that exist, are target names, but are NOT being renamed themselves
    # (e.g. 'cost_centre_parent' exists, we are renaming 'alloc_parent_template' to 'cost_centre_parent',
    # so we must drop original 'cost_centre_parent')
    collisions = [col for col in existing_cols if col in targets and col not in sources]
    
    if collisions:
        df = df.drop(columns=collisions)

    df = df.rename(columns=renamed)

    for key in optional:
        if key not in df.columns:
            df[key] = ""

    return df


def _maybe_melt_monthly(df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    """If monthly columns like apr_25 exist, melt them into long format with date/amount."""
    month_pattern = re.compile(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)_\d{2}$")
    month_cols = [c for c in df.columns if month_pattern.match(c.lower())]
    if not month_cols:
        return df, False

    id_vars = [c for c in df.columns if c not in month_cols and c != "total"]

    def _to_date(key: str) -> pd.Timestamp:
        lower = key.lower()
        mon, yy = lower.split("_")
        year = 2000 + int(yy)
        month = MONTH_MAP.get(mon)
        return pd.Timestamp(year=year, month=month, day=1)

    melted = df.melt(id_vars=id_vars, value_vars=month_cols, var_name="month_key", value_name="amount")
    melted["date"] = melted["month_key"].apply(_to_date)
    melted = melted.dropna(subset=["amount"])
    melted = melted.drop(columns=["month_key"], errors="ignore")
    return melted, True


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce date and amount columns; drop rows that cannot convert."""
    df = df.copy()
    # If debit/credit present but amount missing, derive amount = credit - debit
    if "amount" not in df.columns and "debit" in df.columns and "credit" in df.columns:
        df["amount"] = pd.to_numeric(df["credit"], errors="coerce") - pd.to_numeric(df["debit"], errors="coerce")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount", "ledger"])
    df["ledger"] = df["ledger"].astype(str).str.strip()
    df["customer"] = df["customer"].astype(str).str.strip()
    return df


def _pick_sheet(workbook_source, default_sheet: str, fallbacks: Iterable[str]) -> str:
    """workbook_source can be a Path or a file-like object (BytesIO)."""
    wb = load_workbook(workbook_source, read_only=True)
    if default_sheet in wb.sheetnames:
        return default_sheet
    for name in fallbacks:
        if name in wb.sheetnames:
            return name
    # Heuristic: prefer first sheet containing 'trans' or 'report'
    for name in wb.sheetnames:
        lower = name.lower()
        if "trans" in lower or "report" in lower:
            return name
    return wb.sheetnames[0]


def discover_latest_file(directory: Path, pattern: str) -> Path:
    """Find the latest file by modification time matching pattern."""
    _ensure_directory_exists(directory)
    candidates = sorted(directory.glob(pattern))
    if not candidates:
        raise ExcelLoadError(f"No files matching pattern '{pattern}' in {directory}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def discover_latest_s3_file(bucket: str, prefix: str, pattern: str) -> Tuple[str, datetime]:
    """Find the latest file in S3 bucket/prefix matching regex pattern."""
    # First try with credentials (boto3)
    try:
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' not in response:
            raise ExcelLoadError(f"No files found in S3 bucket '{bucket}' with prefix '{prefix}'")
        
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(regex_pattern, re.IGNORECASE)
        
        candidates = []
        for obj in response['Contents']:
            key = obj['Key']
            filename = os.path.basename(key)
            if regex.match(filename):
                candidates.append((key, obj['LastModified']))
        
        if not candidates:
            raise ExcelLoadError(f"No files matching pattern '{pattern}' in s3://{bucket}/{prefix}")
            
        return max(candidates, key=lambda x: x[1])
    except NoCredentialsError:
        # Fall back to public HTTPS listing - use known filename directly
        # Since bucket is public, try to find the file via public URL pattern
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(regex_pattern, re.IGNORECASE)
        # Try common filenames that match the pattern
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        common_names = ["MIS_Report.xlsx", "mis_report.xlsx", "report.xlsx"]
        for name in common_names:
            if regex.match(name):
                key = f"{prefix}{name}" if prefix else name
                url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
                resp = requests.head(url, timeout=10)
                if resp.status_code == 200:
                    last_modified = datetime.now()
                    return key, last_modified
        raise ExcelLoadError(f"No public files matching pattern '{pattern}' in s3://{bucket}/{prefix}")
    except ExcelLoadError:
        raise
    except Exception as e:
        raise ExcelLoadError(f"Error accessing S3: {e}")


def latest_cache_key(excel_config: Dict[str, object]) -> Tuple[str, float]:
    """Return (path, mtime) for the newest file to drive cache invalidation.

    Priority:
      1. local_excel_path (explicit file path in config) — always wins, skips S3
      2. smb_share local directory scan              — if no S3 bucket configured
      3. S3 bucket                                   — only when s3_bucket is set
    """
    # ── Priority 1: explicit local file path (bypasses S3 entirely) ──────────
    local_excel_path = str(excel_config.get("local_excel_path", "")).strip()
    if local_excel_path:
        p = Path(local_excel_path)
        if p.exists():
            return str(p), p.stat().st_mtime
        # File listed but missing — fall through, don't crash yet

    # ── Priority 2: local SMB/filesystem folder scan ──────────────────────────
    smb_share_raw = str(excel_config.get("smb_share", "")).strip()
    if smb_share_raw and not smb_share_raw.startswith("s3://"):
        smb_share = Path(smb_share_raw)
        if smb_share.is_dir():
            pattern = str(excel_config.get("file_pattern", "*.xlsx"))
            latest_path = discover_latest_file(smb_share, pattern)
            return str(latest_path), latest_path.stat().st_mtime

    # ── Priority 3: S3 bucket ─────────────────────────────────────────────────
    s3_bucket = str(excel_config.get("s3_bucket", "")).strip()
    if s3_bucket:
        prefix = str(excel_config.get("s3_prefix", ""))
        pattern = str(excel_config.get("file_pattern", "*.xlsx"))
        key, mtime = discover_latest_s3_file(s3_bucket, prefix, pattern)
        return f"s3://{s3_bucket}/{key}", mtime.timestamp()

    raise ExcelLoadError("No data source configured: set local_excel_path, smb_share, or s3_bucket in config.json")


def load_excel_at_path(excel_path: Union[Path, str], excel_config: Dict[str, object]) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Load and clean Excel from an explicit path (local or S3)."""
    default_sheet = str(excel_config.get("default_sheet", "Transactions"))
    fallbacks = excel_config.get("fallback_sheets", []) or []
    skip_rows = int(excel_config.get("skip_rows", 0))

    path_str = str(excel_path)
    is_s3 = path_str.startswith("s3://")

    if is_s3:
        bucket = path_str.split("/")[2]
        key = "/".join(path_str.split("/")[3:])
        content = None
        last_modified = datetime.now()
        # Try boto3 first (with credentials)
        try:
            s3 = boto3.client('s3')
            response = s3.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read()
            last_modified = response['LastModified']
        except NoCredentialsError:
            # Fall back to public HTTPS download
            region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200:
                    content = resp.content
                else:
                    raise ExcelLoadError(f"Failed to download public S3 file: HTTP {resp.status_code} from {url}")
            except requests.RequestException as e:
                raise ExcelLoadError(f"Failed to download public S3 file: {e}")
        except Exception as e:
            raise ExcelLoadError(f"Error loading S3 file {path_str}: {e}")
        
        try:
            # Discovery sheet using BytesIO
            with io.BytesIO(content) as f:
                sheet_name = _pick_sheet(f, default_sheet, fallbacks)
            
            # Read into pandas
            with io.BytesIO(content) as f:
                df = pd.read_excel(f, sheet_name=sheet_name, engine="openpyxl", skiprows=skip_rows)
        except ExcelLoadError:
            raise
        except Exception as e:
            raise ExcelLoadError(f"Error parsing S3 file {path_str}: {e}")
    else:
        path_obj = Path(path_str)
        if not path_obj.exists():
            raise ExcelLoadError(f"Excel file not found: {excel_path}")
        sheet_name = _pick_sheet(path_obj, default_sheet, fallbacks)
        df = pd.read_excel(path_obj, sheet_name=sheet_name, engine="openpyxl", skiprows=skip_rows)
        last_modified = datetime.fromtimestamp(path_obj.stat().st_mtime)

    df = _normalize_columns(df)
    df, melted = _maybe_melt_monthly(df)
    df = _resolve_columns(df)
    df = _coerce_types(df)
    df = df.sort_values("date")

    metadata = {
        "file_path": path_str,
        "sheet": sheet_name,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "modified_at": last_modified,
    }
    return df, metadata


def load_latest_excel(excel_config: Dict[str, object]) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Backward-compatible helper: discover then load."""
    latest_path = discover_latest_file(Path(str(excel_config.get("smb_share", ""))), str(excel_config.get("file_pattern", "*.xlsx")))
    return load_excel_at_path(latest_path, excel_config)
