'use client';

import { useAuth } from '@/providers/auth-provider';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useOptimistic, startTransition } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import apiClient from '@/services/api-client';
import { PageWrapper } from '@/components/ui/page-wrapper';
import { SummaryCards } from '@/components/dashboard/summary-cards';
import { FloatingActionButton } from '@/components/ui/floating-action-button';
import { CreateTaskDialog } from '@/components/tasks/create-task-dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import {
  CheckCircle2,
  Trash2,
  RotateCcw,
  Sparkles,
  ClipboardList,
  Search,
  Calendar,
  Edit,
  Maximize2,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from '@/hooks/use-toast';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { SelectSeparator } from '@/components/ui/select';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at?: string;
  updated_at?: string;
}

// API client for backend connection (now uses cookies, no token needed)
const taskApi = {
  getTasks: async (userId: string): Promise<Task[]> => {
    return apiClient.get<Task[]>(`/api/${userId}/tasks`);
  },
  createTask: async (userId: string, taskData: Omit<Task, 'id'>): Promise<Task> => {
    return apiClient.post<Task>(`/api/${userId}/tasks`, taskData);
  },
  updateTask: async (userId: string, id: string, taskData: Partial<Task>): Promise<Task> => {
    return apiClient.put<Task>(`/api/${userId}/tasks/${id}`, taskData);
  },
  deleteTask: async (userId: string, id: string): Promise<{ success: boolean }> => {
    try {
      await apiClient.delete(`/api/${userId}/tasks/${id}`);
      return { success: true };
    } catch (error) {
      console.error('Error deleting task:', error);
      return { success: false };
    }
  }
};

