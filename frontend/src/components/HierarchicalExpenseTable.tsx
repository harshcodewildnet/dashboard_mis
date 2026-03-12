import React, { useState } from 'react';
import {
    Table, Group, Text, Box, ScrollArea, Badge, Divider, Stack, Loader, rem
} from '@mantine/core';
import { Rnd } from 'react-rnd';
import {
    IconChevronRight, IconChevronDown, IconX
} from '@tabler/icons-react';
import { ExpenseSectionNode, ExpenseBreakdownResponse } from '../api/types';
import { formatCurrency } from '../utils/chartHelpers';
import { useLedger } from '../api/hooks';
import dayjs from 'dayjs';
import { FloatingPopup, LedgerPopupContent } from './LedgerDrilldownPopup';

interface Props {
    data: ExpenseBreakdownResponse | null | undefined;
    isLoading?: boolean;
}

// ... removed inlined FloatingPopup and LedgerPopupContent ...

// ─── Section color map ────────────────────────────────────────────────────────
const SECTION_COLORS: Record<string, string> = {
    direct: 'var(--mantine-color-blue-7)',
    outsource_vendor_root: 'var(--mantine-color-orange-7)',
    salary: 'var(--mantine-color-green-7)',
    overhead: 'var(--mantine-color-grape-7)',
    support_salary: 'var(--mantine-color-indigo-7)',
    marketing_salary: 'var(--mantine-color-pink-7)',
    marketing_expenses: 'var(--mantine-color-red-7)',
};

// ─── Variance badge ───────────────────────────────────────────────────────────
function VarianceBadge({ cur, prev }: { cur: number; prev: number }) {
    if (prev === 0 && cur === 0) return <Text size="xs" c="dimmed">–</Text>;
    if (prev === 0) return <Badge color="gray" variant="light" size="xs">New</Badge>;
    const pct = ((cur - prev) / prev) * 100;
    const color = pct > 0 ? (pct > 10 ? 'red' : 'orange') : (pct < -10 ? 'green' : 'teal');
    return (
        <Badge color={color} variant="light" size="xs">
            {pct > 0 ? '+' : ''}{pct.toFixed(1)}%
        </Badge>
    );
}

// ─── Amount cell ──────────────────────────────────────────────────────────────
function AmtCell({ val, bold }: { val: number; bold?: boolean }) {
    return (
        <Table.Td style={{ textAlign: 'right', minWidth: 110 }}>
            <Text size="sm" fw={bold ? 700 : 400} c={val > 0 ? 'inherit' : 'dimmed'}>
                {val > 0 ? formatCurrency(val) : '–'}
            </Text>
        </Table.Td>
    );
}

// ─── Row background per level ─────────────────────────────────────────────────
function rowBg(level: number): string {
    if (level === 0) return 'var(--mantine-color-slate-1)';
    if (level === 1) return 'var(--mantine-color-slate-0)';
    if (level === 2) return '#ffffff';
    return '#fff';
}

// ─── Row component ────────────────────────────────────────────────────────────
interface LedgerTarget { type: 'ledger' | 'costCenter'; name: string; }

interface RowProps {
    node: ExpenseSectionNode;
    level: number;
    monthLabels: string[];
    onOpenLedger: (target: LedgerTarget) => void;
}

const ExpenseRow: React.FC<RowProps> = ({ node, level, monthLabels, onOpenLedger }) => {
    const [opened, setOpened] = useState(false);
    const hasChildren = (node.children?.length ?? 0) > 0;
    const bg = rowBg(level);

    // popup trigger rows — only show pointer, no special colour
    const isPopupRow =
        node.id.startsWith('de_ledger_') ||
        node.id.startsWith('mkte_ledger_') ||
        node.id.startsWith('ov_ledger_');

    const handleClick = () => {
        if (isPopupRow) {
            onOpenLedger({ type: 'ledger', name: node.label });
        } else if (hasChildren) {
            setOpened(o => !o);
        }
    };

    return (
        <>
            <Table.Tr
                onClick={handleClick}
                style={{
                    cursor: (hasChildren || isPopupRow) ? 'pointer' : 'default',
                    backgroundColor: bg,
                }}
            >
                {/* Label cell */}
                <Table.Td
                    style={{
                        paddingLeft: level * 18 + 12,
                        position: 'sticky', left: 0,
                        background: bg,
                        zIndex: 1,
                        borderRight: '1px solid var(--mantine-color-slate-2)',
                        minWidth: rem(260),
                    }}
                >
                    <Group gap={6} wrap="nowrap">
                        {hasChildren ? (
                            opened
                                ? <IconChevronDown size={13} color="#868e96" />
                                : <IconChevronRight size={13} color="#868e96" />
                        ) : (
                            <Box w={13} />
                        )}
                        <Text
                            size="sm"
                            fw={level === 0 ? 700 : level === 1 ? 600 : 400}
                            truncate
                            maw={300}
                            c={level === 0 ? (SECTION_COLORS[node.sectionType ?? ''] ?? 'dark') : 'inherit'}
                        >
                            {node.label}
                        </Text>
                    </Group>
                </Table.Td>

                {/* 3 month columns */}
                <AmtCell val={node.months[0]} bold={level === 0} />
                <AmtCell val={node.months[1]} bold={level === 0} />
                <AmtCell val={node.months[2]} bold={level === 0} />

                {/* Variance */}
                <Table.Td style={{ textAlign: 'center', minWidth: 80 }}>
                    {level > 0 && <VarianceBadge cur={node.months[0]} prev={node.months[1]} />}
                </Table.Td>

                {/* Total */}
                <Table.Td style={{ textAlign: 'right', minWidth: 120 }}>
                    <Text size="sm" fw={level === 0 ? 700 : 500} c={level === 0 ? 'dark' : 'dimmed'}>
                        {formatCurrency(node.total)}
                    </Text>
                </Table.Td>
            </Table.Tr>

            {opened && hasChildren && node.children!.map(child => (
                <ExpenseRow
                    key={child.id}
                    node={child}
                    level={level + 1}
                    monthLabels={monthLabels}
                    onOpenLedger={onOpenLedger}
                />
            ))}
        </>
    );
};

