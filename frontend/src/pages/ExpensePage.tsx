import { Box, Group, Paper, Stack, Text, Title } from "@mantine/core";
import { BarChart } from "@mantine/charts";
import { useMemo } from "react";
import { useExpense, useExpenseHierarchy } from "../api/hooks";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { HierarchicalExpenseTable } from "../components/HierarchicalExpenseTable";
import { getYAxisWidth, formatCurrency } from "../utils/chartHelpers";

interface ExpensePageProps {
  departmentKey?: string | null;
}

export function ExpensePage({ departmentKey }: ExpensePageProps) {
  const query = useExpense(departmentKey);
  const hierarchyQuery = useExpenseHierarchy();
  const items = useMemo(() => {
    return query.data?.items || [];
  }, [query.data?.items]);

  if (query.isLoading) return <LoadingState message="Loading expense details" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const { total_expense, current_month, items: rawItems } = query.data;
  const formatVariance = (variance: number) => `${variance > 0 ? "+" : ""}${variance.toFixed(1)}%`;

  const getVarianceColor = (variance: number) => {
    // For expenses, increase is bad (red), decrease is good (green)
    if (variance > 0) return "red";
    if (variance < 0) return "green";
    return "gray";
  };




  const top10 = items.slice(0, 10);
  const chartData = top10.map(item => ({
    ledger: item.ledger.length > 20 ? item.ledger.substring(0, 20) + "..." : item.ledger,
    amount: item.current_amount
  }));

  return (
    <Stack gap="md">
      {/* Header Card */}
      <Paper
        p="xl"
        radius="md"
        style={{
          background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
          color: "white"
        }}
      >
        <Stack align="center" gap="xs">
          <Text size="xl" fw={500} opacity={0.9}>
            Total Expense - {current_month}
          </Text>
          <Title order={1} size="3.5rem">
            {formatCurrency(total_expense)}
          </Title>
        </Stack>
      </Paper>

      {/* Hierarchical Expense Table */}
      <Paper p="md" radius="md" withBorder>
        <HierarchicalExpenseTable
          data={hierarchyQuery.data}
          isLoading={hierarchyQuery.isLoading}
        />
      </Paper>


      {/* Chart */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <Title order={4}>Top 10 Expense Categories</Title>
          <Box h={400} className="chart-container">
            <BarChart
              h={380}
              data={chartData}
              dataKey="ledger"
              series={[{ name: "amount", label: "Amount", color: "red" }]}
              tickLine="y"
              orientation="horizontal"
              yAxisProps={{
                width: getYAxisWidth(top10.map(i => i.current_amount))
              }}
              xAxisProps={{
                interval: 0,
                angle: -30,
                textAnchor: 'end',
                height: 80
              }}
              valueFormatter={(value) => formatCurrency(value as number)}
              withTooltip={true}
              barProps={{ activeBar: false }}
              tooltipProps={{
                content: ({ label, payload }) => {
                  if (!payload || payload.length === 0) return null;
                  return (
                    <div style={{ backgroundColor: "white", padding: "12px", borderRadius: "4px", border: "1px solid #dee2e6", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
                      <Text fw={500} mb={5}>{label}</Text>
                      {payload.map((item: any) => (
                        <Text key={item.name} size="sm" c="red.7">
                          Amount: {formatCurrency(item.value)}
                        </Text>
                      ))}
                    </div>
                  );
                }
              }}
            />
          </Box>
        </Stack>
      </Paper>

      {/* Summary Stats */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <Title order={4}>📊 Summary Statistics</Title>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
            <div>
              <Text size="sm" c="dimmed">Total Expense Categories</Text>
              <Text size="xl" fw={700}>{items.length}</Text>
            </div>
            <div>
              <Text size="sm" c="dimmed">Average per Category</Text>
              <Text size="xl" fw={700}>
                {formatCurrency(items.reduce((sum, item) => sum + item.current_amount, 0) / items.length || 0)}
              </Text>
            </div>
            <div>
              <Text size="sm" c="dimmed">Highest Expense</Text>
              <Text size="xl" fw={700}>
                {formatCurrency(Math.max(...items.map(item => item.current_amount)))}
              </Text>
            </div>
            <div>
              <Text size="sm" c="dimmed">Avg Variance</Text>
              <Text size="xl" fw={700}>
                {formatVariance(items.reduce((sum, item) => sum + item.variance_pct, 0) / items.length || 0)}
              </Text>
            </div>
          </div>
        </Stack>
      </Paper>

      {/* Key Insights */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <Title order={4}>💡 Key Insights</Title>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div>
              <Text fw={600} mb="xs">⚠️ Significantly Increased</Text>
              {items.filter(item => item.variance_pct > 10).slice(0, 5).map((item, index) => (
                <Text key={index} size="sm" c="red">
                  {item.ledger}: {formatVariance(item.variance_pct)}
                </Text>
              ))}
              {items.filter(item => item.variance_pct > 10).length === 0 && (
                <Text size="sm" c="dimmed">No significant increases</Text>
              )}
            </div>
            <div>
              <Text fw={600} mb="xs" c="green">✅ Significantly Decreased</Text>
              {items.filter(item => item.variance_pct < -10).slice(0, 5).map((item, index) => (
                <Text key={index} size="sm" c="green">
                  {item.ledger}: {formatVariance(item.variance_pct)}
                </Text>
              ))}
              {items.filter(item => item.variance_pct < -10).length === 0 && (
                <Text size="sm" c="dimmed">No significant decreases</Text>
              )}
            </div>
          </div>
        </Stack>
      </Paper>
    </Stack>
  );
}
