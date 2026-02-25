import React from 'react';
import {
    Table, Group, Text, Box, ScrollArea, Divider, Stack, Loader
} from '@mantine/core';
import { Rnd } from 'react-rnd';
import { IconX } from '@tabler/icons-react';
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
                <div style={{
                    width: '100%', height: '100%',
                    display: 'flex', flexDirection: 'column',
                    background: '#fff',
                    borderRadius: 8,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
                    overflow: 'hidden',
                    border: '1px solid #dee2e6',
                }}>
                    <div
                        className="popup-drag-handle"
                        style={{
                            padding: '10px 14px',
                            background: '#f1f3f5',
                            borderBottom: '1px solid #dee2e6',
                            cursor: 'move',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            userSelect: 'none',
                            flexShrink: 0,
                        }}
                    >
                        <Text fw={600} size="sm">{title}</Text>
                        <div
                            onClick={onClose}
                            style={{
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                padding: '2px 4px',
                                borderRadius: 4,
                            }}
                        >
                            <IconX size={16} />
                        </div>
                    </div>
                    <div style={{ flex: 1, overflow: 'auto', padding: '14px 16px' }}>
                        {children}
                    </div>
                </div>
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
        <Stack gap="md">
            <Group justify="space-between" p="sm"
                style={{ background: '#f8f9fa', borderRadius: 6, border: '1px solid #e9ecef' }}>
                <Box>
                    <Text size="xs" c="dimmed">{ledgerName ? 'Ledger' : 'Cost Center'}</Text>
                    <Text fw={700} size="md">{ledgerName || costCenter}</Text>
                </Box>
                <Group gap="xl">
                    {[
                        { label: 'Opening', val: data.opening },
                        { label: 'Movement', val: data.period_total },
                        { label: 'Closing', val: data.closing },
                    ].map(({ label, val }) => (
                        <Box key={label} style={{ textAlign: 'right' }}>
                            <Text size="xs" c="dimmed">{label}</Text>
                            <Text size="sm" fw={600}>{formatCurrency(val)}</Text>
                        </Box>
                    ))}
                </Group>
            </Group>

            {data.monthly_summary && data.monthly_summary.length > 0 && (
                <Box>
                    <Text fw={600} size="sm" mb="xs">6-Month Breakdown</Text>
                    <Table withTableBorder withColumnBorders fz="xs" highlightOnHover>
                        <Table.Thead style={{ background: '#f1f3f5' }}>
                            <Table.Tr>
                                <Table.Th>{ledgerName ? 'Ledger' : 'Ledger Name'}</Table.Th>
                                {data.month_labels?.map(l => (
                                    <Table.Th key={l} style={{ textAlign: 'right' }}>{l}</Table.Th>
                                ))}
                                <Table.Th style={{ textAlign: 'right' }}>6M Total</Table.Th>
                            </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                            {data.monthly_summary.map(item => (
                                <Table.Tr key={item.ledger}>
                                    <Table.Td fw={500}>{item.ledger}</Table.Td>
                                    {item.months.map((amt, i) => (
                                        <Table.Td key={i} style={{ textAlign: 'right' }}>
                                            <Text size="xs" c={amt !== 0 ? 'inherit' : 'dimmed'}>
                                                {amt !== 0 ? formatCurrency(amt) : '–'}
                                            </Text>
                                        </Table.Td>
                                    ))}
                                    <Table.Td style={{ textAlign: 'right' }}>
                                        <Text fw={600} size="xs">{formatCurrency(item.total)}</Text>
                                    </Table.Td>
                                </Table.Tr>
                            ))}
                        </Table.Tbody>
                    </Table>
                </Box>
            )}

            <Divider label="Transactions" labelPosition="center" />

            <ScrollArea h={280}>
                <Table striped highlightOnHover withTableBorder withColumnBorders fz="xs">
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>Date</Table.Th>
                            <Table.Th style={{ textAlign: 'right' }}>Amount</Table.Th>
                            <Table.Th style={{ textAlign: 'right' }}>Balance</Table.Th>
                            <Table.Th>Description</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {data.running_balance.map((row, i) => (
                            <Table.Tr key={i}>
                                <Table.Td style={{ whiteSpace: 'nowrap' }}>
                                    {dayjs(row.date).format('DD MMM YYYY')}
                                </Table.Td>
                                <Table.Td style={{ textAlign: 'right' }}>{formatCurrency(row.amount)}</Table.Td>
                                <Table.Td style={{ textAlign: 'right' }}>{formatCurrency(row.running_balance)}</Table.Td>
                                <Table.Td>
                                    <Text size="xs" truncate maw={260}>{row.description}</Text>
                                </Table.Td>
                            </Table.Tr>
                        ))}
                    </Table.Tbody>
                </Table>
            </ScrollArea>
        </Stack>
    );
}
