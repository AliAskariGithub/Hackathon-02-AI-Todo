'use client';

import { Card } from '@/components/ui/card';
import { Clock, AlertTriangle, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface Task {
  id: string;
  title: string;
  due_date?: string;
  priority?: string;
  completed: boolean;
}

interface DeadlinesWidgetProps {
  tasks: Task[];
  onTaskClick?: (taskId: string) => void;
}

export function DeadlinesWidget({ tasks, onTaskClick }: DeadlinesWidgetProps) {
  // Get current date
  const now = new Date();

  // Filter tasks with due dates in the next 7 days or overdue
  const upcomingTasks = tasks
    .filter(task => !task.completed && task.due_date)
    .map(task => {
      const dueDate = new Date(task.due_date!);
      const timeDiff = dueDate.getTime() - now.getTime();
      const daysDiff = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
      const hoursDiff = Math.floor(timeDiff / (1000 * 60 * 60));

      return {
        ...task,
        dueDate,
        timeDiff,
        daysDiff,
        hoursDiff,
        isOverdue: timeDiff < 0,
        isDueToday: daysDiff === 0 && timeDiff > 0,
        isDueSoon: daysDiff >= 0 && daysDiff <= 7
      };
    })
    .filter(task => task.isOverdue || task.isDueSoon)
    .sort((a, b) => a.timeDiff - b.timeDiff)
    .slice(0, 5); // Show max 5 tasks

  if (upcomingTasks.length === 0) {
    return null;
  }

  const getTimeRemainingText = (task: typeof upcomingTasks[0]) => {
    if (task.isOverdue) {
      const daysOverdue = Math.abs(task.daysDiff);
      const hoursOverdue = Math.abs(task.hoursDiff);

      if (daysOverdue > 0) {
        return `Overdue by ${daysOverdue} ${daysOverdue === 1 ? 'day' : 'days'}`;
      } else {
        return `Overdue by ${hoursOverdue} ${hoursOverdue === 1 ? 'hour' : 'hours'}`;
      }
    }

    if (task.isDueToday) {
      if (task.hoursDiff < 1) {
        const minutesDiff = Math.floor(task.timeDiff / (1000 * 60));
        return `Due in ${minutesDiff} ${minutesDiff === 1 ? 'minute' : 'minutes'}`;
      }
      return `Due in ${task.hoursDiff} ${task.hoursDiff === 1 ? 'hour' : 'hours'}`;
    }

    return `Due in ${task.daysDiff} ${task.daysDiff === 1 ? 'day' : 'days'}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="mb-8"
    >
      <Card className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border-orange-500/20 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-full bg-orange-500/20">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
          </div>
          <div>
            <h3 className="text-lg font-bold">Upcoming Deadlines</h3>
            <p className="text-sm text-muted-foreground">
              {upcomingTasks.filter(t => t.isOverdue).length > 0
                ? `${upcomingTasks.filter(t => t.isOverdue).length} overdue, ${upcomingTasks.filter(t => !t.isOverdue).length} upcoming`
                : `${upcomingTasks.length} ${upcomingTasks.length === 1 ? 'task' : 'tasks'} due soon`}
            </p>
          </div>
        </div>

        <div className="space-y-2">
          {upcomingTasks.map((task, index) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              onClick={() => onTaskClick?.(task.id)}
              className={cn(
                "flex items-center justify-between p-3 rounded-lg transition-all cursor-pointer",
                "hover:bg-background/50 backdrop-blur-sm",
                task.isOverdue
                  ? "bg-red-500/10 border border-red-500/20"
                  : task.isDueToday
                  ? "bg-orange-500/10 border border-orange-500/20"
                  : "bg-background/30 border border-border/50"
              )}
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className={cn(
                  "flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0",
                  task.isOverdue
                    ? "bg-red-500/20"
                    : task.isDueToday
                    ? "bg-orange-500/20"
                    : "bg-blue-500/20"
                )}>
                  <Clock className={cn(
                    "w-4 h-4",
                    task.isOverdue
                      ? "text-red-500"
                      : task.isDueToday
                      ? "text-orange-500"
                      : "text-blue-500"
                  )} />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{task.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <p className={cn(
                      "text-xs font-medium",
                      task.isOverdue
                        ? "text-red-500"
                        : task.isDueToday
                        ? "text-orange-500"
                        : "text-muted-foreground"
                    )}>
                      {getTimeRemainingText(task)}
                    </p>
                    {task.priority && (
                      <span className={cn(
                        "inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium",
                        task.priority === 'High' && "bg-red-500/10 text-red-500",
                        task.priority === 'Medium' && "bg-yellow-500/10 text-yellow-500",
                        task.priority === 'Low' && "bg-green-500/10 text-green-500"
                      )}>
                        {task.priority}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="text-xs text-muted-foreground flex items-center gap-1 flex-shrink-0">
                <Calendar className="w-3 h-3" />
                {task.dueDate.toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </motion.div>
          ))}
        </div>
      </Card>
    </motion.div>
  );
}
