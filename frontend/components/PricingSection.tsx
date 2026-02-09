'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';

interface PricingTier {
    name: string;
    price: {
        monthly: number;
        yearly: number;
    };
    description: string;
    features: string[];
    notIncluded?: string[];
    popular?: boolean;
}

const pricingTiers: PricingTier[] = [
    {
        name: 'Starter',
        price: { monthly: 0, yearly: 0 },
        description: 'Perfect for individuals just getting started.',
        features: [
            'Up to 5 Projects',
            'Basic Task Management',
            '2GB Storage',
            'Community Support',
        ],
        notIncluded: [
            'Team Collaboration',
            'Advanced Analytics',
            'Custom Branding',
        ],
    },
    {
        name: 'Pro',
        price: { monthly: 15, yearly: 144 },
        description: 'The best value for power users and creators.',
        popular: true,
        features: [
            'Unlimited Projects',
            'Advanced Task Management',
            '10GB Storage',
            'Priority Email Support',
            'Team Collaboration (up to 5)',
            'Basic Analytics',
        ],
    },
    {
        name: 'Business',
        price: { monthly: 49, yearly: 470 },
        description: 'For teams that need scalable power and security.',
        features: [
            'Everything in Pro',
            'Unlimited Team Members',
            '1TB Storage',
            '24/7 Phone Support',
            'Advanced Analytics & Reporting',
            'Custom Branding & SSO',
        ],
    },
];

export default function PricingSection() {
    const [isYearly, setIsYearly] = useState(false);

    return (
        <section id="pricing" className="py-24 relative overflow-hidden">
            {/* Background Gradients */}
            <div className="absolute top-0 right-0 w-125 h-125 bg-primary/5 rounded-full blur-[120px] -z-10" />
            <div className="absolute bottom-0 left-0 w-125 h-125 bg-purple-500/5 rounded-full blur-[120px] -z-10" />

            <div className="container mx-auto px-4">
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <motion.h2
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight"
                    >
                        Simple, transparent <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-purple-500 animate-gradient-text">pricing</span>
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-lg text-muted-foreground mb-8"
                    >
                        Choose the plan that&apos;s right for you. switch to yearly billing and save up to 20%.
                    </motion.p>

                    <div className="flex items-center justify-center gap-4">
                        <span className={cn("text-sm font-medium transition-colors", !isYearly ? "text-foreground" : "text-muted-foreground")}>
                            Monthly
                        </span>
                        <Switch
                            checked={isYearly}
                            onCheckedChange={setIsYearly}
                        />
                        <span className={cn("text-sm font-medium transition-colors", isYearly ? "text-foreground" : "text-muted-foreground")}>
                            Yearly <span className="text-primary text-xs ml-1 font-bold">(Save 20%)</span>
                        </span>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
                    {pricingTiers.map((tier, index) => (
                        <motion.div
                            key={tier.name}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                            className={cn(
                                "relative rounded-2xl p-8 border backdrop-blur-xl transition-all duration-300",
                                tier.popular
                                    ? "bg-background/80 border-primary/50 shadow-2xl shadow-primary/10 scale-105 z-10"
                                    : "bg-background/40 border-border/50 hover:border-primary/30 hover:bg-background/60"
                            )}
                        >
                            {tier.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-primary-foreground text-xs font-bold rounded-full uppercase tracking-wider shadow-lg">
                                    Most Popular
                                </div>
                            )}

                            <div className="mb-8">
                                <h3 className="text-xl font-bold mb-2">{tier.name}</h3>
                                <p className="text-sm text-muted-foreground mb-6">{tier.description}</p>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-4xl font-bold">
                                        ${isYearly ? (tier.price.yearly / 12).toFixed(0) : tier.price.monthly}
                                    </span>
                                    <span className="text-muted-foreground">/month</span>
                                </div>
                                {isYearly && tier.price.yearly > 0 && (
                                    <p className="text-xs text-primary mt-2 font-medium">
                                        Billed ${tier.price.yearly} yearly
                                    </p>
                                )}
                            </div>

                            <div className="space-y-4 mb-8">
                                {tier.features.map((feature) => (
                                    <div key={feature} className="flex items-start gap-3">
                                        <div className="mt-1 p-0.5 rounded-full bg-primary/20 text-primary">
                                            <Check className="w-3 h-3" />
                                        </div>
                                        <span className="text-sm">{feature}</span>
                                    </div>
                                ))}
                                {tier.notIncluded?.map((feature) => (
                                    <div key={feature} className="flex items-start gap-3 opacity-50">
                                        <div className="mt-1 p-0.5 rounded-full bg-muted text-muted-foreground">
                                            <X className="w-3 h-3" />
                                        </div>
                                        <span className="text-sm text-muted-foreground">{feature}</span>
                                    </div>
                                ))}
                            </div>

                            <Button
                                className={cn(
                                    "w-full rounded-full transition-all duration-300",
                                    tier.popular
                                        ? "bg-primary hover:bg-primary/90 shadow-lg shadow-primary/25 hover:shadow-primary/40"
                                        : "bg-secondary hover:bg-secondary/80 text-foreground"
                                )}
                                variant={tier.popular ? "default" : "secondary"}
                            >
                                {tier.price.monthly === 0 ? 'Get Started Free' : 'Choose Plan'}
                            </Button>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
