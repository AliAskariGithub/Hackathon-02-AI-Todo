'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Send,
  Bot,
  User,
  Loader2,
  CheckCircle2,
  XCircle,
  Trash2,
  Clock
} from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { KeyboardShortcuts } from '@/components/chat/KeyboardShortcutHint';
import { FocusModeToggle } from '@/components/chat/FocusModeToggle';
import { FocusModeWrapper } from '@/components/chat/FocusModeWrapper';
import { DisplayModeToggle } from '@/components/chat/DisplayModeToggle';
import { JsonMessageView } from '@/components/chat/JsonMessageView';
import { TaskLinkButton } from '@/components/chat/TaskLinkButton';
import { useUIStore } from '@/stores/ui-store';
import { parseTaskReferences } from '@/lib/utils/taskLinkGenerator';

// Types for chat functionality
interface Message {
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

interface BackendToolCall {
  name: string;
  arguments: Record<string, unknown>;
  result?: Record<string, unknown>;
}

const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rateLimitUntil, setRateLimitUntil] = useState<number | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<string>('');
  const [keyboardFocused, setKeyboardFocused] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const { focusMode, setFocusMode, displayMode } = useUIStore();

  // Load chat history on mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  // Scroll to bottom of messages when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check rate limit status on mount and set up countdown timer
  useEffect(() => {
    const rateLimitTimestamp = localStorage.getItem('rateLimitUntil');
    if (rateLimitTimestamp) {
      const timestamp = parseInt(rateLimitTimestamp);
      if (timestamp > Date.now()) {
        setRateLimitUntil(timestamp);
      } else {
        localStorage.removeItem('rateLimitUntil');
      }
    }
  }, []);

  // Update countdown timer every second
  useEffect(() => {
    if (!rateLimitUntil) return;

    const interval = setInterval(() => {
      const now = Date.now();
      const remaining = rateLimitUntil - now;

      if (remaining <= 0) {
        setRateLimitUntil(null);
        setTimeRemaining('');
        localStorage.removeItem('rateLimitUntil');
        clearInterval(interval);
      } else {
        const hours = Math.floor(remaining / (1000 * 60 * 60));
        const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
        setTimeRemaining(`${hours}h ${minutes}m ${seconds}s`);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [rateLimitUntil]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onFocusChat: () => {
      inputRef.current?.focus();
      setKeyboardFocused(true);
      setTimeout(() => setKeyboardFocused(false), 300);
    },
    onEscape: () => {
      if (focusMode) {
        setFocusMode(false);
      } else {
        inputRef.current?.blur();
      }
    },
    enabled: !isLoading && !isLoadingHistory,
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      setIsLoadingHistory(true);
      const conversationId = localStorage.getItem('currentConversationId');
      const userId = localStorage.getItem('userId');
      const authToken = localStorage.getItem('auth-token');

      if (!conversationId || !userId || !authToken) {
        setIsLoadingHistory(false);
        return;
      }

      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
      const response = await fetch(
        `${apiBaseUrl}/api/${userId}/conversations/${conversationId}/messages`,
        {
          headers: {
            'Authorization': `Bearer ${authToken}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        const loadedMessages: Message[] = data.map((msg: {
          id: string;
          role: 'user' | 'assistant';
          content: string;
          created_at: string;
          tool_calls?: BackendToolCall[];
        }) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          createdAt: new Date(msg.created_at),
          toolCalls: msg.tool_calls?.map((toolCall, index) => ({
            id: `${msg.id}-tool-${index}`,
            name: toolCall.name,
            arguments: toolCall.arguments,
            status: toolCall.result ? ('completed' as const) : ('failed' as const),
            result: toolCall.result,
          })),
        }));
        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error('Error loading chat history:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const clearChat = async () => {
    try {
      const conversationId = localStorage.getItem('currentConversationId');
      if (conversationId) {
        localStorage.removeItem('currentConversationId');
      }
      setMessages([]);
      toast({
        variant: "success",
        title: 'Chat cleared',
        description: 'Your conversation has been cleared.',
      });
    } catch (err) {
      console.error('Error clearing chat:', err);
      toast({
        variant: "destructive",
        title: 'Error',
        description: 'Failed to clear chat. Please try again.',
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    // Check if rate limited
    if (rateLimitUntil && rateLimitUntil > Date.now()) {
      toast({
        variant: "warning",
        title: 'Rate Limited',
        description: `Please wait ${timeRemaining} before sending another message.`,
      });
      return;
    }

    // Add user message to the chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      createdAt: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Call the backend API to process the message with the agent
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
      const response = await fetch(`${apiBaseUrl}/api/${localStorage.getItem('userId')}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth-token')}`,
        },
        body: JSON.stringify({
          content: currentInput,
          role: 'user',
          conversation_id: localStorage.getItem('currentConversationId') || null,
        }),
      });

      if (!response.ok) {
        // Check for rate limit error (429)
        if (response.status === 429) {
          const errorData = await response.json().catch(() => ({}));
          const rateLimitMessage = errorData.detail || 'Rate limit exceeded';

          // Set rate limit for 24 hours from now
          const rateLimitTimestamp = Date.now() + (24 * 60 * 60 * 1000);
          localStorage.setItem('rateLimitUntil', rateLimitTimestamp.toString());
          setRateLimitUntil(rateLimitTimestamp);

          throw new Error(rateLimitMessage);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Store the conversation ID for future messages
      if (data.conversation_id) {
        localStorage.setItem('currentConversationId', data.conversation_id);
      }

      // Transform tool calls to match frontend interface
      const transformedToolCalls = data.tool_calls?.map((toolCall: BackendToolCall, index: number) => ({
        id: `${data.id}-tool-${index}`,
        name: toolCall.name,
        arguments: toolCall.arguments,
        status: toolCall.result ? ('completed' as const) : ('failed' as const),
        result: toolCall.result,
      })) || [];

      // Add assistant response to the chat
      const assistantMessage: Message = {
        id: data.id || Date.now().toString(),
        role: 'assistant',
        content: data.content || 'No response from assistant',
        createdAt: new Date(data.created_at || Date.now()),
        toolCalls: transformedToolCalls,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response from the assistant. Please try again.';
      setError(errorMessage);
      console.error('Chat error:', err);
      toast({
        variant: "destructive",
        title: 'Error',
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatDateTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <FocusModeWrapper>
      <div className={cn(
        "flex flex-col bg-background",
        focusMode
          ? "h-full py-6 sm:py-10"
          : "h-[calc(100vh-7rem)] mt-20 sm:mt-24 mb-6 sm:mb-10"
      )}>
        {/* Chat Container */}
        <div className="flex-1 overflow-hidden">
          <div className={cn(
            "mx-auto h-full flex flex-col",
            focusMode
              ? "px-3 sm:px-4 md:px-6 max-w-5xl"
              : "container px-3 sm:px-4 max-w-4xl"
          )}>
            {/* Header with Clear Chat Button and Focus Mode Toggle */}
            <div className="flex items-center justify-between mb-3 sm:mb-4 pb-3 border-b flex-wrap gap-2">
              <div className="min-w-0">
                <h2 className="text-lg sm:text-xl font-semibold truncate">AI Task Assistant</h2>
                <p className="text-xs sm:text-sm text-muted-foreground hidden sm:block">Chat with your AI assistant</p>
              </div>
              <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
                <DisplayModeToggle />
                <FocusModeToggle />
                {messages.length > 0 && (
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline" size="sm" className="gap-1 sm:gap-2">
                        <Trash2 className="h-3 w-3 sm:h-4 sm:w-4" />
                        <span className="hidden sm:inline">Clear Chat</span>
                        <span className="sm:hidden">Clear</span>
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Clear Chat History?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will clear all messages in the current conversation. This action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={clearChat}>Clear Chat</AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                )}
              </div>
            </div>

          {/* Rate Limit Warning */}
          {rateLimitUntil && rateLimitUntil > Date.now() && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 sm:mb-4 p-3 sm:p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg"
            >
              <div className="flex items-start gap-2 sm:gap-3">
                <Clock className="h-4 w-4 sm:h-5 sm:w-5 text-yellow-600 dark:text-yellow-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm sm:text-base text-yellow-800 dark:text-yellow-200">
                    Rate Limit Reached
                  </h3>
                  <p className="text-xs sm:text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    The AI service has reached its rate limit. Please try again in:
                  </p>
                  <p className="text-base sm:text-lg font-mono font-bold text-yellow-900 dark:text-yellow-100 mt-2">
                    {timeRemaining}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          <div className="flex-1 overflow-y-auto mb-3 sm:mb-4 space-y-3 sm:space-y-4 px-1">
            {isLoadingHistory ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-8 sm:py-12"
              >
                <Loader2 className="mx-auto h-6 w-6 sm:h-8 sm:w-8 animate-spin text-muted-foreground" />
                <p className="mt-3 sm:mt-4 text-sm sm:text-base text-muted-foreground">Loading chat history...</p>
              </motion.div>
            ) : messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-8 sm:py-12 flex flex-col justify-center items-center h-full"
              >
                <Bot className="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-muted-foreground" />
                <h3 className="mt-3 sm:mt-4 text-base sm:text-lg font-medium px-4">Welcome to the AI Task Assistant</h3>
                <p className="text-muted-foreground mt-2 text-sm sm:text-base px-4 max-w-md">
                  Ask me to manage your tasks. Try: &quot;Add a task to buy milk&quot; or &quot;Show my tasks&quot;
                </p>
              </motion.div>
            ) : (
              messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    'flex gap-2 sm:gap-3',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <Avatar className="h-7 w-7 sm:h-8 sm:w-8 border flex-shrink-0">
                      <AvatarImage src="/bot-avatar.png" alt="AI Assistant" />
                      <AvatarFallback className="bg-primary/10">
                        <Bot className="h-3 w-3 sm:h-4 sm:w-4 text-primary" />
                      </AvatarFallback>
                    </Avatar>
                  )}

                  <div
                    className={cn(
                      'max-w-[85%] sm:max-w-[80%] rounded-lg px-3 sm:px-4 py-2',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground rounded-br-none'
                        : 'bg-muted rounded-bl-none'
                    )}
                  >
                    {/* Conditional rendering based on display mode */}
                    {displayMode === 'json' ? (
                      <JsonMessageView
                        content={message.content}
                        toolCalls={message.toolCalls}
                      />
                    ) : (
                      <>
                        {/* Human-readable message with task link parsing */}
                        <div className="whitespace-pre-wrap break-words">
                          {message.role === 'assistant' ? (
                            // Parse and render task links for assistant messages
                            (() => {
                              const taskRefs = parseTaskReferences(message.content)
                              if (taskRefs.length === 0) {
                                return message.content
                              }

                              const parts: React.ReactNode[] = []
                              let lastIndex = 0

                              taskRefs.forEach((ref, index) => {
                                // Add text before the task reference
                                if (ref.startIndex > lastIndex) {
                                  parts.push(
                                    message.content.substring(lastIndex, ref.startIndex)
                                  )
                                }

                                // Add task link button
                                parts.push(
                                  <TaskLinkButton
                                    key={`task-${ref.taskId}-${index}`}
                                    taskId={ref.taskId}
                                  >
                                    {ref.originalText}
                                  </TaskLinkButton>
                                )

                                lastIndex = ref.endIndex
                              })

                              // Add remaining text after last task reference
                              if (lastIndex < message.content.length) {
                                parts.push(message.content.substring(lastIndex))
                              }

                              return parts
                            })()
                          ) : (
                            message.content
                          )}
                        </div>

                        {/* Tool Call Visualization */}
                        {message.toolCalls && message.toolCalls.length > 0 && (
                          <div className="mt-2 sm:mt-3 space-y-2">
                            <div className="text-xs font-medium text-muted-foreground">Tool Executions:</div>
                            {message.toolCalls.map((toolCall) => (
                              <div key={toolCall.id} className="mt-2 p-2 sm:p-3 rounded-md bg-background border">
                                <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                                  <span className="font-medium text-xs sm:text-sm">{toolCall.name}</span>
                                  {toolCall.status === 'initiated' || toolCall.status === 'executing' ? (
                                    <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 animate-spin text-blue-500" />
                                  ) : toolCall.status === 'completed' ? (
                                    <CheckCircle2 className="h-3 w-3 sm:h-4 sm:w-4 text-green-500" />
                                  ) : (
                                    <XCircle className="h-3 w-3 sm:h-4 sm:w-4 text-red-500" />
                                  )}
                                  <span className="text-xs capitalize text-muted-foreground">
                                    {toolCall.status}
                                  </span>
                                </div>
                                <div className="mt-1 text-xs text-muted-foreground break-all">
                                  {JSON.stringify(toolCall.arguments)}
                                </div>
                                {toolCall.result && (
                                  <div className="mt-1 text-xs bg-muted p-1.5 sm:p-2 rounded break-all">
                                    Result: {JSON.stringify(toolCall.result)}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    )}

                    <div className="text-xs opacity-70 mt-1">
                      {formatDateTime(message.createdAt)}
                    </div>
                  </div>

                  {message.role === 'user' && (
                    <Avatar className="h-8 w-8 border">
                      <AvatarImage src="/user-avatar.png" alt="User" />
                      <AvatarFallback className="bg-primary/10">
                        <User className="h-4 w-4 text-primary" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </motion.div>
              ))
            )}

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3 justify-start"
              >
                <Avatar className="h-8 w-8 border">
                  <AvatarImage src="/bot-avatar.png" alt="AI Assistant" />
                  <AvatarFallback className="bg-primary/10">
                    <Bot className="h-4 w-4 text-primary" />
                  </AvatarFallback>
                </Avatar>

                <div className="max-w-[80%] rounded-lg px-4 py-2 bg-muted rounded-bl-none">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>AI is thinking...</span>
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form ref={formRef} onSubmit={handleSubmit} className="relative">
            <div className="flex gap-1.5 sm:gap-2">
              <Textarea
                ref={inputRef}
                data-chat-input="true"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  // Submit on Enter (without Shift)
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    formRef.current?.requestSubmit();
                  }
                }}
                placeholder={
                  rateLimitUntil && rateLimitUntil > Date.now()
                    ? `Rate limited. Try again in ${timeRemaining}`
                    : "Ask me to manage your tasks..."
                }
                className={cn(
                  "resize-none min-h-[60px] sm:min-h-15 max-h-32 text-sm sm:text-base transition-all duration-200",
                  keyboardFocused && "ring-2 ring-primary ring-offset-2"
                )}
                disabled={isLoading || isLoadingHistory || (rateLimitUntil !== null && rateLimitUntil > Date.now())}
              />
              <Button
                type="submit"
                disabled={
                  isLoading ||
                  isLoadingHistory ||
                  !inputValue.trim() ||
                  (rateLimitUntil !== null && rateLimitUntil > Date.now())
                }
                className="self-end h-[60px] sm:h-auto px-3 sm:px-4"
                size="default"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Keyboard Shortcut Hints */}
            <div className="mt-2 flex flex-wrap gap-3 sm:gap-4">
              <KeyboardShortcuts.FocusChat />
              <KeyboardShortcuts.SendMessage />
              <KeyboardShortcuts.NewLine />
            </div>

            {error && (
              <div className="mt-2 text-xs sm:text-sm text-red-600 bg-red-50 p-2 rounded">
                {error}
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
    </FocusModeWrapper>
  );
};

export default ChatPage;