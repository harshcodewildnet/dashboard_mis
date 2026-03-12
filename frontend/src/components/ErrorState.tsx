import { Button, Paper, Stack, Text, Group, ActionIcon, Center, rem } from "@mantine/core";
import { IconAlertCircle, IconRefresh } from "@tabler/icons-react";

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <Center h="100%" py={rem(60)}>
      <Paper p="xl" radius="lg" withBorder shadow="sm" w="100%" bg="red.0" style={{ borderColor: 'var(--mantine-color-red-2)', maxWidth: rem(500) }}>
        <Stack gap="lg" align="center">
          <ActionIcon color="red" variant="filled" size="xl" radius="xl">
            <IconAlertCircle size={24} />
          </ActionIcon>
          
          <Stack gap={4} align="center">
            <Text fw={800} size="lg" c="red.9">System Exception Encountered</Text>
            <Text c="red.7" size="sm" ta="center" fw={500}>
                {message || "An unexpected error occurred while processing your request."}
            </Text>
          </Stack>

          {onRetry && (
            <Button 
                variant="filled" 
                color="red.6" 
                onClick={onRetry} 
                leftSection={<IconRefresh size={16} />}
                radius="md"
            >
              Attempt Recovery
            </Button>
          )}
        </Stack>
      </Paper>
    </Center>
  );
}
