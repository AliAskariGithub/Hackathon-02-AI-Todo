'use client';

import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface DayOfWeekPickerProps {
  value: number | null;
  onChange: (value: number | null) => void;
  disabled?: boolean;
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
];

export function DayOfWeekPicker({ value, onChange, disabled = false }: DayOfWeekPickerProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="day-of-week">Day of Week</Label>
      <Select
        value={value !== null ? value.toString() : undefined}
        onValueChange={(val) => onChange(parseInt(val, 10))}
        disabled={disabled}
      >
        <SelectTrigger id="day-of-week" className="w-full">
          <SelectValue placeholder="Select day of week" />
        </SelectTrigger>
        <SelectContent>
          {DAYS_OF_WEEK.map((day) => (
            <SelectItem key={day.value} value={day.value.toString()}>
              {day.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {value !== null && (
        <p className="text-sm text-muted-foreground">
          Task will repeat every {DAYS_OF_WEEK[value].label}
        </p>
      )}
    </div>
  );
}
