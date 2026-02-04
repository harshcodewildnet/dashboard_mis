import { Group, NumberInput, Paper, Stack, Table, Text } from "@mantine/core";
import dayjs from "dayjs";
import { useMemo, useState } from "react";
import { useRows } from "../api/hooks";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";

export function RowsPage() {
  const [range, setRange] = useState<[Date | null, Date | null]>([null, null]);
  const [limit, setLimit] = useState<number>(200);

  const params = useMemo(() => {
    const [start, end] = range;
    return {
      start: start ? dayjs(start).format("YYYY-MM-DD") : undefined,
      end: end ? dayjs(end).format("YYYY-MM-DD") : undefined,
      limit
    };
  }, [range, limit]);

  const query = useRows(params);

  if (query.isLoading) return <LoadingState message="Loading rows" />;
  if (query.isError) return <ErrorState message={(query.error as Error).message} onRetry={() => query.refetch()} />;
  if (!query.data) return null;

  const data = query.data;
  const rows = data.rows;

  const columns = rows.length ? Object.keys(rows[0]) : [];

  return (
    <Stack gap="md">
      <div>
        <Text fw={700} fz="xl">
          Raw Rows
        </Text>
        <Text c="dimmed" size="sm">
          File {data.meta.file_name} · Showing {rows.length} / {data.meta.rows}
        </Text>
      </div>

      <Group gap="md" align="flex-end">
        <DateRangePicker value={range} onChange={setRange} />
        <NumberInput label="Limit" value={limit} min={10} max={5000} onChange={(v) => setLimit(v || 200)} w={140} />
      </Group>

      <Paper withBorder radius="lg" p="sm">
        <Table.ScrollContainer minWidth={900}>
          <Table highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                {columns.map((c) => (
                  <Table.Th key={c}>{c}</Table.Th>
                ))}
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {rows.map((row, idx) => (
                <Table.Tr key={idx}>
                  {columns.map((col) => {
                    const value = row[col as keyof typeof row];
                    const display =
                      typeof value === "string" && col === "date"
                        ? dayjs(value).format("YYYY-MM-DD")
                        : typeof value === "number"
                        ? value.toLocaleString()
                        : value ?? "";
                    return <Table.Td key={`${idx}-${col}`}>{String(display)}</Table.Td>;
                  })}
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>
    </Stack>
  );
}
