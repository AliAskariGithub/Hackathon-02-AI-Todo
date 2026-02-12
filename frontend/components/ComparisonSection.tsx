'use client';

import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card, CardContent } from '@/components/ui/card';

const comparisonData = [
  {
    feature: 'Task Creation',
    traditional: 'Manual forms with multiple fields',
    aiBasic: 'Basic autocomplete templates',
    ytodo: 'Natural conversation - just talk'
  },
  {
    feature: 'Prioritization',
    traditional: 'Manual drag & drop sorting',
    aiBasic: 'Simple keyword detection',
    ytodo: 'AI analyzes deadlines & patterns'
  },
  {
    feature: 'Reminders',
    traditional: 'Time-based only',
    aiBasic: 'Time-based only',
    ytodo: 'Context-aware (time + location)'
  },
  {
    feature: 'Learning',
    traditional: 'None',
    aiBasic: 'None',
    ytodo: 'Adapts to your work patterns'
  },
  {
    feature: 'Natural Language',
    traditional: false,
    aiBasic: 'Limited',
    ytodo: true
  },
  {
    feature: 'Smart Suggestions',
    traditional: false,
    aiBasic: 'Basic',
    ytodo: true
  },
  {
    feature: 'Multi-task Updates',
    traditional: 'One at a time',
    aiBasic: 'One at a time',
    ytodo: 'Bulk operations via chat'
  },
  {
    feature: 'Free Plan',
    traditional: 'Limited features',
    aiBasic: 'Very limited',
    ytodo: '50 AI conversations/month'
  }
];

export default function ComparisonSection() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section id="comparison" className="py-24 relative overflow-hidden">
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
            Why Choose{' '}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
              Y-Todo?
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
            See how we compare to traditional todo apps and basic AI tools
          </p>
        </motion.div>

        <motion.div
          className="max-w-6xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.2 }}
        >
          <Card className="border-white/10 bg-background/40 backdrop-blur-xl overflow-hidden">
            <CardContent className="p-0">
              {/* Desktop Table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left p-6 font-bold text-foreground">Feature</th>
                      <th className="text-center p-6 font-bold text-muted-foreground">Traditional Apps</th>
                      <th className="text-center p-6 font-bold text-muted-foreground">Basic AI Tools</th>
                      <th className="text-center p-6 font-bold text-primary bg-primary/5">
                        Y-Todo
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonData.map((row, index) => (
                      <tr
                        key={index}
                        className="border-b border-border/50 hover:bg-muted/30 transition-colors"
                      >
                        <td className="p-6 font-medium text-foreground">{row.feature}</td>
                        <td className="p-6 text-center text-muted-foreground text-sm">
                          {typeof row.traditional === 'boolean' ? (
                            row.traditional ? (
                              <Check className="w-5 h-5 text-green-500 mx-auto" />
                            ) : (
                              <X className="w-5 h-5 text-red-500 mx-auto" />
                            )
                          ) : (
                            row.traditional
                          )}
                        </td>
                        <td className="p-6 text-center text-muted-foreground text-sm">
                          {typeof row.aiBasic === 'boolean' ? (
                            row.aiBasic ? (
                              <Check className="w-5 h-5 text-green-500 mx-auto" />
                            ) : (
                              <X className="w-5 h-5 text-red-500 mx-auto" />
                            )
                          ) : (
                            row.aiBasic
                          )}
                        </td>
                        <td className="p-6 text-center bg-primary/5">
                          {typeof row.ytodo === 'boolean' ? (
                            row.ytodo ? (
                              <Check className="w-5 h-5 text-primary mx-auto" />
                            ) : (
                              <X className="w-5 h-5 text-red-500 mx-auto" />
                            )
                          ) : (
                            <span className="text-primary font-semibold text-sm">{row.ytodo}</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile Cards */}
              <div className="md:hidden p-4 space-y-4">
                {comparisonData.map((row, index) => (
                  <div
                    key={index}
                    className="border border-border rounded-lg p-4 bg-background/60"
                  >
                    <h3 className="font-bold text-foreground mb-3">{row.feature}</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Traditional:</span>
                        <span className="text-muted-foreground">
                          {typeof row.traditional === 'boolean' ? (
                            row.traditional ? (
                              <Check className="w-4 h-4 text-green-500" />
                            ) : (
                              <X className="w-4 h-4 text-red-500" />
                            )
                          ) : (
                            row.traditional
                          )}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Basic AI:</span>
                        <span className="text-muted-foreground">
                          {typeof row.aiBasic === 'boolean' ? (
                            row.aiBasic ? (
                              <Check className="w-4 h-4 text-green-500" />
                            ) : (
                              <X className="w-4 h-4 text-red-500" />
                            )
                          ) : (
                            row.aiBasic
                          )}
                        </span>
                      </div>
                      <div className="flex justify-between items-center pt-2 border-t border-primary/20">
                        <span className="text-primary font-semibold">Y-Todo:</span>
                        <span className="text-primary font-semibold">
                          {typeof row.ytodo === 'boolean' ? (
                            row.ytodo ? (
                              <Check className="w-4 h-4 text-primary" />
                            ) : (
                              <X className="w-4 h-4 text-red-500" />
                            )
                          ) : (
                            row.ytodo
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* CTA Below Comparison */}
          <motion.div
            className="text-center mt-12"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.4 }}
          >
            <p className="text-muted-foreground mb-6 text-lg">
              Experience the difference with AI-powered task management
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/signup"
                className="inline-flex items-center justify-center px-8 py-4 rounded-full bg-gradient-to-r from-primary to-emerald-500 text-white font-semibold hover:shadow-lg hover:shadow-primary/30 transition-all"
              >
                Start Free Forever
              </a>
              <a
                href="/chat"
                className="inline-flex items-center justify-center px-8 py-4 rounded-full border-2 border-border hover:bg-muted/50 transition-all"
              >
                Try AI Chat Demo
              </a>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
