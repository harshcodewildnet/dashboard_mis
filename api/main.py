from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dashboard.utils.config import load_config
from dashboard.utils.file_loader import ExcelLoadError, latest_cache_key, load_excel_at_path
from dashboard.utils.metrics import (
    calculate_kpis,
    get_current_month_daily_profit,
    get_current_month_profit,
    get_expense_detail_with_variance,
    get_income_detail_with_variance,
    get_monthly_expenses_table,
    group_summary,
    ledger_statement,
    monthly_totals,
    sales_by_item,
    sales_by_month,
    top_customers,
    top_ledgers,
)

# Auth Imports
from api.auth import Token, UserData, create_access_token, get_current_user, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from api.db import SessionLocal, User, Department, init_db
from api.auth import pwd_context

# Create tables and seed if empty
init_db()
db = SessionLocal()
try:
    if not db.query(User).filter(User.role == "ADMIN").first():
        admin = User(
            email="admin@company.com",
            password_hash=pwd_context.hash("admin123"),
            role="ADMIN"
        )
        db.add(admin)
        db.commit()
        print("Default admin created: admin@company.com / admin123")
except Exception as e:
    print(f"Seeding error: {e}")
finally:
    db.close()
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy import func


CONFIG_PATH = Path(__file__).resolve().parents[1] / "dashboard" / "config.json"


@dataclass
class DataBundle:
    df: pd.DataFrame
    meta: Dict[str, Any]
    mtime: float


