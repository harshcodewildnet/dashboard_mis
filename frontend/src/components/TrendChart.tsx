import { AreaChart } from "@mantine/charts";
import { Paper, Title, Group, Text, Box, rem, Stack, Divider, Badge, ActionIcon } from "@mantine/core";
import { MonthlyTrendPoint } from "../api/types";
import { getYAxisWidth, formatCurrency } from "../utils/chartHelpers";
import { IconTrendingUp, IconTrendingDown, IconChartDots, IconArrowUpRight } from "@tabler/icons-react";

export interface TrendChartProps {
    data: MonthlyTrendPoint[];
    dataKey: "income" | "expense" | "profit";
    title: string;
    color: string;
    height?: number;
}

export function TrendChart({ data, dataKey, title, color, height = 300 }: TrendChartProps) {
    const chartData = data.map((point) => ({
        month: point.month_label,
        value: point[dataKey],
    }));

    const values = data.map((p) => p[dataKey]);
    const avg = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    
    // Use more vivid palette
    const getChartColor = () => {
        if (dataKey === "profit") return avg >= 0 ? "indigo.6" : "red.6";
        if (dataKey === "income") return "indigo.6";
        return "slate.6";
    };
    
    const lineColor = getChartColor();

    return (
        <Paper p="xl" radius="lg" withBorder shadow="sm" h="100%" bg="white">
            <Group justify="space-between" mb="xl">
                <Stack gap={0}>
                    <Group gap="xs">
                        <IconChartDots size={16} color="var(--mantine-color-indigo-6)" />
                        <Text size="xs" fw={700} c="dimmed" style={{ textTransform: 'uppercase', letterSpacing: rem(0.5) }}>
                            {title} Trend
                        </Text>
                    </Group>
                    <Title order={3} fw={800} size="h4">Performance Analysis</Title>
                </Stack>
                <ActionIcon variant="light" color="indigo" radius="md">
                    <IconArrowUpRight size={18} />
                </ActionIcon>
            </Group>

            {chartData.length === 0 ? (
                <Box style={{ height, display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Stack align="center" gap="xs">
                        <Badge variant="light" color="slate" size="lg">Zero Volume</Badge>
                        <Text c="dimmed" size="xs" fw={500}>No transaction data in this window</Text>
                    </Stack>
                </Box>
            ) : (
                <div style={{ height }}>
                    <AreaChart
                        h={height}
                        data={chartData}
                        dataKey="month"
                        series={[{ name: "value", color: lineColor, label: title }]}
                        curveType="monotone"
                        withLegend={false}
                        withDots={true}
                        dotProps={{ r: 4, strokeWidth: 2, fill: '#fff' }}
                        activeDotProps={{ r: 6, strokeWidth: 2, fill: '#fff' }}
                        strokeWidth={3}
                        fillOpacity={0.12}
                        gridAxis="xy"
                        tickLine="none"
                        yAxisProps={{ 
                            width: getYAxisWidth(values),
                            tickMargin: 10,
                            fontSize: 10,
                            fontWeight: 600,
                        }}
                        xAxisProps={{
                            tickMargin: 10,
                            fontSize: 10,
                            fontWeight: 600,
                        }}
                        valueFormatter={(value) => formatCurrency(value as number)}
                        tooltipProps={{
                            content: ({ label, payload }) => {
                                if (!payload || payload.length === 0) return null;
                                const value = payload[0].value as number;
                                const isPositive = value >= 0;
                                return (
                                    <Paper px="md" py="sm" withBorder shadow="xl" radius="lg" style={{ backdropFilter: 'blur(8px)', backgroundColor: 'rgba(255, 255, 255, 0.9)' }}>
                                        <Text fw={800} size="sm" mb={4} color="slate.9">{label}</Text>
                                        <Divider mb={8} variant="dashed" />
                                        <Group gap="md">
                                            <Stack gap={0}>
                                                <Text size="xs" c="dimmed" fw={700} style={{ textTransform: 'uppercase' }}>{title}</Text>
                                                <Group gap={4}>
                                                    <Text size="md" fw={900} c={isPositive ? 'indigo.7' : 'red.7'}>
                                                        {formatCurrency(value)}
                                                    </Text>
                                                    {isPositive ? <IconTrendingUp size={14} color="var(--mantine-color-green-6)" /> : <IconTrendingDown size={14} color="var(--mantine-color-red-6)" />}
                                                </Group>
                                            </Stack>
                                        </Group>
                                    </Paper>
                                );
                            },
                        }}
                    />
                </div>
            )}
        </Paper>
    );
}
