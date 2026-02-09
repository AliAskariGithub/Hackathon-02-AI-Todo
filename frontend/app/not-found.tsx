'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Rocket, Home, LayoutDashboard, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PageWrapper } from '@/components/ui/page-wrapper';

const StarsBackground = () => {
    // Pre-generated star data to avoid Math.random in render
    const stars = [
        { id: 0, width: 2.1, height: 2.3, top: 15.5, left: 23.7, opacity: 0.3, duration: 3.2, delay: 1.5 },
        { id: 1, width: 1.8, height: 1.5, top: 42.1, left: 78.3, opacity: 0.7, duration: 4.1, delay: 0.8 },
        { id: 2, width: 2.5, height: 2.7, top: 67.9, left: 12.4, opacity: 0.4, duration: 2.8, delay: 2.3 },
        { id: 3, width: 1.2, height: 1.9, top: 81.6, left: 56.2, opacity: 0.6, duration: 3.5, delay: 0.5 },
        { id: 4, width: 2.9, height: 2.1, top: 34.8, left: 91.7, opacity: 0.5, duration: 2.9, delay: 1.8 },
        { id: 5, width: 1.6, height: 1.4, top: 5.3, left: 38.9, opacity: 0.8, duration: 4.2, delay: 3.1 },
        { id: 6, width: 2.3, height: 2.6, top: 72.4, left: 67.1, opacity: 0.35, duration: 3.7, delay: 0.9 },
        { id: 7, width: 1.9, height: 1.7, top: 29.5, left: 4.8, opacity: 0.65, duration: 2.4, delay: 2.7 },
        { id: 8, width: 2.7, height: 2.2, top: 55.2, left: 85.6, opacity: 0.45, duration: 3.8, delay: 1.2 },
        { id: 9, width: 1.4, height: 1.8, top: 18.9, left: 73.4, opacity: 0.55, duration: 4.5, delay: 2.1 },
        { id: 10, width: 2.0, height: 1.3, top: 94.1, left: 27.3, opacity: 0.75, duration: 2.6, delay: 0.4 },
        { id: 11, width: 1.7, height: 2.4, top: 41.7, left: 52.8, opacity: 0.4, duration: 3.3, delay: 1.6 },
    ];

    return (
        <>
            {stars.map(star => (
                <motion.div
                    key={star.id}
                    className="absolute rounded-full bg-white transition-opacity"
                    style={{
                        width: `${star.width}px`,
                        height: `${star.height}px`,
                        top: `${star.top}%`,
                        left: `${star.left}%`,
                        opacity: star.opacity,
                    }}
                    animate={{
                        opacity: [0.2, 0.8, 0.2],
                        scale: [1, 1.5, 1],
                    }}
                    transition={{
                        duration: star.duration,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: star.delay
                    }}
                />
            ))}
        </>
    );
};

export default function NotFound() {
    return (
        <PageWrapper className="min-h-screen relative overflow-hidden bg-[#0a0a0b] flex items-center justify-center py-20 px-4">
            {/* Space Background Decor */}
            <div className="absolute inset-0 -z-10 overflow-hidden">
                {/* Animated Stars/Particles (Simulated with div blobs) */}
                <StarsBackground />

                {/* Floating Space Blobs */}
                <div className="absolute top-[10%] left-[15%] w-125 h-125 bg-primary/20 rounded-full blur-[120px] animate-pulse" />
                <div className="absolute bottom-[20%] right-[10%] w-100 h-100 bg-purple-500/20 rounded-full blur-[150px] animate-pulse animation-delay-2000" />
                <div className="absolute top-[40%] right-[25%] w-75 h-75 bg-blue-500/10 rounded-full blur-[100px] animate-pulse animation-delay-4000" />
            </div>

            <div className="container max-w-4xl mx-auto text-center relative z-10">
                {/* Animated Hero Icon */}
                <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8 }}
                    className="mb-8 relative inline-block"
                >
                    <motion.div
                        animate={{
                            y: [-10, 10, -10],
                            rotate: [-2, 2, -2]
                        }}
                        transition={{
                            duration: 5,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                        className="relative z-10"
                    >
                        <Rocket className="w-24 h-24 md:w-32 md:h-32 text-primary" />
                    </motion.div>

                    {/* Outer glow for icon */}
                    <div className="absolute inset-x-0 bottom-0 h-10 bg-primary/40 blur-2xl -z-10 rounded-full" />
                </motion.div>

                {/* Glitchy Title */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1, delay: 0.2 }}
                    className="relative mb-6"
                >
                    <h1 className="text-8xl md:text-9xl font-black tracking-tighter text-white relative">
                        404
                        <motion.span
                            className="absolute inset-0 text-primary opacity-50 select-none z-[-1]"
                            animate={{
                                x: [-1, 1, -1],
                                y: [1, -1, 1],
                            }}
                            transition={{ repeat: Infinity, duration: 0.1 }}
                        >
                            404
                        </motion.span>
                        <motion.span
                            className="absolute inset-0 text-purple-500 opacity-50 select-none z-[-2]"
                            animate={{
                                x: [2, -2, 2],
                                y: [-2, 2, -2],
                            }}
                            transition={{ repeat: Infinity, duration: 0.08 }}
                        >
                            404
                        </motion.span>
                    </h1>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.5 }}
                >
                    <h2 className="text-2xl md:text-4xl font-bold text-white mb-4">
                        Oops! You&apos;re <span className="text-transparent bg-clip-text bg-linear-to-r from-primary to-emerald-400">lost in deep space</span>
                    </h2>
                    <p className="text-muted-foreground text-lg mb-12 max-w-xl mx-auto font-light leading-relaxed">
                        The coordinates you provided lead to a place that doesn&apos;t exist.
                        The page you are looking for has likely drifted into a black hole or never existed in this galaxy.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link href="/">
                            <Button
                                size="lg"
                                className="w-full sm:w-auto px-8 h-14 rounded-2xl bg-primary text-[#161616] font-bold text-lg shadow-xl shadow-primary/20 hover:scale-[1.05] transition-transform flex items-center gap-2"
                            >
                                <Home className="w-5 h-5" />
                                Back to Earth
                            </Button>
                        </Link>

                        <Link href="/dashboard">
                            <Button
                                variant="outline"
                                size="lg"
                                className="w-full sm:w-auto px-8 h-14 rounded-2xl border-white/10 bg-white/5 backdrop-blur-xl hover:bg-white/10 font-bold text-lg hover:border-primary/30 transition-all flex items-center gap-2"
                            >
                                <LayoutDashboard className="w-5 h-5" />
                                Go to Dashboard
                            </Button>
                        </Link>

                        <Link href="/contact">
                            <Button
                                variant="ghost"
                                size="lg"
                                className="w-full sm:w-auto px-8 h-14 rounded-2xl hover:bg-white/5 font-bold text-primary flex items-center gap-2"
                            >
                                <Bug className="w-5 h-5" />
                                Report Anomaly
                            </Button>
                        </Link>
                    </div>
                </motion.div>

                {/* Animated Background Sparkle */}
                <motion.div
                    className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary/10 rounded-full blur-[100px]"
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 0.6, 0.3],
                    }}
                    transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                />
            </div>
        </PageWrapper>
    );
}
