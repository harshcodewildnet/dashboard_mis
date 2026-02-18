import React, { useState } from 'react';
import { Table, Group, Text, ActionIcon, Box, ScrollArea, Tooltip } from '@mantine/core';
import { IconChevronRight, IconChevronDown, IconUser } from '@tabler/icons-react';
import { ExpenseNode } from '../api/types';
import { formatCurrency } from '../utils/chartHelpers';

interface HierarchicalExpenseTableProps {
    data: ExpenseNode[];
    isLoading?: boolean;
}

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

interface RowProps {
    node: ExpenseNode;
    level: number;
}

const ExpenseRow: React.FC<RowProps> = ({ node, level }: RowProps) => {
    const [opened, setOpened] = useState(false);
    const hasChildren = node.children && node.children.length > 0;

    return (
        <>
            <Table.Tr
                onClick={() => hasChildren && setOpened(!opened)}
                style={{ cursor: hasChildren ? 'pointer' : 'default', backgroundColor: level === 0 ? '#f8f9fa' : 'transparent' }}
            >
                <Table.Td style={{ paddingLeft: level * 24 + 10, position: 'sticky', left: 0, background: level === 0 ? '#f8f9fa' : 'white', zIndex: 1, borderRight: '1px solid #dee2e6' }}>
                    <Group gap="xs" wrap="nowrap">
                        {hasChildren ? (
                            opened ? <IconChevronDown size={16} /> : <IconChevronRight size={16} />
                        ) : (
                            <Box w={16} />
                        )}
                        {node.isSalary && <IconUser size={14} color="gray" />}
                        <Text size="sm" fw={level === 0 ? 700 : 500} truncate maw={250}>
                            {node.label}
                            {node.empId && (
                                <Text component="span" size="xs" c="dimmed" ml="xs">
                                    ({node.empId})
                                </Text>
                            )}
                        </Text>
                    </Group>
                </Table.Td>

                {node.months.map((val: number, idx: number) => (
                    <Table.Td key={idx} align="right" style={{ minWidth: 100 }}>
                        <Text size="sm" fw={val > 0 ? 500 : 400} c={val > 0 ? 'black' : 'gray.4'}>
                            {val > 0 ? formatCurrency(val) : '-'}
                        </Text>
                    </Table.Td>
                ))}

                <Table.Td align="right" style={{ minWidth: 120 }}>
                    <Text size="sm" fw={700} c="blue">
                        {formatCurrency(node.total)}
                    </Text>
                </Table.Td>
            </Table.Tr>

            {opened && hasChildren && node.children?.map((child: ExpenseNode) => (
                <ExpenseRow key={child.id} node={child} level={level + 1} />
            ))}
        </>
    );
};

export const HierarchicalExpenseTable: React.FC<HierarchicalExpenseTableProps> = ({ data, isLoading }: HierarchicalExpenseTableProps) => {
    if (isLoading) return <Text size="sm" c="dimmed">Loading expenses...</Text>;
    if (!data || data.length === 0) return <Text size="sm" c="dimmed">No expense data found.</Text>;

    return (
        <Box mt="xl">
            <Text fw={700} size="lg" mb="md">Detailed Expense Breakdown (Current Year) - in Lakhs</Text>
            <Table.ScrollContainer minWidth={1200}>
                <Table withBorder withColumnBorders striped highlightOnHover>
                    <Table.Thead style={{ position: 'sticky', top: 0, background: 'white', zIndex: 10 }}>
                        <Table.Tr>
                            <Table.Th style={{
                                position: 'sticky',
                                left: 0,
                                background: 'white',
                                zIndex: 11,
                                borderRight: '1px solid #dee2e6'
                            }}>
                                Item / Name
                            </Table.Th>
                            {/* Hidden Emp ID column as per request, now merged with name */}
                            {MONTH_LABELS.map(m => (
                                <Table.Th key={m} align="right">{m}</Table.Th>
                            ))}
                            <Table.Th align="right">Total</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {data.map((node: ExpenseNode) => (
                            <ExpenseRow key={node.id} node={node} level={0} />
                        ))}
                    </Table.Tbody>
                </Table>
            </Table.ScrollContainer>
        </Box>
    );
};
