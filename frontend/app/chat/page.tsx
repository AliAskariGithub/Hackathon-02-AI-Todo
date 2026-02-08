'use client';

import dynamic from 'next/dynamic';

// Dynamically import the chat content with no SSR to avoid browser API issues during build
const ChatContent = dynamic(() => import('./ChatContent'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>
  ),
});

export default function ChatPage() {
  return <ChatContent />;
}
