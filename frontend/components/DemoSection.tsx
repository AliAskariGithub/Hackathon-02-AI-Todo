'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const demoExamples = [
  "Schedule dentist appointment for next Tuesday at 2pm",
  "Remind me to call mom this weekend",
  "Add buy groceries to my high priority list",
  "Move all Thursday meetings to Friday",
  "What should I focus on today?"
];

export default function DemoSection() {
  const prefersReducedMotion = useReducedMotion();
  const [inputValue, setInputValue] = useState('');
  const [showResult, setShowResult] = useState(false);

  const handleTryDemo = () => {
    setShowResult(true);
    setTimeout(() => setShowResult(false), 3000);
  };

  const handleExampleClick = (example: string) => {
    setInputValue(example);
    setShowResult(false);
  };

  return (
    <section id="demo" className="py-24 relative overflow-hidden bg-secondary/30">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-125 h-125 bg-primary/5 rounded-full blur-[120px] -z-10" />

      <div className="container mx-auto px-4">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
        >
          <h2 className="text-3xl md:text-5xl font-black mb-4">
            Try It{' '}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
              Yourself
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light">
            See how natural language becomes organized tasks instantly
          </p>
        </motion.div>

        <motion.div
          className="max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.2 }}
        >
          <Card className="border-white/10 bg-background/40 backdrop-blur-xl overflow-hidden">
            <CardContent className="p-8">
              {/* Input Area */}
              <div className="mb-6">
                <label className="text-sm text-muted-foreground mb-2 block">
                  Type naturally, like you&apos;re talking to a friend:
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Try: 'Remind me to call mom tomorrow at 3pm'"
                    className="w-full p-4 pr-12 rounded-lg bg-background border border-border focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                  <Sparkles className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-primary" />
                </div>
              </div>

              {/* Try Button */}
              <Button
                onClick={handleTryDemo}
                disabled={!inputValue}
                className="w-full bg-gradient-to-r from-primary to-emerald-500 hover:from-primary/90 hover:to-emerald-500/90 transition-all"
              >
                See AI Magic
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>

              {/* Result Preview */}
              {showResult && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 p-4 bg-primary/10 border border-primary/20 rounded-lg"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                    <div className="flex-1">
                      <p className="font-semibold text-foreground mb-1">Task Created!</p>
                      <p className="text-sm text-muted-foreground">
                        AI extracted: Title, Date, Time, Priority, and Context
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Example Prompts */}
              <div className="mt-8">
                <p className="text-sm text-muted-foreground mb-3">Or try these examples:</p>
                <div className="flex flex-wrap gap-2">
                  {demoExamples.map((example, index) => (
                    <button
                      key={index}
                      onClick={() => handleExampleClick(example)}
                      className="text-xs px-3 py-2 rounded-full bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground transition-all border border-border hover:border-primary/30"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* CTA Below Demo */}
          <motion.div
            className="text-center mt-8"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.4 }}
          >
            <p className="text-muted-foreground mb-4">
              Ready to experience the full power of AI task management?
            </p>
            <Button
              size="lg"
              className="px-8 py-6 text-lg rounded-full shadow-lg shadow-primary/25 bg-linear-to-r from-primary to-emerald-500 border-0 hover:shadow-xl transition-all"
            >
              Start Free Forever
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