// ─── Main export ──────────────────────────────────────────────────────────────
export const HierarchicalExpenseTable: React.FC<Props> = ({ data, isLoading }) => {
    const [popupOpen, setPopupOpen] = useState(false);
    const [selectedTarget, setSelectedTarget] = useState<LedgerTarget | null>(null);

    const handleOpenLedger = (target: LedgerTarget) => {
        setSelectedTarget(target);
        setPopupOpen(true);
    };

    if (isLoading) return <Text size="sm" c="dimmed" p="md">Loading expense breakdown…</Text>;
    if (!data || !data.sections || data.sections.length === 0) {
        return <Text size="sm" c="dimmed" p="md">No expense data found.</Text>;
    }

    const { sections, month_labels: monthLabels } = data;

    return (
        <Box mt="md">
            {/* Draggable / resizable popup */}
            {popupOpen && selectedTarget && (
                <FloatingPopup
                    title={`Ledger: ${selectedTarget.name}`}
                    onClose={() => setPopupOpen(false)}
                >
                    <LedgerPopupContent
                        ledgerName={selectedTarget.type === 'ledger' ? selectedTarget.name : undefined}
                        costCenter={selectedTarget.type === 'costCenter' ? selectedTarget.name : undefined}
                    />
                </FloatingPopup>
            )}

            {/* Header */}
            <Group mb="sm" justify="space-between" align="center">
                <Text fw={700} size="lg">Detailed Expense Breakdown</Text>
                <Group gap="xs">
                    <Badge variant="dot" color="blue">3-Month View</Badge>
                    <Badge variant="dot" color="gray">{monthLabels[0]} ← Latest</Badge>
                </Group>
            </Group>

            <Divider mb="sm" />

            {/* Scrollable table */}
            <Table.ScrollContainer minWidth={900}>
                <Table
                    withTableBorder
                    withColumnBorders
                    striped
                    highlightOnHover
                    style={{ fontSize: 13 }}
                >
                    <Table.Thead
                        style={{
                            position: 'sticky', top: 0,
                            background: 'var(--mantine-color-slate-1)', zIndex: 10,
                        }}
                    >
                        <Table.Tr>
                            <Table.Th
                                style={{
                                    position: 'sticky', left: 0,
                                    background: 'var(--mantine-color-slate-1)', zIndex: 11,
                                    borderRight: '1px solid var(--mantine-color-slate-2)',
                                    minWidth: rem(260),
                                    fontSize: rem(12),
                                    textTransform: 'uppercase',
                                    color: 'var(--mantine-color-dimmed)'
                                }}
                            >
                                Classification
                            </Table.Th>
                            {monthLabels.map((m, i) => (
                                <Table.Th key={m} style={{ textAlign: 'right', minWidth: 110 }}>
                                    <Text size="xs" fw={700} c={i === 0 ? 'indigo.6' : 'dimmed'} h={16}>
                                        {m}
                                    </Text>
                                </Table.Th>
                            ))}
                            <Table.Th style={{ textAlign: 'center', minWidth: 80 }}>
                                <Text size="xs" c="dimmed" fw={700} h={16}>Δ %</Text>
                            </Table.Th>
                            <Table.Th style={{ textAlign: 'right', minWidth: 120 }}>
                                <Text size="xs" fw={700} h={16}>QUARTER TOTAL</Text>
                            </Table.Th>
                        </Table.Tr>
                    </Table.Thead>

                    <Table.Tbody>
                        {sections.map(section => (
                            <ExpenseRow
                                key={section.id}
                                node={section}
                                level={0}
                                monthLabels={monthLabels}
                                onOpenLedger={handleOpenLedger}
                            />
                        ))}
                    </Table.Tbody>
                </Table>
            </Table.ScrollContainer>
        </Box>
    );
};
