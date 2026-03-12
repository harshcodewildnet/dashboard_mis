import { useState } from "react";
import { Button, Group, Modal, Select, Text, Stack, rem, Paper } from "@mantine/core";
import { IconCalendarStats, IconAdjustmentsHorizontal } from "@tabler/icons-react";

export interface MonthRangeFilterProps {
    value: { months?: number; from_date?: string; to_date?: string };
    onChange: (range: { months?: number; from_date?: string; to_date?: string }) => void;
    defaultMonths?: number;
}

export function MonthRangeFilter({ value, onChange, defaultMonths = 3 }: MonthRangeFilterProps) {
    const [modalOpened, setModalOpened] = useState(false);
    const [customFrom, setCustomFrom] = useState("");
    const [customTo, setCustomTo] = useState("");

    const generateMonthOptions = () => {
        const options: { value: string; label: string }[] = [];
        const now = new Date();
        for (let i = 0; i < 24; i++) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            const value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
            const label = date.toLocaleDateString("en-US", { month: "short", year: "numeric" });
            options.push({ value, label });
        }
        return options;
    };

    const monthOptions = generateMonthOptions();

    const handleMonthsClick = (months: number) => {
        onChange({ months });
    };

    const handleCustomApply = () => {
        if (customFrom && customTo) {
            onChange({ from_date: customFrom, to_date: customTo });
            setModalOpened(false);
        }
    };

    const activeMonths = value.months || (value.from_date || value.to_date ? null : defaultMonths);

    return (
        <>
            <Paper radius="md" p={4} withBorder bg="slate.0">
                <Group gap={4}>
                    {[3, 6, 12].map((m) => (
                        <Button
                            key={m}
                            size="compact-xs"
                            variant={activeMonths === m ? "filled" : "subtle"}
                            color={activeMonths === m ? "indigo.6" : "slate.6"}
                            onClick={() => handleMonthsClick(m)}
                            radius="sm"
                            px="md"
                            fw={700}
                        >
                            {m}M
                        </Button>
                    ))}
                    <Button
                        size="compact-xs"
                        variant={!activeMonths && (value.from_date || value.to_date) ? "filled" : "subtle"}
                        color={!activeMonths && (value.from_date || value.to_date) ? "indigo.6" : "slate.6"}
                        onClick={() => setModalOpened(true)}
                        radius="sm"
                        px="xs"
                    >
                        <IconAdjustmentsHorizontal size={14} />
                    </Button>
                </Group>
            </Paper>

            <Modal
                opened={modalOpened}
                onClose={() => setModalOpened(false)}
                title={
                    <Group gap="xs">
                        <IconCalendarStats size={20} color="var(--mantine-color-indigo-6)" />
                        <Text fw={800} style={{ textTransform: 'uppercase', letterSpacing: rem(0.5) }}>Temporal Range Analysis</Text>
                    </Group>
                }
                size="sm"
                radius="lg"
                padding="xl"
                overlayProps={{
                    backgroundOpacity: 0.55,
                    blur: 3,
                }}
            >
                <Stack gap="lg">
                    <Select
                        label="Historical Start Point"
                        placeholder="Choose month"
                        data={monthOptions}
                        value={customFrom}
                        onChange={(val) => setCustomFrom(val || "")}
                        searchable
                        radius="md"
                    />
                    <Select
                        label="Analysis End Point"
                        placeholder="Choose month"
                        data={monthOptions}
                        value={customTo}
                        onChange={(val) => setCustomTo(val || "")}
                        searchable
                        radius="md"
                    />
                    <Group justify="flex-end" gap="sm" pt="md">
                        <Button variant="light" color="slate" onClick={() => setModalOpened(false)} radius="md">
                            Dismiss
                        </Button>
                        <Button onClick={handleCustomApply} disabled={!customFrom || !customTo} radius="md" color="indigo.6">
                            Apply Filter
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </>
    );
}
