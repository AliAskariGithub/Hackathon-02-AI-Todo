import type { Metadata } from "next";
import { Montserrat, Space_Grotesk } from 'next/font/google';
import "./globals.css";
import Navbar from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Providers } from "./providers";
import { Toaster } from "@/components/ui/toaster";
import { MotionConfig } from "framer-motion";

const space = Space_Grotesk({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

const montserrat = Montserrat({
  subsets: ['latin'],
  weight: ['400', '500', '700', '800', '900'],
  variable: '--font-montserrat',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: "AI Todo App - Smart Task Management with Natural Language | Y-Todo",
    template: "%s | Y-Todo"
  },
  description: "Manage tasks by simply chatting with AI. Y-Todo understands natural language, auto-prioritizes your day, and learns your patterns. Free forever plan available.",
  keywords: ["ai todo", "ai task management", "natural language todo", "smart task manager", "ai productivity", "intelligent todo app", "conversational task management", "ai assistant"],
  authors: [{ name: "Ali Askari" }],
  creator: "Ali Askari",
  publisher: "Y-Todo",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ai-y-todo.vercel.app",
    title: "AI Todo App - Smart Task Management with Natural Language",
    description: "Manage tasks by simply chatting with AI. Y-Todo understands natural language, auto-prioritizes your day, and learns your patterns.",
    siteName: "Y-Todo",
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Todo App - Smart Task Management with Natural Language",
    description: "Manage tasks by simply chatting with AI. Y-Todo understands natural language, auto-prioritizes your day, and learns your patterns.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning={true}>
      <body
        className={`${montserrat.variable} ${space.variable} antialiased`}
      >
        <Providers>
          <MotionConfig reducedMotion="user">
            <div className="flex flex-col min-h-screen">
              <Navbar />
              <main className="grow">
                {children}
              </main>
              <Footer />
            </div>
            <Toaster />
          </MotionConfig>
        </Providers>
      </body>
    </html>
  );
}
