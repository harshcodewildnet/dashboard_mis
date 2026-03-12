import { ActionIcon, Badge, Group, NumberInput, Paper, Stack, Table, Text, Title, rem } from "@mantine/core";
import { IconDatabase, IconFilter, IconCalendar, IconArrowRightBar, IconTableExport } from "@tabler/icons-react";
import dayjs from "dayjs";
import { useMemo, useState } from "react";
import { useRows } from "../api/hooks";
import { DateRangePicker } from "../components/DateRangePicker";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";

interface RowsPageProps {
  departmentKey?: string | null;
}

export function RowsPage({ departmentKey }: RowsPageProps) {
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
    <Stack gap="xl">
      <Group justify="space-between" align="flex-end">
        <Stack gap={4}>
          <Text size="sm" fw={600} c="indigo.6" style={{ textTransform: 'uppercase', letterSpacing: rem(1) }}>
            Data Infrastructure
          </Text>
          <Title order={1} size="h2" fw={800}>
            Transaction <Text span c="dimmed" fw={500} size="lg"> Warehouse</Text>
          </Title>
        </Stack>
        <Group gap="md">
          <Badge variant="light" color="indigo" size="lg" radius="sm" leftSection={<IconDatabase size={12} />}>
            {data.meta.rows.toLocaleString()} Total Records
          </Badge>
          <ActionIcon variant="light" color="slate" size="lg" radius="md">
            <IconTableExport size={20} stroke={1.5} />
          </ActionIcon>
        </Group>
      </Group>

      <Paper p="md" radius="lg" withBorder shadow="sm" bg="slate.0">
        <Group justify="space-between" align="flex-end">
          <Group gap="lg">
            <Stack gap={4}>
              <Text size="xs" fw={700} c="dimmed" style={{ textTransform: 'uppercase' }}>Temporal Filter</Text>
              <DateRangePicker value={range} onChange={setRange} />
            </Stack>
            <Stack gap={4}>
              <Text size="xs" fw={700} c="dimmed" style={{ textTransform: 'uppercase' }}>Volume Control</Text>
              <NumberInput 
                value={limit} 
                min={10} 
                max={5000} 
                onChange={(v) => setLimit(typeof v === 'number' ? v : (parseInt(v as string) || 200))} 
                w={140} 
                radius="md"
                leftSection={<IconArrowRightBar size={16} />}
              />
            </Stack>
          </Group>
          <Stack gap={4} align="flex-end">
            <Text size="xs" fw={700} c="dimmed" style={{ textTransform: 'uppercase' }}>Source Origin</Text>
            <Badge variant="outline" color="slate" radius="xs">{data.meta.file_name}</Badge>
          </Stack>
        </Group>
      </Paper>

      <Paper withBorder radius="lg" shadow="md" style={{ overflow: 'hidden' }}>
        <Table.ScrollContainer minWidth={1200}>
          <Table highlightOnHover withColumnBorders verticalSpacing="sm">
            <Table.Thead bg="slate.1" style={{ position: 'sticky', top: 0, zIndex: 10 }}>
              <Table.Tr>
                {columns.map((c) => (
                  <Table.Th key={c} style={{ whiteSpace: 'nowrap', textTransform: 'uppercase', fontSize: rem(11), color: 'var(--mantine-color-slate-7)' }}>
                    {c.replace(/_/g, ' ')}
                  </Table.Th>
                ))}
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {rows.map((row, idx) => (
                <Table.Tr key={idx} bg={idx % 2 === 0 ? 'transparent' : 'slate.0'}>
                  {columns.map((col) => {
                    const value = row[col as keyof typeof row];
                    const isDate = col.toLowerCase().includes('date');
                    const isAmount = col.toLowerCase().includes('amount') || col.toLowerCase().includes('value');
                    
                    const display =
                      typeof value === "string" && isDate
                        ? dayjs(value).format("DD MMM YYYY")
                        : typeof value === "number"
                        ? value.toLocaleString(undefined, { maximumFractionDigits: 2 })
                        : value ?? "-";

                    return (
                      <Table.Td key={`${idx}-${col}`} style={{ whiteSpace: 'nowrap' }}>
                        <Text size="xs" fw={isAmount ? 700 : 500} c={isAmount ? (Number(value) >= 0 ? 'indigo.7' : 'red.7') : 'inherit'}>
                          {String(display)}
                        </Text>
                      </Table.Td>
                    );
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
