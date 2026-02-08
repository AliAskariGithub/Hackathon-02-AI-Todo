'use client';

import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import {
  Mail,
  MapPin,
  Phone,
  Github,
  Twitter,
  Send,
  MessageSquare,
  Globe,
  Sparkles,
  Facebook
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { PageWrapper } from '@/components/ui/page-wrapper';
import { cn } from '@/lib/utils';
import Link from 'next/link';

// Define the form schema using Zod
const contactFormSchema = z.object({
  name: z.string().min(2, { message: 'Name must be at least 2 characters.' }),
  email: z.string().email({ message: 'Please enter a valid email address.' }),
  subject: z.string().min(5, { message: 'Subject must be at least 5 characters.' }),
  message: z.string().min(10, { message: 'Message must be at least 10 characters.' }),
});

type ContactFormValues = z.infer<typeof contactFormSchema>;

export default function ContactPage() {
  const form = useForm<ContactFormValues>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      name: '',
      email: '',
      subject: '',
      message: '',
    },
  });

  function onSubmit(values: ContactFormValues) {
    console.log('Form submitted:', values);
    form.reset();
    alert('Thank you for your message! We\'ll get back to you soon.');
  }

  const contactInfo = [
    {
      icon: <Mail className="w-5 h-5" />,
      title: "Email",
      value: "syedaliaskarizaidi1@gmail.com",
      link: "mailto:syedaliaskarizaidi1@gmail.com",
      color: "bg-blue-500/20 text-blue-400"
    },
    {
      icon: <Phone className="w-5 h-5" />,
      title: "Phone",
      value: "+92 (319) 2046516",
      link: "tel:+923192046516",
      color: "bg-primary/20 text-primary"
    },
    {
      icon: <MapPin className="w-5 h-5" />,
      title: "Location",
      value: "Karachi, Pakistan",
      link: "#",
      color: "bg-purple-500/20 text-purple-400"
    },
    {
      icon: <Globe className="w-5 h-5" />,
      title: "Socials",
      value: "Connect with us",
      link: "https://github.com/AliAskariGithub",
      color: "bg-emerald-500/20 text-emerald-400",
      hasSocials: true
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <PageWrapper className="min-h-screen relative overflow-hidden bg-background py-20 px-4 md:py-32">
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full -z-10">
        <div className="absolute top-[10%] left-[5%] w-100 h-100 bg-primary/10 rounded-full blur-[120px] animate-blob" />
        <div className="absolute bottom-[10%] right-[5%] w-100 h-100 bg-purple-500/10 rounded-full blur-[120px] animate-blob animation-delay-2000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-150 h-150 bg-blue-500/5 rounded-full blur-[150px] animate-blob animation-delay-4000" />
      </div>

      <div className="container mx-auto max-w-7xl relative z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center mb-16 md:mb-24"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold uppercase tracking-wider mb-4">
            <Sparkles className="w-3 h-3" />
            Contact Us
          </div>
          <h1 className="text-4xl md:text-7xl font-black mb-6 tracking-tight">
            Let&apos;s build something <br />
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-emerald-400 to-blue-500">
              incredible together
            </span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto font-light leading-relaxed">
            Have a question, feedback, or a brilliant idea? We&apos;re here to listen and help you reach your goals.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start"
        >
          {/* Left Column: Contact Info */}
          <div className="lg:col-span-5 space-y-6">
            <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
              <MessageSquare className="w-6 h-6 text-primary" />
              Contact Information
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4">
              {contactInfo.map((info) => (
                <motion.div
                  key={info.title}
                  variants={itemVariants}
                  whileHover={{ y: -5, scale: 1.02 }}
                  className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl hover:border-primary/30 transition-all duration-300 group"
                >
                  <div className="flex items-start gap-4">
                    <div className={cn("p-3 rounded-xl transition-transform group-hover:scale-110", info.color)}>
                      {info.icon}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-1">{info.title}</p>
                      {info.hasSocials ? (
                        <div className="flex gap-4 mt-2">
                          <Link href="https://github.com/AliAskariGithub" className="text-muted-foreground hover:text-primary transition-colors"><Github className="w-5 h-5" /></Link>
                          <Link href="https://x.com/Syed_Ali_Askari" className="text-muted-foreground hover:text-primary transition-colors"><Twitter className="w-5 h-5" /></Link>
                          <Link href="https://www.facebook.com/NexuGem" className="text-muted-foreground hover:text-primary transition-colors"><Facebook className="w-5 h-5" /></Link>
                        </div>
                      ) : (
                        <Link href={info.link} className="text-base font-semibold text-foreground hover:text-primary transition-colors">
                          {info.value}
                        </Link>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Support Message */}
            <motion.div
              variants={itemVariants}
              className="mt-8 p-8 rounded-2xl bg-linear-to-br from-primary/10 to-transparent border border-primary/20 backdrop-blur-sm"
            >
              <h3 className="text-lg font-bold mb-2">Our commitment to you</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                We typically respond to all inquiries within 24 business hours. Your success is our priority, and we look forward to hearing from you.
              </p>
            </motion.div>
          </div>

          {/* Right Column: Contact Form */}
          <motion.div
            variants={itemVariants}
            className="lg:col-span-7 bg-white/5 border border-white/10 backdrop-blur-2xl rounded-3xl p-8 md:p-12 shadow-2xl relative"
          >
            {/* Form Glow */}
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/10 rounded-full blur-[80px] -z-10" />

            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs uppercase tracking-widest font-bold opacity-70">Full Name</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Alex Morgan"
                            className="bg-background/40 border-white/10 h-12 focus:border-primary/50 transition-all rounded-xl"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs uppercase tracking-widest font-bold opacity-70">Email Address</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="alex@example.com"
                            className="bg-background/40 border-white/10 h-12 focus:border-primary/50 transition-all rounded-xl"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="subject"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs uppercase tracking-widest font-bold opacity-70">Subject</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="How can we help?"
                          className="bg-background/40 border-white/10 h-12 focus:border-primary/50 transition-all rounded-xl"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="message"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-xs uppercase tracking-widest font-bold opacity-70">Message</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Tell us more about your inquiry..."
                          rows={6}
                          className="bg-background/40 border-white/10 focus:border-primary/50 transition-all rounded-2xl resize-none"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  size="lg"
                  className="w-full h-14 bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-lg rounded-2xl shadow-xl shadow-primary/20 hover:scale-[1.02] transform transition-all group"
                >
                  Send Message
                  <Send className="ml-2 w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                </Button>
              </form>
            </Form>
          </motion.div>
        </motion.div>
      </div>
    </PageWrapper>
  );
}