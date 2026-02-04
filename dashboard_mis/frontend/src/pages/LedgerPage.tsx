import { Button, Grid, Group, Paper, Select, Stack, Table, Text } from "@mantine/core";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";
import { useLedger, useLedgers } from "../api/hooks";
import { ChartCard } from "../components/ChartCard";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";

export function LedgerPage() {
  const ledgersQuery = useLedgers();
  const [selected, setSelected] = useState<string | null>(null);
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);

  useEffect(() => {
    if (!selected && ledgersQuery.data && ledgersQuery.data.length) {
      setSelected(ledgersQuery.data[0]);
    }
  }, [selected, ledgersQuery.data]);

  const params = useMemo(() => {
    const [start, end] = range;
    return {
      name: selected || "",
      start: start ? dayjs(start).format("YYYY-MM-DD") : undefined,
      end: end ? dayjs(end).format("YYYY-MM-DD") : undefined
    };
  }, [selected, range]);

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
          <ChartCard title="Running Balance" option={balanceOption} height={320} />
        </Grid.Col>
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
