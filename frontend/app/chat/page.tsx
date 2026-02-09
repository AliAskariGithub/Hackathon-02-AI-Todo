'use client';

import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';
import { Loader2, MessageSquare } from 'lucide-react';

// Dynamically import the chat page content with SSR disabled
// This prevents "navigator is not defined" errors during build
const ChatPageContent = dynamic(() => import('./ChatPageContent'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col items-center gap-4 p-8"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Loader2 className="h-10 w-10 sm:h-12 sm:w-12 text-primary" />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-col items-center gap-2"
        >
          <MessageSquare className="h-8 w-8 sm:h-10 sm:w-10 text-primary/60" />
          <p className="text-sm sm:text-base font-medium text-muted-foreground">Loading chat...</p>
        </motion.div>
      </motion.div>
    </div>
  ),
});

export default function ChatPage() {
  return <ChatPageContent />;
}