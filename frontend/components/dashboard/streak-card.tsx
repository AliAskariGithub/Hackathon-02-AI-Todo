'use client';

import { Card } from '@/components/ui/card';
import { Flame, Trophy, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface Task {
  id: string;
  completed: boolean;
  completed_at?: string | null;
  created_at?: string;
}

interface StreakCardProps {
  tasks: Task[];
}

export function StreakCard({ tasks }: StreakCardProps) {
  // Calculate current streak and longest streak
  const calculateStreaks = () => {
    // Get all completed tasks sorted by completion date
    const completedTasks = tasks
      .filter(task => task.completed && task.completed_at)
      .sort((a, b) => {
        const dateA = new Date(a.completed_at!).getTime();
        const dateB = new Date(b.completed_at!).getTime();
        return dateB - dateA; // Most recent first
      });

    if (completedTasks.length === 0) {
      return { currentStreak: 0, longestStreak: 0, todayCompleted: 0 };
    }

    // Count tasks completed today
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayCompleted = completedTasks.filter(task => {
      const completedDate = new Date(task.completed_at!);
      completedDate.setHours(0, 0, 0, 0);
      return completedDate.getTime() === today.getTime();
    }).length;

    // Group tasks by date
    const tasksByDate = new Map<string, number>();
    completedTasks.forEach(task => {
      const date = new Date(task.completed_at!);
      date.setHours(0, 0, 0, 0);
      const dateKey = date.toISOString().split('T')[0];
      tasksByDate.set(dateKey, (tasksByDate.get(dateKey) || 0) + 1);
    });

    // Calculate current streak
    let currentStreak = 0;
    const checkDate = new Date();
    checkDate.setHours(0, 0, 0, 0);

    while (true) {
      const dateKey = checkDate.toISOString().split('T')[0];
      if (tasksByDate.has(dateKey)) {
        currentStreak++;
        checkDate.setDate(checkDate.getDate() - 1);
      } else {
        break;
      }
    }

    // Calculate longest streak
    let longestStreak = 0;
    let tempStreak = 0;
    const sortedDates = Array.from(tasksByDate.keys()).sort().reverse();

    for (let i = 0; i < sortedDates.length; i++) {
      if (i === 0) {
        tempStreak = 1;
      } else {
        const currentDate = new Date(sortedDates[i]);
        const prevDate = new Date(sortedDates[i - 1]);
        const dayDiff = Math.floor((prevDate.getTime() - currentDate.getTime()) / (1000 * 60 * 60 * 24));

        if (dayDiff === 1) {
          tempStreak++;
        } else {
          longestStreak = Math.max(longestStreak, tempStreak);
          tempStreak = 1;
        }
      }
    }
    longestStreak = Math.max(longestStreak, tempStreak);

    return { currentStreak, longestStreak, todayCompleted };
  };

  const { currentStreak, longestStreak, todayCompleted } = calculateStreaks();

  // Determine streak level for visual feedback
  const getStreakLevel = (streak: number) => {
    if (streak >= 30) return { level: 'legendary', color: 'from-purple-500 to-pink-500', emoji: '🏆' };
    if (streak >= 14) return { level: 'amazing', color: 'from-orange-500 to-red-500', emoji: '🔥' };
    if (streak >= 7) return { level: 'great', color: 'from-yellow-500 to-orange-500', emoji: '⭐' };
    if (streak >= 3) return { level: 'good', color: 'from-green-500 to-emerald-500', emoji: '✨' };
    return { level: 'starting', color: 'from-blue-500 to-cyan-500', emoji: '🌱' };
  };

  const streakInfo = getStreakLevel(currentStreak);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.1 }}
    >
      <Card className={cn(
        "relative overflow-hidden",
        currentStreak > 0 && "bg-gradient-to-br from-primary/5 to-transparent"
      )}>
        {/* Background Glow Effect */}
        {currentStreak >= 7 && (
          <div className={cn(
            "absolute inset-0 bg-gradient-to-br opacity-10 blur-2xl",
            streakInfo.color
          )} />
        )}

        <div className="relative p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={cn(
                "flex items-center justify-center w-12 h-12 rounded-full",
                currentStreak > 0
                  ? `bg-gradient-to-br ${streakInfo.color}`
                  : "bg-muted"
              )}>
                {currentStreak > 0 ? (
                  <span className="text-2xl">{streakInfo.emoji}</span>
                ) : (
                  <Flame className="w-6 h-6 text-muted-foreground" />
                )}
              </div>
              <div>
                <h3 className="text-sm font-semibold text-muted-foreground">
                  Current Streak
                </h3>
                <div className="flex items-baseline gap-2">
                  <p className="text-3xl font-bold">
                    {currentStreak}
                  </p>
                  <span className="text-sm text-muted-foreground">
                    {currentStreak === 1 ? 'day' : 'days'}
                  </span>
                </div>
              </div>
            </div>

            {longestStreak > currentStreak && (
              <div className="text-right">
                <div className="flex items-center gap-1 text-muted-foreground mb-1">
                  <Trophy className="w-3 h-3" />
                  <span className="text-xs font-medium">Best</span>
                </div>
                <p className="text-xl font-bold text-muted-foreground">
                  {longestStreak}
                </p>
              </div>
            )}
          </div>

          {/* Today's Progress */}
          <div className="flex items-center justify-between pt-4 border-t border-border/50">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                Today
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">
                {todayCompleted} {todayCompleted === 1 ? 'task' : 'tasks'} completed
              </span>
              {todayCompleted > 0 && (
                <span className="text-xs text-emerald-500 font-medium">
                  ✓
                </span>
              )}
            </div>
          </div>

          {/* Motivational Message */}
          {currentStreak > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-4 p-3 rounded-lg bg-primary/5 border border-primary/10"
            >
              <p className="text-xs text-center font-medium text-primary">
                {currentStreak >= 30 && "Legendary! You're unstoppable! 🏆"}
                {currentStreak >= 14 && currentStreak < 30 && "On fire! Keep the momentum going! 🔥"}
                {currentStreak >= 7 && currentStreak < 14 && "Great streak! You're building a habit! ⭐"}
                {currentStreak >= 3 && currentStreak < 7 && "Nice work! Keep it up! ✨"}
                {currentStreak < 3 && "You're on a roll! 🌱"}
              </p>
            </motion.div>
          )}

          {/* No Streak Message */}
          {currentStreak === 0 && (
            <div className="mt-4 p-3 rounded-lg bg-muted/30">
              <p className="text-xs text-center text-muted-foreground">
                Complete a task today to start your streak! 🚀
              </p>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
