'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart3, Eye, EyeOff } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { cn } from '@/lib/utils';

interface Task {
  id: string;
  title: string;
  completed: boolean;
  completed_at?: string | null;
  created_at?: string;
  priority?: string;
  status?: string;
}

interface ProductivityChartsProps {
  tasks: Task[];
}

export function ProductivityCharts({ tasks }: ProductivityChartsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate tasks completed per day (last 7 days)
  const getTasksPerDay = () => {
    const last7Days = [];
    const today = new Date();

    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);

      const completedCount = tasks.filter(task => {
        if (!task.completed || !task.completed_at) return false;
        const completedDate = new Date(task.completed_at);
        completedDate.setHours(0, 0, 0, 0);
        return completedDate.getTime() === date.getTime();
      }).length;

      last7Days.push({
        date: date.toLocaleDateString('en-US', { weekday: 'short' }),
        count: completedCount,
        fullDate: date
      });
    }

    return last7Days;
  };

  // Calculate tasks by priority
  const getTasksByPriority = () => {
    const high = tasks.filter(t => t.priority === 'High').length;
    const medium = tasks.filter(t => t.priority === 'Medium').length;
    const low = tasks.filter(t => t.priority === 'Low').length;
    const none = tasks.filter(t => !t.priority).length;

    return { high, medium, low, none };
  };

  // Calculate tasks by status
  const getTasksByStatus = () => {
    const completed = tasks.filter(t => t.completed).length;
    const active = tasks.filter(t => !t.completed).length;

    return { completed, active };
  };

  // Calculate completion rate
  const getCompletionRate = () => {
    if (tasks.length === 0) return 0;
    const completed = tasks.filter(t => t.completed).length;
    return Math.round((completed / tasks.length) * 100);
  };

  const tasksPerDay = getTasksPerDay();
  const priorityStats = getTasksByPriority();
  const statusStats = getTasksByStatus();
  const completionRate = getCompletionRate();
  const maxCount = Math.max(...tasksPerDay.map(d => d.count), 1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="mb-8"
    >
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-bold">Productivity Analytics</h3>
              <p className="text-sm text-muted-foreground">
                Your task completion insights
              </p>
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="gap-2"
          >
            {isExpanded ? (
              <>
                <EyeOff className="w-4 h-4" />
                Hide Details
              </>
            ) : (
              <>
                <Eye className="w-4 h-4" />
                Show Details
              </>
            )}
          </Button>
        </div>

        {/* Detailed Charts */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-6 overflow-hidden"
            >
              {/* Tasks Completed Per Day (Last 7 Days) */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Tasks Completed (Last 7 Days)</h4>
                <div className="flex items-end justify-between gap-2 h-32">
                  {tasksPerDay.map((day, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center gap-2">
                      <div className="w-full flex items-end justify-center h-24">
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${(day.count / maxCount) * 100}%` }}
                          transition={{ delay: index * 0.1, duration: 0.5 }}
                          className={cn(
                            "w-full rounded-t-lg transition-colors",
                            day.count > 0
                              ? "bg-gradient-to-t from-primary to-primary/50"
                              : "bg-muted/30"
                          )}
                          title={`${day.count} tasks completed`}
                        />
                      </div>
                      <div className="text-center">
                        <p className="text-xs font-medium">{day.date}</p>
                        <p className="text-xs text-muted-foreground">{day.count}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Priority Distribution */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Tasks by Priority</h4>
                <div className="space-y-3">
                  {/* High Priority */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">High Priority</span>
                      <span className="text-sm text-muted-foreground">{priorityStats.high}</span>
                    </div>
                    <div className="h-2 bg-muted/30 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(priorityStats.high / tasks.length) * 100}%` }}
                        transition={{ delay: 0.2, duration: 0.5 }}
                        className="h-full bg-gradient-to-r from-red-500 to-red-600"
                      />
                    </div>
                  </div>

                  {/* Medium Priority */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">Medium Priority</span>
                      <span className="text-sm text-muted-foreground">{priorityStats.medium}</span>
                    </div>
                    <div className="h-2 bg-muted/30 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(priorityStats.medium / tasks.length) * 100}%` }}
                        transition={{ delay: 0.3, duration: 0.5 }}
                        className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600"
                      />
                    </div>
                  </div>

                  {/* Low Priority */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">Low Priority</span>
                      <span className="text-sm text-muted-foreground">{priorityStats.low}</span>
                    </div>
                    <div className="h-2 bg-muted/30 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(priorityStats.low / tasks.length) * 100}%` }}
                        transition={{ delay: 0.4, duration: 0.5 }}
                        className="h-full bg-gradient-to-r from-green-500 to-green-600"
                      />
                    </div>
                  </div>

                  {/* No Priority */}
                  {priorityStats.none > 0 && (
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">No Priority</span>
                        <span className="text-sm text-muted-foreground">{priorityStats.none}</span>
                      </div>
                      <div className="h-2 bg-muted/30 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${(priorityStats.none / tasks.length) * 100}%` }}
                          transition={{ delay: 0.5, duration: 0.5 }}
                          className="h-full bg-gradient-to-r from-gray-500 to-gray-600"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Insights */}
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                <h4 className="text-sm font-semibold mb-2">💡 Insights</h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {completionRate >= 70 && (
                    <li>• Great job! You&apos;re completing {completionRate}% of your tasks.</li>
                  )}
                  {completionRate < 50 && (
                    <li>• Consider breaking down tasks into smaller, manageable pieces.</li>
                  )}
                  {priorityStats.high > priorityStats.medium + priorityStats.low && (
                    <li>• You have many high-priority tasks. Focus on the most urgent ones first.</li>
                  )}
                  {tasksPerDay[6].count > tasksPerDay[5].count && (
                    <li>• You completed more tasks today than yesterday. Keep it up!</li>
                  )}
                  {statusStats.active > statusStats.completed * 2 && (
                    <li>• You have many active tasks. Consider using bulk operations to organize them.</li>
                  )}
                </ul>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
}
