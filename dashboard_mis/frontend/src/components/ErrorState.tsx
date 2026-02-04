import { Button, Paper, Stack, Text } from "@mantine/core";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <Paper p="md" radius="lg" withBorder>
      <Stack gap="sm">
        <Text fw={600}>Something went wrong</Text>
        <Text c="red" size="sm">
          {message}
        </Text>
        {onRetry && (
          <Button variant="light" onClick={onRetry} size="xs">
            Retry
          </Button>
        )}
      </Stack>
    </Paper>
  );
}
