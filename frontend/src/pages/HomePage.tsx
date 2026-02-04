import { Badge, Box, Button, Grid, Paper, Stack, Table, Text, Title } from "@mantine/core";
import { LineChart } from "@mantine/charts";
import { useNavigate } from "react-router-dom";
import { useHome } from "../api/hooks";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";

export function HomePage() {
  const query = useHome();
  const navigate = useNavigate();

  if (query.isLoading) return <LoadingState message="Loading dashboard" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const data = query.data;
  const formatCurrency = (amount: number) => `₹${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

  const profitColor = data.profit >= 0 ? "#10b981" : "#ef4444";

  // Chart data
  const chartData = data.daily_profit.map((item: any) => ({
    date: new Date(item.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }),
    Income: item.income,
    Expense: item.expense,
    Profit: item.profit
  }));

  return (
    <Stack gap="md">
      {/* Header */}
      <Title order={2}>💰 Profit by Month - {data.current_month}</Title>

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
              <Text size="lg" opacity={0.9}>Income</Text>
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
            📈 View Income Details
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

      {/* Graph and Quick Stats */}
      <Grid>
        <Grid.Col span={{ base: 12, md: 8 }}>
          <Paper p="md" radius="md" withBorder>
            <Stack gap="md">
              <Title order={3}>📈 Graph of Current Month</Title>
              <Box h={400}>
                <LineChart
                  h={380}
                  data={chartData}
                  dataKey="date"
                  series={[
                    { name: "Income", color: "violet" },
                    { name: "Expense", color: "pink" },
                    { name: "Profit", color: "teal" }
                  ]}
                  curveType="linear"
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
            </Stack>
          </Paper>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper p="md" radius="md" withBorder>
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
      </Grid>

      {/* Monthly Expenses */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <Title order={3}>📅 Monthly Expenses</Title>
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
