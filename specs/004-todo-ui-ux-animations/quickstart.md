# Quickstart Guide: Advanced UI/UX & Animations

**Feature**: Advanced UI/UX & Animations
**Date**: 2026-02-05
**Status**: Draft

## Overview
This guide will help you set up and run the enhanced UI/UX with animations for the todo application. The feature includes dark/light theme support, smooth animations, and improved dashboard experience.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Next.js 16.1.2 project with existing frontend
- Shadcn UI components already configured

## Installation Steps

### 1. Install Dependencies
```bash
npm install next-themes framer-motion @radix-ui/react-dialog
```

### 2. Configure Fonts
Update your layout to include the new fonts:

```tsx
// app/layout.tsx
import { Montserrat } from 'next/font/google';

const montserrat = Montserrat({
  subsets: ['latin'],
  variable: '--font-montserrat',
  display: 'swap',
});
```

### 3. Set Up Theme Provider
Create a provider wrapper in your app:

```tsx
// app/providers.tsx
'use client';
import { ThemeProvider } from 'next-themes';
import { ReactNode } from 'react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark">
      {children}
    </ThemeProvider>
  );
}
```

### 4. Update Root Layout
Integrate providers and font classes in your root layout:

```tsx
// app/layout.tsx
import { Providers } from './providers';
import { montserrat } from './fonts';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${montserrat.variable}`}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

### 5. Add Custom Colors to Tailwind
Add the new color palette to your Tailwind configuration:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0FFF50',
          light: '#f6f6f6',
          dark: '#161616',
        },
        secondary: {
          dark: '#232323',
          light: '#f5f4f2',
        },
      },
      fontFamily: {
        'montserrat': 'var(--font-montserrat)',
      },
    },
  },
};
```

## Running the Application

### Development Mode
```bash
npm run dev
```

Visit `http://localhost:3000` to see the enhanced UI with themes and animations.

### Build for Production
```bash
npm run build
npm start
```

## Key Features

### Theme Switching
- Toggle between dark/light modes using the theme switch in the header
- Theme preference persists across sessions
- Automatic system preference detection

### Dashboard Enhancements
- Summary cards showing task statistics with animated counters
- Floating action button for creating new tasks
- Create task dialog with smooth animations

### Loading States
- Skeleton loaders during data fetching
- Consistent loading states across all data-dependent components
- No layout shift during loading transitions

### Animations
- Smooth page transitions using Framer Motion
- Staggered animations for task lists
- Entrance animations for dashboard elements

## Troubleshooting

### Font Loading Issues
If fonts don't appear:
1. Verify you've added the font imports to your layout
2. Check that Tailwind is properly configured with the font variables
3. Confirm the font families are correctly named

### Theme Not Persisting
If the theme doesn't persist:
1. Check browser's localStorage for theme values
2. Verify ThemeProvider is wrapping the entire app
3. Ensure no conflicting theme systems exist

### Animation Performance
If animations are janky:
1. Check if you're animating layout properties
2. Verify you're using transform and opacity for animations
3. Consider reducing animation complexity on lower-end devices

## Next Steps
- Customize the theme colors to match brand guidelines
- Add more animated components based on the established patterns
- Implement reduced motion preferences for accessibility