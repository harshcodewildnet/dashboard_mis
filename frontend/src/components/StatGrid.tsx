import { Group, Paper, SimpleGrid, Stack, Text, rem } from "@mantine/core";

type StatGridProps = {
  items: { label: string; value: string; hint?: string; color?: string }[];
};

export function StatGrid({ items }: StatGridProps) {
  return (
    <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="lg">
      {items.map((item) => (
        <Paper 
          key={item.label} 
          p="xl" 
          radius="lg" 
          withBorder 
          shadow="sm"
          bg="transparent"
          style={{
            borderLeft: `${rem(4)} solid ${item.color || 'var(--mantine-color-indigo-6)'}`,
            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            cursor: 'default',
          }}
        >
          <Stack gap={4}>
            <Group justify="space-between" align="flex-start">
              <Text size="xs" fw={700} c="dimmed" style={{ textTransform: 'uppercase', letterSpacing: rem(0.5) }}>
                {item.label}
              </Text>
              {item.hint && (
                <Text size="xs" fw={600} c="dimmed">
                  {item.hint}
                </Text>
              )}
            </Group>
            <Text fw={800} fz={rem(24)} c={item.color || "var(--mantine-color-slate-9)"}>
              {item.value}
            </Text>
          </Stack>
        </Paper>
      ))}
    </SimpleGrid>
  );
}
