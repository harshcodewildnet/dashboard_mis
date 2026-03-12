import { useState } from "react";
import { Badge, Box, Button, Grid, Group, Paper, Stack, Table, Text, Title, ActionIcon, rem, Card, Divider } from "@mantine/core";
import { LineChart } from "@mantine/charts";
import { IconArrowUpRight, IconArrowDownRight, IconChartLine, IconCreditCard, IconReceipt, IconTrendingUp, IconCalendar } from "@tabler/icons-react";
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
    <Stack gap="xl">
      {/* Header */}
      <Group justify="space-between" align="flex-end">
        <Stack gap={4}>
          <Text size="sm" fw={600} c="indigo.6" style={{ textTransform: 'uppercase', letterSpacing: rem(1) }}>
            Executive Overview
          </Text>
          <Title order={1} size="h2" fw={800}>
            Financial Dashboard <Text span c="dimmed" fw={500} size="lg">— {data.current_month}</Text>
          </Title>
        </Stack>
        <Group gap="xs">
          <Badge variant="dot" size="lg" color="green">Live Data</Badge>
          <Text size="xs" c="dimmed" fw={500}>Last updated: {new Date().toLocaleTimeString()}</Text>
        </Group>
      </Group>

      {/* Primary KPI Cards */}
      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, sm: 6, lg: 4 }}>
          <Card
            p="xl"
            radius="lg"
            style={{
              background: "linear-gradient(45deg, var(--mantine-color-indigo-7) 0%, var(--mantine-color-indigo-9) 100%)",
              color: "white",
              overflow: 'hidden',
              position: 'relative'
            }}
          >
            <Box style={{ position: 'absolute', top: rem(-20), right: rem(-20), opacity: 0.15 }}>
              <IconTrendingUp size={rem(140)} />
            </Box>
            <Stack gap="md" style={{ position: 'relative', zIndex: 1 }}>
              <Group justify="space-between">
                <Text size="sm" fw={600} style={{ opacity: 0.8, textTransform: 'uppercase' }}>Total Revenue</Text>
                <ActionIcon variant="transparent" color="white" onClick={() => navigate("/income")}>
                  <IconArrowUpRight size={20} />
                </ActionIcon>
              </Group>
              <Title order={1} size="2.5rem" fw={800}>{formatCurrency(data.income)}</Title>
              <Button 
                variant="white" 
                color="indigo" 
                fullWidth 
                radius="md" 
                size="sm"
                onClick={() => navigate("/income")}
                leftSection={<IconChartLine size={16} />}
              >
                Revenue Details
              </Button>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6, lg: 4 }}>
          <Card
            p="xl"
            radius="lg"
            style={{
              background: "linear-gradient(45deg, var(--mantine-color-pink-6) 0%, var(--mantine-color-red-8) 100%)",
              color: "white",
              overflow: 'hidden',
              position: 'relative'
            }}
          >
            <Box style={{ position: 'absolute', top: rem(-20), right: rem(-20), opacity: 0.15 }}>
              <IconReceipt size={rem(140)} />
            </Box>
            <Stack gap="md" style={{ position: 'relative', zIndex: 1 }}>
              <Group justify="space-between">
                <Text size="sm" fw={600} style={{ opacity: 0.8, textTransform: 'uppercase' }}>Total Expenses</Text>
                <ActionIcon variant="transparent" color="white" onClick={() => navigate("/expense")}>
                  <IconArrowDownRight size={20} />
                </ActionIcon>
              </Group>
              <Title order={1} size="2.5rem" fw={800}>{formatCurrency(data.expense)}</Title>
              <Button 
                variant="white" 
                color="pink" 
                fullWidth 
                radius="md" 
                size="sm"
                onClick={() => navigate("/expense")}
                leftSection={<IconReceipt size={16} />}
              >
                Expense Analysis
              </Button>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, lg: 4 }}>
          <Paper p="xl" radius="lg" withBorder shadow="md">
            <Stack gap="md">
              <Group justify="space-between">
                <Text size="sm" fw={600} c="dimmed" style={{ textTransform: 'uppercase' }}>Net Profit Margins</Text>
                <Badge color={data.profit >= 0 ? "green" : "red"} variant="light" size="lg" radius="sm">
                  {((data.profit / data.income) * 100).toFixed(1)}% margin
                </Badge>
              </Group>
              <Title order={1} size="2.5rem" fw={800} c={data.profit >= 0 ? "green.7" : "red.7"}>
                {formatCurrency(data.profit)}
              </Title>
              <Divider label="Cash Liquidity" labelPosition="center" />
              <Group justify="space-between">
                <Text size="sm" fw={600} c="dimmed">Cash Balance</Text>
                <Text fw={700} size="lg">{formatCurrency(data.cash_balance)}</Text>
              </Group>
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>

      {/* Main Monthly Trends Overview */}
      <Paper p="xl" radius="lg" withBorder shadow="sm">
        <Stack gap="lg">
          <Group justify="space-between" wrap="nowrap">
            <Group gap="sm">
              <ActionIcon variant="light" color="indigo" size="lg" radius="md">
                <IconChartLine size={20} />
              </ActionIcon>
              <div>
                <Text fw={700} size="lg">Monthly Performance Trends</Text>
                <Text size="xs" c="dimmed">Comparative analysis of financial movement</Text>
              </div>
            </Group>
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
      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Stack gap="md">
            <Group justify="space-between">
              <Group gap="xs">
                <IconTrendingUp size={18} color="var(--mantine-color-green-6)" />
                <Text fw={600} size="sm">Profit Velocity</Text>
              </Group>
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
                color="var(--mantine-color-green-5)"
                height={260}
              />
            )}
          </Stack>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Stack gap="md">
            <Group justify="space-between">
              <Group gap="xs">
                <IconReceipt size={18} color="var(--mantine-color-orange-6)" />
                <Text fw={600} size="sm">Expense Flow</Text>
              </Group>
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
                color="var(--mantine-color-orange-5)"
                height={260}
              />
            )}
          </Stack>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Stack gap="md">
            <Group justify="space-between">
              <Group gap="xs">
                <IconChartLine size={18} color="var(--mantine-color-blue-6)" />
                <Text fw={600} size="sm">Revenue Growth</Text>
              </Group>
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
                color="var(--mantine-color-blue-5)"
                height={260}
              />
            )}
          </Stack>
        </Grid.Col>
      </Grid>

      {/* Quick Stats and Monthly Expenses */}
      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper p="xl" radius="lg" withBorder h="100%" shadow="sm">
            <Stack gap="lg">
              <Group gap="xs">
                <ActionIcon color="indigo" variant="light"><IconCreditCard size={18} /></ActionIcon>
                <Text fw={700}>Financial Summary</Text>
              </Group>
              
              <Stack gap="xs">
                <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Available Liquidity</Text>
                <Text size="xl" fw={800}>{formatCurrency(data.cash_balance)}</Text>
              </Stack>

              <Stack gap="xs">
                <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Gross Revenue</Text>
                <Text size="xl" fw={800}>{formatCurrency(data.total_revenue)}</Text>
              </Stack>

              <Stack gap="xs">
                <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Total Burn</Text>
                <Text size="xl" fw={800}>{formatCurrency(data.total_expenses)}</Text>
              </Stack>

              <Stack gap="xs">
                <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Net Yield</Text>
                <Group justify="space-between">
                  <Text size="xl" fw={800} c={data.net_profit >= 0 ? "green.6" : "red.6"}>
                    {formatCurrency(data.net_profit)}
                  </Text>
                  <Badge
                    color={data.net_profit >= 0 ? "green" : "red"}
                    variant="filled"
                    size="lg"
                  >
                    {((data.net_profit / data.total_revenue) * 100).toFixed(1)}%
                  </Badge>
                </Group>
              </Stack>
            </Stack>
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 8 }}>
          <Paper p="xl" radius="lg" withBorder h="100%" shadow="sm">
            <Stack gap="lg">
              <Group justify="space-between">
                <Group gap="xs">
                  <ActionIcon color="orange" variant="light"><IconCalendar size={18} /></ActionIcon>
                  <Text fw={700}>Expense History</Text>
                </Group>
                <Badge variant="light" color="orange">Past 6 Months</Badge>
              </Group>
              <Table verticalSpacing="md" highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th style={{ color: 'var(--mantine-color-dimmed)', fontSize: rem(12), textTransform: 'uppercase' }}>Month</Table.Th>
                    <Table.Th style={{ textAlign: "right", color: 'var(--mantine-color-dimmed)', fontSize: rem(12), textTransform: 'uppercase' }}>Total Expenditure</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {data.monthly_expenses.map((item, index) => (
                    <Table.Tr key={index}>
                      <Table.Td fw={600}>{item.month}</Table.Td>
                      <Table.Td style={{ textAlign: "right" }}>
                        <Text fw={700} c="slate.8">{formatCurrency(item.total_expense)}</Text>
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
