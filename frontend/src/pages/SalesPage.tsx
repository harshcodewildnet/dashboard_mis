import { ActionIcon, Badge, Card, Grid, Group, NumberInput, Paper, Stack, Text, Title, rem } from "@mantine/core";
import { IconShoppingBag, IconUsers, IconTicket, IconTrendingUp, IconChartBar, IconInfoCircle } from "@tabler/icons-react";
import dayjs from "dayjs";
import { useMemo, useState } from "react";
import { useSales } from "../api/hooks";
import { ChartCard } from "../components/ChartCard";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { StatGrid } from "../components/StatGrid";
import { formatCurrency } from "../utils/chartHelpers";

interface SalesPageProps {
  departmentKey?: string | null;
}

export function SalesPage({ departmentKey }: SalesPageProps) {
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);
  const [topN, setTopN] = useState<number>(10);

  const params = useMemo(() => {
    const [start, end] = range;
    return {
      start: start ? dayjs(start).format("YYYY-MM-DD") : undefined,
      end: end ? dayjs(end).format("YYYY-MM-DD") : undefined,
      top: topN
    };
  }, [range, topN]);

  const query = useSales(params);

  if (query.isLoading) return <LoadingState message="Loading sales" />;
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
        color: "#5b21b6"
      }
    ],
    grid: { left: 48, right: 16, top: 32, bottom: 48 }
  };

  const customersOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: data.top_customers.map((c) => c.label) },
    series: [
      {
        type: "bar",
        data: data.top_customers.map((c) => c.value),
        itemStyle: { color: "#22c55e" }
      }
    ],
    grid: { left: 120, right: 16, top: 16, bottom: 16 }
  };

  const itemsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "value" },
    yAxis: { type: "category", data: data.top_items.map((c) => c.label) },
    series: [
      {
        type: "bar",
        data: data.top_items.map((c) => c.value),
        itemStyle: { color: "#0ea5e9" }
      }
    ],
    grid: { left: 120, right: 16, top: 16, bottom: 16 }
  };

  return (
    <Stack gap="xl">
      <Group justify="space-between" align="flex-end">
        <Stack gap={4}>
          <Text size="sm" fw={600} c="indigo.6" style={{ textTransform: 'uppercase', letterSpacing: rem(1) }}>
            Sales Intelligence
          </Text>
          <Title order={1} size="h2" fw={800}>
            Sales Analysis <Text span c="dimmed" fw={500} size="lg"> (in Lakhs)</Text>
          </Title>
        </Stack>
        <Group gap="md" align="flex-end">
          <NumberInput 
            label="Top N Items" 
            value={topN} 
            min={3} 
            max={30} 
            onChange={(val) => setTopN(typeof val === 'number' ? val : (parseInt(val as string) || 10))} 
            w={120} 
            radius="md"
          />
          <DateRangePicker value={range} onChange={setRange} />
        </Group>
      </Group>

      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card radius="lg" p="lg" withBorder shadow="sm">
            <Group gap="sm" mb="xs">
              <ActionIcon variant="light" color="indigo" radius="md"><IconShoppingBag size={18} /></ActionIcon>
              <Text size="sm" c="dimmed" fw={600}>TOTAL REVENUE</Text>
            </Group>
            <Title order={2} fw={800}>{formatCurrency(data.totals.total_sales)}</Title>
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card radius="lg" p="lg" withBorder shadow="sm">
            <Group gap="sm" mb="xs">
              <ActionIcon variant="light" color="teal" radius="md"><IconUsers size={18} /></ActionIcon>
              <Text size="sm" c="dimmed" fw={600}>UNIQUE CLIENTS</Text>
            </Group>
            <Title order={2} fw={800}>{data.totals.unique_customers.toLocaleString()}</Title>
          </Card>
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <Card radius="lg" p="lg" withBorder shadow="sm">
            <Group gap="sm" mb="xs">
              <ActionIcon variant="light" color="orange" radius="md"><IconTicket size={18} /></ActionIcon>
              <Text size="sm" c="dimmed" fw={600}>AVG TICKET SIZE</Text>
            </Group>
            <Title order={2} fw={800}>{formatCurrency(data.totals.avg_ticket)}</Title>
          </Card>
        </Grid.Col>
      </Grid>

      <Grid gutter="lg">
        <Grid.Col span={{ base: 12, lg: 7 }}>
          <Paper p="xl" radius="lg" withBorder shadow="sm">
            <Stack gap="lg">
              <Group gap="xs">
                <ActionIcon color="indigo" variant="light" radius="md"><IconTrendingUp size={18} /></ActionIcon>
                <Title order={3} size="h5" fw={700}>Sales Volume Trends</Title>
              </Group>
              <ChartCard naked title="Sales by Month" option={monthlyOption} height={320} />
            </Stack>
          </Paper>
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 5 }}>
          <Paper p="xl" radius="lg" withBorder shadow="sm">
            <Stack gap="lg">
              <Group gap="xs">
                <ActionIcon color="teal" variant="light" radius="md"><IconUsers size={18} /></ActionIcon>
                <Title order={3} size="h5" fw={700}>Top Performance Clients</Title>
              </Group>
              <ChartCard naked title="Top Customers" option={customersOption} height={320} />
            </Stack>
          </Paper>
        </Grid.Col>
      </Grid>

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, lg: 6 }}>
          <ChartCard title="Top Items" option={itemsOption} height={360} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, lg: 6 }}>
          <ChartCard
            title="Meta"
            option={{
              tooltip: {},
              series: [
                {
                  type: "pie",
                  radius: ["40%", "70%"],
                  data: [
                    { value: data.totals.total_sales, name: "Total" },
                    { value: data.totals.avg_ticket * Math.max(data.totals.unique_customers, 1), name: "Avg Ticket * Customers" }
                  ]
                }
              ]
            }}
            height={320}
          />
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
