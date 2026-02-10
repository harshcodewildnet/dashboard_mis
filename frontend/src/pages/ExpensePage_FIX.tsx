import { ActionIcon, Anchor, Badge, Box, Group, Paper, ScrollArea, Stack, Table, Text, Title } from "@mantine/core";
import { BarChart } from "@mantine/charts";
import { IconArrowDown, IconArrowUp, IconArrowsSort } from "@tabler/icons-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useExpense } from "../api/hooks";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";

interface ExpensePageProps {
    departmentKey?: string | null;
}

export function ExpensePage({ departmentKey }: ExpensePageProps) {
    const query = useExpense(departmentKey);
    const [sortBy, setSortBy] = useState<"amount" | "variance" | null>(null);
    const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

    if (query.isLoading) return <LoadingState message="Loading expense details" />;
    if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
    if (!query.data) return null;

    const { total_expense, current_month, items: rawItems } = query.data;

    const formatCurrency = (amount: number) => `₹${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
    const formatVariance = (variance: number) => `${variance > 0 ? "+" : ""}${variance.toFixed(1)}%`;

    const getVarianceColor = (variance: number) => {
        // For expenses, increase is bad (red), decrease is good (green)
        if (variance > 0) return "red";
        if (variance < 0) return "green";
        return "gray";
    };

    const handleSort = (column: "amount" | "variance") => {
        if (sortBy === column) {
            setSortDirection(sortDirection === "asc" ? "desc" : "asc");
        } else {
            setSortBy(column);
            setSortDirection("desc");
        }
    };

    const getSortIcon = (column: "amount" | "variance") => {
        if (sortBy !== column) return <IconArrowsSort size={14} />;
        return sortDirection === "asc" ? <IconArrowUp size={14} /> : <IconArrowDown size={14} />;
    };

    // Apply sorting if active
    let items = rawItems;
    if (sortBy) {
        items = [...rawItems].sort((a, b) => {
            const aVal = sortBy === "amount" ? a.current_amount : a.variance_pct;
            const bVal = sortBy === "amount" ? b.current_amount : b.variance_pct;
            return sortDirection === "asc" ? aVal - bVal : bVal - aVal;
        });
    }
