'use client';

import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface RecurrenceSelectorProps {
  value: string | null;
  onChange: (value: string | null) => void;
  disabled?: boolean;
}

export function RecurrenceSelector({ value, onChange, disabled = false }: RecurrenceSelectorProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="recurrence">Recurrence</Label>
      <Select
        value={value || 'none'}
        onValueChange={(val) => onChange(val === 'none' ? null : val)}
        disabled={disabled}
      >
        <SelectTrigger id="recurrence" className="w-full">
          <SelectValue placeholder="Select recurrence pattern" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="none">No recurrence</SelectItem>
          <SelectItem value="Daily">Daily</SelectItem>
          <SelectItem value="Weekly">Weekly</SelectItem>
          <SelectItem value="Monthly">Monthly</SelectItem>
        </SelectContent>
      </Select>
      {value && (
        <p className="text-sm text-muted-foreground">
          {value === 'Daily' && 'Task will repeat every day'}
          {value === 'Weekly' && 'Task will repeat every week on a specific day'}
          {value === 'Monthly' && 'Task will repeat every month on a specific day'}
        </p>
      )}
    </div>
  );
}
