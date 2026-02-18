import { Paper, Stack, Text } from "@mantine/core";
import ReactECharts from "echarts-for-react";
import { CSSProperties } from "react";

export type ChartCardProps = {
  title: string;
  option: Record<string, unknown>;
  height?: number;
  style?: CSSProperties;
};

export function ChartCard({ title, option, height = 320, style }: ChartCardProps) {
  return (
    <Paper radius="lg" withBorder p="md" style={style}>
      <Stack gap="xs">
        <Text fw={600}>{title}</Text>
        <ReactECharts option={option} style={{ height }} />
      </Stack>
    </Paper>
  );
}

