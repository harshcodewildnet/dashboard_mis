import { Center, Loader, Stack, Text, rem } from "@mantine/core";

export function LoadingState({ message = "Synchronizing data..." }: { message?: string }) {
  return (
    <Center h="100%" py={rem(80)}>
      <Stack gap="md" align="center">
        <Loader size="lg" type="dots" color="indigo.6" />
        <Stack gap={4} align="center">
          <Text size="sm" fw={600} c="slate.8">
            {message}
          </Text>
          <Text size="xs" c="dimmed">
            This may take a moment while we fetch the latest records.
          </Text>
        </Stack>
      </Stack>
    </Center>
  );
}
