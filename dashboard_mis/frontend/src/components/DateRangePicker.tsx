import { DatePickerInput, DatePickerInputProps } from "@mantine/dates";
import dayjs from "dayjs";
import { useMemo } from "react";

type Props = {
  label?: string;
  value: [Date | null, Date | null];
  onChange: (val: [Date | null, Date | null]) => void;
  minDate?: Date;
  maxDate?: Date;
} & Omit<DatePickerInputProps, "value" | "onChange" | "type">;

export function DateRangePicker({ label = "Date range", value, onChange, minDate, maxDate, ...rest }: Props) {
  const placeholder = useMemo(() => {
    if (!value[0] && !value[1]) return "Select dates";
    const [s, e] = value;
    const fmt = (d?: Date | null) => (d ? dayjs(d).format("YYYY-MM-DD") : "?");
    return `${fmt(s)} → ${fmt(e)}`;
  }, [value]);

  return (
    <DatePickerInput
      type="range"
      label={label}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      minDate={minDate}
      maxDate={maxDate}
      allowSingleDateInRange
      {...rest}
    />
  );
}
