'use client';

import { useEffect, useState, useRef } from 'react';
import { analyticsService, type AnalyticsStats } from '@/services/analytics-service';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { RotateCcw, Cloud, Clock, User, TrendingUp } from 'lucide-react';
import { CountUp } from '@/components/ui/count-up';
import { cn } from '@/lib/utils';

// ... (TiltCard implementation remains the same but with enhanced children rendering)
interface TiltCardProps {
  children: React.ReactNode;
  className?: string;
  index: number;
  prefersReducedMotion: boolean;
}

function TiltCard({ children, className, index, prefersReducedMotion }: TiltCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springConfig = { damping: 20, stiffness: 300 };
  const rotateX = useSpring(useTransform(y, [-100, 100], [5, -5]), springConfig); // Reduced tilt for robustness
  const rotateY = useSpring(useTransform(x, [-100, 100], [-5, 5]), springConfig);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (prefersReducedMotion || !ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    x.set(event.clientX - centerX);
    y.set(event.clientY - centerY);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{
        type: 'spring',
        duration: prefersReducedMotion ? 0 : 0.8,
        delay: prefersReducedMotion ? 0 : index * 0.1,
      }}
      style={{
        rotateX: prefersReducedMotion ? 0 : rotateX,
        rotateY: prefersReducedMotion ? 0 : rotateY,
        transformPerspective: 1000,
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export default function StatsShowcase() {
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await analyticsService.getStats();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError('Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();

    // Set up periodic refresh every 30 seconds
    const intervalId = setInterval(fetchStats, 30000);

    return () => clearInterval(intervalId);
  }, []);

  const statItems = [
    {
      title: 'Total Users',
      value: stats?.all_users,
      icon: User,
      gradient: "from-blue-500 to-indigo-600",
      description: 'Active community interactions',
      prefix: '',
      suffix: ''
    },
    {
      title: 'Tasks Created',
      value: stats?.total_tasks,
      icon: RotateCcw,
      gradient: "from-green-500 to-emerald-600",
      description: 'Tasks managed successfully',
      prefix: '',
      suffix: ''
    },
    {
      title: 'Uptime',
      value: stats?.uptime_hours,
      icon: Clock,
      gradient: "from-orange-500 to-amber-600",
      description: 'Reliable service availability',
      prefix: '',
      suffix: 'hrs'
    },
    {
      title: 'Server Status',
      value: stats?.server_status,
      icon: Cloud,
      gradient: "from-purple-500 to-pink-600",
      description: 'Distributed global nodes',
      prefix: '',
      suffix: ''
    }
  ];

  return (
    <section id="stats" className="py-24 relative">
      {/* Background */}
      <div className="absolute inset-0 bg-background/50 -z-10" />

      <div className="container mx-auto px-4">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider mb-4 border border-primary/20">
            <TrendingUp className="w-3 h-3" />
            Live Metrics
          </div>
          <h2 className="text-3xl md:text-5xl font-black mb-4">Platform Statistics</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">Real-time usage data from our growing ecosystem.</p>
        </motion.div>

        {error ? (
          <div className="text-center text-red-500 p-8 rounded-xl bg-red-500/5 border border-red-200 dark:border-red-900/50">
            <p>Unable to load live stats. Please try again later.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 align-stretch">
            {statItems.map((item, index) => (
              <TiltCard
                key={item.title}
                index={index}
                prefersReducedMotion={prefersReducedMotion}
                className="h-full"
              >
                <Card className="h-full border-white/10 bg-background/40 backdrop-blur-xl hover:bg-background/60 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 group overflow-hidden">
                  <div className={`absolute inset-0 bg-linear-to-br ${item.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
                    <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-widest">
                      {item.title}
                    </CardTitle>
                    <div className={cn("p-2 rounded-lg bg-linear-to-br opacity-80 shadow-inner text-white transition-transform duration-300 group-hover:scale-110", item.gradient)}>
                      <item.icon className="h-4 w-4" />
                    </div>
                  </CardHeader>
                  <CardContent className="relative z-10">
                    {loading ? (
                      <Skeleton className="h-10 w-32 rounded bg-muted/50" />
                    ) : (
                      <div className="text-4xl font-black tracking-tight mb-2 flex items-baseline gap-1">
                        {typeof item.value === 'number' ? (
                          <CountUp
                            key={item.value}
                            end={item.value}
                            prefix={item.prefix}
                            suffix={item.suffix}
                            duration={2.5}
                            decimals={item.value % 1 !== 0 ? 1 : 0}
                          />
                        ) : (
                          // Fallback for string values
                          <span className={item.value === 'Online' ? 'text-green-500' : ''}>
                            {item.value}
                          </span>
                        )}
                      </div>
                    )}
                    <p className="text-sm text-muted-foreground/80 font-medium">
                      {item.description}
                    </p>
                  </CardContent>
                </Card>
              </TiltCard>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}