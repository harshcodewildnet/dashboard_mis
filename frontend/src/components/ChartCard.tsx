import { Paper, Stack, Text } from "@mantine/core";
import ReactECharts from "echarts-for-react";
import { CSSProperties } from "react";

export type ChartCardProps = {
  title: string;
  subtitle?: string;
  option: Record<string, unknown>;
  height?: number;
  style?: CSSProperties;
  naked?: boolean;
};

export function ChartCard({ title, subtitle, option, height = 320, style, naked }: ChartCardProps) {
  const content = (
    <Stack gap="xs">
      {!naked && (
        <Stack gap={2}>
          <Text fw={600} size="sm">{title}</Text>
          {subtitle && <Text size="xs" c="dimmed">{subtitle}</Text>}
        </Stack>
      )}
      <ReactECharts option={option} style={{ height }} />
    </Stack>
  );

  if (naked) return content;

  return (
    <Paper radius="lg" withBorder p="md" style={style}>
      {content}
    </Paper>
  );
}

