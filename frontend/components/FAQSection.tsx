'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface FAQItem {
  question: string;
  answer: string;
}

const faqs: FAQItem[] = [
  {
    question: "What is AI Todo and how does it work?",
    answer: "AI Todo is an intelligent task management application that combines traditional todo list functionality with AI-powered assistance. Our AI chatbot helps you create, organize, and manage tasks through natural conversation, making task management effortless and intuitive."
  },
  {
    question: "Is my data secure and private?",
    answer: "Yes, absolutely! We take data security seriously. All your data is encrypted and stored securely in our database. We use JWT-based authentication to protect your account, and we never share your personal information or tasks with third parties."
  },
  {
    question: "Can I use AI Todo on multiple devices?",
    answer: "Yes! AI Todo is a web-based application that works seamlessly across all your devices. Simply log in with your account credentials on any device with a web browser, and all your tasks will be synchronized automatically."
  },
  {
    question: "How does the AI chatbot help with task management?",
    answer: "Our AI chatbot understands natural language and can help you create tasks, set priorities, organize your workflow, and provide suggestions. Simply chat with it like you would with a personal assistant, and it will handle the task management for you."
  },
  {
    question: "Is there a free plan available?",
    answer: "Yes! We offer a free plan that includes all core features like task creation, editing, completion tracking, and basic AI chat functionality. Premium plans offer additional features like advanced AI capabilities, priority support, and enhanced analytics."
  },
  {
    question: "Can I export my tasks and data?",
    answer: "Yes, you can export your tasks and data at any time. We believe in data portability and want you to have full control over your information. Export options are available in your account settings."
  },
  {
    question: "What happens if I forget my password?",
    answer: "If you forget your password, you can use the 'Forgot Password' link on the login page to reset it. We'll send you a secure reset link to your registered email address to help you regain access to your account."
  },
  {
    question: "Do you offer customer support?",
    answer: "Yes! We provide customer support through multiple channels. Free users have access to our help center and community forums, while premium users get priority email support and faster response times."
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
      <div className="max-w-4xl mx-auto">
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
