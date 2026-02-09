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
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { scaleIn } from '@/lib/animations';
import Link from 'next/link';

interface CreateTaskDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (taskData: { title: string; description?: string }) => Promise<void>;
  isSubmitting?: boolean;
}

export function CreateTaskDialog({ isOpen, onOpenChange, onSubmit, isSubmitting = false }: CreateTaskDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const prefersReducedMotion = useReducedMotion();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      try {
        await onSubmit({ title: title.trim(), description: description.trim() || undefined });
        setTitle('');
        setDescription('');
      } catch (error) {
        console.error('Error submitting task:', error);
        // Optionally show an error message to the user
      }
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent>
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
              Add a new task to your dashboard. Title is required.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} id="create-task-form">
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="title" className="text-right">
                  Title *
                </Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="col-span-4"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="description" className="text-right">
                  Description
                </Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="col-span-4"
                  rows={3}
                />
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