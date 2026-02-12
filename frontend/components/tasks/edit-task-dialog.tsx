'use client';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { scaleIn } from '@/lib/animations';
import { RecurrenceSelector } from './RecurrenceSelector';
import { DayOfWeekPicker } from './DayOfWeekPicker';
import { DayOfMonthPicker } from './DayOfMonthPicker';

interface Task {
  id: string;
  title: string;
  description?: string;
  priority?: string;
  due_date?: string;
  recurrence?: string | null;
  recurrence_day_of_week?: number | null;
  recurrence_day_of_month?: number | null;
  tags?: string[];
}

interface TaskData {
  title: string;
  description?: string;
  priority?: string;
  due_date?: string;
  recurrence?: string | null;
  recurrence_day_of_week?: number | null;
  recurrence_day_of_month?: number | null;
  tags?: string[];
}

interface EditTaskDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (taskData: TaskData) => Promise<void>;
  task: Task | null;
  isSubmitting?: boolean;
}

export function EditTaskDialog({ isOpen, onOpenChange, onSubmit, task, isSubmitting = false }: EditTaskDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<string>('Medium');
  const [dueDate, setDueDate] = useState<string>('');
  const [recurrence, setRecurrence] = useState<string | null>(null);
  const [recurrenceDayOfWeek, setRecurrenceDayOfWeek] = useState<number | null>(null);
  const [recurrenceDayOfMonth, setRecurrenceDayOfMonth] = useState<number | null>(null);
  const [tags, setTags] = useState<string>('');
  const prefersReducedMotion = useReducedMotion();

  // Update form when task changes
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (task) {
      setTitle(task.title || '');
      setDescription(task.description || '');
      setPriority(task.priority || 'Medium');
      setDueDate(task.due_date || '');
      setRecurrence(task.recurrence || null);
      setRecurrenceDayOfWeek(task.recurrence_day_of_week ?? null);
      setRecurrenceDayOfMonth(task.recurrence_day_of_month ?? null);
      setTags(task.tags?.join(', ') || '');
    }
  }, [task]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      try {
        const taskData: TaskData = {
          title: title.trim(),
          description: description.trim() || undefined,
          priority,
          due_date: dueDate || undefined,
          recurrence: recurrence || undefined,
          recurrence_day_of_week: recurrenceDayOfWeek ?? undefined,
          recurrence_day_of_month: recurrenceDayOfMonth ?? undefined,
          tags: tags.trim() ? tags.split(',').map(t => t.trim()).filter(Boolean) : undefined,
        };

        await onSubmit(taskData);
      } catch (error) {
        console.error('Error submitting task:', error);
      }
    }
  };

  // Reset recurrence-specific fields when recurrence type changes
  const handleRecurrenceChange = (value: string | null) => {
    setRecurrence(value);
    if (value !== 'Weekly') {
      setRecurrenceDayOfWeek(null);
    }
    if (value !== 'Monthly') {
      setRecurrenceDayOfMonth(null);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={prefersReducedMotion ? { duration: 0.1 } : {
            ...scaleIn.transition,
            type: 'spring',
            stiffness: 300,
            damping: 30
          }}
        >
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>
              Update task details including recurrence, priority, and due date.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} id="edit-task-form">
            <div className="grid gap-4 py-4">
              {/* Title */}
              <div className="space-y-2">
                <Label htmlFor="edit-title">
                  Title <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="edit-title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter task title"
                  required
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter task description (optional)"
                  rows={3}
                />
              </div>

              {/* Priority */}
              <div className="space-y-2">
                <Label htmlFor="edit-priority">Priority</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger id="edit-priority">
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="High">High</SelectItem>
                    <SelectItem value="Medium">Medium</SelectItem>
                    <SelectItem value="Low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Due Date */}
              <div className="space-y-2">
                <Label htmlFor="edit-due-date">Due Date</Label>
                <Input
                  id="edit-due-date"
                  type="datetime-local"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>

              {/* Recurrence */}
              <RecurrenceSelector
                value={recurrence}
                onChange={handleRecurrenceChange}
              />

              {/* Day of Week (for Weekly recurrence) */}
              {recurrence === 'Weekly' && (
                <DayOfWeekPicker
                  value={recurrenceDayOfWeek}
                  onChange={setRecurrenceDayOfWeek}
                />
              )}

              {/* Day of Month (for Monthly recurrence) */}
              {recurrence === 'Monthly' && (
                <DayOfMonthPicker
                  value={recurrenceDayOfMonth}
                  onChange={setRecurrenceDayOfMonth}
                />
              )}

              {/* Tags */}
              <div className="space-y-2">
                <Label htmlFor="edit-tags">Tags</Label>
                <Input
                  id="edit-tags"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="Enter tags separated by commas"
                />
                <p className="text-xs text-muted-foreground">
                  Example: shopping, urgent, work
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" form="edit-task-form" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <span className="animate-spin mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full inline-block align-middle"></span>
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </Button>
            </DialogFooter>
          </form>
        </motion.div>
      </DialogContent>
    </Dialog>
  );
}
