'use client';

import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface DayOfMonthPickerProps {
  value: number | null;
  onChange: (value: number | null) => void;
  disabled?: boolean;
}

// Generate days 1-31
const DAYS_OF_MONTH = Array.from({ length: 31 }, (_, i) => i + 1);

// Helper function to get ordinal suffix
function getOrdinalSuffix(day: number): string {
  if (day >= 11 && day <= 13) return 'th';
  switch (day % 10) {
    case 1: return 'st';
    case 2: return 'nd';
    case 3: return 'rd';
    default: return 'th';
  }
}

export function DayOfMonthPicker({ value, onChange, disabled = false }: DayOfMonthPickerProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="day-of-month">Day of Month</Label>
      <Select
        value={value !== null ? value.toString() : undefined}
        onValueChange={(val) => onChange(parseInt(val, 10))}
        disabled={disabled}
      >
        <SelectTrigger id="day-of-month" className="w-full">
          <SelectValue placeholder="Select day of month" />
        </SelectTrigger>
        <SelectContent className="max-h-[300px]">
          {DAYS_OF_MONTH.map((day) => (
            <SelectItem key={day} value={day.toString()}>
              {day}{getOrdinalSuffix(day)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {value !== null && (
        <p className="text-sm text-muted-foreground">
          Task will repeat on the {value}{getOrdinalSuffix(value)} of every month
        </p>
      )}
      {value !== null && value > 28 && (
        <p className="text-xs text-amber-600 dark:text-amber-400">
          Note: For months with fewer days, the task will be scheduled on the last day of the month
        </p>
      )}
    </div>
  );
}
