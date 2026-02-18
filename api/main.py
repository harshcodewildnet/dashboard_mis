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
    get_monthly_profit_by_cost_center,
    group_summary,
    ledger_statement,
    monthly_totals,
    sales_by_item,
    sales_by_month,
    top_customers,
    top_ledgers,
    get_monthly_profit_by_client,
    get_hierarchical_expenses,
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
        # If it's not S3, convert to Path for consistency, otherwise keep as string
        excel_path = path_str if path_str.startswith("s3://") else Path(path_str)
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
def _apply_rbac(
    df: pd.DataFrame, 
    user: UserData,
    admin_filter_dept_key: Optional[str] = None
) -> pd.DataFrame:
    """Filter DataFrame based on user role and department.
    
    Args:
        df: Data to filter
        user: Current authenticated user
        admin_filter_dept_key: Optional department filter (ADMIN only)
    
    Returns:
        Filtered dataframe based on RBAC rules
    """
    # ADMIN with optional department filter
    if user.role == "ADMIN":
        if admin_filter_dept_key:
            # Admin filtering by specific department
            db = SessionLocal()
            try:
                dept = db.query(Department).filter(
                    Department.department_key == admin_filter_dept_key
                ).first()
                if dept and "cost_centre_parent" in df.columns:
                    return df[df["cost_centre_parent"] == dept.cost_centre_parent]
            finally:
                db.close()
        # Admin without filter sees all data
        return df
    
    # DEPT_HEAD always filtered by their department (ignore admin_filter_dept_key)
    if user.cost_centre_parent:
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


class DepartmentComparisonItem(BaseModel):
    label: str
    current: float
    previous: float
    variance: float


class LedgerResponse(BaseModel):
    meta: MetaPayload
    ledger: str
    opening: float
    period_total: float
    closing: float
    running_balance: List[LedgerRow]
    department_breakdown: Optional[List[DepartmentComparisonItem]] = None


class RowsResponse(BaseModel):
    meta: MetaPayload
    rows: List[Dict[str, Any]]
    count: int


class VarianceItem(BaseModel):
    ledger: str
    current_amount: float
    previous_amount: float
    two_months_ago_amount: float
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


class MonthlyTrendPoint(BaseModel):
    month: str
    month_label: str
    income: float
    expense: float
    profit: float


class MonthlyTrendsSummary(BaseModel):
    avg_income: float
    avg_expense: float
    avg_profit: float
    best_month: Optional[str] = None
    worst_month: Optional[str] = None


class MonthlyTrendsResponse(BaseModel):
    meta: MetaPayload
    trends: List[MonthlyTrendPoint]
    summary: MonthlyTrendsSummary


class MonthlyCostCenterProfit(BaseModel):
    cost_center: str
    months: Dict[str, float]
    total: float


class ProfitByCostCenterResponse(BaseModel):
    meta: MetaPayload
    matrix: List[MonthlyCostCenterProfit]
    monthly_totals: Dict[str, float]
    month_labels: List[str]


class MonthlyClientProfit(BaseModel):
    client: str
    months: Dict[str, float]
    total: float
    deviation: Optional[float] = None


class ProfitByClientResponse(BaseModel):
    meta: MetaPayload
    matrix: List[MonthlyClientProfit]
    monthly_totals: Dict[str, float]
    month_labels: List[str]
    deviation_label: Optional[str] = None



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
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


class DepartmentPayload(BaseModel):
    department_key: str
    department_name: str
    cost_centre_parent: str


