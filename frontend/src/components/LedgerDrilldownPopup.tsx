import { ActionIcon, Badge, Box, Divider, Group, Loader, Paper, ScrollArea, Stack, Table, Text, Title, rem } from '@mantine/core';
import { Rnd } from 'react-rnd';
import { IconX, IconTrendingUp, IconTrendingDown, IconBook, IconListNumbers, IconHistory } from '@tabler/icons-react';
import { formatCurrency } from '../utils/chartHelpers';
import { useLedger } from '../api/hooks';
import dayjs from 'dayjs';

// ─── Draggable / Resizable Popup ─────────────────────────────────────────────
interface FloatingPopupProps {
    title: string;
    onClose: () => void;
    children: React.ReactNode;
}

export function FloatingPopup({ title, onClose, children }: FloatingPopupProps) {
    const initW = Math.min(window.innerWidth * 0.72, 1000);
    const initH = Math.min(window.innerHeight * 0.80, 700);
    const initX = (window.innerWidth - initW) / 2;
    const initY = (window.innerHeight - initH) / 2;

    return (
        <div
            style={{
                position: 'fixed', inset: 0,
                zIndex: 1000,
                pointerEvents: 'none',
            }}
        >
            <Rnd
                default={{ x: initX, y: initY, width: initW, height: initH }}
                minWidth={400}
                minHeight={300}
                bounds="window"
                style={{ pointerEvents: 'all' }}
                dragHandleClassName="popup-drag-handle"
                enableResizing={{
                    top: true, bottom: true,
                    left: true, right: true,
                    topLeft: true, topRight: true,
                    bottomLeft: true, bottomRight: true,
                }}
            >
                <Paper
                    shadow="xl"
                    radius="lg"
                    withBorder
                    style={{
                        width: '100%', height: '100%',
                        display: 'flex', flexDirection: 'column',
                        overflow: 'hidden',
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(10px)',
                    }}
                >
                    <Group
                        className="popup-drag-handle"
                        justify="space-between"
                        px="md"
                        py="xs"
                        bg="slate.0"
                        style={{
                            borderBottom: '1px solid var(--mantine-color-slate-2)',
                            cursor: 'move',
                            userSelect: 'none',
                            flexShrink: 0,
                        }}
                    >
                        <Group gap="xs">
                            <IconBook size={16} color="var(--mantine-color-indigo-6)" />
                            <Text fw={700} size="sm" c="slate.8">{title}</Text>
                        </Group>
                        <ActionIcon 
                            onClick={onClose}
                            variant="subtle"
                            color="slate"
                            radius="md"
                        >
                            <IconX size={18} />
                        </ActionIcon>
                    </Group>
                    <Box style={{ flex: 1, overflow: 'hidden' }} p="md">
                        {children}
                    </Box>
                </Paper>
            </Rnd>
        </div>
    );
}

