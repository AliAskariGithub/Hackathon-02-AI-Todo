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
    default: "Todo App - Manage Your Tasks Efficiently",
    template: "%s | Todo App"
  },
  description: "Boost your productivity with our intuitive todo application. Manage tasks, track progress, and stay organized.",
  keywords: ["todo", "productivity", "task management", "organizer"],
  authors: [{ name: "Ali Askari" }],
  creator: "Ali Askari",
  publisher: "Ali Askari",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://todo-app.example.com",
    title: "Todo App - Manage Your Tasks Efficiently",
    description: "Boost your productivity with our intuitive todo application. Manage tasks, track progress, and stay organized.",
    siteName: "Todo App",
  },
  twitter: {
    card: "summary_large_image",
    title: "Todo App - Manage Your Tasks Efficiently",
    description: "Boost your productivity with our intuitive todo application. Manage tasks, track progress, and stay organized.",
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
