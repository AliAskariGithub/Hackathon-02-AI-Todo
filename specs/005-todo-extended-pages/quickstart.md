# Quickstart Guide: Extended Pages & Carousel

**Feature**: Extended Pages & Carousel
**Date**: 2026-02-05
**Status**: Draft

## Overview
This guide will help you set up and run the Extended Pages & Carousel feature. The feature includes enhanced authentication pages, testimonial carousel, contact page, user settings page, and an improved footer.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Next.js 16.1.2 project with existing frontend
- Better Auth configured for authentication
- Shadcn UI components already configured

## Installation Steps

### 1. Install Dependencies (if not already installed)
```bash
npm install lucide-react
# Note: Framer Motion, Better Auth, and Shadcn UI should already be installed
```

### 2. Create Carousel Component
Create the testimonial carousel with automatic rotation:

```tsx
// components/testimonials/carousel.tsx
'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Testimonial } from '@/types/testimonial'; // Assuming you have this type

interface CarouselProps {
  testimonials: Testimonial[];
}

export default function TestimonialCarousel({ testimonials }: CarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const itemsPerPage = 3;

  // Calculate pages
  const totalPages = Math.ceil(testimonials.length / itemsPerPage);

  // Pad testimonials to ensure even division
  const paddedTestimonials = [...testimonials];
  while (paddedTestimonials.length % itemsPerPage !== 0 && paddedTestimonials.length > 0) {
    paddedTestimonials.push({ ...testimonials[testimonials.length % testimonials.length] }); // Duplicate last item
  }

  // Split testimonials into pages
  const pages = [];
  for (let i = 0; i < paddedTestimonials.length; i += itemsPerPage) {
    pages.push(paddedTestimonials.slice(i, i + itemsPerPage));
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % totalPages);
    }, 5000); // 5 seconds

    return () => clearInterval(interval);
  }, [totalPages]);

  return (
    <div className="relative overflow-hidden">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -100 }}
          transition={{ duration: 0.5 }}
          className="flex gap-4"
        >
          {pages[currentIndex]?.map((testimonial, idx) => (
            <div key={`${currentIndex}-${idx}`} className="flex-1 p-4 bg-card rounded-lg shadow">
              <p className="text-foreground">"{testimonial.quote}"</p>
              <p className="mt-2 font-semibold text-primary">- {testimonial.author}</p>
            </div>
          ))}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
```

### 3. Create Contact Page
Set up the contact page with form validation:

```tsx
// app/contact/page.tsx
'use client';

import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
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

const contactFormSchema = z.object({
  name: z.string().min(2, { message: 'Name must be at least 2 characters.' }),
  email: z.string().email({ message: 'Please enter a valid email.' }),
  subject: z.string().min(5, { message: 'Subject must be at least 5 characters.' }),
  message: z.string().min(10, { message: 'Message must be at least 10 characters.' }),
});

export default function ContactPage() {
  const form = useForm<z.infer<typeof contactFormSchema>>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      name: '',
      email: '',
      subject: '',
      message: '',
    },
  });

  function onSubmit(values: z.infer<typeof contactFormSchema>) {
    console.log(values);
    // Process the form submission
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Contact Us</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-2xl">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input placeholder="John Doe" {...field} />
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
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input placeholder="john@example.com" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="subject"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Subject</FormLabel>
                <FormControl>
                  <Input placeholder="How can we help?" {...field} />
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
                <FormLabel>Message</FormLabel>
                <FormControl>
                  <Textarea placeholder="Your message here..." rows={5} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit">Send Message</Button>
        </form>
      </Form>
    </div>
  );
}
```

### 4. Create Settings Page
Implement the settings page with tabbed UI:

