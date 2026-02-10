import { useQuery } from "@tanstack/react-query";
import { api } from "./client";
import {
  ExpenseResponse,
  HomeDataResponse,
  IncomeResponse,
  LedgerResponse,
  MetaPayload,
  MonthlyTrendsResponse,
  RowsResponse,
  SalesResponse,
  SummaryResponse
} from "./types";

export const useMeta = () =>
  useQuery({
    queryKey: ["meta"],
    queryFn: async () => {
      const res = await api.get<MetaPayload>("/api/meta");
      return res.data;
    }
  });

export const useLedgers = (departmentKey?: string | null) =>
  useQuery({
    queryKey: ["ledgers", departmentKey],
    queryFn: async () => {
      const params = departmentKey ? { department_key: departmentKey } : {};
      const res = await api.get<string[]>("/api/ledgers", { params });
      return res.data;
    }
  });

export const useHome = (departmentKey?: string | null) =>
  useQuery({
    queryKey: ["home", departmentKey],
    queryFn: async () => {
      const params = departmentKey ? { department_key: departmentKey } : {};
      const res = await api.get<HomeDataResponse>("/api/home", { params });
      return res.data;
    }
  });

export const useIncome = (departmentKey?: string | null) =>
  useQuery({
    queryKey: ["income", departmentKey],
    queryFn: async () => {
      const params = departmentKey ? { department_key: departmentKey } : {};
      const res = await api.get<IncomeResponse>("/api/income", { params });
      return res.data;
    }
  });

export const useExpense = (departmentKey?: string | null) =>
  useQuery({
    queryKey: ["expense", departmentKey],
    queryFn: async () => {
      const params = departmentKey ? { department_key: departmentKey } : {};
      const res = await api.get<ExpenseResponse>("/api/expense", { params });
      return res.data;
    }
  });

export const useSummary = (params: { start?: string; end?: string; departmentKey?: string | null }) =>
  useQuery({
    queryKey: ["summary", params],
    queryFn: async () => {
      const apiParams: Record<string, any> = {};
      if (params.start) apiParams.start = params.start;
      if (params.end) apiParams.end = params.end;
      if (params.departmentKey) apiParams.department_key = params.departmentKey;
      const res = await api.get<SummaryResponse>("/api/summary", { params: apiParams });
      return res.data;
    }
  });

export const useSales = (params: { start?: string; end?: string; top?: number; departmentKey?: string | null }) =>
  useQuery({
    queryKey: ["sales", params],
    queryFn: async () => {
      const apiParams: Record<string, any> = {};
      if (params.start) apiParams.start = params.start;
      if (params.end) apiParams.end = params.end;
      if (params.top) apiParams.top = params.top;
      if (params.departmentKey) apiParams.department_key = params.departmentKey;
      const res = await api.get<SalesResponse>("/api/sales", { params: apiParams });
      return res.data;
    }
  });

export const useLedger = (params: { name: string; start?: string; end?: string; departmentKey?: string | null }) =>
  useQuery({
    queryKey: ["ledger", params],
    enabled: Boolean(params.name),
    queryFn: async () => {
      const apiParams: Record<string, any> = { name: params.name };
      if (params.start) apiParams.start = params.start;
      if (params.end) apiParams.end = params.end;
      if (params.departmentKey) apiParams.department_key = params.departmentKey;
      const res = await api.get<LedgerResponse>("/api/ledger", { params: apiParams });
      return res.data;
    }
  });

export const useRows = (params: { start?: string; end?: string; limit?: number; departmentKey?: string | null }) =>
  useQuery({
    queryKey: ["rows", params],
    queryFn: async () => {
      const apiParams: Record<string, any> = {};
      if (params.start) apiParams.start = params.start;
      if (params.end) apiParams.end = params.end;
      if (params.limit) apiParams.limit = params.limit;
      if (params.departmentKey) apiParams.department_key = params.departmentKey;
      const res = await api.get<RowsResponse>("/api/rows", { params: apiParams });
      return res.data;
    }
  });

export const useMonthlyTrends = (params: {
  months?: number;
  from_date?: string;
  to_date?: string;
  departmentKey?: string | null;
}) =>
  useQuery({
    queryKey: ["monthly_trends", params],
    queryFn: async () => {
      const apiParams: Record<string, any> = {};
      if (params.months) apiParams.months = params.months;
      if (params.from_date) apiParams.from_date = params.from_date;
      if (params.to_date) apiParams.to_date = params.to_date;
      if (params.departmentKey) apiParams.department_key = params.departmentKey;
      const res = await api.get<MonthlyTrendsResponse>("/api/monthly_trends", { params: apiParams });
      return res.data;
    }
  });

