import { useState } from "react";
import { Button, Group, Modal, Select } from "@mantine/core";

export interface MonthRangeFilterProps {
    value: { months?: number; from_date?: string; to_date?: string };
    onChange: (range: { months?: number; from_date?: string; to_date?: string }) => void;
    defaultMonths?: number;
}

export function MonthRangeFilter({ value, onChange, defaultMonths = 3 }: MonthRangeFilterProps) {
    const [modalOpened, setModalOpened] = useState(false);
    const [customFrom, setCustomFrom] = useState("");
    const [customTo, setCustomTo] = useState("");

    // Generate month options for dropdowns (last 24 months)
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
            <Group gap="xs">
                <Button
                    size="xs"
                    variant={activeMonths === 3 ? "filled" : "default"}
                    onClick={() => handleMonthsClick(3)}
                >
                    3M
                </Button>
                <Button
                    size="xs"
                    variant={activeMonths === 6 ? "filled" : "default"}
                    onClick={() => handleMonthsClick(6)}
                >
                    6M
                </Button>
                <Button
                    size="xs"
                    variant={activeMonths === 12 ? "filled" : "default"}
                    onClick={() => handleMonthsClick(12)}
                >
                    12M
                </Button>
                <Button
                    size="xs"
                    variant={!activeMonths && (value.from_date || value.to_date) ? "filled" : "default"}
                    onClick={() => setModalOpened(true)}
                >
                    ⋯
                </Button>
            </Group>

            <Modal
                opened={modalOpened}
                onClose={() => setModalOpened(false)}
                title="Select Custom Date Range"
                size="sm"
            >
                <Select
                    label="From Month"
                    placeholder="Select start month"
                    data={monthOptions}
                    value={customFrom}
                    onChange={(val) => setCustomFrom(val || "")}
                    searchable
                    mb="md"
                />
                <Select
                    label="To Month"
                    placeholder="Select end month"
                    data={monthOptions}
                    value={customTo}
                    onChange={(val) => setCustomTo(val || "")}
                    searchable
                    mb="md"
                />
                <Group justify="flex-end" gap="sm">
                    <Button variant="default" onClick={() => setModalOpened(false)}>
                        Cancel
                    </Button>
                    <Button onClick={handleCustomApply} disabled={!customFrom || !customTo}>
                        Apply
                    </Button>
                </Group>
            </Modal>
        </>
    );
}
