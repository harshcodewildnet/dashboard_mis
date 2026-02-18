export type SeriesPoint = { label: string; value: number };

export type DepartmentComparisonItem = {
  label: string;
  current: number;
  previous: number;
  variance: number;
};

export type MetaPayload = {
  file_name: string;
  sheet: string;
  rows: number;
  modified_at: string;
  columns: string[];
};

export type SummaryResponse = {
  meta: MetaPayload;
  kpis: {
    total_revenue: number;
    total_expenses: number;
    net_profit: number;
    cash_balance: number;
  };
  monthly: SeriesPoint[];
  by_group: SeriesPoint[];
  top_ledgers: SeriesPoint[];
};

export type SalesResponse = {
  meta: MetaPayload;
  totals: {
    total_sales: number;
    unique_customers: number;
    avg_ticket: number;
  };
  monthly: SeriesPoint[];
  top_customers: SeriesPoint[];
  top_items: SeriesPoint[];
};

export type LedgerRow = {
  date: string;
  amount: number;
  running_balance: number;
  description?: string | null;
  reference?: string | null;
  voucher_type?: string | null;
};

export type LedgerResponse = {
  meta: MetaPayload;
  ledger: string;
  opening: number;
  period_total: number;
  closing: number;
  running_balance: LedgerRow[];
  department_breakdown?: DepartmentComparisonItem[];
};

export type RowsResponse = {
  meta: MetaPayload;
  rows: Record<string, unknown>[];
  count: number;
};

export type VarianceItem = {
  ledger: string;
  current_amount: number;
  previous_amount: number;
  two_months_ago_amount: number;
  variance_pct: number;
};

export type IncomeResponse = {
  meta: MetaPayload;
  total_income: number;
  current_month: string;
  items: VarianceItem[];
};

export type ExpenseResponse = {
  meta: MetaPayload;
  total_expense: number;
  current_month: string;
  items: VarianceItem[];
};

export type MonthlyExpenseItem = {
  month: string;
  total_expense: number;
};

export type HomeDataResponse = {
  meta: MetaPayload;
  current_month: string;
  income: number;
  expense: number;
  profit: number;
  cash_balance: number;
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  monthly_expenses: MonthlyExpenseItem[];
  daily_profit: Record<string, unknown>[];
};

export type MonthlyTrendPoint = {
  month: string;
  month_label: string;
  income: number;
  expense: number;
  profit: number;
};

export type MonthlyTrendsSummary = {
  avg_income: number;
  avg_expense: number;
  avg_profit: number;
  best_month?: string | null;
  worst_month?: string | null;
};

export type MonthlyTrendsResponse = {
  meta: MetaPayload;
  trends: MonthlyTrendPoint[];
  summary: MonthlyTrendsSummary;
};

export type MonthlyCostCenterProfit = {
  cost_center: string;
  months: Record<string, number>;
  total: number;
};

export type ProfitByCostCenterResponse = {
  meta: MetaPayload;
  matrix: MonthlyCostCenterProfit[];
  monthly_totals: Record<string, number>;
  month_labels: string[];
};

export type MonthlyClientProfit = {
  client: string;
  months: Record<string, number>;
  total: number;
  deviation?: number;
};

export type ProfitByClientResponse = {
  meta: MetaPayload;
  matrix: MonthlyClientProfit[];
  monthly_totals: Record<string, number>;
  month_labels: string[];
  deviation_label?: string;
};

export type ExpenseNode = {
  id: string;
  label: string;
  months: number[];
  total: number;
  isSalary?: boolean;
  empId?: string;
  children?: ExpenseNode[];
};

export type ExpenseHierarchyResponse = {
  hierarchy: ExpenseNode[];
};