```tsx
// app/settings/page.tsx
'use client';

import { useSession } from 'better-auth/react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function SettingsPage() {
  const { data: session, update: updateSession } = useSession();

  // Server Action to update user profile (to be implemented in app/actions/user.ts)
  const updateUserProfile = async (formData: FormData) => {
    // Implementation will go here
  };

  if (!session) {
    return <div>Please log in to access settings</div>;
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">User Settings</h1>

      <Tabs defaultValue="profile" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
            </CardHeader>
            <CardContent>
              <form action={updateUserProfile} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    name="name"
                    defaultValue={session.user.name || ''}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    defaultValue={session.user.email || ''}
                    required
                  />
                </div>

                <Button type="submit">Update Profile</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preferences">
          <Card>
            <CardHeader>
              <CardTitle>Preferences</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Preferences settings will go here...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### 5. Create Enhanced Footer
Implement the responsive footer with navigation and social links:

```tsx
// components/footer.tsx
import Link from 'next/link';
import { Twitter, Github, Linkedin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-secondary py-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">Todo App</h3>
            <p className="text-secondary-foreground">
              Boost your productivity with our intuitive todo application.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-4">Pages</h4>
            <ul className="space-y-2">
              <li><Link href="/" className="text-secondary-foreground hover:text-primary">Home</Link></li>
              <li><Link href="/dashboard" className="text-secondary-foreground hover:text-primary">Dashboard</Link></li>
              <li><Link href="/settings" className="text-secondary-foreground hover:text-primary">Settings</Link></li>
              <li><Link href="/contact" className="text-secondary-foreground hover:text-primary">Contact</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-4">Legal</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-secondary-foreground hover:text-primary">Privacy Policy</a></li>
              <li><a href="#" className="text-secondary-foreground hover:text-primary">Terms of Service</a></li>
              <li><a href="#" className="text-secondary-foreground hover:text-primary">Cookie Policy</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium mb-4">Connect</h4>
            <div className="flex space-x-4">
              <a href="#" className="text-secondary-foreground hover:text-primary">
                <Twitter className="h-6 w-6" />
              </a>
              <a href="#" className="text-secondary-foreground hover:text-primary">
                <Github className="h-6 w-6" />
              </a>
              <a href="#" className="text-secondary-foreground hover:text-primary">
                <Linkedin className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-border mt-8 pt-6 text-center text-secondary-foreground">
          <p>© {new Date().getFullYear()} Todo App. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
```

### 6. Update Main Layout
Add the footer to the main layout:

```tsx
// Update app/layout.tsx or wherever you include the main layout
// Add the Footer component to your main layout file
import Footer from '@/components/footer';

// In your main layout JSX:
return (
  <html lang="en">
    <body>
      <Providers>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          <main className="flex-grow">
            {children}
          </main>
          <Footer />
        </div>
      </Providers>
    </body>
  </html>
);
```

### 7. Create Custom Auth Pages
Override the default auth pages with custom designs:

```tsx
// app/login/page.tsx
'use client';

import { useState } from 'react';
import { authClient } from '@/lib/auth'; // assuming this is your auth client
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const result = await authClient.signIn.email({
        email,
        password,
        redirectTo: '/dashboard',
      });

      if (result.error) {
        setError(result.error.message);
      } else {
        router.push('/dashboard');
      }
    } catch (err) {
      setError('An error occurred during login');
      console.error(err);
    }
  };

  return (
    <div className="container mx-auto py-8 flex justify-center">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center">Login</h1>

        {error && <div className="mb-4 p-3 bg-destructive text-destructive-foreground rounded">{error}</div>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <Button type="submit" className="w-full">Login</Button>
        </form>

        <p className="mt-4 text-center">
          Don't have an account? <a href="/signup" className="text-primary hover:underline">Sign up</a>
        </p>
      </div>
    </div>
  );
}
```

```tsx
// app/signup/page.tsx
'use client';

import { useState } from 'react';
import { authClient } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const result = await authClient.signUp.email({
        email,
        password,
        name,
        redirectTo: '/dashboard',
      });

      if (result.error) {
        setError(result.error.message);
      } else {
        router.push('/dashboard');
      }
    } catch (err) {
      setError('An error occurred during signup');
      console.error(err);
    }
  };

  return (
    <div className="container mx-auto py-8 flex justify-center">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center">Create Account</h1>

        {error && <div className="mb-4 p-3 bg-destructive text-destructive-foreground rounded">{error}</div>}

        <form onSubmit={handleSignup} className="space-y-4">
          <div>
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <Button type="submit" className="w-full">Sign Up</Button>
        </form>

        <p className="mt-4 text-center">
          Already have an account? <a href="/login" className="text-primary hover:underline">Log in</a>
        </p>
      </div>
    </div>
  );
}
```

### 8. Update proxy.ts for Route Protection
Add the settings route to proxy configuration:

```ts
// proxy.ts (or middleware configuration)
// Add the settings route to protected routes
export default withProxy({
  proxies: {
    // ... other proxies
    '/settings': {
      target: process.env.NEXTAUTH_URL || 'http://localhost:3000',
      // Add authentication check for /settings route
      middleware: (req, res) => {
        // Implement auth check here
        const isAuthenticated = req.cookies['auth-token']; // or however you track auth

        if (!isAuthenticated) {
          // Redirect to login
          return new Response(null, {
            status: 302,
            headers: {
              Location: '/login',
            },
          });
        }
      }
    }
  }
});
```

## Running the Application

### Development Mode
```bash
npm run dev
```

Visit `http://localhost:3000` to see the enhanced UI with new pages and features.

### Build for Production
```bash
npm run build
npm start
```

## Key Features

### Enhanced Authentication
- Custom login and signup pages with Electric Lime theme
- Proper form validation and error handling
- Seamless integration with Better Auth

### Dynamic Testimonial Carousel
- Automatic rotation every 5 seconds
- Smooth slide transitions using Framer Motion
- Responsive design with 3 testimonials at a time

### New Core Pages
- Contact page with form validation
- User settings page with tabbed UI
- Protected route for settings page

### Comprehensive Footer
- Organized navigation links
- Social media integration
- Responsive layout for all devices

## Troubleshooting

### Carousel Issues
If the carousel doesn't rotate:
1. Check if useEffect is properly updating the index
2. Verify the interval is set to 5000ms
3. Ensure testimonials array is populated

### Route Protection
If settings page is accessible without authentication:
1. Check proxy.ts or middleware configuration
2. Verify authentication token is being checked properly
3. Ensure redirects to login page work correctly

### Form Validation
If forms don't show validation errors:
1. Verify Zod schema is properly defined
2. Check that react-hook-form is correctly integrated
3. Confirm error messages are being displayed properly