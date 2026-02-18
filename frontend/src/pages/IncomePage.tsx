import { ActionIcon, Anchor, Badge, Box, Group, Paper, ScrollArea, SegmentedControl, Stack, Table, Text, Title } from "@mantine/core";
import { BarChart } from "@mantine/charts";
import { IconArrowDown, IconArrowUp, IconArrowsSort } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useIncome, useProfitByCostCenter, useProfitByClient } from "../api/hooks";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { getYAxisWidth, formatCurrency } from "../utils/chartHelpers";

interface IncomePageProps {
  departmentKey?: string | null;
}

export function IncomePage({ departmentKey }: IncomePageProps) {
  const query = useIncome(departmentKey);
  const profitMatrixQuery = useProfitByCostCenter(departmentKey);
  const [clientSort, setClientSort] = useState<"asc" | "desc">("desc");
  const [clientSortBy, setClientSortBy] = useState<"total" | "deviation">("total");
  const profitByClientQuery = useProfitByClient(departmentKey, 20, clientSort, clientSortBy);
  const [sortBy, setSortBy] = useState<"amount" | "variance" | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  const handleClientSort = (column: "total" | "deviation") => {
    if (clientSortBy === column) {
      setClientSort(clientSort === "asc" ? "desc" : "asc");
    } else {
      setClientSortBy(column);
      setClientSort("desc");
    }
  };

  const getClientSortIcon = (column: "total" | "deviation") => {
    if (clientSortBy !== column) return <IconArrowsSort size={14} />;
    return clientSort === "asc" ? <IconArrowUp size={14} /> : <IconArrowDown size={14} />;
  };

  const items = useMemo(() => {
    const rawItems = query.data?.items || [];
    if (!sortBy) return rawItems;
    return [...rawItems].sort((a, b) => {
      const aVal = sortBy === "amount" ? a.current_amount : a.variance_pct;
      const bVal = sortBy === "amount" ? b.current_amount : b.variance_pct;
      return sortDirection === "asc" ? aVal - bVal : bVal - aVal;
    });
  }, [query.data?.items, sortBy, sortDirection]);

  if (query.isLoading) return <LoadingState message="Loading revenue details" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const { total_income, current_month } = query.data;

  const formatVariance = (variance: number) => `${variance > 0 ? "+" : ""}${variance.toFixed(1)}%`;

  const getVarianceColor = (variance: number) => {
    // For income, increase is good (green), decrease is bad (red)
    if (variance > 0) return "green";
    if (variance < 0) return "red";
    return "gray";
  };

  const getProfitColor = (profit: number): string => {
    if (profit > 0) return "#d4edda";
    if (profit < 0) return "#f8d7da";
    return "transparent";
  };

  const getProfitTextColor = (profit: number): string => {
    if (profit > 0) return "#155724";
    if (profit < 0) return "#721c24";
    return "inherit";
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
            Total Revenue - {current_month}
          </Text>
          <Title order={1} size="3.5rem">
            {formatCurrency(total_income)}
          </Title>
        </Stack>
      </Paper>

      {/* Monthly Profit by Cost Center Matrix */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <div>
            <Title order={3}>📊 Monthly Profit by Cost Center</Title>
            <Text size="sm" c="dimmed">Profit breakdown for current year</Text>
          </div>

          {profitMatrixQuery.isLoading ? (
            <LoadingState message="Loading profit matrix..." />
          ) : profitMatrixQuery.isError ? (
            <ErrorState message="Failed to load profit matrix" onRetry={() => profitMatrixQuery.refetch()} />
          ) : profitMatrixQuery.data?.matrix && profitMatrixQuery.data.matrix.length > 0 ? (
            <ScrollArea>
              <Table striped highlightOnHover style={{ minWidth: 800 }}>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th style={{ position: "sticky", left: 0, background: "white", zIndex: 1 }}>
                      Cost Center
                    </Table.Th>
                    {profitMatrixQuery.data.month_labels.map((label, idx) => (
                      <Table.Th key={idx} style={{ textAlign: "right" }}>{label}</Table.Th>
                    ))}
                    <Table.Th style={{ textAlign: "right", fontWeight: "bold" }}>Total</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {profitMatrixQuery.data.matrix.map((row, rowIdx) => (
                    <Table.Tr key={rowIdx}>
                      <Table.Td
                        style={{
                          position: "sticky",
                          left: 0,
                          background: "white",
                          zIndex: 1,
                          fontWeight: 500
                        }}
                      >
                        {row.cost_center}
                      </Table.Td>
                      {Object.keys(row.months).sort().map((month, monthIdx) => {
                        const profit = row.months[month];
                        return (
                          <Table.Td
                            key={monthIdx}
                            style={{
                              textAlign: "right",
                              backgroundColor: getProfitColor(profit),
                              color: getProfitTextColor(profit),
                              fontWeight: profit !== 0 ? 600 : 400
                            }}
                          >
                            {formatCurrency(profit)}
                          </Table.Td>
                        );
                      })}
                      <Table.Td
                        style={{
                          textAlign: "right",
                          fontWeight: "bold",
                          backgroundColor: getProfitColor(row.total),
                          color: getProfitTextColor(row.total)
                        }}
                      >
                        {formatCurrency(row.total)}
                      </Table.Td>
                    </Table.Tr>
                  ))}

                  {/* Total Row */}
                  <Table.Tr style={{ fontWeight: "bold", borderTop: "2px solid #dee2e6" }}>
                    <Table.Td style={{ position: "sticky", left: 0, background: "white", zIndex: 1 }}>
                      TOTAL
                    </Table.Td>
                    {Object.keys(profitMatrixQuery.data.monthly_totals).sort().map((month, idx) => {
                      const total = profitMatrixQuery.data.monthly_totals[month];
                      return (
                        <Table.Td
                          key={idx}
                          style={{
                            textAlign: "right",
                            backgroundColor: getProfitColor(total),
                            color: getProfitTextColor(total)
                          }}
                        >
                          {formatCurrency(total)}
                        </Table.Td>
                      );
                    })}
                    <Table.Td style={{ textAlign: "right" }}>
                      {formatCurrency(
                        profitMatrixQuery.data.matrix.reduce((sum, row) => sum + row.total, 0)
                      )}
                    </Table.Td>
                  </Table.Tr>
                </Table.Tbody>
              </Table>
            </ScrollArea>
          ) : (
            <Text c="dimmed" ta="center" py="xl">No profit data available</Text>
          )}
        </Stack>
      </Paper>

      {/* Monthly Profit by Client Matrix */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <Group justify="space-between" align="center">
            <div>
              <Title order={3}>📊 Monthly Profit by Client</Title>
              <Text size="sm" c="dimmed">
                Top 20 clients by {clientSort === "desc" ? "Profit" : "Loss"}. (Profit = Revenue - Expense).
              </Text>
            </div>
            <SegmentedControl
              value={clientSortBy === "total" ? clientSort : null}
              onChange={(value) => {
                setClientSortBy("total");
                setClientSort(value as "asc" | "desc");
              }}
              data={[
                { label: 'Highest Profit', value: 'desc' },
                { label: 'Biggest Loss', value: 'asc' },
              ]}
            />
          </Group>

          {profitByClientQuery.isLoading ? (
            <LoadingState message="Loading client data..." />
          ) : profitByClientQuery.data && profitByClientQuery.data.matrix.length > 0 ? (
            <ScrollArea>
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th style={{ position: "sticky", left: 0, background: "white", zIndex: 1 }}>
                      Client
                    </Table.Th>
                    <Table.Th
                      style={{ textAlign: "right", cursor: "pointer", whiteSpace: "nowrap" }}
                      onClick={() => handleClientSort("deviation")}
                    >
                      <Group gap={4} justify="flex-end">
                        {profitByClientQuery.data.deviation_label || "Deviation"}
                        {getClientSortIcon("deviation")}
                      </Group>
                    </Table.Th>
                    {profitByClientQuery.data.month_labels.map((month, idx) => (
                      <Table.Th key={idx} style={{ textAlign: "right" }}>{month}</Table.Th>
                    ))}
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {profitByClientQuery.data.matrix.map((row) => (
                    <Table.Tr key={row.client}>
                      <Table.Td style={{ position: "sticky", left: 0, background: "white", zIndex: 1, fontWeight: 500 }}>
                        {row.client}
                      </Table.Td>
                      {/* Deviation Column (First) */}
                      <Table.Td
                        style={{
                          textAlign: "right",
                          fontWeight: 600,
                          color: row.deviation !== undefined ? (row.deviation > 0 ? "#155724" : row.deviation < 0 ? "#721c24" : "inherit") : "inherit",
                          backgroundColor: row.deviation !== undefined ? (row.deviation > 0 ? "#d4edda" : row.deviation < 0 ? "#f8d7da" : "transparent") : "transparent"
                        }}
                      >
                        {row.deviation !== undefined ? formatCurrency(row.deviation) : "-"}
                      </Table.Td>
                      {profitByClientQuery.data.month_labels.map((month) => {
                        const profit = row.months[month] || 0;
                        return (
                          <Table.Td
                            key={month}
                            style={{
                              textAlign: "right",
                              backgroundColor: getProfitColor(profit),
                              color: getProfitTextColor(profit)
                            }}
                          >
                            {formatCurrency(profit)}
                          </Table.Td>
                        );
                      })}
                    </Table.Tr>
                  ))}

                  {/* Total Row */}
                  <Table.Tr style={{ fontWeight: "bold", borderTop: "2px solid #dee2e6" }}>
                    <Table.Td style={{ position: "sticky", left: 0, background: "white", zIndex: 1 }}>
                      TOTAL (Top {profitByClientQuery.data.matrix.length})
                    </Table.Td>
                    {/* Empty cell for Deviation total */}
                    <Table.Td style={{ textAlign: "right" }}>-</Table.Td>
                    {profitByClientQuery.data.month_labels.map((month, idx) => {
                      const total = profitByClientQuery.data.monthly_totals[month] || 0;
                      return (
                        <Table.Td
                          key={idx}
                          style={{
                            textAlign: "right",
                            backgroundColor: getProfitColor(total),
                            color: getProfitTextColor(total)
                          }}
                        >
                          {formatCurrency(total)}
                        </Table.Td>
                      );
                    })}
                  </Table.Tr>
                </Table.Tbody>
              </Table>
            </ScrollArea>
          ) : (
            <Text c="dimmed" ta="center" py="xl">No client profit data available</Text>
          )}
        </Stack>
      </Paper>

      {/* Income Breakdown by Ledger Table */}
      <Paper p="md" radius="md" withBorder>
        <Stack gap="md">
          <div>
            <Title order={3}>📊 Revenue Breakdown by Ledger</Title>
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
      </Paper >

      {/* Chart */}
      < Paper p="md" radius="md" withBorder >
        <Stack gap="md">
          <Title order={4}>Top 10 Revenue Sources</Title>
          <Box h={400} className="chart-container">
            <BarChart
              h={380}
              data={chartData}
              dataKey="ledger"
              series={[{ name: "amount", label: "Amount", color: "violet" }]}
              tickLine="y"
              orientation="horizontal"
              yAxisProps={{
                width: getYAxisWidth(top10.map(i => i.current_amount))
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
      </Paper >

      {/* Summary Stats */}
      < Paper p="md" radius="md" withBorder >
        <Stack gap="md">
          <Title order={4}>📊 Summary Statistics</Title>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
            <div>
              <Text size="sm" c="dimmed">Total Revenue Ledgers</Text>
              <Text size="xl" fw={700}>{items.length}</Text>
            </div>
            <div>
              <Text size="sm" c="dimmed">Average per Ledger</Text>
              <Text size="xl" fw={700}>
                {formatCurrency(items.reduce((sum, item) => sum + item.current_amount, 0) / items.length || 0)}
              </Text>
            </div>
            <div>
              <Text size="sm" c="dimmed">Highest Revenue Source</Text>
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
      </Paper >
    </Stack >
  );
}