class DataCache:
    """Keeps a cached dataframe reloaded when the Excel mtime changes."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._bundle: Optional[DataBundle] = None
        self._lock = Lock()

    def get_bundle(self) -> DataBundle:
        path_str, mtime = latest_cache_key(self.config["excel_loader"])
        excel_path = Path(path_str)
        with self._lock:
            if self._bundle and self._bundle.mtime == mtime:
                return self._bundle
            df, meta = load_excel_at_path(excel_path, self.config["excel_loader"])
            self._bundle = DataBundle(df=df, meta=meta, mtime=mtime)
            return self._bundle


def _filter_by_date(df: pd.DataFrame, start: Optional[date], end: Optional[date]) -> pd.DataFrame:
    if start is None and end is None:
        return df
    start_ts = pd.Timestamp(start) if start else df["date"].min()
    end_ts = pd.Timestamp(end) if end else df["date"].max()
    return df.loc[(df["date"] >= start_ts) & (df["date"] <= end_ts)]


def _ts_to_iso(ts: pd.Timestamp | datetime | date) -> str:
    if isinstance(ts, pd.Timestamp):
        ts = ts.to_pydatetime()
    if isinstance(ts, datetime):
        return ts.isoformat()
    return datetime.combine(ts, datetime.min.time()).isoformat()


def _df_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        if "date" in row and isinstance(row["date"], (pd.Timestamp, datetime, date)):
            row["date"] = _ts_to_iso(row["date"])
        records.append(row)
    return records


# --- RBAC Helper ---
def _apply_rbac(df: pd.DataFrame, user: UserData) -> pd.DataFrame:
    """Filter DataFrame based on user role and department."""
    if user.role == "ADMIN":
        return df
    
    if user.cost_centre_parent:
        # Filter by Cost Centre Parent
        if "cost_centre_parent" in df.columns:
             return df[df["cost_centre_parent"] == user.cost_centre_parent]
    
    # Return empty if no match
    return df.iloc[0:0]


class MetaPayload(BaseModel):
    file_name: str
    sheet: str
    rows: int
    modified_at: str
    columns: List[str]


class KpiPayload(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float
    cash_balance: float


class SeriesPoint(BaseModel):
    label: str
    value: float


class SummaryResponse(BaseModel):
    meta: MetaPayload
    kpis: KpiPayload
    monthly: List[SeriesPoint]
    by_group: List[SeriesPoint]
    top_ledgers: List[SeriesPoint]


class SalesResponse(BaseModel):
    meta: MetaPayload
    totals: Dict[str, float]
    monthly: List[SeriesPoint]
    top_customers: List[SeriesPoint]
    top_items: List[SeriesPoint]


class LedgerRow(BaseModel):
    date: str
    amount: float
    running_balance: float
    description: Optional[str] = None
    reference: Optional[str] = None
    voucher_type: Optional[str] = None


class LedgerResponse(BaseModel):
    meta: MetaPayload
    ledger: str
    opening: float
    period_total: float
    closing: float
    running_balance: List[LedgerRow]


class RowsResponse(BaseModel):
    meta: MetaPayload
    rows: List[Dict[str, Any]]
    count: int


class VarianceItem(BaseModel):
    ledger: str
    current_amount: float
    previous_amount: float
    variance_pct: float


class IncomeResponse(BaseModel):
    meta: MetaPayload
    total_income: float
    current_month: str
    items: List[VarianceItem]


class ExpenseResponse(BaseModel):
    meta: MetaPayload
    total_expense: float
    current_month: str
    items: List[VarianceItem]


class MonthlyExpenseItem(BaseModel):
    month: str
    total_expense: float


class HomeDataResponse(BaseModel):
    meta: MetaPayload
    current_month: str
    income: float
    expense: float
    profit: float
    cash_balance: float
    total_revenue: float
    total_expenses: float
    net_profit: float
    monthly_expenses: List[MonthlyExpenseItem]
    daily_profit: List[Dict[str, Any]]


def _meta_from_dict(meta: Dict[str, Any]) -> MetaPayload:
    return MetaPayload(
        file_name=Path(meta["file_path"]).name,
        sheet=str(meta["sheet"]),
        rows=int(meta["rows"]),
        modified_at=_ts_to_iso(meta["modified_at"]),
        columns=[str(c) for c in meta.get("columns", [])],
    )


def _series_from_df(df: pd.DataFrame, label_col: str, value_col: str) -> List[SeriesPoint]:
    return [SeriesPoint(label=str(row[label_col]), value=float(row[value_col])) for _, row in df.iterrows()]


def _monthly_series(df: pd.DataFrame, label_col: str = "month", value_col: str = "amount") -> List[SeriesPoint]:
    out: List[SeriesPoint] = []
    for _, row in df.iterrows():
        label = row[label_col]
        if isinstance(label, (pd.Timestamp, datetime, date)):
            label = label.strftime("%Y-%m-%d")
        out.append(SeriesPoint(label=str(label), value=float(row[value_col])))
    return out


config = load_config(CONFIG_PATH)
data_cache = DataCache(config)

app = FastAPI(title="MIS Dashboard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth Endpoints ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        username = form_data.username.strip().lower()
        password = form_data.password.strip()
        
        print(f"Login attempt for: {username}")
        user = db.query(User).filter(func.lower(User.email) == username).first()
        
        if not user:
            print(f"User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        is_valid = verify_password(password, user.password_hash)
        print(f"Password valid for {username}: {is_valid}")
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        db.close()


@app.get("/api/me", response_model=UserData)
async def read_users_me(current_user: UserData = Depends(get_current_user)):
    return current_user


@app.get("/api/meta", response_model=MetaPayload)
def meta(current_user: UserData = Depends(get_current_user)):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return _meta_from_dict(bundle.meta)


@app.get("/api/ledgers", response_model=List[str])
def ledgers(current_user: UserData = Depends(get_current_user)):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    # Apply RBAC
    df = _apply_rbac(bundle.df, current_user)

    if "ledger" not in df.columns:
        return []
    ledgers = sorted(df["ledger"].dropna().unique())
    return [str(l) for l in ledgers]


@app.get("/api/summary", response_model=SummaryResponse)
def summary(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC First
    rbac_df = _apply_rbac(bundle.df, current_user)
    
    df = _filter_by_date(rbac_df, start, end)
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])
    cash_ledgers = config.get("cash_ledgers", [])

    kpi = calculate_kpis(df, revenue_keywords, expense_keywords, cash_ledgers)
    monthly = monthly_totals(df).rename(columns={"amount": "amount"})
    by_group = group_summary(df, "expense_ledger_group", top_n=10)
    top = top_ledgers(df, limit=10)

    return SummaryResponse(
        meta=_meta_from_dict(bundle.meta),
        kpis=KpiPayload(**asdict(kpi)),
        monthly=_monthly_series(monthly, label_col="month", value_col="amount"),
        by_group=_series_from_df(by_group, "expense_ledger_group", "total"),
        top_ledgers=_series_from_df(top, "ledger", "total"),
    )


@app.get("/api/sales", response_model=SalesResponse)
def sales(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    top: int = Query(10, ge=3, le=50),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC
    rbac_df = _apply_rbac(bundle.df, current_user)
    df = _filter_by_date(rbac_df, start, end)
    revenue_keywords = config.get("revenue_keywords", [])

    sales_df = df.copy()
    monthly_df = sales_by_month(sales_df, revenue_keywords)
    top_cust_df = top_customers(sales_df, revenue_keywords, limit=top)
    top_items_df = sales_by_item(sales_df, revenue_keywords, limit=top)

    total_sales = float(sales_df["amount"].sum()) if not sales_df.empty else 0.0
    unique_customers = int(sales_df["customer"].nunique()) if "customer" in sales_df.columns else 0
    avg_ticket = total_sales / unique_customers if unique_customers else 0.0

    return SalesResponse(
        meta=_meta_from_dict(bundle.meta),
        totals={
            "total_sales": total_sales,
            "unique_customers": unique_customers,
            "avg_ticket": avg_ticket,
        },
        monthly=_monthly_series(monthly_df, label_col="month", value_col="total"),
        top_customers=_series_from_df(top_cust_df, "customer", "total"),
        top_items=_series_from_df(top_items_df, "item", "total"),
    )


@app.get("/api/ledger", response_model=LedgerResponse)
def ledger(
    name: str = Query(..., description="Ledger name"),
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC
    df = _apply_rbac(bundle.df, current_user)
    
    if "ledger" not in df.columns:
        raise HTTPException(status_code=400, detail="Ledger column missing in data")

    if name not in df["ledger"].unique():
        raise HTTPException(status_code=404, detail=f"Ledger not found: {name}")

    start_ts = pd.Timestamp(start) if start else df["date"].min()
    end_ts = pd.Timestamp(end) if end else df["date"].max()

    opening, period_total, closing, statement = ledger_statement(df, name, start_ts, end_ts)
    rows = []
    if not statement.empty:
        for rec in statement.to_dict(orient="records"):
            rows.append(
                LedgerRow(
                    date=_ts_to_iso(rec.get("date")),
                    amount=float(rec.get("amount", 0)),
                    running_balance=float(rec.get("running_balance", 0)),
                    description=rec.get("description") or None,
                    reference=rec.get("reference") or None,
                    voucher_type=rec.get("voucher_type") or None,
                )
            )

    return LedgerResponse(
        meta=_meta_from_dict(bundle.meta),
        ledger=name,
        opening=opening,
        period_total=period_total,
        closing=closing,
        running_balance=rows,
    )


@app.get("/api/rows", response_model=RowsResponse)
def rows(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC
    rbac_df = _apply_rbac(bundle.df, current_user)
    df = _filter_by_date(rbac_df, start, end)
    trimmed = df.head(limit)
    records = _df_to_records(trimmed)

    return RowsResponse(meta=_meta_from_dict(bundle.meta), rows=records, count=len(records))


@app.get("/api/home", response_model=HomeDataResponse)
def home(current_user: UserData = Depends(get_current_user)):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC
    df = _apply_rbac(bundle.df, current_user)
    
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])
    cash_ledgers = config.get("cash_ledgers", [])

    # Current month profit
    income, expense, profit = get_current_month_profit(df, revenue_keywords, expense_keywords)
    current_month = df["date"].max().strftime("%B %Y")

    # KPIs
    kpis = calculate_kpis(df, revenue_keywords, expense_keywords, cash_ledgers)

    # Monthly expenses
    monthly_expenses_df = get_monthly_expenses_table(df, expense_keywords, n_months=3)
    monthly_expenses = [
        MonthlyExpenseItem(
            month=row["month"].strftime("%B %Y"),
            total_expense=float(row["total_expense"])
        )
        for _, row in monthly_expenses_df.iterrows()
    ]

    # Daily profit
    daily_profit_df = get_current_month_daily_profit(df, revenue_keywords, expense_keywords)
    daily_profit = _df_to_records(daily_profit_df)

    return HomeDataResponse(
        meta=_meta_from_dict(bundle.meta),
        current_month=current_month,
        income=income,
        expense=expense,
        profit=profit,
        cash_balance=kpis.cash_balance,
        total_revenue=kpis.total_revenue,
        total_expenses=kpis.total_expenses,
        net_profit=kpis.net_profit,
        monthly_expenses=monthly_expenses,
        daily_profit=daily_profit,
    )


@app.get("/api/income", response_model=IncomeResponse)
def income(current_user: UserData = Depends(get_current_user)):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC
    df = _apply_rbac(bundle.df, current_user)
    
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])

    # Get total income
    total_income, _, _ = get_current_month_profit(df, revenue_keywords, expense_keywords)
    if df.empty:
        current_month = "No data"
    else:
        current_month = df["date"].max().strftime("%B %Y")

    # Get variance details
    income_details = get_income_detail_with_variance(df, revenue_keywords)
    items = [
        VarianceItem(
            ledger=row["ledger"],
            current_amount=float(row["current_amount"]),
            previous_amount=float(row["previous_amount"]),
            variance_pct=float(row["variance_pct"])
        )
        for _, row in income_details.iterrows()
    ]

    return IncomeResponse(
        meta=_meta_from_dict(bundle.meta),
        total_income=total_income,
        current_month=current_month,
        items=items,
    )


@app.get("/api/expense", response_model=ExpenseResponse)
def expense(current_user: UserData = Depends(get_current_user)):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC
    df = _apply_rbac(bundle.df, current_user)
    
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])

    # Get total expense
    _, total_expense, _ = get_current_month_profit(df, revenue_keywords, expense_keywords)
    if df.empty:
        current_month = "No data"
    else:
        current_month = df["date"].max().strftime("%B %Y")

    # Get variance details
    expense_details = get_expense_detail_with_variance(df, expense_keywords)
    items = [
        VarianceItem(
            ledger=row["ledger"],
            current_amount=float(row["current_amount"]),
            previous_amount=float(row["previous_amount"]),
            variance_pct=float(row["variance_pct"])
        )
        for _, row in expense_details.iterrows()
    ]

    return ExpenseResponse(
        meta=_meta_from_dict(bundle.meta),
        total_expense=total_expense,
        current_month=current_month,
        items=items,
    )


@app.get("/healthz")
def health() -> Dict[str, str]:
    return {"status": "ok"}
