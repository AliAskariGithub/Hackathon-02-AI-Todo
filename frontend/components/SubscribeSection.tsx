'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, CheckCircle2, SubscriptIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function SubscribeSection() {
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success'>('idle');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email) return;

        setStatus('loading');

        // Simulate API call
        setTimeout(() => {
            setStatus('success');
            setEmail('');

            // Reset success message after 3 seconds
            setTimeout(() => setStatus('idle'), 3000);
        }, 1500);
    };

    return (
        <section id="subscribe" className="py-24 relative overflow-hidden">
            {/* Background Mesh */}
            <div className="absolute inset-0 bg-linear-to-b from-transparent via-primary/5 to-transparent opacity-50 pointer-events-none" />

            <div className="container mx-auto px-4 relative z-10 text-center">

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/5 text-primary text-sm font-bold uppercase tracking-widest mb-6 border border-primary/10 hover:bg-primary/10 transition-colors cursor-default"
                >
                    <SubscriptIcon className="w-4 h-4" />
                    Stay Updated
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="max-w-4xl mx-auto rounded-3xl p-1 bg-linear-to-r from-primary/20 via-purple-500/20 to-blue-500/20 shadow-2xl"
                >
                    <div className="bg-background/80 backdrop-blur-xl rounded-[22px] px-8 py-16 md:px-16 md:py-20 text-center border border-white/10 dark:border-white/5">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.1 }}
                            className="mb-8"
                        >
                            <h2 className="text-3xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-linear-to-r from-foreground to-foreground/70">
                                Stay in the <span className="text-primary">loop</span>
                            </h2>
                            <p className="text-lg text-muted-foreground max-w-xl mx-auto">
                                Join our newsletter for exclusive tips, product updates, and early access to new features.
                            </p>
                        </motion.div>

                        <motion.form
                            onSubmit={handleSubmit}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            className="max-w-md mx-auto relative group"
                        >
                            <div className="relative flex items-center">
                                <Input
                                    type="email"
                                    placeholder="Enter your email address"
                                    className="h-14 rounded-full pl-6 pr-36 text-base bg-background/50 border-primary/20 focus:border-primary/50 focus:ring-primary/20 transition-all"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={status === 'loading' || status === 'success'}
                                />
                                <Button
                                    type="submit"
                                    disabled={status === 'loading' || status === 'success'}
                                    className={cn(
                                        "absolute right-1.5 h-11 rounded-full px-6 transition-all duration-300",
                                        status === 'success' ? "bg-green-500 hover:bg-green-600" : "bg-primary hover:bg-primary/90"
                                    )}
                                >
                                    {status === 'loading' ? (
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    ) : status === 'success' ? (
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            className="flex items-center gap-2"
                                        >
                                            <CheckCircle2 className="w-4 h-4" />
                                            <span>Joined!</span>
                                        </motion.div>
                                    ) : (
                                        <div className="flex items-center gap-2">
                                            <span>Subscribe</span>
                                            <Send className="w-4 h-4" />
                                        </div>
                                    )}
                                </Button>
                            </div>
                            {/* Glow Effect */}
                            <div className="absolute inset-0 -z-10 bg-primary/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        </motion.form>

                        <p className="mt-6 text-xs text-muted-foreground">
                            No spam, unsubscribe at any time.
                        </p>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
