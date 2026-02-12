'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, CircleQuestionMark } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface FAQItem {
  question: string;
  answer: string;
}

const faqs: FAQItem[] = [
  {
    question: "What is AI Todo and how does it work?",
    answer: "AI Todo is an intelligent task management app that lets you manage your to-do list through natural conversation. Instead of filling out forms, just type or speak what you need: 'Schedule team meeting for Thursday at 2pm' or 'Remind me to follow up with the client next week.' Our AI understands context, extracts details, and organizes everything automatically. It learns your patterns over time to make smarter suggestions about priorities, scheduling, and task organization."
  },
  {
    question: "How does the AI chatbot help with task management?",
    answer: "Our AI assistant acts like a personal productivity coach. You can: • Create tasks by speaking naturally: 'Buy groceries tomorrow afternoon' • Update multiple tasks at once: 'Move all Thursday meetings to Friday' • Ask for insights: 'What should I focus on today?' • Get smart suggestions: AI recommends priorities based on deadlines and importance • Set contextual reminders: 'Remind me when I'm at the office'. The more you use it, the better it understands your work style and preferences."
  },
  {
    question: "What makes your AI different from other todo apps?",
    answer: "Most todo apps with 'AI' just have basic autocomplete or templates. Our AI actually understands natural language, context, and your personal patterns. You can have a real conversation about your tasks, and it learns how you work. It's like having a personal assistant who knows your schedule, understands your priorities, and helps you stay organized without you having to think about it."
  },
  {
    question: "Is my data secure and private?",
    answer: "Yes, absolutely! We take data security seriously. All your data is encrypted and stored securely in our database. We use JWT-based authentication to protect your account, and we never share your personal information or tasks with third parties."
  },
  {
    question: "What kind of data does the AI use to learn my patterns?",
    answer: "The AI analyzes your task creation patterns, completion rates, preferred work times, and scheduling habits—but only within your account. Your data is never shared with other users or used to train models for others. You have complete privacy, and you can clear your AI learning history anytime from settings."
  },
  {
    question: "Does the AI work offline?",
    answer: "You can view and check off tasks offline, and they'll sync when you're back online. However, AI-powered features like natural language task creation and smart suggestions require an internet connection. We're working on offline AI capabilities for a future update."
  },
  {
    question: "Can I use AI Todo on multiple devices?",
    answer: "Yes! AI Todo is a web-based application that works seamlessly across all your devices. Simply log in with your account credentials on any device with a web browser, and all your tasks will be synchronized automatically."
  },
  {
    question: "Is there a free plan available?",
    answer: "Yes! We offer a free plan that includes up to 50 AI conversations per month, 5 projects with unlimited tasks, basic AI suggestions, and mobile & web access. Premium plans offer unlimited AI conversations, advanced prioritization, and context-aware reminders."
  }
];

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const prefersReducedMotion = useReducedMotion();

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="py-20 px-4 bg-secondary-light dark:bg-secondary-dark">
      <div className="max-w-4xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/5 text-primary text-sm font-bold uppercase tracking-widest mb-6 border border-primary/10 hover:bg-primary/10 transition-colors cursor-default"
        >
          <CircleQuestionMark className="w-4 h-4" />
          FAQs
        </motion.div>

        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
        >
          <motion.h2
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight"
          >
            Frequently <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">Asked Questions</span>
          </motion.h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Got questions? We&apos;ve got answers. Find everything you need to know about AI Todo.
          </p>
        </motion.div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{
                duration: prefersReducedMotion ? 0 : 0.5,
                delay: prefersReducedMotion ? 0 : index * 0.1
              }}
              className="border border-border rounded-xl overflow-hidden bg-card hover:border-primary/30 transition-colors duration-300"
            >
              <button
                onClick={() => toggleFAQ(index)}
                className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-accent/5 transition-colors duration-200"
                aria-expanded={openIndex === index}
              >
                <span className="text-lg font-semibold pr-8">
                  {faq.question}
                </span>
                <motion.div
                  animate={{ rotate: openIndex === index ? 180 : 0 }}
                  transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
                  className="flex-shrink-0"
                >
                  <ChevronDown className="w-5 h-5 text-primary" />
                </motion.div>
              </button>

              <AnimatePresence initial={false}>
                {openIndex === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{
                      duration: prefersReducedMotion ? 0 : 0.3,
                      ease: 'easeInOut'
                    }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-5 pt-2 text-muted-foreground leading-relaxed">
                      {faq.answer}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.6, delay: prefersReducedMotion ? 0 : 0.8 }}
        >
          <p className="text-muted-foreground mb-4">
            Still have questions?
          </p>
          <a
            href="/contact"
            className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-gradient-to-r from-primary-custom to-[#0CCC40] text-[#161616] font-semibold hover:from-[#0CCC40] hover:to-[#0AAA30] transition-all duration-300 hover:shadow-lg hover:shadow-primary/30"
          >
            Contact Support
          </a>
        </motion.div>
      </div>
    </section>
  );
}
