import { LineChart } from "@mantine/charts";
import { Paper, Title, Group, Text, Box } from "@mantine/core";
import { MonthlyTrendPoint } from "../api/types";

export interface TrendChartProps {
    data: MonthlyTrendPoint[];
    dataKey: "income" | "expense" | "profit";
    title: string;
    color: string;
    height?: number;
}

export function TrendChart({ data, dataKey, title, color, height = 300 }: TrendChartProps) {
    // Transform data for chart
    const chartData = data.map((point) => ({
        month: point.month_label,
        value: point[dataKey],
    }));

    const formatCurrency = (val: number) => `₹${val.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

    // Determine color for profit (green if positive, red if negative)
    const values = data.map((p) => p[dataKey]);
    const avg = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    const lineColor = dataKey === "profit" ? (avg >= 0 ? "#10b981" : "#ef4444") : color;

    return (
        <Paper p="md" shadow="sm" radius="md" h="100%">
            <Group justify="space-between" mb="md">
                <Title order={4}>{title}</Title>
            </Group>

            {chartData.length === 0 ? (
                <Box style={{ height, display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Text c="dimmed">No data available</Text>
                </Box>
            ) : (
                <LineChart
                    h={height}
                    data={chartData}
                    dataKey="month"
                    series={[{ name: "value", color: lineColor, label: title }]}
                    curveType="monotone"
                    withLegend={false}
                    withDots
                    gridAxis="xy"
                    valueFormatter={(value) => formatCurrency(value as number)}
                    tooltipProps={{
                        content: ({ label, payload }) => {
                            if (!payload || payload.length === 0) return null;
                            const value = payload[0].value as number;
                            return (
                                <Paper p="xs" shadow="md">
                                    <Text size="sm" fw={500}>{label}</Text>
                                    <Text size="sm" c={lineColor}>{formatCurrency(value)}</Text>
                                </Paper>
                            );
                        },
                    }}
                />
            )}
        </Paper>
    );
}
