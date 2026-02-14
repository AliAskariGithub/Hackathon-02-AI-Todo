import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Task Event Types
 */
export type TaskEventType = 'task.created' | 'task.updated' | 'task.completed' | 'task.deleted';

export interface TaskEventData {
  event_type: TaskEventType;
  payload: {
    task_id: string;
    user_id: string;
    task_data: {
      id: string;
      title: string;
      description?: string;
      status: string;
      priority: string;
      due_date?: string;
      recurrence?: string;
      recurrence_day_of_week?: number;
      recurrence_day_of_month?: number;
      tags?: string[];
      completed?: boolean;
      created_at?: string;
      updated_at?: string;
      completed_at?: string;
      deleted_at?: string;
    };
  };
  timestamp: string;
  correlation_id: string;
}

export interface TaskEventHandlers {
  onTaskCreated?: (data: TaskEventData) => void;
  onTaskUpdated?: (data: TaskEventData) => void;
  onTaskCompleted?: (data: TaskEventData) => void;
  onTaskDeleted?: (data: TaskEventData) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: Event) => void;
}

export interface UseTaskEventsOptions {
  enabled?: boolean;
  reconnectDelay?: number;
}

export interface UseTaskEventsReturn {
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

const RECONNECT_DELAY = 5000; // 5 seconds
const MAX_RECONNECT_ATTEMPTS = 10;

/**
 * Custom hook for subscribing to real-time task events via SSE
 *
 * @param handlers - Event handlers for different task event types
 * @param options - Configuration options
 * @returns Connection status and control functions
 */
export function useTaskEvents(
  handlers: TaskEventHandlers,
  options: UseTaskEventsOptions = {}
): UseTaskEventsReturn {
  const { enabled = true, reconnectDelay = RECONNECT_DELAY } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualCloseRef = useRef(false);

  /**
   * Connect to SSE endpoint
   */
  const connect = useCallback(() => {
    // Don't connect if disabled or already connected
    if (!enabled || eventSourceRef.current) {
      return;
    }

    try {
      // Get JWT token from localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      // Decode token to get user_id
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userId = payload.sub || payload.user_id;

      if (!userId) {
        setError('Invalid token: missing user_id');
        return;
      }

      // Create EventSource with token in URL (EventSource doesn't support custom headers)
      // Note: In production, consider using a more secure method
      const url = `/api/events/stream?user_id=${userId}`;
      const eventSource = new EventSource(url);

      eventSourceRef.current = eventSource;
      isManualCloseRef.current = false;

      // Handle connection open
      eventSource.onopen = () => {
        console.log('SSE connection established');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        handlers.onConnected?.();
      };

      // Handle incoming messages
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Handle different event types
          if (data.type === 'heartbeat') {
            // Heartbeat - connection is alive
            return;
          }

          if (data.type === 'connected') {
            // Initial connection message
            console.log('SSE connected:', data);
            return;
          }

          if (data.type === 'error') {
            console.error('SSE error message:', data.message);
            setError(data.message);
            return;
          }

          // Handle task events
          const taskEvent = data as TaskEventData;
          switch (taskEvent.event_type) {
            case 'task.created':
              handlers.onTaskCreated?.(taskEvent);
              break;
            case 'task.updated':
              handlers.onTaskUpdated?.(taskEvent);
              break;
            case 'task.completed':
              handlers.onTaskCompleted?.(taskEvent);
              break;
            case 'task.deleted':
              handlers.onTaskDeleted?.(taskEvent);
              break;
            default:
              console.warn('Unknown event type:', taskEvent.event_type);
          }
        } catch (err) {
          console.error('Error parsing SSE message:', err);
        }
      };

      // Handle errors
      eventSource.onerror = (event) => {
        console.error('SSE connection error:', event);
        setIsConnected(false);
        handlers.onError?.(event);

        // Close the connection
        eventSource.close();
        eventSourceRef.current = null;

        // Attempt reconnection if not manually closed
        if (!isManualCloseRef.current && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
          const delay = reconnectDelay * reconnectAttemptsRef.current; // Exponential backoff

          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);
          setError(`Connection lost. Reconnecting... (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
          setError('Max reconnection attempts reached. Please refresh the page.');
          handlers.onDisconnected?.();
        }
      };
    } catch (err) {
      console.error('Error creating SSE connection:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  }, [enabled, reconnectDelay, handlers]);

  /**
   * Disconnect from SSE endpoint
   */
  const disconnect = useCallback(() => {
    isManualCloseRef.current = true;

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setIsConnected(false);
    handlers.onDisconnected?.();
  }, [handlers]);

  /**
   * Manual reconnect function
   */
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    isManualCloseRef.current = false;
    setTimeout(() => connect(), 100);
  }, [connect, disconnect]);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    isConnected,
    error,
    reconnect,
  };
}
