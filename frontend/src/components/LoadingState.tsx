import { Center, Loader, Stack, Text } from "@mantine/core";

export function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <Center py="xl">
      <Stack gap="xs" align="center">
        <Loader color="indigo" />
        <Text size="sm" c="dimmed">
          {message}
        </Text>
      </Stack>
    </Center>
  );
}
