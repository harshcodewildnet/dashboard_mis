import { useState } from "react";
import { Badge, Box, Button, Grid, Group, Paper, Stack, Table, Text, Title } from "@mantine/core";
import { LineChart } from "@mantine/charts";
import { useNavigate } from "react-router-dom";
import { useHome, useMonthlyTrends } from "../api/hooks";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MonthRangeFilter } from "../components/MonthRangeFilter";
import { TrendChart } from "../components/TrendChart";
import { getYAxisWidth, formatCurrency } from "../utils/chartHelpers";

interface HomePageProps {
  departmentKey?: string | null;
}

export function HomePage({ departmentKey }: HomePageProps) {
  const query = useHome(departmentKey);
  const navigate = useNavigate();

  // Filter states for each graph
  const [mainRange, setMainRange] = useState<{ months?: number; from_date?: string; to_date?: string }>({ months: 3 });
  const [profitRange, setProfitRange] = useState<{ months?: number; from_date?: string; to_date?: string }>({ months: 3 });
  const [expenseRange, setExpenseRange] = useState<{ months?: number; from_date?: string; to_date?: string }>({ months: 3 });
  const [incomeRange, setIncomeRange] = useState<{ months?: number; from_date?: string; to_date?: string }>({ months: 3 });

  // Fetch monthly trends for each graph
  const mainTrends = useMonthlyTrends({ ...mainRange, departmentKey });
  const profitTrends = useMonthlyTrends({ ...profitRange, departmentKey });
  const expenseTrends = useMonthlyTrends({ ...expenseRange, departmentKey });
  const incomeTrends = useMonthlyTrends({ ...incomeRange, departmentKey });

  if (query.isLoading) return <LoadingState message="Loading dashboard" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const data = query.data;

  const profitColor = data.profit >= 0 ? "#10b981" : "#ef4444";

  // Transform main trends for multi-line chart
  const mainChartData = mainTrends.data?.trends.map((item) => ({
    month: item.month_label,
    Revenue: item.income,
    Expense: item.expense,
    Profit: item.profit,
  })) || [];

  return (
    <Stack gap="md">
      {/* Header */}
      <Title order={2}>💰 Financial Dashboard - {data.current_month}</Title>

      {/* Income and Expense Cards */}
      <Grid>
        <Grid.Col span={{ base: 12, sm: 6 }}>
          <Paper
            p="xl"
            radius="md"
            style={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              cursor: "pointer",
              transition: "transform 0.2s",
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = "scale(1.02)"}
            onMouseLeave={(e) => e.currentTarget.style.transform = "scale(1)"}
            onClick={() => navigate("/income")}
          >
            <Stack gap="xs">
              <Text size="lg" opacity={0.9}>Revenue</Text>
              <Title order={1} size="2.5rem">{formatCurrency(data.income)}</Title>
            </Stack>
          </Paper>
          <Button
            fullWidth
            mt="xs"
            variant="light"
            color="violet"
            onClick={() => navigate("/income")}
          >
            📈 View Revenue Details
          </Button>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6 }}>
          <Paper
            p="xl"
            radius="md"
            style={{
              background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
              color: "white",
              cursor: "pointer",
              transition: "transform 0.2s",
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = "scale(1.02)"}
            onMouseLeave={(e) => e.currentTarget.style.transform = "scale(1)"}
            onClick={() => navigate("/expense")}
          >
            <Stack gap="xs">
              <Text size="lg" opacity={0.9}>Expense</Text>
              <Title order={1} size="2.5rem">{formatCurrency(data.expense)}</Title>
            </Stack>
          </Paper>
          <Button
            fullWidth
            mt="xs"
            variant="light"
            color="pink"
            onClick={() => navigate("/expense")}
          >
            📉 View Expense Details
          </Button>
        </Grid.Col>
      </Grid>

      {/* Net Profit */}
      <Paper
        p="md"
        radius="md"
        style={{
          background: `rgba(${data.profit >= 0 ? "16, 185, 129" : "239, 68, 68"}, 0.1)`,
          border: `2px solid ${profitColor}`,
          textAlign: "center"
        }}
      >
        <Text fw={600} size="lg" style={{ color: profitColor }}>
          Net Profit: {formatCurrency(data.profit)}
        </Text>
      </Paper>

      {/* Main Monthly Trends Overview */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <Group justify="space-between">
            <Title order={3}>📈 Monthly Trends Overview</Title>
            <MonthRangeFilter value={mainRange} onChange={setMainRange} defaultMonths={3} />
          </Group>

          {mainTrends.isLoading ? (
            <LoadingState message="Loading trends..." />
          ) : mainTrends.isError ? (
            <ErrorState message="Failed to load trends" onRetry={() => mainTrends.refetch()} />
          ) : (
            <>
              {/* Custom Horizontal Legend */}
              <Group justify="center" gap="xl" mb="sm">
                <Group gap={8}>
                  <Box w={12} h={12} bg="#3b82f6" style={{ borderRadius: '50%' }} />
                  <Text size="sm" fw={500}>Revenue</Text>
                </Group>
                <Group gap={8}>
                  <Box w={12} h={12} bg="#f97316" style={{ borderRadius: '50%' }} />
                  <Text size="sm" fw={500}>Expense</Text>
                </Group>
                <Group gap={8}>
                  <Box w={12} h={12} bg="#10b981" style={{ borderRadius: '50%' }} />
                  <Text size="sm" fw={500}>Profit</Text>
                </Group>
              </Group>

              <Box h={400}>
                <LineChart
                  h={380}
                  data={mainChartData}
                  dataKey="month"
                  series={[
                    { name: "Revenue", color: "#3b82f6" },
                    { name: "Expense", color: "#f97316" },
                    { name: "Profit", color: "#10b981" }
                  ]}
                  curveType="monotone"
                  withLegend={false}
                  yAxisProps={{
                    width: getYAxisWidth(mainChartData.flatMap(d => [d.Revenue, d.Expense, d.Profit]))
                  }}
                  valueFormatter={(value) => formatCurrency(value as number)}
                  tooltipProps={{
                    content: ({ label, payload }) => {
                      if (!payload || payload.length === 0) return null;
                      return (
                        <Paper px="md" py="sm" withBorder shadow="md" radius="md" style={{ backgroundColor: "white" }}>
                          <Text fw={500} mb={5}>{label}</Text>
                          {payload.map((item: any) => (
                            <Text key={item.name} size="sm" style={{ color: item.color }}>
                              {item.name}: {formatCurrency(item.value)}
                            </Text>
                          ))}
                        </Paper>
                      );
                    }
                  }}
                />
              </Box>
            </>
          )}
        </Stack>
      </Paper>

      {/* Three Individual Trend Graphs */}
      <Grid>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Stack gap="md" h="100%">
            <Group justify="space-between">
              <Title order={4}>📈 Profit Trend</Title>
              <MonthRangeFilter value={profitRange} onChange={setProfitRange} defaultMonths={3} />
            </Group>
            {profitTrends.isLoading ? (
              <LoadingState message="Loading..." />
            ) : profitTrends.isError ? (
              <ErrorState message="Failed to load" onRetry={() => profitTrends.refetch()} />
            ) : (
              <TrendChart
                data={profitTrends.data?.trends || []}
                dataKey="profit"
                title="Profit"
                color="#10b981"
                height={300}
              />
            )}
          </Stack>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Stack gap="md" h="100%">
            <Group justify="space-between">
              <Title order={4}>📉 Expense Trend</Title>
              <MonthRangeFilter value={expenseRange} onChange={setExpenseRange} defaultMonths={3} />
            </Group>
            {expenseTrends.isLoading ? (
              <LoadingState message="Loading..." />
            ) : expenseTrends.isError ? (
              <ErrorState message="Failed to load" onRetry={() => expenseTrends.refetch()} />
            ) : (
              <TrendChart
                data={expenseTrends.data?.trends || []}
                dataKey="expense"
                title="Expense"
                color="#f97316"
                height={300}
              />
            )}
          </Stack>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Stack gap="md" h="100%">
            <Group justify="space-between">
              <Title order={4}>💰 Revenue Trend</Title>
              <MonthRangeFilter value={incomeRange} onChange={setIncomeRange} defaultMonths={3} />
            </Group>
            {incomeTrends.isLoading ? (
              <LoadingState message="Loading..." />
            ) : incomeTrends.isError ? (
              <ErrorState message="Failed to load" onRetry={() => incomeTrends.refetch()} />
            ) : (
              <TrendChart
                data={incomeTrends.data?.trends || []}
                dataKey="income"
                title="Revenue"
                color="#3b82f6"
                height={300}
              />
            )}
          </Stack>
        </Grid.Col>
      </Grid>

      {/* Quick Stats and Monthly Expenses */}
      <Grid>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper p="md" radius="md" withBorder h="100%">
            <Stack gap="md">
              <Title order={4}>📊 Quick Stats</Title>
              <div>
                <Text size="sm" c="dimmed">💰 Cash Balance</Text>
                <Text size="xl" fw={700}>{formatCurrency(data.cash_balance)}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">📈 Total Revenue</Text>
                <Text size="xl" fw={700}>{formatCurrency(data.total_revenue)}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">📉 Total Expenses</Text>
                <Text size="xl" fw={700}>{formatCurrency(data.total_expenses)}</Text>
              </div>
              <div>
                <Text size="sm" c="dimmed">💵 Net Profit</Text>
                <Text size="xl" fw={700}>
                  {formatCurrency(data.net_profit)}
                </Text>
                <Badge
                  color={data.net_profit >= 0 ? "green" : "red"}
                  variant="light"
                  mt="xs"
                >
                  {((data.net_profit / data.total_revenue) * 100).toFixed(1)}%
                </Badge>
              </div>
            </Stack>
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 8 }}>
          <Paper p="md" radius="md" withBorder h="100%">
            <Stack gap="md">
              <Title order={4}>📅 Monthly Expenses</Title>
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Month</Table.Th>
                    <Table.Th style={{ textAlign: "right" }}>Total Expense</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {data.monthly_expenses.map((item, index) => (
                    <Table.Tr key={index}>
                      <Table.Td>{item.month}</Table.Td>
                      <Table.Td style={{ textAlign: "right", fontWeight: 600 }}>
                        {formatCurrency(item.total_expense)}
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>

      {/* Footer */}
      <Paper p="xs" radius="md" withBorder>
        <Text size="xs" c="dimmed" ta="center">
          📁 File: {data.meta.file_name} | 📄 Sheet: {data.meta.sheet} |
          📊 Rows: {data.meta.rows} | 🕒 Last modified: {new Date(data.meta.modified_at).toLocaleString()}
        </Text>
      </Paper>
    </Stack>
  );
}
