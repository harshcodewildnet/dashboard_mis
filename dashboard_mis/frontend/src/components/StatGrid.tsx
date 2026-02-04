import { Group, Paper, SimpleGrid, Stack, Text } from "@mantine/core";

type StatGridProps = {
  items: { label: string; value: string; hint?: string; color?: string }[];
};

export function StatGrid({ items }: StatGridProps) {
  return (
    <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
      {items.map((item) => (
        <Paper key={item.label} p="md" radius="lg" withBorder>
          <Stack gap={4}>
            <Group justify="space-between" gap="xs">
              <Text size="sm" c="dimmed">
                {item.label}
              </Text>
              {item.hint && (
                <Text size="xs" c="dimmed">
                  {item.hint}
                </Text>
              )}
            </Group>
            <Text fw={700} fz="xl" c={item.color || "var(--mantine-color-text)"}>
              {item.value}
            </Text>
          </Stack>
        </Paper>
      ))}
    </SimpleGrid>
  );
}
