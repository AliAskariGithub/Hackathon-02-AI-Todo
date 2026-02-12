'use client';

import { motion } from 'framer-motion';
import { Briefcase, GraduationCap, Home, ArrowRight } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const useCases = [
  {
    title: 'Busy Professional',
    icon: Briefcase,
    gradient: 'from-blue-400 to-indigo-500',
    color: 'text-blue-500',
    before: 'Manually creating 15 meeting tasks, setting reminders, organizing by priority',
    after: 'You: "I have client calls all day Tuesday starting at 9am, 30 minutes each, with prep time between."',
    result: 'AI: Creates 15 tasks, sets reminders, blocks prep time automatically.'
  },
  {
    title: 'Student',
    icon: GraduationCap,
    gradient: 'from-purple-400 to-pink-500',
    color: 'text-purple-500',
    before: 'Tracking assignment deadlines across multiple classes, missing due dates',
    after: 'You: "Math homework due Friday, Chemistry project next Monday, study for History exam on the 15th."',
    result: 'AI: Prioritizes by deadline, suggests study schedule, sends timely reminders.'
  },
  {
    title: 'Homeowner',
    icon: Home,
    gradient: 'from-green-400 to-emerald-500',
    color: 'text-emerald-500',
    before: 'Forgetting errands, making multiple trips to stores',
    after: 'You: "Get groceries, pick up dry cleaning, and stop at pharmacy when I\'m out."',
    result: 'AI: Groups tasks by location, reminds you when you\'re nearby each place.'
  }
];

export default function UseCasesSection() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section id="use-cases" className="py-24 relative overflow-hidden bg-secondary/30">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-125 h-125 bg-primary/5 rounded-full blur-[120px] -z-10" />
      <div className="absolute bottom-0 left-0 w-125 h-125 bg-purple-500/5 rounded-full blur-[120px] -z-10" />

      <div className="container mx-auto px-4">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
        >
          <h2 className="text-3xl md:text-5xl font-black mb-4">
            See AI in{' '}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
              Action
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
            Real examples of how AI transforms everyday task management
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {useCases.map((useCase, index) => (
            <motion.div
              key={useCase.title}
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
                <div className={`absolute inset-0 bg-linear-to-br ${useCase.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                <CardHeader className="relative z-10">
                  {/* Icon */}
                  <div className={cn(
                    "w-14 h-14 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300 shadow-inner group-hover:scale-110",
                    "bg-background/80 border border-white/10",
                    useCase.color
                  )}>
                    <div className={`absolute inset-0 bg-linear-to-br ${useCase.gradient} opacity-10 rounded-2xl`} />
                    <useCase.icon className="w-7 h-7" />
                  </div>

                  <CardTitle className="text-xl font-bold mb-4">{useCase.title}</CardTitle>
                </CardHeader>

                <CardContent className="relative z-10 space-y-4">
                  {/* Before */}
                  <div className="space-y-2">
                    <div className="text-xs font-bold uppercase tracking-wider text-red-500">Before</div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {useCase.before}
                    </p>
                  </div>

                  {/* Arrow */}
                  <div className="flex justify-center">
                    <ArrowRight className="w-5 h-5 text-primary" />
                  </div>

                  {/* After */}
                  <div className="space-y-2">
                    <div className="text-xs font-bold uppercase tracking-wider text-green-500">After</div>
                    <p className="text-sm text-foreground leading-relaxed bg-muted/30 p-3 rounded-lg border border-border/50">
                      {useCase.after}
                    </p>
                  </div>

                  {/* Result */}
                  <div className="space-y-2 pt-2">
                    <p className="text-sm text-primary font-medium leading-relaxed">
                      {useCase.result}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
