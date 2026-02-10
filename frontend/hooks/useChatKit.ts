import { useState, useCallback } from 'react';
import { toast } from './use-toast';
import { useAuth } from '@/providers/auth-provider';

// VERSION: 2.0.0 - Added Authorization header support for production
// Types for ChatKit functionality
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: Date;
  toolCalls?: ToolCall[];
}

interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  status: 'initiated' | 'executing' | 'completed' | 'failed';
  result?: Record<string, unknown>;
}

interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface UseChatKitReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  createNewConversation: () => Promise<string | null>;
  getConversations: () => Promise<Conversation[]>;
}

const useChatKit = (): UseChatKitReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { session } = useAuth();

  const sendMessage = useCallback(async (message: string, conversationId?: string | null) => {
    const userId = session?.user?.id;

    if (!userId) {
      setError('Authentication required');
      toast({
        title: 'Authentication Error',
        description: 'Please log in to use the chat functionality',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Add user message immediately to UI
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        createdAt: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);

      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

      // Get token from localStorage for authentication
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

      // DEBUG: Log token status
      console.log('[ChatKit] Sending message - Token exists:', !!token);
      console.log('[ChatKit] Token length:', token ? token.length : 0);
      console.log('[ChatKit] Token preview:', token ? token.substring(0, 30) + '...' : 'null');

      // Prepare headers with Authorization token
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        console.log('[ChatKit] Authorization header added to request');
      } else {
        console.error('[ChatKit] NO TOKEN FOUND - Authorization header NOT added!');
      }

      console.log('[ChatKit] Request headers:', headers);

      // Call the backend API to process the message with the agent
      const response = await fetch(`${apiBaseUrl}/api/${userId}/chat`, {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify({
          content: message,
          conversation_id: conversationId || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add assistant response to the chat
      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.content || data.message || 'No response from assistant',
        createdAt: new Date(),
        toolCalls: data.tool_calls || [],
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to send message. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [session]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const createNewConversation = useCallback(async (): Promise<string | null> => {
    const userId = session?.user?.id;

    if (!userId) {
      setError('Authentication required');
      toast({
        title: 'Authentication Error',
        description: 'Please log in to create a conversation',
        variant: 'destructive',
      });
      return null;
    }

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

      // Get token from localStorage for authentication
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

      // Prepare headers with Authorization token
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${apiBaseUrl}/api/${userId}/conversations`, {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify({
          title: `Conversation ${new Date().toLocaleDateString()}`,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.id;
    } catch (err) {
      console.error('Create conversation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to create conversation');
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to create conversation. Please try again.',
        variant: 'destructive',
      });
      return null;
    }
  }, [session]);

  const getConversations = useCallback(async (): Promise<Conversation[]> => {
    const userId = session?.user?.id;

    if (!userId) {
      setError('Authentication required');
      toast({
        title: 'Authentication Error',
        description: 'Please log in to access conversations',
        variant: 'destructive',
      });
      return [];
    }

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

      // Get token from localStorage for authentication
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

      // Prepare headers with Authorization token
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${apiBaseUrl}/api/${userId}/conversations`, {
        method: 'GET',
        credentials: 'include',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.conversations || data || [];
    } catch (err) {
      console.error('Get conversations error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch conversations');
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to fetch conversations. Please try again.',
        variant: 'destructive',
      });
      return [];
    }
  }, [session]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    createNewConversation,
    getConversations,
  };
};

export default useChatKit;