'use client';

import { useEffect, useState } from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import {
  User,
  Bell,
  Shield,
  Save,
  CheckCircle,
  Camera,
  Mail,
  Lock,
  Smartphone,
  CreditCard,
  LogOut,
  Sparkles,
  ChevronRight
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
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { useAuth } from '@/providers/auth-provider';
import { PageWrapper } from '@/components/ui/page-wrapper';
import Link from 'next/link';

// Define the profile form schema
const profileFormSchema = z.object({
  name: z.string().min(2, { message: 'Name must be at least 2 characters.' }),
  email: z.string().email({ message: 'Please enter a valid email address.' }),
});

type ProfileFormValues = z.infer<typeof profileFormSchema>;

export default function SettingsPage() {
  const { session, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues: {
      name: session?.user?.name || '',
      email: session?.user?.email || '',
    },
  });

  // Update form when session data changes
  useEffect(() => {
    if (session?.user) {
      form.reset({
        name: session.user.name || '',
        email: session.user.email || '',
      });
    }
  }, [session, form]);

  async function onSubmit(values: ProfileFormValues) {
    setIsLoading(true);
    setSaveStatus('idle');

    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      console.log('Profile update submitted:', values);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Error updating profile:', error);
      setSaveStatus('error');
    } finally {
      setIsLoading(false);
    }
  }

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

  if (!session) {
    return (
      <PageWrapper className="min-h-screen flex items-center justify-center py-20 px-4">
        <div className="absolute inset-0 -z-10 bg-background overflow-hidden">
          <div className="absolute top-[10%] left-[10%] w-125 h-125 bg-primary/5 rounded-full blur-[120px]" />
          <div className="absolute bottom-[10%] right-[10%] w-125 h-125 bg-destructive/5 rounded-full blur-[120px]" />
        </div>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-white/5 border border-white/10 backdrop-blur-2xl rounded-3xl p-8 md:p-12 text-center shadow-2xl"
        >
          <div className="mx-auto w-20 h-20 bg-destructive/10 rounded-2xl flex items-center justify-center mb-6">
            <Shield className="w-10 h-10 text-destructive" />
          </div>
          <h1 className="text-3xl font-bold mb-4">Access Denied</h1>
          <p className="text-muted-foreground mb-8">
            You must be logged in to access the settings page.
          </p>
          <Button asChild className="w-full bg-primary hover:bg-primary/90 text-primary-foreground h-12 rounded-xl text-lg font-bold">
            <a href="/login">Go to Login</a>
          </Button>
        </motion.div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper className="min-h-screen relative overflow-hidden bg-background py-24 px-4 md:py-40">
      {/* Background Atmosphere */}
      <div className="absolute top-0 left-0 w-full h-full -z-10">
        <div className="absolute top-[5%] right-[10%] w-150 h-150 bg-primary/10 rounded-full blur-[150px] animate-blob" />
        <div className="absolute bottom-[5%] left-[10%] w-150 h-150 bg-purple-500/10 rounded-full blur-[150px] animate-blob animation-delay-2000" />
      </div>

      <div className="container mx-auto max-w-6xl relative z-10">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12 md:mb-16"
        >
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold uppercase tracking-wider mb-4">
              <Sparkles className="w-3 h-3" />
              Settings
            </div>
            <h1 className="text-4xl md:text-6xl font-black tracking-tight mb-2">
              Control your <span className="text-transparent bg-clip-text bg-linear-to-r from-primary to-emerald-400">universe</span>
            </h1>
            <p className="text-lg text-muted-foreground font-light">
              Manage your personal vault, security, and digital presence.
            </p>
          </div>
          <Button
            variant="outline"
            className="rounded-xl h-12 px-6 border-white/10 bg-white/5 hover:bg-white/10 text-destructive hover:border-destructive/30 transition-all flex items-center gap-2"
            onClick={async () => {
              await logout();
              window.location.href = '/login';
            }}
          >
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Navigation Tabs */}
          <div className="lg:col-span-3">
            <Tabs defaultValue="profile" className="w-full">
              <TabsList className="flex lg:flex-col items-stretch h-auto bg-transparent gap-2 p-0 border-0 overflow-x-auto lg:overflow-visible pb-4 lg:pb-0">
                <TabsTrigger
                  value="profile"
                  className="justify-start px-6 py-4 rounded-2xl border border-white/5 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-lg data-[state=active]:shadow-primary/25 transition-all flex items-center gap-3 text-base font-bold"
                >
                  <User className="w-5 h-5" />
                  Profile
                </TabsTrigger>
                <TabsTrigger
                  value="preferences"
                  className="justify-start px-6 py-4 rounded-2xl border border-white/5 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-lg data-[state=active]:shadow-primary/25 transition-all flex items-center gap-3 text-base font-bold"
                >
                  <Bell className="w-5 h-5" />
                  Notifications
                </TabsTrigger>
                <TabsTrigger
                  value="security"
                  className="justify-start px-6 py-4 rounded-2xl border border-white/5 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-lg data-[state=active]:shadow-primary/25 transition-all flex items-center gap-3 text-base font-bold"
                >
                  <Shield className="w-5 h-5" />
                  Security
                </TabsTrigger>
              </TabsList>

              <div className="lg:hidden h-px bg-white/10 my-6" />
            </Tabs>
          </div>

          {/* Settings Content */}
          <div className="lg:col-span-9">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="space-y-8"
            >
              {/* Profile Card */}
              <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 backdrop-blur-2xl rounded-3xl overflow-hidden shadow-2xl">
                <div className="bg-linear-to-r from-primary/10 to-transparent p-6 md:p-8 border-b border-white/10 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center">
                      <User className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold">Profile Identity</h3>
                      <p className="text-sm text-muted-foreground">This is how the world sees you.</p>
                    </div>
                  </div>
                </div>

                <div className="p-6 md:p-8 space-y-8">
                  {/* Avatar Section */}
                  <div className="flex flex-col md:flex-row items-center gap-8">
                    <div className="relative group">
                      <div className="w-32 h-32 rounded-3xl bg-linear-to-br from-primary/20 to-purple-500/20 border-2 border-dashed border-primary/40 flex items-center justify-center overflow-hidden transition-all group-hover:border-primary">
                        {session?.user?.name ? (
                          <span className="text-5xl font-black text-primary/50 group-hover:scale-110 transition-transform">
                            {session.user.name.charAt(0)}
                          </span>
                        ) : (
                          <User className="w-12 h-12 text-primary/30" />
                        )}
                      </div>
                      <button className="absolute -bottom-2 -right-2 p-2 bg-primary text-primary-foreground rounded-xl shadow-lg hover:scale-110 transition-all">
                        <Camera className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="text-center md:text-left">
                      <h4 className="font-bold text-lg mb-1">Your Avatar</h4>
                      <p className="text-sm text-muted-foreground mb-4 max-w-sm">
                        Recommended size is 256x256px. Support for JPG, PNG, and GIF.
                      </p>
                      <div className="flex flex-wrap justify-center md:justify-start gap-2">
                        <Button size="sm" className="bg-primary hover:bg-primary/90 rounded-lg">Upload New</Button>
                        <Button size="sm" variant="outline" className="border-white/10 bg-transparent rounded-lg">Remove</Button>
                      </div>
                    </div>
                  </div>

                  <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <FormField
                          control={form.control}
                          name="name"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="text-xs uppercase tracking-widest font-bold opacity-70">Display Name</FormLabel>
                              <FormControl>
                                <div className="relative">
                                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                  <Input
                                    placeholder="Your Name"
                                    className="bg-background/40 border-white/10 h-12 pl-10 focus:border-primary/50 transition-all rounded-xl"
                                    {...field}
                                  />
                                </div>
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
                                <div className="relative opacity-60">
                                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                  <Input
                                    disabled
                                    className="bg-background/20 border-white/10 h-12 pl-10 rounded-xl cursor-not-allowed"
                                    {...field}
                                  />
                                </div>
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>

                      <div className="flex items-center justify-between pt-4 border-t border-white/10">
                        <motion.div
                          animate={{ opacity: saveStatus !== 'idle' ? 1 : 0 }}
                          className="flex items-center gap-2"
                        >
                          {saveStatus === 'success' && (
                            <span className="text-green-400 flex items-center gap-2 text-sm font-medium">
                              <CheckCircle className="w-4 h-4" />
                              Changes updated successfully
                            </span>
                          )}
                        </motion.div>
                        <Button
                          type="submit"
                          disabled={isLoading}
                          className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold px-8 h-12 rounded-xl shadow-lg shadow-primary/20 flex items-center gap-2"
                        >
                          {isLoading ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          ) : (
                            <>
                              <Save className="w-4 h-4" />
                              Save Profile
                            </>
                          )}
                        </Button>
                      </div>
                    </form>
                  </Form>
                </div>
              </motion.div>

              {/* Preferences & Security (Quick Actions) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 backdrop-blur-2xl rounded-3xl p-8 hover:border-primary/20 transition-all group">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <Bell className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">Notifications</h3>
                  <p className="text-sm text-muted-foreground mb-8">Manage how you receive alerts and updates.</p>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5">
                      <span className="font-medium text-sm">Push Notifications</span>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5">
                      <span className="font-medium text-sm">Security Alerts</span>
                      <Switch defaultChecked />
                    </div>
                  </div>
                </motion.div>

                <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 backdrop-blur-2xl rounded-3xl p-8 hover:border-purple-500/20 transition-all group">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <Shield className="w-6 h-6 text-purple-400" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">Vault Security</h3>
                  <p className="text-sm text-muted-foreground mb-8">Keep your account safe with extra layers.</p>

                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-between h-14 rounded-2xl border-white/10 bg-white/5 hover:bg-white/10 group/btn">
                      <div className="flex items-center gap-3">
                        <Lock className="w-4 h-4" />
                        <span>Change Password</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground group-hover/btn:translate-x-1 transition-transform" />
                    </Button>
                    <Button variant="outline" className="w-full justify-between h-14 rounded-2xl border-white/10 bg-white/5 hover:bg-white/10 group/btn">
                      <div className="flex items-center gap-3">
                        <Smartphone className="w-4 h-4" />
                        <span>2-Step Verification</span>
                      </div>
                      <div className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider">Enabled</div>
                    </Button>
                  </div>
                </motion.div>
              </div>

              {/* Subscription Status (Bonus) */}
              <motion.div variants={itemVariants} className="bg-linear-to-r from-primary/20 via-primary/5 to-transparent border border-primary/20 backdrop-blur-xl rounded-3xl p-8 flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex items-center gap-6">
                  <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center shrink-0">
                    <CreditCard className="w-8 h-8 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">Pro Plan</h3>
                    <p className="text-muted-foreground">Your next billing date is <span className="text-foreground font-medium">Sept 21, 2026</span></p>
                  </div>
                </div>
                <Link href="/#pricing">
                  <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold px-8 h-12 rounded-xl shrink-0">
                    Manage Billing
                  </Button>
                </Link>

              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}