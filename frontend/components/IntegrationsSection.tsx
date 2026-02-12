'use client';

import { motion } from 'framer-motion';
import { Calendar, Mail, MessageSquare, Zap, Apple } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const integrations = [
  {
    name: 'Google Calendar',
    description: 'Sync events & tasks seamlessly',
    icon: Calendar,
    gradient: 'from-blue-400 to-indigo-500',
    color: 'text-blue-500',
    status: 'Available'
  },
  {
    name: 'Microsoft Outlook',
    description: 'Calendar integration',
    icon: Calendar,
    gradient: 'from-orange-400 to-red-500',
    color: 'text-orange-500',
    status: 'Available'
  },
  {
    name: 'Slack',
    description: 'Create tasks from messages',
    icon: MessageSquare,
    gradient: 'from-purple-400 to-pink-500',
    color: 'text-purple-500',
    status: 'Coming Soon'
  },
  {
    name: 'Email',
    description: 'Forward emails to create tasks',
    icon: Mail,
    gradient: 'from-green-400 to-emerald-500',
    color: 'text-emerald-500',
    status: 'Coming Soon'
  },
  {
    name: 'Apple Reminders',
    description: 'Import existing tasks',
    icon: Apple,
    gradient: 'from-gray-400 to-gray-600',
    color: 'text-gray-500',
    status: 'Coming Soon'
  },
  {
    name: 'Zapier',
    description: 'Connect to 5,000+ apps',
    icon: Zap,
    gradient: 'from-yellow-400 to-orange-500',
    color: 'text-yellow-500',
    status: 'Coming Soon'
  }
];

export default function IntegrationsSection() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section id="integrations" className="py-24 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-background/50 -z-20" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] bg-primary/5 rounded-full blur-[120px] -z-10" />

      <div className="container mx-auto px-4">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
        >
          <h2 className="text-3xl md:text-5xl font-black mb-4">
            Connects With Your{' '}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
              Workflow
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
            Seamlessly integrate with the tools you already use every day
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
          {integrations.map((integration, index) => (
            <motion.div
              key={integration.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{
                duration: prefersReducedMotion ? 0 : 0.5,
                delay: prefersReducedMotion ? 0 : index * 0.1
              }}
            >
              <Card className="h-full border-white/10 bg-background/40 backdrop-blur-xl hover:bg-background/60 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 group relative overflow-hidden">
                {/* Gradient overlay */}
                <div className={`absolute inset-0 bg-linear-to-br ${integration.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                <CardHeader className="relative z-10">
                  <div className="flex items-start justify-between mb-2">
                    {/* Icon */}
                    <div className={cn(
                      "w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300 shadow-inner group-hover:scale-110",
                      "bg-background/80 border border-white/10",
                      integration.color
                    )}>
                      <div className={`absolute inset-0 bg-linear-to-br ${integration.gradient} opacity-10 rounded-xl`} />
                      <integration.icon className="w-6 h-6" />
                    </div>

                    {/* Status badge */}
                    <span className={cn(
                      "text-xs px-2 py-1 rounded-full font-medium",
                      integration.status === 'Available'
                        ? "bg-green-500/10 text-green-500 border border-green-500/20"
                        : "bg-yellow-500/10 text-yellow-500 border border-yellow-500/20"
                    )}>
                      {integration.status}
                    </span>
                  </div>

                  <CardTitle className="text-lg font-bold">{integration.name}</CardTitle>
                  <CardDescription className="text-sm text-muted-foreground">
                    {integration.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          className="text-center mt-12"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.6 }}
        >
          <p className="text-muted-foreground">
            More integrations coming soon. Vote for your favorites in our community.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
