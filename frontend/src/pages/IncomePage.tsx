import { ActionIcon, Anchor, Badge, Box, Group, Paper, ScrollArea, Stack, Table, Text, Title } from "@mantine/core";
import { BarChart } from "@mantine/charts";
import { IconArrowDown, IconArrowUp, IconArrowsSort } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useIncome } from "../api/hooks";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";

interface IncomePageProps {
  departmentKey?: string | null;
}

export function IncomePage({ departmentKey }: IncomePageProps) {
  const query = useIncome(departmentKey);
  const [sortBy, setSortBy] = useState<"amount" | "variance" | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const items = useMemo(() => {
    const rawItems = query.data?.items || [];
    if (!sortBy) return rawItems;
    return [...rawItems].sort((a, b) => {
      const aVal = sortBy === "amount" ? a.current_amount : a.variance_pct;
      const bVal = sortBy === "amount" ? b.current_amount : b.variance_pct;
      return sortDirection === "asc" ? aVal - bVal : bVal - aVal;
    });
  }, [query.data?.items, sortBy, sortDirection]);

  if (query.isLoading) return <LoadingState message="Loading income details" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const { total_income, current_month } = query.data;

  const formatCurrency = (amount: number) => `₹${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  const formatVariance = (variance: number) => `${variance > 0 ? "+" : ""}${variance.toFixed(1)}%`;

  const getVarianceColor = (variance: number) => {
    // For income, increase is good (green), decrease is bad (red)
    if (variance > 0) return "green";
    if (variance < 0) return "red";
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
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white"
        }}
      >
        <Stack align="center" gap="xs">
          <Text size="xl" fw={500} opacity={0.9}>
            Total Income - {current_month}
          </Text>
          <Title order={1} size="3.5rem">
            {formatCurrency(total_income)}
          </Title>
        </Stack>
      </Paper>

      {/* Table */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <div>
            <Title order={3}>📊 Income Breakdown by Ledger</Title>
            <Text size="sm" c="dimmed">Comparison with previous month</Text>
          </div>

          <ScrollArea>
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Header</Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>
                    <Group gap="xs" justify="flex-end">
                      Amount
                      <ActionIcon
                        variant="subtle"
                        color="gray"
                        size="sm"
                        onClick={() => handleSort("amount")}
                      >
                        {getSortIcon("amount")}
                      </ActionIcon>
                    </Group>
                  </Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>
                    <Group gap="xs" justify="flex-end">
                      Variance %
                      <ActionIcon
                        variant="subtle"
                        color="gray"
                        size="sm"
                        onClick={() => handleSort("variance")}
                      >
                        {getSortIcon("variance")}
                      </ActionIcon>
                    </Group>
                  </Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>Previous Month</Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>2 Months Ago</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {items.map((item, index) => (
                  <Table.Tr key={index}>
                    <Table.Td>
                      <Anchor
                        component={Link}
                        to={`/ledger?name=${encodeURIComponent(item.ledger)}`}
                        underline="never"
                        c="inherit"
                        style={{ cursor: "pointer" }}
                      >
                        {item.ledger}
                      </Anchor>
                    </Table.Td>
                    <Table.Td style={{ textAlign: "right", fontWeight: 600 }}>
                      {formatCurrency(item.current_amount)}
                    </Table.Td>
                    <Table.Td style={{ textAlign: "right" }}>
                      <Badge color={getVarianceColor(item.variance_pct)} variant="light">
                        {formatVariance(item.variance_pct)}
                      </Badge>
                    </Table.Td>
                    <Table.Td style={{ textAlign: "right" }}>
                      {formatCurrency(item.previous_amount)}
                    </Table.Td>
                    <Table.Td style={{ textAlign: "right" }}>
                      {formatCurrency(item.two_months_ago_amount)}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </ScrollArea>
        </Stack>
      </Paper>

      {/* Chart */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <Title order={4}>Top 10 Income Sources</Title>
          <Box h={400} className="chart-container">
            <BarChart
              h={380}
              data={chartData}
              dataKey="ledger"
              series={[{ name: "amount", label: "Amount", color: "violet" }]}
              tickLine="y"
              orientation="horizontal"
              yAxisProps={{ width: 150 }}
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
                        <Text key={item.name} size="sm" c="violet.7">
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
              <Text size="sm" c="dimmed">Total Income Ledgers</Text>
              <Text size="xl" fw={700}>{items.length}</Text>
            </div>
            <div>
              <Text size="sm" c="dimmed">Average per Ledger</Text>
              <Text size="xl" fw={700}>
                {formatCurrency(items.reduce((sum, item) => sum + item.current_amount, 0) / items.length || 0)}
              </Text>
            </div>
            <div>
              <Text size="sm" c="dimmed">Highest Income Source</Text>
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
    </Stack>
  );
}
