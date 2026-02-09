"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Zap, Shield, Smartphone, Globe, Layout, Palette } from "lucide-react";
import { motion, Variants } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import React from "react";
import { cn } from "@/lib/utils";

const features = [
    {
        title: "Lighting Fast",
        description: "Built with Next.js 16 for incredible speed and performance.",
        icon: Zap,
        gradient: "from-yellow-400 to-orange-500",
        color: "text-yellow-500"
    },
    {
        title: "Secure by Design",
        description: "Enterprise-grade security to keep your data safe and private.",
        icon: Shield,
        gradient: "from-blue-400 to-indigo-500",
        color: "text-blue-500"
    },
    {
        title: "Fully Responsive",
        description: "Works perfectly on desktop, tablet, and mobile devices.",
        icon: Smartphone,
        gradient: "from-purple-400 to-pink-500",
        color: "text-purple-500"
    },
    {
        title: "Global Sync",
        description: "Access your tasks from anywhere, anytime, on any device.",
        icon: Globe,
        gradient: "from-green-400 to-emerald-500",
        color: "text-emerald-500"
    },
    {
        title: "Intuitive Layout",
        description: "Clean, clutter-free interface designed for focus.",
        icon: Layout,
        gradient: "from-cyan-400 to-blue-500",
        color: "text-cyan-500"
    },
    {
        title: "Premium Themes",
        description: "Beautiful dark and light modes with custom accent colors.",
        icon: Palette,
        gradient: "from-red-400 to-rose-500",
        color: "text-rose-500"
    },
];

export function FeaturesSection() {
    const prefersReducedMotion = useReducedMotion();

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: prefersReducedMotion ? 0 : 0.15,
            },
        },
    };

    const item: Variants = {
        hidden: { opacity: 0, y: prefersReducedMotion ? 0 : 30 },
        show: {
            opacity: 1,
            y: 0,
            transition: {
                type: "spring",
                stiffness: 50,
                damping: 20
            },
        },
    };

    return (
        <section id="features" className="py-24 sm:py-32 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 bg-secondary/30 -z-20" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] bg-primary/5 rounded-full blur-[120px] -z-10" />

            <div className="container mx-auto px-4 md:px-6">
                <motion.div
                    className="mx-auto max-w-2xl text-center mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: prefersReducedMotion ? 0 : 0.6 }}
                >
                    <h2 className="text-3xl font-black tracking-tight sm:text-5xl mb-4">
                        Everything needed to <br />
                        <span className="text-transparent bg-clip-text bg-linear-to-r from-primary to-emerald-500">stay organized</span>
                    </h2>
                    <p className="mt-4 text-xl text-muted-foreground/80 font-light">
                        Our platform provides all the tools you need to manage your tasks efficiently and elegantly.
                    </p>
                </motion.div>

                <motion.div
                    variants={container}
                    initial="hidden"
                    whileInView="show"
                    viewport={{ once: true, margin: "-100px" }}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                >
                    {features.map((feature, index) => (
                        <motion.div key={index} variants={item} whileHover={{ y: -8 }} className="h-full">
                            <Card className="h-full border-white/10 shadow-lg hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 bg-background/40 backdrop-blur-xl group relative overflow-hidden">
                                {/* Gradient Mesh Overlay */}
                                <div className={`absolute inset-0 bg-linear-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                                {/* Large Watermark Icon */}
                                <div className={cn(
                                    "absolute -right-8 -bottom-8 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-500 rotate-12 scale-150 pointer-events-none",
                                    feature.color
                                )}>
                                    <feature.icon className="w-40 h-40" />
                                </div>

                                <CardHeader className="relative z-10">
                                    <div className={cn(
                                        "w-14 h-14 rounded-2xl flex items-center justify-center mb-4 transition-all duration-300 shadow-inner group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-primary/10",
                                        "bg-background/80 border border-white/10",
                                        feature.color
                                    )}>
                                        <div className={`absolute inset-0 bg-linear-to-br ${feature.gradient} opacity-10 rounded-2xl`} />
                                        <feature.icon className={`w-7 h-7 ${prefersReducedMotion ? '' : 'group-hover:animate-bounce-subtle'}`} />
                                    </div>
                                    <CardTitle className="text-xl font-bold">{feature.title}</CardTitle>
                                </CardHeader>
                                <CardContent className="relative z-10">
                                    <CardDescription className="text-base text-muted-foreground leading-relaxed">
                                        {feature.description}
                                    </CardDescription>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </motion.div>
            </div>
        </section>
    );
}
