'use client';

import { motion } from 'framer-motion';
import { MessageSquare, Brain, Sparkles, Cloud, WorkflowIcon } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const steps = [
  {
    number: '01',
    title: 'Talk to Your Tasks',
    description: 'Just type or speak naturally: "Schedule dentist appointment for next Tuesday at 2pm" or "Remind me to call mom this weekend". No forms, no fields.',
    icon: MessageSquare,
    gradient: 'from-blue-400 to-indigo-500',
    color: 'text-blue-500'
  },
  {
    number: '02',
    title: 'Smart Understanding',
    description: 'Our AI extracts dates, priorities, categories, and context from your message. It understands "tomorrow", "next week", "urgent", and even "when I\'m near the grocery store".',
    icon: Brain,
    gradient: 'from-purple-400 to-pink-500',
    color: 'text-purple-500'
  },
  {
    number: '03',
    title: 'Automatic Prioritization',
    description: 'AI analyzes deadlines, importance, and your patterns to suggest what to focus on. Get your daily plan without lifting a finger.',
    icon: Sparkles,
    gradient: 'from-yellow-400 to-orange-500',
    color: 'text-yellow-500'
  },
  {
    number: '04',
    title: 'Always in Sync',
    description: 'Access your AI-organized tasks on any device. Your assistant knows your schedule whether you\'re on desktop, mobile, or tablet.',
    icon: Cloud,
    gradient: 'from-green-400 to-emerald-500',
    color: 'text-emerald-500'
  }
];

export default function HowItWorksSection() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section id="how-it-works" className="py-24 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-background/50 -z-20" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] bg-primary/5 rounded-full blur-[120px] -z-10" />

      <div className="container mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/5 text-primary text-sm font-bold uppercase tracking-widest mb-6 border border-primary/10 hover:bg-primary/10 transition-colors cursor-default"
        >
          <WorkflowIcon className="w-4 h-4" />
          How It Works
        </motion.div>

        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
        >
          <h2 className="text-3xl md:text-5xl font-black mb-4">
            How AI Transforms Your{' '}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
              Task Management
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
            Four simple steps to effortless productivity
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto text-left">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
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
                <div className={`absolute inset-0 bg-linear-to-br ${step.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                <CardHeader className="relative z-10 py-4">
                  {/* Step number */}

                  <div className='flex justify-between items-center'>
                  <div className="text-6xl font-black text-primary/10">
                    {step.number}
                  </div>

                  {/* Icon */}
                  <div className={cn(
                    "w-14 h-14 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300 shadow-inner group-hover:scale-110",
                    "bg-background/80 border border-white/10",
                    step.color
                  )}>
                    <div className={`absolute inset-0 bg-linear-to-br ${step.gradient} opacity-10 rounded-2xl`} />
                    <step.icon className="w-7 h-7" />
                  </div>
                  </div>

                  <CardTitle className="text-xl font-bold">{step.title}</CardTitle>
                </CardHeader>

                <CardContent className="relative z-10">
                  <CardDescription className="text-base text-muted-foreground leading-relaxed">
                    {step.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
