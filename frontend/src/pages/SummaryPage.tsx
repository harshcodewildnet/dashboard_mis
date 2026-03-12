import { ActionIcon, Badge, Card, Grid, Group, Paper, Stack, Text, Title, rem } from "@mantine/core";
import { IconPresentation, IconTrendingUp, IconTrendingDown, IconBuildingBank, IconChevronRight, IconChartDots, IconReportAnalytics, IconCalendarStats } from "@tabler/icons-react";
import dayjs from "dayjs";
import { useMemo, useState } from "react";
import { useSummary } from "../api/hooks";
import { ChartCard } from "../components/ChartCard";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { formatCurrency } from "../utils/chartHelpers";

interface SummaryPageProps {
  departmentKey?: string | null;
}

export function SummaryPage({ departmentKey }: SummaryPageProps) {
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);

  const params = useMemo(() => {
    const [start, end] = range;
    return {
      start: start ? dayjs(start).format("YYYY-MM-DD") : undefined,
      end: end ? dayjs(end).format("YYYY-MM-DD") : undefined
    };
  }, [range]);

  const query = useSummary(params);

  if (query.isLoading) return <LoadingState message="Loading summary" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const data = query.data;

  const monthlyOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.monthly.map((m) => m.label) },
    yAxis: { type: "value" },
    series: [
      {
        data: data.monthly.map((m) => m.value),
        type: "line",
        smooth: true,
        areaStyle: {},
        color: "#4f46e5"
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 48 }
  };

  const groupOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.by_group.map((g) => g.label), axisLabel: { rotate: 30 } },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: data.by_group.map((g) => g.value),
        itemStyle: { color: "#22c55e" }
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 72 }
  };

  const ledgerOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.top_ledgers.map((g) => g.label), axisLabel: { rotate: 30 } },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: data.top_ledgers.map((g) => g.value),
        itemStyle: { color: "#38bdf8" }
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 72 }
  };

  return (
    <Stack gap="xl">
      <Group justify="space-between" align="flex-end">
        <Stack gap={4}>
          <Text size="sm" fw={600} c="indigo.6" style={{ textTransform: 'uppercase', letterSpacing: rem(1) }}>
            Executive Dashboard
          </Text>
          <Title order={1} size="h2" fw={800}>
            Financial Strategy <Text span c="dimmed" fw={500} size="lg"> Overview</Text>
          </Title>
        </Stack>
        <Group gap="md" align="flex-end">
          <DateRangePicker value={range} onChange={setRange} />
        </Group>
      </Group>

      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card radius="lg" p="lg" withBorder shadow="sm">
            <Group gap="sm" mb="xs">
              <ActionIcon variant="light" color="blue" radius="md"><IconTrendingUp size={18} /></ActionIcon>
              <Text size="xs" c="dimmed" fw={700} style={{ textTransform: 'uppercase' }}>Gross Revenue</Text>
            </Group>
            <Title order={2} fw={800}>{formatCurrency(data.kpis.total_revenue)}</Title>
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card radius="lg" p="lg" withBorder shadow="sm">
            <Group gap="sm" mb="xs">
              <ActionIcon variant="light" color="red" radius="md"><IconTrendingDown size={18} /></ActionIcon>
              <Text size="xs" c="dimmed" fw={700} style={{ textTransform: 'uppercase' }}>Total Expenses</Text>
            </Group>
            <Title order={2} fw={800}>{formatCurrency(data.kpis.total_expenses)}</Title>
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card radius="lg" p="lg" withBorder shadow="sm" style={{ 
            background: data.kpis.net_profit >= 0 ? "rgba(34, 197, 94, 0.05)" : "rgba(239, 68, 68, 0.05)",
            borderColor: data.kpis.net_profit >= 0 ? "var(--mantine-color-green-2)" : "var(--mantine-color-red-2)"
          }}>
            <Group gap="sm" mb="xs">
              <ActionIcon variant="filled" color={data.kpis.net_profit >= 0 ? "green.6" : "red.6"} radius="md">
                <IconPresentation size={18} />
              </ActionIcon>
              <Text size="xs" c={data.kpis.net_profit >= 0 ? "green.7" : "red.7"} fw={700} style={{ textTransform: 'uppercase' }}>Net Margin</Text>
            </Group>
            <Title order={2} fw={800} c={data.kpis.net_profit >= 0 ? "green.8" : "red.8"}>
              {formatCurrency(data.kpis.net_profit)}
            </Title>
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card radius="lg" p="lg" withBorder shadow="sm">
            <Group gap="sm" mb="xs">
              <ActionIcon variant="light" color="orange" radius="md"><IconBuildingBank size={18} /></ActionIcon>
              <Text size="xs" c="dimmed" fw={700} style={{ textTransform: 'uppercase' }}>Cash Position</Text>
            </Group>
            <Title order={2} fw={800}>{formatCurrency(data.kpis.cash_balance)}</Title>
          </Card>
        </Grid.Col>
      </Grid>

      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, lg: 8 }}>
          <Paper p="xl" radius="lg" withBorder shadow="sm">
            <Stack gap="lg">
              <Group justify="space-between">
                <Group gap="xs">
                  <ActionIcon color="indigo" variant="light" radius="md"><IconCalendarStats size={18} /></ActionIcon>
                  <Title order={3} size="h4" fw={700}>Performance Velocity</Title>
                </Group>
                <Badge variant="dot" color="indigo" size="lg">Monthly Flux</Badge>
              </Group>
              <ChartCard naked title="Monthly Trends" option={monthlyOption} height={320} />
            </Stack>
          </Paper>
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 4 }}>
          <Stack gap="lg" h="100%">
            <Card p="xl" radius="lg" withBorder shadow="sm" h="100%" bg="slate.0">
              <Stack gap="md">
                <Group gap="xs">
                  <ActionIcon color="slate" variant="white" radius="md"><IconReportAnalytics size={18} /></ActionIcon>
                  <Text fw={700} size="sm">Metadata Summary</Text>
                </Group>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: rem(16) }}>
                  <div>
                    <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>File Origin</Text>
                    <Text size="sm" fw={600} truncate>{data.meta.file_name}</Text>
                  </div>
                  <div>
                    <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Last Sync</Text>
                    <Text size="sm" fw={600}>{dayjs(data.meta.modified_at).format("DD MMM, HH:mm")}</Text>
                  </div>
                </div>
                <div>
                  <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>Data Spectrum (Cols)</Text>
                  <Group gap={4} mt={4}>
                    {data.meta.columns.slice(0, 6).map(c => (
                      <Badge key={c} size="xs" variant="outline" color="slate">{c}</Badge>
                    ))}
                    {data.meta.columns.length > 6 && <Badge size="xs" variant="outline">+{data.meta.columns.length - 6}</Badge>}
                  </Group>
                </div>
              </Stack>
            </Card>
          </Stack>
        </Grid.Col>
      </Grid>

      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Paper p="xl" radius="lg" withBorder shadow="sm">
            <Stack gap="lg">
              <Group gap="xs">
                <ActionIcon color="green" variant="light" radius="md"><IconChartDots size={18} /></ActionIcon>
                <Title order={3} size="h5" fw={700}>Ledger Distribution</Title>
              </Group>
              <ChartCard naked title="Top Groups" option={groupOption} height={320} />
            </Stack>
          </Paper>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Paper p="xl" radius="lg" withBorder shadow="sm">
            <Stack gap="lg">
              <Group gap="xs">
                <ActionIcon color="sky" variant="light" radius="md"><IconChartDots size={18} /></ActionIcon>
                <Title order={3} size="h5" fw={700}>Contribution Analysis</Title>
              </Group>
              <ChartCard naked title="Top Ledgers" option={ledgerOption} height={320} />
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
