import { useQuery } from "@tanstack/react-query";
import { api } from "./client";
import { 
  ExpenseResponse, 
  HomeDataResponse, 
  IncomeResponse, 
  LedgerResponse, 
  MetaPayload, 
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

export const useLedgers = () =>
  useQuery({
    queryKey: ["ledgers"],
    queryFn: async () => {
      const res = await api.get<string[]>("/api/ledgers");
      return res.data;
    }
  });

export const useHome = () =>
  useQuery({
    queryKey: ["home"],
    queryFn: async () => {
      const res = await api.get<HomeDataResponse>("/api/home");
      return res.data;
    }
  });

export const useIncome = () =>
  useQuery({
    queryKey: ["income"],
    queryFn: async () => {
      const res = await api.get<IncomeResponse>("/api/income");
      return res.data;
    }
  });

export const useExpense = () =>
  useQuery({
    queryKey: ["expense"],
    queryFn: async () => {
      const res = await api.get<ExpenseResponse>("/api/expense");
      return res.data;
    }
  });

export const useSummary = (params: { start?: string; end?: string }) =>
  useQuery({
    queryKey: ["summary", params],
    queryFn: async () => {
      const res = await api.get<SummaryResponse>("/api/summary", { params });
      return res.data;
    }
  });

export const useSales = (params: { start?: string; end?: string; top?: number }) =>
  useQuery({
    queryKey: ["sales", params],
    queryFn: async () => {
      const res = await api.get<SalesResponse>("/api/sales", { params });
      return res.data;
    }
  });

export const useLedger = (params: { name: string; start?: string; end?: string }) =>
  useQuery({
    queryKey: ["ledger", params],
    enabled: Boolean(params.name),
    queryFn: async () => {
      const res = await api.get<LedgerResponse>("/api/ledger", { params });
      return res.data;
    }
  });

export const useRows = (params: { start?: string; end?: string; limit?: number }) =>
  useQuery({
    queryKey: ["rows", params],
    queryFn: async () => {
      const res = await api.get<RowsResponse>("/api/rows", { params });
      return res.data;
    }
  });
