'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion, useSpring, useTransform } from 'framer-motion';
import { useEffect, useState, cloneElement } from 'react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { CheckCircle, Circle, List, TrendingUp } from 'lucide-react';

interface SummaryCardProps {
  title: string;
  count: number;
  icon?: React.ReactNode;
  color?: string;
  isLoading?: boolean;
  index?: number;
  gradient: string;
}

const SummaryCard = ({
  title,
  count,
  icon,
  isLoading = false,
  index = 0,
  gradient
}: SummaryCardProps) => {
  const prefersReducedMotion = useReducedMotion();
  const springValue = useSpring(0, { stiffness: 50, damping: 15 });
  const displayValue = useTransform(springValue, (current) => Math.round(current));
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    if (!prefersReducedMotion && !hasAnimated) {
      springValue.set(count);
      setTimeout(() => setHasAnimated(true), 0); // Defer the state update
    } else if (prefersReducedMotion) {
      springValue.set(count);
    }
  }, [count, prefersReducedMotion, springValue, hasAnimated]);

  // Update spring target if count changes after initial animation
  useEffect(() => {
    springValue.set(count);
  }, [count, springValue]);

  // Create a large version of the icon for the background
  const largeIcon = icon && React.isValidElement(icon)
    ? cloneElement(icon as React.ReactElement<React.SVGProps<SVGSVGElement>>, {
      className: "w-32 h-32 text-current opacity-100",
      strokeWidth: 1
    })
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        delay: index * 0.1,
        duration: 0.5,
        type: "spring"
      }}
      whileHover={{ y: -5, scale: 1.02 }}
      className="h-full"
    >
      <Card className="overflow-hidden border-border/50 bg-background/40 backdrop-blur-xl shadow-xl hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 h-full relative group">
        <div className={`absolute inset-0 bg-linear-to-br ${gradient} opacity-5 group-hover:opacity-10 transition-opacity duration-500`} />

        {/* Large Background Icon */}
        <div className={`absolute -right-8 -bottom-8 opacity-[0.07] group-hover:opacity-[0.12] transition-opacity duration-500 rotate-12 scale-150 pointer-events-none text-foreground`}>
          {largeIcon}
        </div>

        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0 relative z-10">
          <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">{title}</CardTitle>
          <div className={`p-2 rounded-xl bg-linear-to-br ${gradient} bg-opacity-10 shadow-inner`}>
            {icon || <List className="h-4 w-4 text-muted-foreground" />}
          </div>
        </CardHeader>
        <CardContent className="relative z-10">
          {isLoading ? (
            <div className="h-10 w-24 bg-muted/50 rounded animate-pulse" />
          ) : (
            <div className="flex items-end gap-2">
              <motion.div className="text-4xl font-bold tracking-tight">
                {prefersReducedMotion ? count : <motion.span>{displayValue}</motion.span>}
              </motion.div>
              <div className="mb-1 text-xs text-muted-foreground font-medium flex items-center gap-1">
                <TrendingUp className="w-3 h-3 text-green-500" />
                <span>+12%</span>
              </div>  
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

interface SummaryCardsProps {
  totalTasks: number;
  completedTasks: number;
  remainingTasks: number;
  isLoading?: boolean;
}

import React from 'react';

export const SummaryCards = ({
  totalTasks,
  completedTasks,
  remainingTasks,
  isLoading = false
}: SummaryCardsProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <SummaryCard
        title="Total Tasks"
        count={totalTasks}
        icon={<List className="h-5 w-5 text-white" />}
        gradient="from-blue-500 to-indigo-600"
        isLoading={isLoading}
        index={0}
      />
      <SummaryCard
        title="Completed"
        count={completedTasks}
        icon={<CheckCircle className="h-5 w-5 text-white" />}
        gradient="from-green-500 to-emerald-600"
        isLoading={isLoading}
        index={1}
      />
      <SummaryCard
        title="Remaining"
        count={remainingTasks}
        icon={<Circle className="h-5 w-5 text-white" />}
        gradient="from-orange-500 to-red-600"
        isLoading={isLoading}
        index={2}
      />
    </div>
  );
};

export default SummaryCards;