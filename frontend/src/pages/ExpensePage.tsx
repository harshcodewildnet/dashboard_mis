import { ActionIcon, Box, Card, Group, Paper, Stack, Text, Title, rem, Badge, Divider, Grid } from "@mantine/core";
import { BarChart } from "@mantine/charts";
import { IconReceipt, IconTrendingUp, IconTrendingDown, IconChartBar, IconInfoCircle, IconAlertTriangle, IconChecklist } from "@tabler/icons-react";
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
    <Stack gap="xl">
      {/* Header Card */}
      <Card
        p="xl"
        radius="lg"
        style={{
          background: "linear-gradient(135deg, var(--mantine-color-orange-6) 0%, var(--mantine-color-red-7) 100%)",
          color: "white",
          minHeight: rem(180),
          display: 'flex',
          justifyContent: 'center'
        }}
      >
        <Stack align="center" gap="xs">
          <Badge variant="white" color="red" size="lg" radius="sm">Expense Auditor</Badge>
          <Text size="sm" fw={600} opacity={0.8} style={{ textTransform: 'uppercase', letterSpacing: rem(1) }}>
            Operational Burn — {current_month}
          </Text>
          <Title order={1} size="3.5rem" fw={800}>
            {formatCurrency(total_expense)}
          </Title>
        </Stack>
      </Card>

      {/* Hierarchical Expense Table */}
      <Paper p="xl" radius="lg" withBorder shadow="sm">
        <Stack gap="lg">
          <Group gap="xs">
            <ActionIcon color="red" variant="light" radius="md"><IconChecklist size={18} /></ActionIcon>
            <Title order={3} size="h4" fw={700}>Expense Hierarchy</Title>
          </Group>
          <HierarchicalExpenseTable
            data={hierarchyQuery.data}
            isLoading={hierarchyQuery.isLoading}
          />
        </Stack>
      </Paper>


      {/* Chart */}
      <Paper p="xl" radius="lg" withBorder shadow="sm">
        <Stack gap="lg">
          <Group gap="xs">
            <ActionIcon color="orange" variant="light" radius="md"><IconChartBar size={18} /></ActionIcon>
            <Title order={4} size="h5" fw={700}>Top Contribution Categories</Title>
          </Group>
          <Box h={400} className="chart-container">
            <BarChart
              h={380}
              data={chartData}
              dataKey="ledger"
              series={[{ name: "amount", label: "Amount", color: "orange.6" }]}
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
              barProps={{ activeBar: false, radius: [4, 4, 0, 0] }}
              tooltipProps={{
                content: ({ label, payload }) => {
                  if (!payload || payload.length === 0) return null;
                  return (
                    <Paper shadow="md" p="sm" withBorder radius="md">
                      <Text fw={700} size="sm" mb={4}>{label}</Text>
                      {payload.map((item: any) => (
                        <Text key={item.name} size="xs" c="orange.7" fw={600}>
                          {formatCurrency(item.value)}
                        </Text>
                      ))}
                    </Paper>
                  );
                }
              }}
            />
          </Box>
        </Stack>
      </Paper>

      {/* Summary Stats */}
      <Paper p="xl" radius="lg" withBorder shadow="sm">
        <Stack gap="lg">
          <Group gap="xs">
            <ActionIcon color="slate" variant="light" radius="md"><IconInfoCircle size={18} /></ActionIcon>
            <Title order={4} size="h5" fw={700}>Expense Intelligence</Title>
          </Group>
          <Grid gutter="xl">
            <Grid.Col span={{ base: 6, md: 3 }}>
              <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Categories</Text>
              <Text size="xl" fw={800}>{items.length}</Text>
            </Grid.Col>
            <Grid.Col span={{ base: 6, md: 3 }}>
              <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Avg per Category</Text>
              <Text size="xl" fw={800}>
                {formatCurrency(items.reduce((sum, item) => sum + item.current_amount, 0) / items.length || 0)}
              </Text>
            </Grid.Col>
            <Grid.Col span={{ base: 6, md: 3 }}>
              <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Peak Expense</Text>
              <Text size="xl" fw={800}>
                {formatCurrency(Math.max(...items.map(item => item.current_amount)))}
              </Text>
            </Grid.Col>
            <Grid.Col span={{ base: 6, md: 3 }}>
              <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Variance avg</Text>
              <Text size="xl" fw={800} c={items.reduce((sum, item) => sum + item.variance_pct, 0) / items.length > 0 ? 'red.6' : 'green.6'}>
                {formatVariance(items.reduce((sum, item) => sum + item.variance_pct, 0) / items.length || 0)}
              </Text>
            </Grid.Col>
          </Grid>
        </Stack>
      </Paper>

      {/* Key Insights */}
      <Paper p="xl" radius="lg" withBorder shadow="sm">
        <Stack gap="lg">
          <Group gap="xs">
            <ActionIcon color="orange" variant="light" radius="md"><IconAlertTriangle size={18} /></ActionIcon>
            <Title order={4} size="h5" fw={700}>Anomalies & Savings</Title>
          </Group>
          <Grid gutter="xl">
            <Grid.Col span={{ base: 12, md: 6 }}>
              <Stack gap="xs">
                <Group gap="xs">
                  <IconTrendingUp size={16} color="var(--mantine-color-red-6)" />
                  <Text fw={700} size="sm">Budget Overruns</Text>
                </Group>
                <Divider />
                {items.filter(item => item.variance_pct > 10).slice(0, 5).map((item, index) => (
                  <Group key={index} justify="space-between">
                    <Text size="xs" fw={500}>{item.ledger}</Text>
                    <Badge color="red" variant="light" size="xs">{formatVariance(item.variance_pct)}</Badge>
                  </Group>
                ))}
                {items.filter(item => item.variance_pct > 10).length === 0 && (
                  <Text size="xs" c="dimmed">No significant increases detected</Text>
                )}
              </Stack>
            </Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}>
              <Stack gap="xs">
                <Group gap="xs">
                  <IconTrendingDown size={16} color="var(--mantine-color-green-6)" />
                  <Text fw={700} size="sm">Savings Achieved</Text>
                </Group>
                <Divider />
                {items.filter(item => item.variance_pct < -10).slice(0, 5).map((item, index) => (
                  <Group key={index} justify="space-between">
                    <Text size="xs" fw={500}>{item.ledger}</Text>
                    <Badge color="green" variant="light" size="xs">{formatVariance(item.variance_pct)}</Badge>
                  </Group>
                ))}
                {items.filter(item => item.variance_pct < -10).length === 0 && (
                  <Text size="xs" c="dimmed">No significant savings detected</Text>
                )}
              </Stack>
            </Grid.Col>
          </Grid>
        </Stack>
      </Paper>
    </Stack>
  );
}