@app.get("/api/departments", response_model=List[DepartmentPayload])
def get_departments(current_user: UserData = Depends(get_current_user)):
    """Get list of all departments. Admin only."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access departments list"
        )
    
    db = SessionLocal()
    try:
        depts = db.query(Department).order_by(Department.department_name).all()
        return [
            DepartmentPayload(
                department_key=d.department_key,
                department_name=d.department_name,
                cost_centre_parent=d.cost_centre_parent
            )
            for d in depts
        ]
    finally:
        db.close()


@app.get("/api/meta", response_model=MetaPayload)
def meta(current_user: UserData = Depends(get_current_user)):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return _meta_from_dict(bundle.meta)


@app.get("/api/ledgers", response_model=List[str])
def ledgers(
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user)
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    # Apply RBAC with optional admin filter
    df = _apply_rbac(bundle.df, current_user, department_key)

    if "ledger" not in df.columns:
        return []
    ledgers = sorted(df["ledger"].dropna().unique())
    return [str(l) for l in ledgers]


@app.get("/api/summary", response_model=SummaryResponse)
def summary(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC First with optional admin filter
    rbac_df = _apply_rbac(bundle.df, current_user, department_key)
    
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
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC with optional admin filter
    rbac_df = _apply_rbac(bundle.df, current_user, department_key)
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
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC with optional admin filter
    df = _apply_rbac(bundle.df, current_user, department_key)
    
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

    # Calculate department breakdown if in Global View (no department_key)
    department_breakdown = None
    if department_key is None and "cost_centre_parent" in df.columns:
        # Filter for this ledger only
        ledger_df = df[df["ledger"] == name]
        
                # Determine Current and Previous Month
        if not ledger_df.empty:
            max_date = ledger_df["date"].max()
            current_month_start = max_date.replace(day=1)
            previous_month_start = (current_month_start - pd.DateOffset(months=1)).replace(day=1)
            
            # Filter Data
            current_df = ledger_df[ledger_df["date"] >= current_month_start]
            previous_df = ledger_df[
                (ledger_df["date"] >= previous_month_start) & 
                (ledger_df["date"] < current_month_start)
            ]
            
            # Group by Department
            curr_grp = current_df.groupby("cost_centre_parent")["amount"].sum()
            prev_grp = previous_df.groupby("cost_centre_parent")["amount"].sum()
            
            # Merge
            all_depts = set(curr_grp.index) | set(prev_grp.index)
            breakdown_list = []
            
            for dept in all_depts:
                # Helper to sanitize floats
                def safe_float(val):
                    f_val = float(val)
                    if f_val == float('inf') or f_val == float('-inf') or f_val != f_val:
                        return 0.0
                    return f_val

                curr_val = safe_float(curr_grp.get(dept, 0))
                prev_val = safe_float(prev_grp.get(dept, 0))
                
                variance_pct = 0.0
                if prev_val != 0:
                    try:
                        raw_variance = ((curr_val - prev_val) / abs(prev_val)) * 100
                        variance_pct = safe_float(raw_variance)
                    except ZeroDivisionError:
                        variance_pct = 0.0
                
                breakdown_list.append({
                    "label": str(dept) if dept else "Unknown",
                    "current": curr_val,
                    "previous": prev_val,
                    "variance": variance_pct
                })
                
            # Sort by current amount desc
            breakdown_list.sort(key=lambda x: x["current"], reverse=True)
            department_breakdown = breakdown_list

    return LedgerResponse(
        meta=_meta_from_dict(bundle.meta),
        ledger=name,
        opening=opening,
        period_total=period_total,
        closing=closing,
        running_balance=rows,
        department_breakdown=department_breakdown,
    )


@app.get("/api/rows", response_model=RowsResponse)
def rows(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user),
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC with optional admin filter
    rbac_df = _apply_rbac(bundle.df, current_user, department_key)
    df = _filter_by_date(rbac_df, start, end)
    trimmed = df.head(limit)
    records = _df_to_records(trimmed)

    return RowsResponse(meta=_meta_from_dict(bundle.meta), rows=records, count=len(records))


@app.get("/api/home", response_model=HomeDataResponse)
def home(
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user)
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC with optional admin filter
    df = _apply_rbac(bundle.df, current_user, department_key)
    
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
def income(
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user)
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC with optional admin filter
    df = _apply_rbac(bundle.df, current_user, department_key)
    
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
            two_months_ago_amount=float(row["two_months_ago_amount"]),
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
def expense(
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user)
):
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC with optional admin filter
    df = _apply_rbac(bundle.df, current_user, department_key)
    
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
            two_months_ago_amount=float(row["two_months_ago_amount"]),
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


@app.get("/api/monthly_trends", response_model=MonthlyTrendsResponse)
def monthly_trends(
    months: Optional[int] = Query(None, ge=1, le=24, description="Number of months to fetch"),
    from_date: Optional[str] = Query(None, description="Start month (YYYY-MM)"),
    to_date: Optional[str] = Query(None, description="End month (YYYY-MM)"),
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user),
):
    """Get monthly aggregated trends for income, expense, and profit.
    
    Can specify either:
    - `months`: Number of recent months (default: 3)
    - `from_date` and `to_date`: Custom range (YYYY-MM format)
    """
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC filtering
    df = _apply_rbac(bundle.df, current_user, department_key)
    
    if df.empty:
        return MonthlyTrendsResponse(
            meta=_meta_from_dict(bundle.meta),
            trends=[],
            summary=MonthlyTrendsSummary(
                avg_income=0.0,
                avg_expense=0.0,
                avg_profit=0.0
            )
        )
    
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])
    
    # Add month column
    df["month"] = df["date"].dt.to_period("M")
    
    # Determine date range
    if from_date and to_date:
        # Custom range
        try:
            start_period = pd.Period(from_date, freq="M")
            end_period = pd.Period(to_date, freq="M")
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM (e.g., 2026-01)"
            )
    else:
        # Last N months (default: 3)
        n_months = months if months else 3
        end_period = df["month"].max()
        start_period = end_period - (n_months - 1)
    
    # Filter by date range
    df_filtered = df[(df["month"] >= start_period) & (df["month"] <= end_period)]
    
    # Determine which column to use for filtering (primary_group or ledger)
    filter_col = "primary_group" if "primary_group" in df_filtered.columns else "ledger"
    
    # Group by month
    monthly_data = []
    for period in pd.period_range(start=start_period, end=end_period, freq="M"):
        month_df = df_filtered[df_filtered["month"] == period]
        
        # Calculate income (revenue ledgers)
        if revenue_keywords and filter_col in month_df.columns:
            filter_series = month_df[filter_col].astype(str)
            revenue_pattern = "|".join(revenue_keywords)
            income_mask = filter_series.str.contains(revenue_pattern, case=False, na=False)
            income = float(month_df.loc[income_mask, "amount"].sum()) if income_mask.any() else 0.0
        else:
            income = 0.0
        
        # Calculate expense (expense ledgers)
        if expense_keywords and filter_col in month_df.columns:
            filter_series = month_df[filter_col].astype(str)
            expense_pattern = "|".join(expense_keywords)
            expense_mask = filter_series.str.contains(expense_pattern, case=False, na=False)
            expense = float(abs(month_df.loc[expense_mask, "amount"].sum())) if expense_mask.any() else 0.0
        else:
            expense = 0.0
        
        profit = income - expense
        
        monthly_data.append({
            "month": str(period),
            "month_label": period.strftime("%b %Y"),
            "income": income,
            "expense": expense,
            "profit": profit
        })
    
    # Calculate summary statistics
    if monthly_data:
        avg_income = sum(m["income"] for m in monthly_data) / len(monthly_data)
        avg_expense = sum(m["expense"] for m in monthly_data) / len(monthly_data)
        avg_profit = sum(m["profit"] for m in monthly_data) / len(monthly_data)
        
        # Find best and worst months by profit
        best = max(monthly_data, key=lambda x: x["profit"])
        worst = min(monthly_data, key=lambda x: x["profit"])
        
        summary = MonthlyTrendsSummary(
            avg_income=avg_income,
            avg_expense=avg_expense,
            avg_profit=avg_profit,
            best_month=best["month_label"],
            worst_month=worst["month_label"]
        )
    else:
        summary = MonthlyTrendsSummary(
            avg_income=0.0,
            avg_expense=0.0,
            avg_profit=0.0
        )
    
    trends = [MonthlyTrendPoint(**m) for m in monthly_data]
    
    return MonthlyTrendsResponse(
        meta=_meta_from_dict(bundle.meta),
        trends=trends,
        summary=summary
    )


@app.get("/api/profit_by_cost_center", response_model=ProfitByCostCenterResponse)
def profit_by_cost_center(
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    current_user: UserData = Depends(get_current_user),
):
    """Get monthly profit breakdown by cost center for current year.
    
    Returns a matrix with cost centers as rows and months as columns.
    """
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC filtering
    df = _apply_rbac(bundle.df, current_user, department_key)
    
    if df.empty:
        return ProfitByCostCenterResponse(
            meta=_meta_from_dict(bundle.meta),
            matrix=[],
            monthly_totals={},
            month_labels=[]
        )
    
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])
    
    # Get the pivot table
    pivot_df = get_monthly_profit_by_cost_center(df, revenue_keywords, expense_keywords)
    
    if pivot_df.empty or "cost_centre_parent" not in pivot_df.columns:
        return ProfitByCostCenterResponse(
            meta=_meta_from_dict(bundle.meta),
            matrix=[],
            monthly_totals={},
            month_labels=[]
        )
    
    # Get month columns (exclude cost_centre_parent and total)
    month_columns = [col for col in pivot_df.columns if col not in ["cost_centre_parent", "total"]]
    
    # Sort month columns chronologically
    month_columns_sorted = sorted(month_columns)
    
    # Create month labels (e.g., "Jan", "Feb", "Mar")
    month_labels = [pd.Period(str(month)).strftime("%b") for month in month_columns_sorted]
    
    # Build matrix
    matrix = []
    for _, row in pivot_df.iterrows():
        cost_center = str(row["cost_centre_parent"])
        # Use label as key to match frontend expectation
        months_dict = {}
        for month in month_columns_sorted:
            label = pd.Period(str(month)).strftime("%b")
            months_dict[label] = float(row[month])
        
        total = float(row["total"]) if "total" in row else sum(months_dict.values())
        
        matrix.append(MonthlyCostCenterProfit(
            cost_center=cost_center,
            months=months_dict,
            total=total
        ))
    
    # Calculate monthly totals (sum of all cost centers for each month)
    monthly_totals = {}
    for month in month_columns_sorted:
        label = pd.Period(str(month)).strftime("%b")
        monthly_totals[label] = float(pivot_df[month].sum())
    
    return ProfitByCostCenterResponse(
        meta=_meta_from_dict(bundle.meta),
        matrix=matrix,
        monthly_totals=monthly_totals,
        month_labels=month_labels
    )



@app.get("/api/profit_by_client", response_model=ProfitByClientResponse)
def profit_by_client(
    department_key: Optional[str] = Query(None, description="Filter by department (Admin only)"),
    limit: int = Query(20, ge=1, le=500, description="Limit number of clients"),
    sort: str = Query("desc", regex="^(asc|desc)$", description="Sort order (asc=lowest, desc=highest)"),
    sort_by: str = Query("total", regex="^(total|deviation)$", description="Column to sort by"),
    current_user: UserData = Depends(get_current_user),
):
    """Get monthly profit breakdown by client for current year.
    
    Returns a matrix with clients as rows and months as columns.
    Sorted by total profit descending.
    """
    try:
        bundle = data_cache.get_bundle()
    except ExcelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Apply RBAC filtering
    df = _apply_rbac(bundle.df, current_user, department_key)
    
    if df.empty:
        return ProfitByClientResponse(
            meta=_meta_from_dict(bundle.meta),
            matrix=[],
            monthly_totals={},
            month_labels=[]
        )
    
    revenue_keywords = config.get("revenue_keywords", [])
    expense_keywords = config.get("expense_keywords", [])
    
    # Get the pivot table
    pivot_df = get_monthly_profit_by_client(df, revenue_keywords, expense_keywords, sort_order=sort)
    
    if pivot_df.empty or "name" not in pivot_df.columns:
        return ProfitByClientResponse(
            meta=_meta_from_dict(bundle.meta),
            matrix=[],
            monthly_totals={},
            month_labels=[]
        )
    
    
    # Get month columns (exclude name and total)
    month_columns = [col for col in pivot_df.columns if col not in ["name", "total"]]
    
    # Sort month columns chronologically
    month_columns_sorted = sorted(month_columns)
    
    # Calculate deviation for ALL clients before limiting
    current_month_col = month_columns_sorted[-1] if month_columns_sorted else None
    prev_month_col = month_columns_sorted[-2] if len(month_columns_sorted) >= 2 else None
    
    if current_month_col and prev_month_col:
        pivot_df["deviation"] = pivot_df[current_month_col] - pivot_df[prev_month_col]
    else:
        pivot_df["deviation"] = 0
        
    # Apply requested sorting
    if sort_by == "deviation":
        pivot_df = pivot_df.sort_values("deviation", ascending=(sort == "asc"))
    else:
        pivot_df = pivot_df.sort_values("total", ascending=(sort == "asc"))

    # Apply limit (Top N)
    if limit > 0:
        pivot_df = pivot_df.head(limit)
    
    # Limit to last 3 months for display
    month_columns_display = month_columns_sorted[-3:] if len(month_columns_sorted) > 3 else month_columns_sorted
    
    deviation_label = None
    if current_month_col and prev_month_col:
        curr_label = pd.Period(str(current_month_col)).strftime("%b")
        prev_label = pd.Period(str(prev_month_col)).strftime("%b")
        deviation_label = f"Profit Deviation ({curr_label} vs {prev_label})"
    
    # Create month labels (e.g., "Jan", "Feb", "Mar") - Reversed for user request
    month_labels = [pd.Period(str(month)).strftime("%b") for month in reversed(month_columns_display)]
    
    # Build matrix
    matrix = []
    for _, row in pivot_df.iterrows():
        client = str(row["name"])
        # Use label as key to match frontend expectation
        months_dict = {}
        total_calc = 0.0
        for month in month_columns_display:
            label = pd.Period(str(month)).strftime("%b")
            val = float(row[month])
            months_dict[label] = val
            total_calc += val
            
        total = float(row["total"]) if "total" in row else total_calc
        
        # Use deviation from pivot_df
        deviation = float(row["deviation"]) if "deviation" in row and not pd.isna(row["deviation"]) else None
        
        matrix.append(MonthlyClientProfit(
            client=client,
            months=months_dict,
            total=total,
            deviation=deviation
        ))
    
    # Calculate monthly totals (sum of all clients displayed for each month)
    monthly_totals = {}
    for month in month_columns_display:
        label = pd.Period(str(month)).strftime("%b")
        monthly_totals[label] = float(pivot_df[month].sum())
    
    return ProfitByClientResponse(
        meta=_meta_from_dict(bundle.meta),
        matrix=matrix,
        monthly_totals=monthly_totals,
        month_labels=month_labels,
        deviation_label=deviation_label
    )


@app.get("/api/expenses/hierarchy")
def expense_hierarchy(
    current_user: UserData = Depends(get_current_user),
):
    """Returns a hierarchical structure of expenses (Salary & Direct Expenses) for the current year."""
    try:
        bundle = data_cache.get_bundle()
        # Get actual file path for Salary List loading
        excel_path, _ = latest_cache_key(config["excel_loader"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    is_admin = current_user.role == "ADMIN"
    user_cp = current_user.cost_centre_parent
    print(f"Hierarchy request for user: {current_user.email}, Role: {current_user.role}, Admin: {is_admin}, CP: {user_cp}")
    
    hierarchy = get_hierarchical_expenses(
        bundle.df, 
        excel_path, 
        user_cost_centre_parent=user_cp,
        is_admin=is_admin
    )
    
    return {"hierarchy": hierarchy}


@app.get("/healthz")
def health() -> Dict[str, str]:
    return {"status": "ok"}

