import { Grid, Group, NumberInput, Stack, Text } from "@mantine/core";
import dayjs from "dayjs";
import { useMemo, useState } from "react";
import { useSales } from "../api/hooks";
import { ChartCard } from "../components/ChartCard";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { StatGrid } from "../components/StatGrid";

export function SalesPage() {
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);
  const [topN, setTopN] = useState<number>(10);

  const params = useMemo(() => {
    const [start, end] = range;
    return {
      start: start ? dayjs(start).format("YYYY-MM-DD") : undefined,
      end: end ? dayjs(end).format("YYYY-MM-DD") : undefined,
      top: topN
    };
  }, [range, topN]);

  const query = useSales(params);

  if (query.isLoading) return <LoadingState message="Loading sales" />;
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
        color: "#5b21b6"
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 48 }
  };

  const customersOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: data.top_customers.map((c) => c.label) },
    series: [
      {
        type: "bar",
        data: data.top_customers.map((c) => c.value),
        itemStyle: { color: "#22c55e" }
      }
    ],
    grid: { left: 120, right: 16, top: 16, bottom: 16 }
  };

  const itemsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: data.top_items.map((c) => c.label) },
    series: [
      {
        type: "bar",
        data: data.top_items.map((c) => c.value),
        itemStyle: { color: "#0ea5e9" }
      }
    ],
    grid: { left: 120, right: 16, top: 16, bottom: 16 }
  };

  return (
    <Stack gap="md">
      <Group justify="space-between" align="center">
        <div>
          <Text fw={700} fz="xl">
            Sales Analysis
          </Text>
          <Text c="dimmed" size="sm">
            File {data.meta.file_name} · Sheet {data.meta.sheet}
          </Text>
        </div>
        <Group gap="md">
          <NumberInput label="Top N" value={topN} min={3} max={30} onChange={(val) => setTopN(val || 10)} w={120} />
          <DateRangePicker value={range} onChange={setRange} />
        </Group>
      </Group>

      <StatGrid
        items={[
          { label: "Total Sales", value: data.totals.total_sales.toLocaleString(undefined, { maximumFractionDigits: 2 }) },
          { label: "Unique Customers", value: data.totals.unique_customers.toLocaleString() },
          { label: "Average Ticket", value: data.totals.avg_ticket.toLocaleString(undefined, { maximumFractionDigits: 2 }) }
        ]}
      />

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, lg: 7 }}>
          <ChartCard title="Sales by Month" option={monthlyOption} height={360} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 5 }}>
          <ChartCard title="Top Customers" option={customersOption} height={360} />
        </Grid.Col>
      </Grid>

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, lg: 6 }}>
          <ChartCard title="Top Items" option={itemsOption} height={360} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 6 }}>
          <ChartCard
            title="Meta"
            option={{
              tooltip: {},
              series: [
                {
                  type: "pie",
                  radius: ["40%", "70%"],
                  data: [
                    { value: data.totals.total_sales, name: "Total" },
                    { value: data.totals.avg_ticket * Math.max(data.totals.unique_customers, 1), name: "Avg Ticket * Customers" }
                  ]
                }
              ]
            }}
            height={320}
          />
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