export default function DashboardPage() {
  const { session, isLoading } = useAuth();
  const router = useRouter();
  const prefersReducedMotion = useReducedMotion();

  interface OptimisticTask {
    type: 'add' | 'update' | 'delete';
    data: Task;
  }

  // State management
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isCreatingTask, setIsCreatingTask] = useState(false);
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null);
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'created_at' | 'updated_at' | 'title'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [fullscreenTask, setFullscreenTask] = useState<Task | null>(null);
  const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);
  const [isFullscreenUpdating, setIsFullscreenUpdating] = useState(false);

  // Optimistic updates
  const [optimisticTasks, addOptimisticTask] = useOptimistic(
    tasks,
    (state, newTask: OptimisticTask) => {
      if (newTask.type === 'add') {
        return [{ ...newTask.data, id: 'optimistic-' + Date.now() }, ...state];
      }
      if (newTask.type === 'update') {
        return state.map(t =>
          t.id === newTask.data.id ? { ...t, ...newTask.data } : t
        );
      }
      if (newTask.type === 'delete') {
        return state.filter(t => t.id !== newTask.data.id);
      }
      return state;
    }
  );

  // Load tasks on mount - MUST be before any early returns (Rules of Hooks)
  useEffect(() => {
    // Check for token in localStorage as fallback
    const hasToken = typeof window !== 'undefined' && localStorage.getItem('access_token');

    // Don't do anything while loading
    if (isLoading) {
      return;
    }

    // Redirect to login if no session and no token
    if (!session && !hasToken) {
      router.push('/login');
      return;
    }

    // Wait for auth provider to initialize if we have token but no session
    if (hasToken && !session) {
      console.log('Token exists, waiting for session to initialize...');
      return;
    }

    // Load tasks if we have a session
    if (session) {
      const loadTasks = async () => {
        setIsLoadingTasks(true);
        const userId = session?.user?.id;
        try {
          if (userId) {
            const loadedTasks = await taskApi.getTasks(userId);
            setTasks(loadedTasks as Task[]);
          }
        } catch (error) {
          console.error('Error loading tasks:', error);
        } finally {
          setIsLoadingTasks(false);
        }
      };
      loadTasks();
    }
  }, [session, isLoading, router]);

  // Show loading state while auth is initializing
  if (isLoading) {
    return (
      <PageWrapper>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="flex flex-col items-center gap-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="h-8 w-8 text-primary" />
            </motion.div>
            <p className="text-muted-foreground">Loading your dashboard...</p>
          </div>
        </div>
      </PageWrapper>
    );
  }

  // Show loading state while waiting for session to initialize (has token but no session yet)
  const hasToken = typeof window !== 'undefined' && localStorage.getItem('access_token');
  if (!session && hasToken) {
    return (
      <PageWrapper>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="flex flex-col items-center gap-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="h-8 w-8 text-primary" />
            </motion.div>
            <p className="text-muted-foreground">Initializing session...</p>
          </div>
        </div>
      </PageWrapper>
    );
  }

  // Handle task creation via dialog
  const handleAddTaskViaDialog = async (taskData: { title: string; description?: string }) => {
    const newTask: Omit<Task, 'id'> = {
      title: taskData.title,
      description: taskData.description,
      completed: false,
    };

    const tempId = 'optimistic-' + Date.now();

    // Optimistically add task
    startTransition(() => {
      addOptimisticTask({ type: 'add', data: { ...newTask, id: tempId } });
    });

    const userId = session?.user?.id;
    if (userId) {
      try {
        const createdTask: Task = await taskApi.createTask(userId, newTask);
        setTasks(prev => [createdTask, ...prev.filter(t => !t.id.startsWith('optimistic-'))]);

        // Show success toast
        toast({
          variant: "success",
          title: "Task Created!",
          description: `"${taskData.title}" has been added to your tasks.`,
        });

        return createdTask;
      } catch (error) {
        console.error('Error creating task:', error);
        setTasks(prev => prev.filter(t => !t.id.startsWith('optimistic-')));

        // Show error toast
        toast({
          variant: "destructive",
          title: "Failed to Create Task",
          description: "Could not create the task. Please try again.",
        });

        throw error;
      }
    } else {
      setTasks(prev => prev.filter(t => !t.id.startsWith('optimistic-')));

      toast({
        variant: "destructive",
        title: "Authentication Error",
        description: "No user session available. Please log in again.",
      });

      throw new Error('No user session available');
    }
  };

  // Handle dialog submission
  const handleDialogSubmit = async (taskData: { title: string; description?: string }) => {
    setIsCreatingTask(true);
    try {
      await handleAddTaskViaDialog(taskData);
      setIsCreateDialogOpen(false);
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setIsCreatingTask(false);
    }
  };

  // Toggle task completion
  const handleToggleTask = async (task: Task) => {
    setUpdatingTaskId(task.id);
    const updatedTask = { ...task, completed: !task.completed };

    // Optimistically update
    addOptimisticTask({ type: 'update', data: updatedTask });

    const userId = session?.user?.id;
    if (userId) {
      try {
        await taskApi.updateTask(userId, task.id, updatedTask);
        setTasks(prev => prev.map(t => t.id === task.id ? updatedTask : t));

        // Show success toast
        toast({
          variant: "success",
          title: updatedTask.completed ? "Task Completed!" : "Task Reactivated",
          description: updatedTask.completed
            ? `"${task.title}" marked as complete.`
            : `"${task.title}" marked as active.`,
        });
      } catch (error) {
        console.error('Error updating task:', error);
        // Revert optimistic update on error
        addOptimisticTask({ type: 'update', data: task });

        toast({
          variant: "destructive",
          title: "Update Failed",
          description: "Could not update task status. Please try again.",
        });
      } finally {
        setUpdatingTaskId(null);
      }
    } else {
      setUpdatingTaskId(null);
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId: string) => {
    setDeletingTaskId(taskId);

    // Find the task to get its title for the toast
    const taskToDelete = tasks.find(t => t.id === taskId);

    // Optimistically delete
    addOptimisticTask({ type: 'delete', data: { id: taskId, title: '', completed: false } });

    const userId = session?.user?.id;
    if (userId) {
      try {
        await taskApi.deleteTask(userId, taskId);
        setTasks(prev => prev.filter(t => t.id !== taskId));

        // Show success toast
        toast({
          variant: "success",
          title: "Task Deleted",
          description: taskToDelete
            ? `"${taskToDelete.title}" has been removed.`
            : "Task has been removed successfully.",
        });
      } catch (error) {
        console.error('Error deleting task:', error);

        toast({
          variant: "destructive",
          title: "Delete Failed",
          description: "Could not delete task. Please try again.",
        });
      } finally {
        setDeletingTaskId(null);
      }
    } else {
      setDeletingTaskId(null);
    }
  };

  // Edit task
  const handleEditTask = async (taskId: string, updates: { title: string; description?: string }) => {
    const userId = session?.user?.id;
    if (userId) {
      try {
        const updatedTask = await taskApi.updateTask(userId, taskId, updates);
        setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
        setIsEditDialogOpen(false);
        setEditingTask(null);

        // Show success toast
        toast({
          variant: "success",
          title: "Task Updated!",
          description: `"${updates.title}" has been updated successfully.`,
        });
      } catch (error) {
        console.error('Error updating task:', error);

        toast({
          variant: "destructive",
          title: "Update Failed",
          description: "Could not update task. Please try again.",
        });

        throw error;
      }
    }
  };

  // Open edit dialog
  const openEditDialog = (task: Task) => {
    setEditingTask(task);
    setIsEditDialogOpen(true);
  };

  // Open fullscreen dialog
  const openFullscreen = (task: Task) => {
    setFullscreenTask(task);
    setIsFullscreenOpen(true);
  };

  // Toggle sort order
  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  // Handle fullscreen task toggle with loading state and toast
  const handleFullscreenToggle = async (task: Task) => {
    setIsFullscreenUpdating(true);
    const updatedTask = { ...task, completed: !task.completed };

    // Optimistically update
    addOptimisticTask({ type: 'update', data: updatedTask });
    setFullscreenTask(updatedTask);

    const userId = session?.user?.id;
    if (userId) {
      try {
        await taskApi.updateTask(userId, task.id, updatedTask);
        setTasks(prev => prev.map(t => t.id === task.id ? updatedTask : t));

        // Show success toast
        toast({
          variant: "success",
          title: updatedTask.completed ? 'Task Completed!' : 'Task Reactivated',
          description: updatedTask.completed
            ? `"${task.title}" has been marked as complete.`
            : `"${task.title}" has been marked as active.`,
        });
      } catch (error) {
        console.error('Error updating task:', error);
        // Revert optimistic update on error
        addOptimisticTask({ type: 'update', data: task });
        setFullscreenTask(task);

        toast({
          variant: "destructive",
          title: 'Error',
          description: 'Failed to update task. Please try again.',
        });
      } finally {
        setIsFullscreenUpdating(false);
      }
    } else {
      setIsFullscreenUpdating(false);
    }
  };

  // Filter, search, and sort tasks
  const filteredTasks = optimisticTasks
    .filter(task => {
      if (filter === 'active') return !task.completed;
      if (filter === 'completed') return task.completed;
      return true;
    })
    .filter(task =>
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()))
    )
    .sort((a, b) => {
      let comparison = 0;

      if (sortBy === 'title') {
        comparison = a.title.localeCompare(b.title);
      } else if (sortBy === 'created_at' && a.created_at && b.created_at) {
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      } else if (sortBy === 'updated_at' && a.updated_at && b.updated_at) {
        comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

  // Calculate statistics
  const totalTasks = optimisticTasks.length;
  const completedTasks = optimisticTasks.filter(task => task.completed).length;
  const remainingTasks = totalTasks - completedTasks;

  // Loading state
  if (isLoadingTasks) {
    return (
      <PageWrapper className="min-h-screen py-20 relative overflow-hidden">
        <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] right-[-5%] w-125 h-125 rounded-full bg-primary/5 blur-[100px] animate-pulse-slow" />
          <div className="absolute bottom-[-10%] left-[-5%] w-150 h-150 rounded-full bg-purple-500/5 blur-[120px] animate-pulse-slow delay-1000" />
        </div>

        <div className="container mx-auto py-8 px-4 max-w-6xl">
          <Skeleton className="h-12 w-64 mb-4" />
          <Skeleton className="h-6 w-96 mb-12" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Skeleton className="h-32 rounded-2xl" />
            <Skeleton className="h-32 rounded-2xl" />
            <Skeleton className="h-32 rounded-2xl" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-48 rounded-2xl" />
            ))}
          </div>
        </div>
      </PageWrapper>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <PageWrapper className="min-h-screen py-20 relative overflow-hidden">
      {/* Dynamic Background Mesh */}
      <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-125 h-125 rounded-full bg-primary/5 blur-[100px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] left-[-5%] w-150 h-150 rounded-full bg-purple-500/5 blur-[120px] animate-pulse-slow delay-1000" />
      </div>

      <div className="container mx-auto py-8 px-4 max-w-6xl relative z-10">
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12"
        >
          <div>
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="text-4xl md:text-5xl font-black tracking-tight"
            >
              Good <span className="text-transparent bg-clip-text bg-linear-to-r from-primary to-emerald-400">Morning</span>,
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="text-xl text-muted-foreground mt-2 font-light"
            >
              {session?.user?.name || 'User'}. Ready to conquer the day?
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="flex items-center justify-between gap-2 bg-background/50 backdrop-blur-md p-1 rounded-full border border-border/50"
          >
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tasks..."
                className="pl-9 h-10 w-full md:w-64 bg-transparent border-none focus-visible:ring-0 rounded-full"
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button size="icon" variant="ghost" className="rounded-full mr-2">
                  <ArrowUpDown className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-max pr-2">
                <DropdownMenuItem onClick={() => setSortBy('created_at')}>
                  <Calendar className="w-max h-4" />
                  Sort by Created Date
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy('updated_at')}>
                  <Calendar className="w-max h-4" />
                  Sort by Updated Date
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setSortBy('title')}>
                  <ClipboardList className="w-max h-4" />
                  Sort by Title
                </DropdownMenuItem>
                <SelectSeparator />
                <DropdownMenuItem onClick={toggleSortOrder}>
                  {sortOrder === 'asc' ? <ArrowDown className="w-max h-4" /> : <ArrowUp className="w-max h-4" />}
                  {sortOrder === 'asc' ? 'Descending' : 'Ascending'}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </motion.div>
        </motion.div>

        {/* Summary Cards */}
        <SummaryCards
          totalTasks={totalTasks}
          completedTasks={completedTasks}
          remainingTasks={remainingTasks}
          isLoading={isLoadingTasks && optimisticTasks.length === 0}
        />

        {/* Tasks Grid */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <ClipboardList className="w-6 h-6 text-primary" />
              Tasks
            </h2>
            <div className="flex gap-2 p-1 bg-muted/30 rounded-lg">
              {(['all', 'active', 'completed'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={cn(
                    "px-4 py-1.5 rounded-md text-sm font-medium transition-all",
                    filter === f
                      ? "bg-background shadow text-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <motion.div
            layout
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            <AnimatePresence mode="popLayout">
              {isLoadingTasks && optimisticTasks.length === 0 ? (
                // Loading skeletons
                Array.from({ length: 6 }).map((_, i) => (
                  <motion.div
                    key={`skeleton-${i}`}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <Skeleton className="h-48 rounded-2xl" />
                  </motion.div>
                ))
              ) : filteredTasks.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="col-span-full py-20 text-center"
                >
                  <div className="w-24 h-24 bg-muted/30 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Sparkles className="w-10 h-10 text-muted-foreground/50" />
                  </div>
                  <h3 className="text-xl font-semibold text-muted-foreground">
                    {searchQuery ? 'No tasks found' : 'All caught up!'}
                  </h3>
                  <p className="text-muted-foreground/60">
                    {searchQuery
                      ? 'Try adjusting your search or filters.'
                      : 'No tasks found. Create your first task!'}
                  </p>
                </motion.div>
              ) : (
                filteredTasks.map((task, index) => (
                  <motion.div
                    key={task.id}
                    layout
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
                    transition={{
                      duration: prefersReducedMotion ? 0 : 0.3,
                      delay: prefersReducedMotion ? 0 : Math.min(index * 0.05, 0.3)
                    }}
                    whileHover={prefersReducedMotion ? {} : { y: -5, transition: { duration: 0.2 } }}
                    className="group"
                  >
                    <div className={cn(
                      "h-full relative bg-background/40 backdrop-blur-md border border-white/5 rounded-2xl p-5 transition-all duration-300",
                      "hover:shadow-xl hover:shadow-primary/5 hover:border-primary/20",
                      task.completed && "opacity-60 bg-muted/20 grayscale-[0.5]"
                    )}>
                      {/* Glow Effect */}
                      <div className="absolute inset-0 bg-linear-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl pointer-events-none" />

                      <div className="relative z-10 flex flex-col h-full justify-between gap-4">
                        <div>
                          <div className="flex items-start justify-between gap-3 mb-2">
                            <h3 className={cn(
                              "font-semibold text-lg leading-tight transition-all",
                              task.completed && "line-through text-muted-foreground"
                            )}>
                              {task.title}
                            </h3>
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 rounded-full"
                                onClick={() => openEditDialog(task)}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 rounded-full"
                                onClick={() => openFullscreen(task)}
                              >
                                <Maximize2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                          {task.description && (
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {task.description}
                            </p>
                          )}
                        </div>

                        <div className="pt-4 border-t border-white/5 flex items-center justify-between gap-2 mt-auto">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleToggleTask(task)}
                            disabled={updatingTaskId === task.id}
                            className={cn(
                              "flex-1 justify-start gap-2 h-9 rounded-xl transition-colors",
                              task.completed
                                ? "text-orange-500 hover:text-orange-600 hover:bg-orange-500/10"
                                : "text-emerald-500 hover:text-emerald-600 hover:bg-emerald-500/10"
                            )}
                          >
                            {updatingTaskId === task.id ? (
                              <>
                                <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                                <span className="font-medium">{task.completed ? 'Undoing...' : 'Completing...'}</span>
                              </>
                            ) : (
                              <>
                                {task.completed ? <RotateCcw className="w-4 h-4" /> : <CheckCircle2 className="w-4 h-4" />}
                                <span className="font-medium">{task.completed ? "Undo" : "Mark as Complete"}</span>
                              </>
                            )}
                          </Button>

                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeleteTask(task.id)}
                            disabled={deletingTaskId === task.id}
                            className="h-9 w-9 rounded-xl text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                          >
                            {deletingTaskId === task.id ? (
                              <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>

      {/* Floating Action Button */}
      <FloatingActionButton
        onClick={() => setIsCreateDialogOpen(true)}
        label="Create new task"
      />

      {/* Create Task Dialog */}
      <CreateTaskDialog
        isOpen={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSubmit={handleDialogSubmit}
        isSubmitting={isCreatingTask}
      />

      {/* Edit Task Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>
              Update the task title and description.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const title = formData.get('title') as string;
              const description = formData.get('description') as string;

              if (editingTask) {
                try {
                  await handleEditTask(editingTask.id, { title, description });
                } catch (error) {
                  console.error('Failed to update task:', error);
                }
              }
            }}
          >
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-title">Title</Label>
                <Input
                  id="edit-title"
                  name="title"
                  defaultValue={editingTask?.title}
                  placeholder="Task title"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  name="description"
                  defaultValue={editingTask?.description}
                  placeholder="Task description (optional)"
                  rows={4}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Save Changes</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Fullscreen Task View Dialog */}
      <Dialog open={isFullscreenOpen} onOpenChange={setIsFullscreenOpen}>
        <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl">{fullscreenTask?.title}</DialogTitle>
            <DialogDescription>
              {fullscreenTask?.completed ? (
                <span className="inline-flex items-center gap-1 text-emerald-600">
                  <CheckCircle2 className="w-4 h-4" />
                  Completed
                </span>
              ) : (
                <span className="text-muted-foreground">Active Task</span>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 py-4">
            {/* Task Details */}
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-muted-foreground mb-2">Description</h3>
                <div className="bg-muted/30 rounded-lg p-4">
                  {fullscreenTask?.description ? (
                    <p className="text-sm whitespace-pre-wrap">{fullscreenTask.description}</p>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No description provided</p>
                  )}
                </div>
              </div>

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4">
                {fullscreenTask?.created_at && (
                  <div>
                    <h3 className="text-sm font-semibold text-muted-foreground mb-2">Created</h3>
                    <div className="bg-muted/30 rounded-lg p-3">
                      <p className="text-sm">
                        {new Date(fullscreenTask.created_at).toLocaleString('en-US', {
                          dateStyle: 'medium',
                          timeStyle: 'short'
                        })}
                      </p>
                    </div>
                  </div>
                )}
                {fullscreenTask?.updated_at && (
                  <div>
                    <h3 className="text-sm font-semibold text-muted-foreground mb-2">Last Updated</h3>
                    <div className="bg-muted/30 rounded-lg p-3">
                      <p className="text-sm">
                        {new Date(fullscreenTask.updated_at).toLocaleString('en-US', {
                          dateStyle: 'medium',
                          timeStyle: 'short'
                        })}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Status */}
              <div>
                <h3 className="text-sm font-semibold text-muted-foreground mb-2">Status</h3>
                <div className="bg-muted/30 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    {fullscreenTask?.completed ? (
                      <>
                        <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        <span className="text-sm font-medium text-emerald-600">Completed</span>
                      </>
                    ) : (
                      <>
                        <div className="w-5 h-5 rounded-full border-2 border-muted-foreground" />
                        <span className="text-sm font-medium">Active</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => {
                if (fullscreenTask) {
                  openEditDialog(fullscreenTask);
                  setIsFullscreenOpen(false);
                }
              }}
            >
              <Edit className="w-max h-4" />
              Edit Task
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (fullscreenTask) {
                  handleDeleteTask(fullscreenTask.id);
                  setIsFullscreenOpen(false);
                }
              }}
              disabled={deletingTaskId === fullscreenTask?.id}
            >
              {deletingTaskId === fullscreenTask?.id ? (
                <>
                  <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="w-max h-4" />
                  Delete Task
                </>
              )}
            </Button>
            <Button
              variant={fullscreenTask?.completed ? "outline" : "default"}
              onClick={() => {
                if (fullscreenTask) {
                  handleFullscreenToggle(fullscreenTask);
                }
              }}
              disabled={isFullscreenUpdating}
            >
              {isFullscreenUpdating ? (
                <>
                  <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
                  {fullscreenTask?.completed ? 'Reactivating...' : 'Completing...'}
                </>
              ) : fullscreenTask?.completed ? (
                <>
                  <RotateCcw className="w-max h-4" />
                  Mark as Active
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-max h-4" />
                  Mark as Complete
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </PageWrapper>
  );
}