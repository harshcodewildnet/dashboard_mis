import { Grid, Group, Paper, Stack, Text } from "@mantine/core";
import dayjs from "dayjs";
import { useMemo, useState } from "react";
import { useSummary } from "../api/hooks";
import { ChartCard } from "../components/ChartCard";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { StatGrid } from "../components/StatGrid";

interface SummaryPageProps {
  departmentKey?: string | null;
}

export function SummaryPage({ departmentKey }: SummaryPageProps) {
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);

  const params = useMemo(() => {
    const [start, end] = range;
    return {
      start: start ? dayjs(start).format("YYYY-MM-DD") : undefined,
      end: end ? dayjs(end).format("YYYY-MM-DD") : undefined
    };
  }, [range]);

  const query = useSummary(params);

  if (query.isLoading) return <LoadingState message="Loading summary" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const data = query.data;

  const monthlyOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.monthly.map((m) => m.label) },
    yAxis: { type: "value" },
    series: [
      {
        data: data.monthly.map((m) => m.value),
        type: "line",
        smooth: true,
        areaStyle: {},
        color: "#4f46e5"
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 48 }
  };

  const groupOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.by_group.map((g) => g.label), axisLabel: { rotate: 30 } },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: data.by_group.map((g) => g.value),
        itemStyle: { color: "#22c55e" }
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 72 }
  };

  const ledgerOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.top_ledgers.map((g) => g.label), axisLabel: { rotate: 30 } },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: data.top_ledgers.map((g) => g.value),
        itemStyle: { color: "#38bdf8" }
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 72 }
  };

  return (
    <Stack gap="md">
      <Group justify="space-between" align="center">
        <div>
          <Text fw={700} fz="xl">
            Executive Summary
          </Text>
          <Text c="dimmed" size="sm">
            File {data.meta.file_name} · Sheet {data.meta.sheet} · Rows {data.meta.rows}
          </Text>
        </div>
        <DateRangePicker value={range} onChange={setRange} />
      </Group>

      <StatGrid
        items={[
          { label: "Total Revenue", value: data.kpis.total_revenue.toLocaleString(undefined, { maximumFractionDigits: 2 }) },
          { label: "Total Expenses", value: data.kpis.total_expenses.toLocaleString(undefined, { maximumFractionDigits: 2 }) },
          { label: "Net Profit", value: data.kpis.net_profit.toLocaleString(undefined, { maximumFractionDigits: 2 }), color: data.kpis.net_profit >= 0 ? "#16a34a" : "#dc2626" },
          { label: "Cash / Bank", value: data.kpis.cash_balance.toLocaleString(undefined, { maximumFractionDigits: 2 }) }
        ]}
      />

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, lg: 8 }}>
          <ChartCard title="Monthly Net Amount" option={monthlyOption} height={360} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 4 }}>
          <Paper withBorder radius="lg" p="md">
            <Stack gap="xs">
              <Text fw={600}>Last Updated</Text>
              <Text>{dayjs(data.meta.modified_at).format("YYYY-MM-DD HH:mm")}</Text>
              <Text c="dimmed" size="sm">
                Columns: {data.meta.columns.join(", ")}
              </Text>
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ChartCard title="Top Ledger Groups" option={groupOption} height={320} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <ChartCard title="Top Ledgers" option={ledgerOption} height={320} />
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
