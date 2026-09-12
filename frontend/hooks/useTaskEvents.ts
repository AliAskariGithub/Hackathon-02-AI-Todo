import { useEffect, useRef, useState, useCallback } from 'react';
import { getApiBaseUrl, getCredentialsMode } from '@/lib/api-config';

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
  userId?: string;
  token?: string;
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
  const enabled = options.enabled ?? true;
  const reconnectDelay = options.reconnectDelay ?? RECONNECT_DELAY;
  const userId = options.userId;
  const token = options.token;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Keep handlers in a ref so changes never cause connect/disconnect to be recreated
  const handlersRef = useRef<TaskEventHandlers>(handlers);
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManualCloseRef = useRef(false);

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
    handlersRef.current.onDisconnected?.();
  }, []);

  /**
   * Connect to SSE endpoint
   */
  const connect = useCallback(() => {
    // Don't connect if disabled, missing userId, or already active
    if (!enabled || !userId || eventSourceRef.current) {
      return;
    }

    try {
      // Get JWT token from props or localStorage ('access_token' or 'token')
      const effectiveToken = token || (typeof window !== 'undefined'
        ? (localStorage.getItem('access_token') || localStorage.getItem('token'))
        : null);

      // Connect to backend SSE endpoint
      const apiBaseUrl = getApiBaseUrl();
      const tokenParam = effectiveToken ? `&token=${encodeURIComponent(effectiveToken)}` : '';
      const url = `${apiBaseUrl}/api/events/stream?user_id=${encodeURIComponent(userId)}${tokenParam}`;

      const eventSource = new EventSource(url, { withCredentials: getCredentialsMode() === 'include' });
      eventSourceRef.current = eventSource;
      isManualCloseRef.current = false;

      // Handle connection open
      eventSource.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        handlersRef.current.onConnected?.();
      };

      // Handle incoming messages
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Handle heartbeat
          if (data.type === 'heartbeat') {
            setIsConnected(true);
            setError(null);
            return;
          }

          // Handle connected acknowledgement
          if (data.type === 'connected') {
            setIsConnected(true);
            setError(null);
            return;
          }

          // Handle error message from server
          if (data.type === 'error') {
            setError(data.message);
            return;
          }

          // Handle task events
          const taskEvent = data as TaskEventData;
          switch (taskEvent.event_type) {
            case 'task.created':
              handlersRef.current.onTaskCreated?.(taskEvent);
              break;
            case 'task.updated':
              handlersRef.current.onTaskUpdated?.(taskEvent);
              break;
            case 'task.completed':
              handlersRef.current.onTaskCompleted?.(taskEvent);
              break;
            case 'task.deleted':
              handlersRef.current.onTaskDeleted?.(taskEvent);
              break;
          }
        } catch (err) {
          console.error('Error parsing SSE message:', err);
        }
      };

      // Handle errors
      eventSource.onerror = (event) => {
        setIsConnected(false);
        handlersRef.current.onError?.(event);

        // Close current connection instance
        eventSource.close();
        eventSourceRef.current = null;

        // Attempt reconnection if not manually closed
        if (!isManualCloseRef.current && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
          const delay = reconnectDelay * reconnectAttemptsRef.current;

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
          setError('Live updates disconnected. Click Reconnect to retry.');
          handlersRef.current.onDisconnected?.();
        }
      };
    } catch (err) {
      console.error('Error creating SSE connection:', err);
    }
  }, [enabled, userId, token, reconnectDelay]);

  /**
   * Manual reconnect function
   */
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    isManualCloseRef.current = false;
    setError(null);
    setTimeout(() => connect(), 100);
  }, [connect, disconnect]);

  // Connect when enabled and userId is available, disconnect on unmount
  useEffect(() => {
    if (enabled && userId) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, userId, token, connect, disconnect]);

  return {
    isConnected,
    error,
    reconnect,
  };
}
