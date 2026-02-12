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
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { scaleIn } from '@/lib/animations';
import Link from 'next/link';
import { RecurrenceSelector } from './RecurrenceSelector';
import { DayOfWeekPicker } from './DayOfWeekPicker';
import { DayOfMonthPicker } from './DayOfMonthPicker';

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

interface CreateTaskDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (taskData: TaskData) => Promise<void>;
  isSubmitting?: boolean;
}

export function CreateTaskDialog({ isOpen, onOpenChange, onSubmit, isSubmitting = false }: CreateTaskDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<string>('Medium');
  const [dueDate, setDueDate] = useState<string>('');
  const [recurrence, setRecurrence] = useState<string | null>(null);
  const [recurrenceDayOfWeek, setRecurrenceDayOfWeek] = useState<number | null>(null);
  const [recurrenceDayOfMonth, setRecurrenceDayOfMonth] = useState<number | null>(null);
  const [tags, setTags] = useState<string>('');
  const prefersReducedMotion = useReducedMotion();

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

        // Reset form
        setTitle('');
        setDescription('');
        setPriority('Medium');
        setDueDate('');
        setRecurrence(null);
        setRecurrenceDayOfWeek(null);
        setRecurrenceDayOfMonth(null);
        setTags('');
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
            <DialogTitle>Create New Task</DialogTitle>
            <DialogDescription>
              Add a new task with optional recurrence, priority, and due date.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} id="create-task-form">
            <div className="grid gap-4 py-4">
              {/* Title */}
              <div className="space-y-2">
                <Label htmlFor="title">
                  Title <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter task title"
                  required
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter task description (optional)"
                  rows={3}
                />
              </div>

              {/* Priority */}
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger id="priority">
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
                <Label htmlFor="due-date">Due Date</Label>
                <Input
                  id="due-date"
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
                <Label htmlFor="tags">Tags</Label>
                <Input
                  id="tags"
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
              <div className='flex justify-end md:justify-center items-center gap-2 mt-2'>
                <Button type="submit" form="create-task-form" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <span className="animate-spin mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full inline-block align-middle"></span>
                      Creating...
                    </>
                  ) : (
                    'Create Task'
                  )}
                </Button>
                <Link href="./#testimonials">
                  <Button variant="secondary">
                    Your Feedback
                  </Button>
                </Link>
              </div>
            </DialogFooter>
          </form>
        </motion.div>
      </DialogContent>
    </Dialog>
  );
}