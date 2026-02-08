"use client";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { motion, Variants } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { Sparkles, ArrowRight } from "lucide-react";
import Image from "next/image";
import { useSession } from "@/lib/auth";

export default function HeroSection() {
  const prefersReducedMotion = useReducedMotion();
  const { data: session } = useSession();

  // Animation variants
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: prefersReducedMotion ? 0 : 0.2,
        delayChildren: prefersReducedMotion ? 0 : 0.1,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: prefersReducedMotion ? 0 : 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: prefersReducedMotion ? 0 : 0.8,
        ease: [0.22, 1, 0.36, 1] as const,
      },
    },
  };

  return (
    <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      {/* dynamic background mesh */}
      <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-200 h-200 rounded-full bg-primary/10 blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-150 h-150 rounded-full bg-purple-500/10 blur-[120px] animate-pulse-slow delay-1000" />
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03] pointer-events-none" />

      <motion.div
        className="container py-16 mx-auto px-4 text-center relative z-10"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div
          variants={itemVariants}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8 border border-primary/20 backdrop-blur-sm"
        >
          <Sparkles className="w-4 h-4" />
          <span>Reimagined for productivity</span>
        </motion.div>

        <motion.h1
          className="text-5xl md:text-7xl font-black mb-8 leading-tight tracking-tight"
          variants={itemVariants}
        >
          Master Your Day <br />
          <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">
            With Elegance.
          </span>
        </motion.h1>

        <motion.p
          className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto mb-12 font-light leading-relaxed"
          variants={itemVariants}
        >
          Manage your tasks efficiently with an intuitive, beautiful interface
          designed to keep you focused and organized.
        </motion.p>

        <motion.div
          className="flex flex-col sm:flex-row gap-5 justify-center"
          variants={itemVariants}
        >
          <Link href="/signup">
            <motion.div
              whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
            >
              {!session?.user ? (
                <>
                  <Link href="/signup">
                    <motion.div
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Button
                        size="lg"
                        className="px-8 py-6 text-lg rounded-full shadow-lg shadow-primary/25 bg-linear-to-r from-primary to-emerald-500 border-0 hover:shadow-xl transition-all"
                      >
                        Get Started Free
                        <ArrowRight className="ml-2 w-5 h-5" />
                      </Button>
                    </motion.div>
                  </Link>
                </>
              ) : (
                <>
                  <Link href="/dashboard">
                    <Button
                      size="lg"
                      className="px-8 py-6 text-lg rounded-full shadow-lg shadow-primary/25 bg-linear-to-r from-primary to-emerald-500 border-0 hover:shadow-xl transition-all"
                    >
                      Create Tasks
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </Button>
                  </Link>
                </>
              )}
            </motion.div>
          </Link>

          <Link href="/#features">
            <motion.div
              whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
              whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
            >
              <Button
                variant="outline"
                size="lg"
                className="px-8 py-6 text-lg rounded-full border-2 hover:bg-muted/50 transition-all backdrop-blur-sm"
              >
                Learn More
              </Button>
            </motion.div>
          </Link>
        </motion.div>

        {/* Floating UI Elements Showcase Placeholder */}
        <motion.div
          variants={itemVariants}
          className="mt-20 relative mx-auto max-w-5xl h-auto"
        >
          <div className="rounded-xl border border-white/10 bg-background/50 backdrop-blur-xl shadow-2xl p-2 md:p-4 rotate-x-12 perspective-1000">
            <Image
              width={1000}
              height={1000}
              src="/image.png"
              alt="App Preview UI"
              className="rounded-lg bg-background border border-border/50 overflow-hidden shadow-inner flex items-center justify-center bg-linear-to-br from-background to-muted/50"
            />
          </div>

          {/* Decorative floating elements */}
          <div className="absolute -top-10 -left-10 w-24 h-24 bg-primary/20 rounded-2xl rotate-12 backdrop-blur-md animate-float" />
          <div className="absolute -bottom-5 -right-5 w-32 h-32 bg-purple-500/20 rounded-full blur-xl animate-pulse-slow delay-700" />
        </motion.div>
      </motion.div>
    </section>
  );
}
