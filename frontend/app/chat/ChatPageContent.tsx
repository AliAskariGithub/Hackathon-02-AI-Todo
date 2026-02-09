'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Send,
  Bot,
  User,
  Loader2,
  XCircle,
  Trash2,
  Clock,
  Sparkles,
  ChevronDown
} from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import { useAuth } from '@/providers/auth-provider';
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
import { useUIStore } from '@/stores/ui-store';

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
  type: string;
  function: {
    name: string;
    arguments: string;
  };
}

interface ApiMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
  tool_calls?: ToolCall[];
}

// Animation variants
const messageVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring" as const,
      stiffness: 300,
      damping: 30
    }
  },
  exit: {
    opacity: 0,
    y: -20,
    scale: 0.95,
    transition: { duration: 0.2 }
  }
};

const loadingDots = {
  initial: { opacity: 0.3 },
  animate: {
    opacity: [0.3, 1, 0.3],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut" as const
    }
  }
};

const ChatPageContent = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [rateLimitUntil, setRateLimitUntil] = useState<number | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<string>('');
  const [keyboardFocused, setKeyboardFocused] = useState(false);
  const [loadingText, setLoadingText] = useState('Thinking');
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [isNearBottom, setIsNearBottom] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { focusMode, displayMode } = useUIStore();
  const { session } = useAuth();

  // Get API base URL from environment
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  // Determine loading message based on user input
  const getLoadingMessage = (userInput: string): string => {
    const input = userInput.toLowerCase();

    if (input.includes('create') || input.includes('add') || input.includes('make') || input.includes('new task')) {
      return 'Creating task';
    }
    if (input.includes('update') || input.includes('edit') || input.includes('change') || input.includes('modify')) {
      return 'Updating task';
    }
    if (input.includes('delete') || input.includes('remove') || input.includes('clear')) {
      return 'Deleting task';
    }
    if (input.includes('complete') || input.includes('finish') || input.includes('done') || input.includes('mark as')) {
      return 'Completing task';
    }
    if (input.includes('list') || input.includes('show') || input.includes('get') || input.includes('all tasks') || input.includes('my tasks')) {
      return 'Listing tasks';
    }
    if (input.includes('find') || input.includes('search') || input.includes('look for')) {
      return 'Searching';
    }
    return 'Thinking';
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [inputValue]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (isNearBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isNearBottom]);

  // Handle scroll detection
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

      setShowScrollButton(distanceFromBottom > 200);
      setIsNearBottom(distanceFromBottom < 100);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Scroll to bottom function
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Load conversation history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        if (!session?.user?.id) {
          setIsLoadingHistory(false);
          return;
        }

        const userId = session.user.id;

        const response = await fetch(`${apiBaseUrl}/api/${userId}/conversations`, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const conversations = await response.json();

          if (conversations && conversations.length > 0) {
            const latestConversation = conversations[0];
            setConversationId(latestConversation.id);

            const messagesResponse = await fetch(
              `${apiBaseUrl}/api/${userId}/conversations/${latestConversation.id}/messages`,
              {
                credentials: 'include',
                headers: {
                  'Content-Type': 'application/json',
                },
              }
            );

            if (messagesResponse.ok) {
              const conversationMessages = await messagesResponse.json();
              setMessages(
                conversationMessages.map((msg: ApiMessage) => {
                  let createdAt;
                  try {
                    createdAt = msg.created_at ? new Date(msg.created_at) : new Date();
                  } catch (e) {
                    console.error('Failed to parse message date:', e);
                    createdAt = new Date();
                  }

                  return {
                    id: msg.id || Date.now().toString(),
                    role: msg.role || 'assistant',
                    content: msg.content || '',
                    createdAt,
                    toolCalls: msg.tool_calls || undefined,
                  };
                })
              );
            }
          }
        }
      } catch (error) {
        console.error('Error loading conversation history:', error);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadHistory();
  }, [apiBaseUrl, session?.user?.id]);

  // Handle rate limit countdown
  useEffect(() => {
    if (rateLimitUntil && rateLimitUntil > Date.now()) {
      const interval = setInterval(() => {
        const remaining = rateLimitUntil - Date.now();
        if (remaining <= 0) {
          setRateLimitUntil(null);
          setTimeRemaining('');
        } else {
          const hours = Math.floor(remaining / (1000 * 60 * 60));
          const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
          setTimeRemaining(`${hours}h ${minutes}m ${seconds}s`);
        }
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [rateLimitUntil]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onFocusChat: () => {
      textareaRef.current?.focus();
      setKeyboardFocused(true);
      setTimeout(() => setKeyboardFocused(false), 1000);
    },
    onEscape: () => {
      if (focusMode) {
        useUIStore.getState().setFocusMode(false);
      } else {
        textareaRef.current?.blur();
      }
    },
    enabled: true,
  });

  // Helper function to format tool calls into user-friendly messages
  const formatToolCallMessage = (toolCall: ToolCall): string => {
    try {
      const args = typeof toolCall.function.arguments === 'string'
        ? JSON.parse(toolCall.function.arguments)
        : toolCall.function.arguments || {};

      switch (toolCall.function.name) {
        case 'create_task':
          return `✅ Created task: "${args.title || 'New task'}"`;
        case 'update_task':
          return `✏️ Updated task successfully`;
        case 'delete_task':
          return `🗑️ Deleted task successfully`;
        case 'list_tasks':
          return `📋 Retrieved your tasks`;
        case 'get_task':
          return `🔍 Found task details`;
        case 'complete_task':
          return `✓ Marked task as complete`;
        default:
          return `✓ Action completed: ${toolCall.function.name.replace(/_/g, ' ')}`;
      }
    } catch {
      return `✓ Action completed`;
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading || isLoadingHistory) return;
    if (rateLimitUntil && rateLimitUntil > Date.now()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      createdAt: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputValue;

    setLoadingText(getLoadingMessage(inputValue));
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      if (!session?.user?.id) {
        throw new Error('Please log in to use the chat feature');
      }

      const userId = session.user.id;

      const response = await fetch(`${apiBaseUrl}/api/${userId}/chat`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: currentInput,
          role: 'user',
          conversation_id: conversationId,
        }),
      });

      if (response.status === 429) {
        const errorData = await response.json();
        const limitedUntil = Date.now() + 24 * 60 * 60 * 1000;
        setRateLimitUntil(limitedUntil);
        setError(errorData.detail || 'Rate limit exceeded. Please try again later.');

        toast({
          title: 'Rate Limit Exceeded',
          description: errorData.detail || 'Please try again after 24 hours.',
          variant: 'destructive',
        });
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const aiMessage = await response.json();

      if (!conversationId && aiMessage.conversation_id) {
        setConversationId(aiMessage.conversation_id);
      }

      let createdAt;
      try {
        createdAt = aiMessage.created_at ? new Date(aiMessage.created_at) : new Date();
      } catch (e) {
        console.error('Failed to parse AI message date:', e);
        createdAt = new Date();
      }

      const assistantMessage: Message = {
        id: aiMessage.id || Date.now().toString(),
        role: 'assistant',
        content: aiMessage.content || '',
        createdAt,
        toolCalls: aiMessage.tool_calls || undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setError(errorMessage);
      setInputValue(currentInput);

      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage();
  };

  const handleRetry = () => {
    if (inputValue.trim()) {
      setError(null);
      sendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    setRateLimitUntil(null);

    toast({
      title: 'Chat Cleared',
      description: 'All messages have been removed',
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (isLoadingHistory) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-center min-h-screen"
      >
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading conversation...</p>
        </div>
      </motion.div>
    );
  }

  return (
    <FocusModeWrapper>
      <div className={cn(
        "flex flex-col bg-background transition-all duration-300 mx-auto w-full relative",
        focusMode
          ? "h-screen py-4 sm:py-6 md:py-8 lg:py-10 max-w-5xl px-3 sm:px-4 md:px-6 lg:px-8"
          : "h-[calc(100vh-4rem)] sm:h-[calc(100vh-5rem)] md:h-[calc(100vh-6rem)] mt-16 sm:mt-20 md:mt-24 mb-4 sm:mb-6 md:mb-8 max-w-6xl px-3 sm:px-4 md:px-6 lg:px-8"
      )}>
        {/* Header - Fixed height */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex-shrink-0 flex items-center justify-between mb-3 sm:mb-4 pb-3 sm:pb-4 border-b"
        >
          <div className="flex items-center gap-2 sm:gap-3">
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            >
              <Bot className="h-5 w-5 sm:h-6 sm:w-6 md:h-7 md:w-7 text-primary" />
            </motion.div>
            <div>
              <h1 className="text-base sm:text-lg md:text-xl lg:text-2xl font-semibold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                AI Task Assistant
              </h1>
              <p className="text-[10px] sm:text-xs md:text-sm text-muted-foreground hidden sm:block">
                Chat with AI to manage your tasks
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2">
            <DisplayModeToggle />
            <FocusModeToggle />
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 w-7 sm:h-8 sm:w-8 md:h-9 md:w-9 p-0 hover:bg-destructive/10 hover:text-destructive transition-colors"
                >
                  <Trash2 className="h-3 w-3 sm:h-3.5 sm:w-3.5 md:h-4 md:w-4" />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="max-w-[90vw] sm:max-w-md">
                <AlertDialogHeader>
                  <AlertDialogTitle>Clear Chat History?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will remove all messages from the current conversation. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleClearChat} className="bg-destructive hover:bg-destructive/90">
                    Clear Chat
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </motion.div>

        {/* Messages Container - Flexible height with proper overflow */}
        <div
          ref={messagesContainerRef}
          className="flex-1 overflow-y-auto mb-3 sm:mb-4 space-y-3 sm:space-y-4 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent hover:scrollbar-thumb-muted-foreground/20 min-h-0"
        >
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center h-full text-center p-4 sm:p-6 md:p-8"
            >
              <motion.div
                animate={{
                  y: [0, -10, 0],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              >
                <Bot className="h-12 w-12 sm:h-14 sm:w-14 md:h-16 md:w-16 lg:h-20 lg:w-20 text-primary/60 mb-4" />
              </motion.div>
              <h2 className="text-lg sm:text-xl md:text-2xl font-semibold mb-2 bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
                Start a Conversation
              </h2>
              <p className="text-xs sm:text-sm md:text-base text-muted-foreground max-w-md px-4">
                Ask me to create, update, or manage your tasks. I can help you stay organized!
              </p>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-6 sm:mt-8 grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 w-full max-w-lg"
              >
                {[
                  { icon: "✨", text: "Create a new task" },
                  { icon: "📋", text: "List my tasks" },
                  { icon: "✅", text: "Mark task as complete" },
                  { icon: "🔍", text: "Find a task" }
                ].map((item, idx) => (
                  <motion.button
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + idx * 0.1 }}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setInputValue(item.text)}
                    className="flex items-center gap-2 p-3 rounded-lg border bg-card hover:bg-accent transition-colors text-left text-xs sm:text-sm"
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span className="text-muted-foreground">{item.text}</span>
                  </motion.button>
                ))}
              </motion.div>
            </motion.div>
          ) : (
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  variants={messageVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  layout
                  className={cn(
                    'flex gap-2 sm:gap-3',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <Avatar className="h-7 w-7 sm:h-8 sm:w-8 md:h-9 md:w-9 flex-shrink-0 ring-2 ring-primary/10">
                      <AvatarFallback className="bg-gradient-to-br from-primary to-primary/60 text-primary-foreground">
                        <Bot className="h-4 w-4 sm:h-4.5 sm:w-4.5 md:h-5 md:w-5" />
                      </AvatarFallback>
                    </Avatar>
                  )}

                  <motion.div
                    layout
                    className={cn(
                      'rounded-2xl px-3 py-2 sm:px-4 sm:py-3 max-w-[85%] sm:max-w-[80%] md:max-w-[75%] lg:max-w-[70%] text-xs sm:text-sm md:text-base shadow-sm',
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-primary to-primary/80 text-primary-foreground'
                        : 'bg-muted/50 backdrop-blur-sm border border-border/50'
                    )}
                  >
                    {displayMode === 'json' && message.toolCalls ? (
                      <JsonMessageView
                        content={message.content}
                        toolCalls={message.toolCalls
                          ?.filter(tc => tc && tc.function)
                          ?.map(tc => {
                            let args;
                            try {
                              args = typeof tc.function.arguments === 'string'
                                ? JSON.parse(tc.function.arguments)
                                : tc.function.arguments || {};
                            } catch (e) {
                              console.error('Failed to parse tool call arguments:', e);
                              args = {};
                            }
                            return {
                              id: tc.id || 'unknown',
                              name: tc.function.name || 'unknown',
                              arguments: args,
                              status: 'completed'
                            };
                          })}
                      />
                    ) : (
                      <>
                        <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
                        {message.toolCalls && message.toolCalls.length > 0 && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="mt-3 pt-3 border-t border-border/30"
                          >
                            <div className="space-y-2">
                              {message.toolCalls
                                .filter(toolCall => toolCall && toolCall.function)
                                .map((toolCall, idx) => (
                                  <motion.div
                                    key={toolCall.id || idx}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className="flex items-center gap-2 text-xs sm:text-sm bg-background/50 rounded-lg px-3 py-2"
                                  >
                                    <span>{formatToolCallMessage(toolCall)}</span>
                                  </motion.div>
                                ))}
                            </div>
                          </motion.div>
                        )}
                      </>
                    )}
                    <div className="flex items-center gap-1.5 mt-2 text-[10px] sm:text-xs opacity-60">
                      <Clock className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                      {message.createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </motion.div>

                  {message.role === 'user' && (
                    <Avatar className="h-7 w-7 sm:h-8 sm:w-8 md:h-9 md:w-9 flex-shrink-0 ring-2 ring-primary/10">
                      <AvatarFallback className="bg-gradient-to-br from-foreground/10 to-foreground/5">
                        <User className="h-4 w-4 sm:h-4.5 sm:w-4.5 md:h-5 md:w-5" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </motion.div>
              ))}

              {/* Loading Animation */}
              {isLoading && (
                <motion.div
                  variants={messageVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  className="flex gap-2 sm:gap-3 justify-start"
                >
                  <Avatar className="h-7 w-7 sm:h-8 sm:w-8 md:h-9 md:w-9 flex-shrink-0 ring-2 ring-primary/10">
                    <AvatarFallback className="bg-gradient-to-br from-primary to-primary/60 text-primary-foreground">
                      <Bot className="h-4 w-4 sm:h-4.5 sm:w-4.5 md:h-5 md:w-5" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="rounded-2xl px-3 py-2 sm:px-4 sm:py-3 bg-muted/50 backdrop-blur-sm border border-border/50 shadow-sm">
                    <div className="flex items-center gap-2">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        <Sparkles className="h-4 w-4 text-primary" />
                      </motion.div>
                      <span className="text-xs sm:text-sm font-medium flex items-center gap-1">
                        {loadingText}
                        <motion.span variants={loadingDots} initial="initial" animate="animate">.</motion.span>
                        <motion.span variants={loadingDots} initial="initial" animate="animate" transition={{ delay: 0.2 }}>.</motion.span>
                        <motion.span variants={loadingDots} initial="initial" animate="animate" transition={{ delay: 0.4 }}>.</motion.span>
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Scroll to Bottom Button */}
        <AnimatePresence>
          {showScrollButton && (
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              onClick={scrollToBottom}
              className="absolute right-4 sm:right-6 md:right-8 bottom-32 sm:bottom-36 md:bottom-40 bg-primary text-primary-foreground rounded-full p-2 sm:p-2.5 shadow-lg hover:shadow-xl transition-shadow z-10"
            >
              <ChevronDown className="h-4 w-4 sm:h-5 sm:w-5" />
            </motion.button>
          )}
        </AnimatePresence>

        {/* Input Form - Fixed height */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex-shrink-0 border-t pt-3 sm:pt-4 bg-background/80 backdrop-blur-sm"
        >
          <form onSubmit={handleSubmit} className="space-y-2 sm:space-y-3">
            <div className="flex gap-2">
              <Textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                autoFocus={!focusMode}
                onFocus={() => {
                  if (focusMode) {
                    useUIStore.getState().setFocusMode(false);
                  }
                }}
                placeholder={
                  rateLimitUntil && rateLimitUntil > Date.now()
                    ? `Rate limited. Try again in ${timeRemaining}`
                    : "Ask me to manage your tasks..."
                }
                className={cn(
                  "resize-none min-h-[44px] sm:min-h-[52px] md:min-h-[60px] max-h-[200px] text-xs sm:text-sm md:text-base transition-all duration-200 rounded-xl",
                  keyboardFocused && "ring-2 ring-primary ring-offset-2",
                  "focus:ring-2 focus:ring-primary"
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
                className="self-end h-[44px] sm:h-[52px] md:h-[60px] px-3 sm:px-4 md:px-5 rounded-xl transition-all hover:shadow-lg disabled:opacity-50"
                size="default"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                ) : (
                  <Send className="h-4 w-4 sm:h-5 sm:w-5" />
                )}
              </Button>
            </div>

            {/* Keyboard Shortcut Hints */}
            <div className="flex flex-wrap gap-2 sm:gap-3 md:gap-4">
              <KeyboardShortcuts.FocusChat />
              <KeyboardShortcuts.SendMessage />
              <KeyboardShortcuts.NewLine />
            </div>

            {/* Error Display */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="flex items-center justify-between gap-3 p-3 rounded-xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900">
                    <div className="flex items-center gap-2 flex-1">
                      <XCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0" />
                      <p className="text-xs sm:text-sm text-red-600 dark:text-red-400">{error}</p>
                    </div>
                    <Button
                      onClick={handleRetry}
                      variant="outline"
                      size="sm"
                      className="flex-shrink-0 border-red-300 dark:border-red-800 hover:bg-red-100 dark:hover:bg-red-900/30 text-xs sm:text-sm h-7 sm:h-8"
                    >
                      Try Again
                    </Button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </form>
        </motion.div>
      </div>
    </FocusModeWrapper>
  );
};

export default ChatPageContent;