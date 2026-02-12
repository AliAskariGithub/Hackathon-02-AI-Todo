'use client';

import { motion } from 'framer-motion';
import { Shield, Lock, Eye } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const securityFeatures = [
  {
    title: 'Enterprise Security',
    icon: Shield,
    gradient: 'from-blue-400 to-indigo-500',
    color: 'text-blue-500',
    features: [
      '256-bit AES encryption at rest and in transit',
      'Regular security audits & penetration testing',
      'SOC 2 Type II certified infrastructure'
    ]
  },
  {
    title: 'Privacy First',
    icon: Eye,
    gradient: 'from-purple-400 to-pink-500',
    color: 'text-purple-500',
    features: [
      'Your tasks and data are never sold or shared',
      'GDPR and CCPA compliant',
      'You can export or delete your data anytime'
    ]
  },
  {
    title: 'Transparent AI',
    icon: Lock,
    gradient: 'from-green-400 to-emerald-500',
    color: 'text-emerald-500',
    features: [
      'AI training data stays in your account only',
      'No cross-user data sharing',
      'Clear AI usage policies & opt-out options'
    ]
  }
];

export default function SecuritySection() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section id="security" className="py-24 relative overflow-hidden bg-secondary/30">
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
            Your Data,{' '}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
              Your Control
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
            Enterprise-grade security and privacy protection built into every layer
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {securityFeatures.map((feature, index) => (
            <motion.div
              key={feature.title}
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
                <div className={`absolute inset-0 bg-linear-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                <CardHeader className="relative z-10">
                  {/* Icon */}
                  <div className={cn(
                    "w-14 h-14 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300 shadow-inner group-hover:scale-110",
                    "bg-background/80 border border-white/10",
                    feature.color
                  )}>
                    <div className={`absolute inset-0 bg-linear-to-br ${feature.gradient} opacity-10 rounded-2xl`} />
                    <feature.icon className="w-7 h-7" />
                  </div>

                  <CardTitle className="text-xl font-bold mb-2">{feature.title}</CardTitle>
                </CardHeader>

                <CardContent className="relative z-10">
                  <ul className="space-y-3">
                    {feature.features.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <span className="text-primary mt-1">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