// ─── Ledger popup content ─────────────────────────────────────────────────────
export function LedgerPopupContent({ costCenter, ledgerName }: { costCenter?: string; ledgerName?: string }) {
    const { data, isLoading, error } = useLedger({ costCenter, name: ledgerName });

    if (isLoading) return <Group justify="center" p="xl"><Loader size="md" /></Group>;
    if (error) return <Text c="red" p="md">Error loading ledger: {(error as Error).message}</Text>;
    if (!data) return <Text c="dimmed" p="md">No data available.</Text>;

    return (
        <Stack gap="lg" h="100%">
            <Paper p="md" bg="indigo.0" radius="md" style={{ border: '1px solid var(--mantine-color-indigo-1)' }}>
                <Group justify="space-between">
                    <Box>
                        <Text size="xs" c="indigo.7" fw={700} style={{ textTransform: 'uppercase' }}>
                            {ledgerName ? 'Active Financial Ledger' : 'Active Cost Center'}
                        </Text>
                        <Title order={4} fw={800}>{ledgerName || costCenter}</Title>
                    </Box>
                    <Group gap="lg">
                        {[
                            { label: 'Opening', val: data.opening, color: 'slate.7' },
                            { label: 'Movement', val: data.period_total, color: data.period_total >= 0 ? 'green.7' : 'red.7' },
                            { label: 'Closing', val: data.closing, color: 'indigo.7' },
                        ].map(({ label, val, color }) => (
                            <Box key={label} style={{ textAlign: 'right' }}>
                                <Text size="xs" c="dimmed" fw={600} style={{ textTransform: 'uppercase' }}>{label}</Text>
                                <Text size="md" fw={800} c={color}>{formatCurrency(val)}</Text>
                            </Box>
                        ))}
                    </Group>
                </Group>
            </Paper>

            {data.monthly_summary && data.monthly_summary.length > 0 && (
                <Box>
                    <Group gap="xs" mb="sm">
                        <IconHistory size={16} color="var(--mantine-color-slate-5)" />
                        <Text fw={700} size="sm" style={{ textTransform: 'uppercase' }}>6-Month Performance Matrix</Text>
                    </Group>
                    <Paper withBorder radius="md" style={{ overflow: 'hidden' }}>
                        <Table highlightOnHover verticalSpacing="xs">
                            <Table.Thead bg="slate.0">
                                <Table.Tr>
                                    <Table.Th style={{ fontSize: rem(10) }}>ENTITY</Table.Th>
                                    {data.month_labels?.map(l => (
                                        <Table.Th key={l} style={{ textAlign: 'right', fontSize: rem(10) }}>{l.toUpperCase()}</Table.Th>
                                    ))}
                                    <Table.Th style={{ textAlign: 'right', fontSize: rem(10) }}>6M VOLUME</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {data.monthly_summary.map(item => (
                                    <Table.Tr key={item.ledger}>
                                        <Table.Td fw={600} style={{ whiteSpace: 'nowrap' }}>
                                            <Text size="xs" c="indigo.7" fw={600}>{item.ledger}</Text>
                                        </Table.Td>
                                        {item.months.map((amt, i) => (
                                            <Table.Td key={i} style={{ textAlign: 'right' }}>
                                                <Text size="xs" fw={500} c={amt !== 0 ? 'inherit' : 'dimmed'}>
                                                    {amt !== 0 ? formatCurrency(amt) : '–'}
                                                </Text>
                                            </Table.Td>
                                        ))}
                                        <Table.Td style={{ textAlign: 'right' }}>
                                            <Text fw={700} size="xs" c="indigo.9">{formatCurrency(item.total)}</Text>
                                        </Table.Td>
                                    </Table.Tr>
                                ))}
                            </Table.Tbody>
                        </Table>
                    </Paper>
                </Box>
            )}

            <Box style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                <Group gap="xs" mb="sm">
                    <IconListNumbers size={16} color="var(--mantine-color-slate-5)" />
                    <Text fw={700} size="sm" style={{ textTransform: 'uppercase' }}>Verified Transaction Journal</Text>
                </Group>
                
                <Paper withBorder radius="md" shadow="sm" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                    <ScrollArea style={{ flex: 1 }}>
                        <Table highlightOnHover verticalSpacing="sm">
                            <Table.Thead bg="slate.0" style={{ position: 'sticky', top: 0, zIndex: 1, backgroundColor: 'var(--mantine-color-slate-0)' }}>
                                <Table.Tr>
                                    <Table.Th style={{ fontSize: rem(10) }}>DATE</Table.Th>
                                    <Table.Th style={{ textAlign: 'right', fontSize: rem(10) }}>AMOUNT</Table.Th>
                                    <Table.Th style={{ textAlign: 'right', fontSize: rem(10) }}>BALANCE</Table.Th>
                                    <Table.Th style={{ fontSize: rem(10) }}>DESCRIPTION</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {data.running_balance.map((row, i) => (
                                    <Table.Tr key={i}>
                                        <Table.Td style={{ whiteSpace: 'nowrap' }}>
                                            <Text fw={600} c="indigo.7" size="xs">{dayjs(row.date).format('DD MMM YYYY')}</Text>
                                        </Table.Td>
                                        <Table.Td style={{ textAlign: 'right' }}>
                                            <Text fw={700} c={row.amount >= 0 ? 'green.8' : 'red.8'} size="xs">{formatCurrency(row.amount)}</Text>
                                        </Table.Td>
                                        <Table.Td style={{ textAlign: 'right' }}>
                                            <Text fw={500} c="dimmed" size="xs">{formatCurrency(row.running_balance)}</Text>
                                        </Table.Td>
                                        <Table.Td>
                                            <Text size="xs" fw={500} lineClamp={1} maw={350}>{row.description || '-'}</Text>
                                        </Table.Td>
                                    </Table.Tr>
                                ))}
                            </Table.Tbody>
                        </Table>
                    </ScrollArea>
                </Paper>
            </Box>
        </Stack>
    );
}
