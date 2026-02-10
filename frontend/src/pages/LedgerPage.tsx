import { BarChart } from "@mantine/charts";
import { Button, Grid, Group, Paper, Select, Stack, Table, Text } from "@mantine/core";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useLedger, useLedgers } from "../api/hooks";
import { ChartCard } from "../components/ChartCard";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";

interface LedgerPageProps {
  departmentKey?: string | null;
}

export function LedgerPage({ departmentKey }: LedgerPageProps) {
  const [searchParams] = useSearchParams();
  const ledgersQuery = useLedgers(departmentKey);
  const [selected, setSelected] = useState<string | null>(null);
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);

  const formatCurrency = (amount: number) => `₹${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  const formatVariance = (variance: number) => `${variance > 0 ? "+" : ""}${variance.toFixed(1)}%`;

  const getVarianceColor = (variance: number) => {
    if (variance > 0) return "red.6";
    if (variance < 0) return "green.6";
    return "gray.6";
  };

  // Reset selected ledger when department changes
  useEffect(() => {
    setSelected(null);
  }, [departmentKey]);

  // Auto-select ledger from URL query parameter or default to first ledger
  useEffect(() => {
    const ledgerFromUrl = searchParams.get("name");

    if (ledgerFromUrl && ledgersQuery.data) {
      // If URL has a ledger name and it exists in the list, select it
      const ledgerExists = ledgersQuery.data.includes(ledgerFromUrl);
      if (ledgerExists) {
        setSelected(ledgerFromUrl);
      } else if (!selected && ledgersQuery.data.length) {
        // If ledger from URL doesn't exist, fall back to first ledger
        setSelected(ledgersQuery.data[0]);
      }
    } else if (!selected && ledgersQuery.data && ledgersQuery.data.length) {
      // No URL parameter, select first ledger
      setSelected(ledgersQuery.data[0]);
    }
  }, [searchParams, selected, ledgersQuery.data]);

  const params = useMemo(() => {
    const [start, end] = range;
    return {
      name: selected || "",
      start: start ? dayjs(start).format("YYYY-MM-DD") : undefined,
      end: end ? dayjs(end).format("YYYY-MM-DD") : undefined,
      departmentKey
    };
  }, [selected, range, departmentKey]);

  const ledgerQuery = useLedger(params);

  const loading = ledgersQuery.isLoading || ledgerQuery.isLoading;
  if (loading) return <LoadingState message="Loading ledger" />;
  if (ledgersQuery.isError) return <ErrorState message={(ledgersQuery.error as Error).message} onRetry={() => ledgersQuery.refetch()} />;
  if (ledgerQuery.isError) return <ErrorState message={(ledgerQuery.error as Error).message} onRetry={() => ledgerQuery.refetch()} />;
  if (!ledgerQuery.data || !ledgersQuery.data) return null;

  const data = ledgerQuery.data;
  const balanceOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.running_balance.map((r) => dayjs(r.date).format("YYYY-MM-DD")) },
    yAxis: { type: "value" },
    series: [
      {
        type: "line",
        data: data.running_balance.map((r) => r.running_balance),
        smooth: true,
        areaStyle: {},
        color: "#0ea5e9"
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 48 }
  };

  return (
    <Stack gap="md">
      <Group justify="space-between" align="center">
        <div>
          <Text fw={700} fz="xl">
            Ledger Explorer
          </Text>
          <Text c="dimmed" size="sm">
            {data.meta.file_name}
          </Text>
        </div>
        <Group gap="md">
          <Select
            label="Ledger"
            data={ledgersQuery.data.map((l) => ({ label: l, value: l }))}
            value={selected}
            onChange={setSelected}
            searchable
            nothingFoundMessage="No ledger"
            w={240}
          />
          <DateRangePicker value={range} onChange={setRange} />
        </Group>
      </Group>

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Paper withBorder radius="lg" p="md">
            <Stack gap={8}>
              <Text fw={600}>Balances</Text>
              <Text size="sm">Opening: {data.opening.toLocaleString(undefined, { maximumFractionDigits: 2 })}</Text>
              <Text size="sm">Movement: {data.period_total.toLocaleString(undefined, { maximumFractionDigits: 2 })}</Text>
              <Text size="sm">Closing: {data.closing.toLocaleString(undefined, { maximumFractionDigits: 2 })}</Text>
              <Button variant="light" size="xs" onClick={() => ledgerQuery.refetch()}>
                Refresh
              </Button>
            </Stack>
          </Paper>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 8 }}>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 8 }}>
          <ChartCard title="Running Balance" option={balanceOption} height={320} />
        </Grid.Col>

        {data.department_breakdown && (
          <Grid.Col span={12}>
            <Paper withBorder radius="lg" p="md">
              <Text fw={600} mb="md">
                Department Breakdown (Current Month)
              </Text>
              <div className="chart-container">
                <BarChart
                  h={300}
                  data={data.department_breakdown}
                  dataKey="label"
                  type="default"
                  series={[
                    { name: "current", color: "blue.6", label: "Current Month" },
                    { name: "previous", color: "gray.5", label: "Previous Month" }
                  ]}
                  tickLine="xy"
                  gridAxis="xy"
                  tooltipAnimationDuration={200}
                  withTooltip
                  barProps={{ activeBar: false }}
                  tooltipProps={{
                    content: ({ label, payload }) => {
                      if (!payload || payload.length === 0) return null;
                      // We expect payload to have data from the item
                      // payload[0].payload contains the full data object (current, previous, variance)
                      const item = payload[0].payload;

                      return (
                        <Paper px="md" py="sm" withBorder shadow="md" radius="md">
                          <Text fw={600} size="sm" mb={4} style={{ borderBottom: "1px solid #eee", paddingBottom: 4 }}>
                            {label}
                          </Text>
                          <Group justify="space-between" gap="xl" mb={4}>
                            <Text size="xs" c="dimmed">Current</Text>
                            <Text size="sm" fw={600} c="blue.7">{formatCurrency(item.current)}</Text>
                          </Group>
                          <Group justify="space-between" gap="xl" mb={4}>
                            <Text size="xs" c="dimmed">Previous</Text>
                            <Text size="sm" fw={500} c="gray.6">{formatCurrency(item.previous)}</Text>
                          </Group>
                          <Group justify="space-between" gap="xl" pt={4} style={{ borderTop: "1px dashed #eee" }}>
                            <Text size="xs" c="dimmed">Variance</Text>
                            <Text size="sm" fw={700} c={getVarianceColor(item.variance)}>
                              {formatVariance(item.variance)}
                            </Text>
                          </Group>
                        </Paper>
                      );
                    }
                  }}
                />
              </div>
            </Paper>
          </Grid.Col>
        )}
      </Grid>

      <Paper withBorder radius="lg" p="md">
        <Group justify="space-between" align="center" mb="sm">
          <Text fw={600}>Transactions</Text>
          <Text size="sm" c="dimmed">
            Showing {data.running_balance.length} rows
          </Text>
        </Group>
        <Table.ScrollContainer minWidth={700}>
          <Table highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Date</Table.Th>
                <Table.Th>Amount</Table.Th>
                <Table.Th>Running</Table.Th>
                <Table.Th>Description</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.running_balance.map((row, idx) => (
                <Table.Tr key={`${row.date}-${idx}`}>
                  <Table.Td>{dayjs(row.date).format("YYYY-MM-DD")}</Table.Td>
                  <Table.Td>{row.amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}</Table.Td>
                  <Table.Td>{row.running_balance.toLocaleString(undefined, { maximumFractionDigits: 2 })}</Table.Td>
                  <Table.Td>{row.description || ""}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>
    </Stack>
  );
}
