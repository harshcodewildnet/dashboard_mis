import { DatePickerInput, DatePickerInputProps } from "@mantine/dates";
import { IconCalendar } from "@tabler/icons-react";
import dayjs from "dayjs";
import { useMemo } from "react";
import { rem } from "@mantine/core";

type Props = {
  label?: string;
  value: [Date | null, Date | null];
  onChange: (val: [Date | null, Date | null]) => void;
  minDate?: Date;
  maxDate?: Date;
} & Omit<DatePickerInputProps, "value" | "onChange" | "type">;

export function DateRangePicker({ label = "Select Temporal Window", value, onChange, minDate, maxDate, ...rest }: Props) {
  const placeholder = useMemo(() => {
    if (!value[0] && !value[1]) return "Pick Date Range";
    const [s, e] = value;
    const fmt = (d?: Date | null) => (d ? dayjs(d).format("DD MMM") : "...");
    return `${fmt(s)} — ${fmt(e)}`;
  }, [value]);

  return (
    <DatePickerInput
      type="range"
      label={label}
      placeholder={placeholder}
      value={value as [Date | null, Date | null]}
      onChange={onChange}
      minDate={minDate}
      maxDate={maxDate}
      allowSingleDateInRange
      leftSection={<IconCalendar size={16} color="var(--mantine-color-indigo-6)" stroke={1.5} />}
      leftSectionPointerEvents="none"
      size="sm"
      radius="md"
      w={280}
      styles={{
        input: {
            fontWeight: 600,
            borderWidth: rem(1.5),
        }
      }}
    />
  );
}
