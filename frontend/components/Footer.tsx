'use client';

import Link from 'next/link';
import { Twitter, Github, Facebook } from 'lucide-react';
import { motion } from 'framer-motion';
import { useReducedMotion } from '@/hooks/useReducedMotion';

export function Footer() {
  const prefersReducedMotion = useReducedMotion();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: prefersReducedMotion ? 0 : 0.1,
        delayChildren: prefersReducedMotion ? 0 : 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: prefersReducedMotion ? 0 : 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: prefersReducedMotion ? 0 : 0.5,
      },
    },
  };

  const socialIconVariants = {
    hover: prefersReducedMotion
      ? {}
      : {
        scale: 1.2,
        rotate: [0, -10, 10, 0],
        transition: {
          rotate: { duration: 0.5 },
          scale: { duration: 0.2 },
        },
      },
  };

  return (
    <motion.footer
      className="bg-secondary py-12 mt-auto"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-100px" }}
      variants={containerVariants}
    >
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <motion.div variants={itemVariants}>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 rounded bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">Y</span>
              </div>
              <span className="font-semibold text-lg">Y-Todo</span>
            </div>
            <p className="text-secondary-foreground">
              Boost your productivity with our intuitive todo application.
            </p>
          </motion.div>

          <motion.div variants={itemVariants}>
            <h4 className="font-bold mb-4">Pages</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/chat" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Chat
                </Link>
              </li>
              <li>
                <Link href="/#features" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Features
                </Link>
              </li>
              <li>
                <Link href="/#pricing" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Contact
                </Link>
              </li>
            </ul>
          </motion.div>

          <motion.div variants={itemVariants}>
            <h4 className="font-bold mb-4">Legal</h4>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="text-secondary-foreground hover:text-primary transition-colors underline-slide inline-block opacity-75">
                  Cookie Policy
                </a>
              </li>
            </ul>
          </motion.div>

          <motion.div variants={itemVariants}>
            <h4 className="font-bold mb-4">Connect</h4>
            <div className="flex space-x-4">
              <motion.a
                href="https://x.com/Syed_Ali_Askari"
                target="_blank"
                rel="noopener noreferrer"
                className="text-secondary-foreground hover:text-primary transition-colors"
                aria-label="Twitter"
                variants={socialIconVariants}
                whileHover="hover"
              >
                <Twitter className="h-6 w-6 opacity-75" />
              </motion.a>
              <motion.a
                href="https://github.com/AliAskariGithub"
                target="_blank"
                rel="noopener noreferrer"
                className="text-secondary-foreground hover:text-primary transition-colors"
                aria-label="GitHub"
                variants={socialIconVariants}
                whileHover="hover"
              >
                <Github className="h-6 w-6 opacity-75" />
              </motion.a>
              <motion.a
                href="https://www.facebook.com/NexuGem"
                target="_blank"
                rel="noopener noreferrer"
                className="text-secondary-foreground hover:text-primary transition-colors"
                aria-label="Facebook"
                variants={socialIconVariants}
                whileHover="hover"
              >
                <Facebook className="h-6 w-6 opacity-75" />
              </motion.a>
            </div>
          </motion.div>
        </div>

        <motion.div
          className="border-t border-border mt-8 pt-8 text-center text-secondary-foreground"
          variants={itemVariants}
        >
          <p>© {new Date().getFullYear()} Y-Todo. All rights reserved.</p>
        </motion.div>
      </div>
    </motion.footer>
  );
}
