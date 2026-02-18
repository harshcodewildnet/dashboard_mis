/**
 * Formats a number in Lakhs with suffix 'L'
 * Example: 1,50,00,000 -> 150.00 L
 */
export const formatCurrency = (amount: number) => {
    const inLakhs = (amount || 0) / 100000;
    // Use 2 decimal places for precision
    return `₹${inLakhs.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })} L`;
};

/**
 * Estimates the width in pixels required for the Y-Axis label.
 * Since values are now in Lakhs, labels are generally shorter.
 */
export const getYAxisWidth = (values: number[], baseMargin: number = 10) => {
    if (!values || values.length === 0) return 60;

    const absValues = values.map(v => Math.abs(v || 0));
    const maxVal = Math.max(...absValues);
    const formatted = formatCurrency(maxVal);

    // Estimation: ~8px per character
    return Math.max(65, formatted.length * 8 + baseMargin);
};
