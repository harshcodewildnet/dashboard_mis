import { ActionIcon, Badge, Button, Card, Divider, Grid, Group, Paper, Select, Stack, Table, Text, Title, rem } from "@mantine/core";
import { IconBook, IconTrendingUp, IconTrendingDown, IconBuildingBank, IconReplace, IconChartLine, IconListNumbers, IconInfoCircle } from "@tabler/icons-react";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useLedger, useLedgers } from "../api/hooks";
import { ChartCard } from "../components/ChartCard";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { getYAxisWidth, formatCurrency } from "../utils/chartHelpers";
import { BarChart } from "@mantine/charts";

interface LedgerPageProps {
  departmentKey?: string | null;
}

export function LedgerPage({ departmentKey }: LedgerPageProps) {
  const [searchParams] = useSearchParams();
  const ledgersQuery = useLedgers(departmentKey);
  const [selected, setSelected] = useState<string | null>(null);
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);
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
    grid: { left: getYAxisWidth(data.running_balance.map(r => r.running_balance)), right: 16, top: 32, bottom: 48 }
  };

  return (
    <Stack gap="xl">
      <Group justify="space-between" align="flex-end">
        <Stack gap={4}>
          <Text size="sm" fw={600} c="indigo.6" style={{ textTransform: 'uppercase', letterSpacing: rem(1) }}>
            Account Intelligence
          </Text>
          <Title order={1} size="h2" fw={800}>
            Ledger Explorer <Text span c="dimmed" fw={500} size="lg"> Analytics</Text>
          </Title>
        </Stack>
        <Group gap="md" align="flex-end">
          <Select
            label="Select Financial Ledger"
            data={(ledgersQuery.data || []).map((l) => ({ label: l, value: l }))}
            value={selected}
            onChange={setSelected}
            searchable
            nothingFoundMessage="No ledger found"
            w={280}
            radius="md"
            leftSection={<IconBook size={16} />}
          />
          <DateRangePicker value={range} onChange={setRange} />
        </Group>
      </Group>

      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Stack gap="lg" h="100%">
            <Card radius="lg" p="xl" withBorder shadow="sm" h="100%">
              <Stack gap="xl">
                <Group justify="space-between">
                  <Text fw={700} size="sm">Balance Sheet Summary</Text>
                  <ActionIcon variant="light" color="indigo" radius="md" onClick={() => ledgerQuery.refetch()}>
                    <IconReplace size={18} stroke={1.5} />
                  </ActionIcon>
                </Group>
                
                <Stack gap="md">
                  <Paper p="md" radius="md" bg="slate.0" withBorder>
                    <Text size="xs" c="dimmed" fw={700} mb={4} style={{ textTransform: 'uppercase' }}>Opening Position</Text>
                    <Title order={3} fw={800}>{formatCurrency(data.opening)}</Title>
                  </Paper>

                  <Paper p="md" radius="md" bg={data.period_total >= 0 ? "green.0" : "red.0"} withBorder style={{ 
                    borderColor: data.period_total >= 0 ? "var(--mantine-color-green-2)" : "var(--mantine-color-red-2)"
                  }}>
                    <Group justify="space-between">
                      <Text size="xs" c={data.period_total >= 0 ? "green.7" : "red.7"} fw={700} style={{ textTransform: 'uppercase' }}>Period Movement</Text>
                      {data.period_total >= 0 ? <IconTrendingUp size={14} color="var(--mantine-color-green-6)" /> : <IconTrendingDown size={14} color="var(--mantine-color-red-6)" />}
                    </Group>
                    <Title order={3} fw={800} c={data.period_total >= 0 ? "green.8" : "red.8"}>{formatCurrency(data.period_total)}</Title>
                  </Paper>

                  <Paper p="md" radius="md" bg="indigo.6" variant="filled">
                    <Text size="xs" c="white" opacity={0.8} fw={700} mb={4} style={{ textTransform: 'uppercase' }}>Final Closing</Text>
                    <Title order={3} fw={800} c="white">{formatCurrency(data.closing)}</Title>
                  </Paper>
                </Stack>

                <Group gap="xs">
                  <IconInfoCircle size={14} color="var(--mantine-color-dimmed)" />
                  <Text size="xs" c="dimmed" fw={500}>Aggregated in Lakhs (₹)</Text>
                </Group>
              </Stack>
            </Card>
          </Stack>
        </Grid.Col>
        
        <Grid.Col span={{ base: 12, md: 8 }}>
          <Paper p="xl" radius="lg" withBorder shadow="sm" h="100%">
            <Stack gap="lg">
              <Group gap="xs">
                <ActionIcon color="sky" variant="light" radius="md"><IconChartLine size={18} /></ActionIcon>
                <Title order={3} size="h5" fw={700}>Running Liquidity Trend</Title>
              </Group>
              <ChartCard naked title="Trend Analysis" option={balanceOption} height={320} />
            </Stack>
          </Paper>
        </Grid.Col>

        {data.department_breakdown && (
          <Grid.Col span={12}>
            <Paper p="xl" radius="lg" withBorder shadow="sm">
              <Stack gap="lg">
                <Group gap="xs">
                  <ActionIcon color="indigo" variant="light" radius="md"><IconBuildingBank size={18} /></ActionIcon>
                  <Title order={3} size="h5" fw={700}>Department Allocation Matrix</Title>
                </Group>
                <div className="chart-container">
                  <BarChart
                    h={300}
                    data={data.department_breakdown as unknown as Record<string, any>[]}
                    dataKey="label"
                    type="default"
                    series={[
                      { name: "current", color: "indigo.6", label: "Current Month" },
                      { name: "previous", color: "slate.3", label: "Previous Month" }
                    ]}
                    yAxisProps={{
                      width: getYAxisWidth(data.department_breakdown.flatMap(d => [d.current, d.previous]))
                    }}
                    tickLine="xy"
                    gridAxis="xy"
                    tooltipAnimationDuration={200}
                    withTooltip
                    barProps={{ activeBar: false, radius: [4, 4, 0, 0] }}
                    tooltipProps={{
                      content: ({ label, payload }) => {
                        if (!payload || payload.length === 0) return null;
                        const item = payload[0].payload;
                        return (
                          <Paper px="md" py="sm" withBorder shadow="xl" radius="lg" style={{ backdropFilter: 'blur(8px)', backgroundColor: 'rgba(255, 255, 255, 0.9)' }}>
                            <Text fw={800} size="sm" mb={10} color="indigo.7" style={{ borderBottom: "1px solid var(--mantine-color-slate-1)", paddingBottom: 6 }}>
                              {label}
                            </Text>
                            <Stack gap={6}>
                              <Group justify="space-between" gap="xl">
                                <Text size="xs" c="dimmed" fw={600}>CURRENT</Text>
                                <Text size="sm" fw={800} c="indigo.7">{formatCurrency(item.current)}</Text>
                              </Group>
                              <Group justify="space-between" gap="xl">
                                <Text size="xs" c="dimmed" fw={600}>PREVIOUS</Text>
                                <Text size="sm" fw={600} c="slate.5">{formatCurrency(item.previous)}</Text>
                              </Group>
                              <Divider variant="dashed" />
                              <Group justify="space-between" gap="xl">
                                <Text size="xs" c="dimmed" fw={600}>VARIANCE</Text>
                                <Badge size="sm" variant="light" color={getVarianceColor(item.variance)}>
                                  {formatVariance(item.variance)}
                                </Badge>
                              </Group>
                            </Stack>
                          </Paper>
                        );
                      }
                    }}
                  />
                </div>
              </Stack>
            </Paper>
          </Grid.Col>
        )}
      </Grid>

      <Paper p="xl" radius="lg" withBorder shadow="sm">
        <Stack gap="lg">
          <Group justify="space-between" align="center">
            <Group gap="xs">
              <ActionIcon color="indigo" variant="light" radius="md"><IconListNumbers size={18} /></ActionIcon>
              <Title order={3} size="h5" fw={700}>Transaction Audit Trail</Title>
            </Group>
            <Badge variant="light" color="slate" size="lg" radius="sm">
              {data.running_balance.length} Records Verified
            </Badge>
          </Group>
          <Table.ScrollContainer minWidth={700}>
            <Table highlightOnHover verticalSpacing="md">
              <Table.Thead bg="slate.0">
                <Table.Tr>
                  <Table.Th style={{ borderRadius: '8px 0 0 0' }}>DATE</Table.Th>
                  <Table.Th>TRANS. AMOUNT</Table.Th>
                  <Table.Th>REMAINING BAL.</Table.Th>
                  <Table.Th style={{ borderRadius: '0 8px 0 0' }}>DESCRIPTION / NARRATION</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {data.running_balance.map((row, idx) => (
                  <Table.Tr key={`${row.date}-${idx}`}>
                    <Table.Td fw={600} c="indigo.7" style={{ whiteSpace: 'nowrap' }}>{dayjs(row.date).format("DD MMM YYYY")}</Table.Td>
                    <Table.Td fw={700} c={row.amount >= 0 ? 'green.8' : 'red.8'}>{formatCurrency(row.amount)}</Table.Td>
                    <Table.Td fw={500} c="dimmed">{formatCurrency(row.running_balance)}</Table.Td>
                    <Table.Td style={{ maxWidth: 350 }}>
                      <Text size="xs" fw={500} lineClamp={1}>{row.description || "N/A"}</Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        </Stack>
      </Paper>
    </Stack>
  );
}
