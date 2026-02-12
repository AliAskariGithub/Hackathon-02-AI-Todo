'use client';

import { motion } from 'framer-motion';
import { Shield, Zap, Lock } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const valueProps = [
  {
    title: '99.9% Uptime',
    description: 'Reliable service availability',
    icon: Zap,
    gradient: 'from-yellow-400 to-orange-500',
    color: 'text-yellow-500'
  },
  {
    title: 'Sub-100ms Response',
    description: 'Lightning-fast AI processing',
    icon: Zap,
    gradient: 'from-blue-400 to-indigo-500',
    color: 'text-blue-500'
  },
  {
    title: 'Bank-Level Encryption',
    description: 'AES-256 security standard',
    icon: Lock,
    gradient: 'from-purple-400 to-pink-500',
    color: 'text-purple-500'
  },
  {
    title: 'GDPR Compliant',
    description: 'Privacy-first architecture',
    icon: Shield,
    gradient: 'from-green-400 to-emerald-500',
    color: 'text-emerald-500'
  }
];

export default function ValuePropsSection() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section id="value-props" className="py-24 relative">
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
          <h2 className="text-3xl md:text-5xl font-black mb-4">
            Built for{' '}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
              Performance & Reliability
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
            Enterprise-grade infrastructure you can trust
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {valueProps.map((item, index) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{
                duration: prefersReducedMotion ? 0 : 0.5,
                delay: prefersReducedMotion ? 0 : index * 0.1
              }}
            >
              <Card className="h-full border-white/10 bg-background/40 backdrop-blur-xl hover:bg-background/60 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 group overflow-hidden">
                <div className={`absolute inset-0 bg-linear-to-br ${item.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                <CardContent className="p-6 relative z-10 text-center">
                  <div className={cn(
                    "w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4 transition-all duration-300 shadow-inner group-hover:scale-110",
                    "bg-background/80 border border-white/10",
                    item.color
                  )}>
                    <div className={`absolute inset-0 bg-linear-to-br ${item.gradient} opacity-10 rounded-2xl`} />
                    <item.icon className="w-7 h-7" />
                  </div>

                  <h3 className="text-2xl font-black mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
