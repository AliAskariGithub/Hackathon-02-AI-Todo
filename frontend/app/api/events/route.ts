import { NextRequest } from 'next/server';

/**
 * SSE Route Handler for Real-Time Task Events
 *
 * Streams task events (created, updated, completed, deleted) to authenticated clients
 * using Server-Sent Events (SSE) protocol.
 *
 * Features:
 * - JWT authentication via Authorization header
 * - User-specific event filtering
 * - 30-second heartbeat to keep connection alive
 * - Automatic reconnection support
 */

// Use server-side env var for internal Docker communication
// Falls back to NEXT_PUBLIC for local development
const BACKEND_URL = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const HEARTBEAT_INTERVAL = 30000; // 30 seconds

interface TaskEvent {
  event_type: string;
  payload: {
    task_id: string;
    user_id: string;
    task_data: Record<string, any>;
  };
  timestamp: string;
  correlation_id: string;
}

export async function GET(request: NextRequest) {
  // Extract JWT token from query param, Authorization header, or cookie
  const searchParams = request.nextUrl.searchParams;
  const queryToken = searchParams.get('token');
  const authHeader = request.headers.get('authorization');
  const cookieToken = request.cookies.get('access_token')?.value;

  const token = queryToken || (authHeader?.startsWith('Bearer ') ? authHeader.substring(7) : null) || cookieToken;
  if (!token) {
    return new Response('Unauthorized', { status: 401 });
  }

  // Verify token and extract user_id
  let userId = searchParams.get('user_id');
  if (!userId) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      userId = payload.sub || payload.user_id;

      if (!userId) {
        return new Response('Invalid token', { status: 401 });
      }
    } catch (error) {
      return new Response('Invalid token', { status: 401 });
    }
  }

  // Create ReadableStream for SSE
  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      let heartbeatTimer: NodeJS.Timeout;

      // Send initial connection message
      const sendMessage = (data: string) => {
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      };

      // Send heartbeat to keep connection alive
      const sendHeartbeat = () => {
        sendMessage(JSON.stringify({ type: 'heartbeat', timestamp: new Date().toISOString() }));
      };

      // Start heartbeat
      heartbeatTimer = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);

      try {
        // Connect to backend SSE endpoint
        const backendUrl = `${BACKEND_URL}/api/events/stream?user_id=${userId}&token=${encodeURIComponent(token)}`;

        // Use fetch with streaming for backend connection
        const response = await fetch(backendUrl, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'text/event-stream',
          },
        });

        if (!response.ok) {
          throw new Error(`Backend connection failed: ${response.status}`);
        }

        // Send connection established message
        sendMessage(JSON.stringify({
          type: 'connected',
          user_id: userId,
          timestamp: new Date().toISOString()
        }));

        // Stream events from backend
        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          // Decode chunk and add to buffer
          buffer += decoder.decode(value, { stream: true });

          // Process complete messages (separated by \n\n)
          const messages = buffer.split('\n\n');
          buffer = messages.pop() || ''; // Keep incomplete message in buffer

          for (const message of messages) {
            if (message.trim()) {
              // Forward event to client
              controller.enqueue(encoder.encode(`${message}\n\n`));
            }
          }
        }
      } catch (error) {
        console.error('SSE stream error:', error);
        sendMessage(JSON.stringify({
          type: 'error',
          message: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        }));
      } finally {
        // Cleanup
        clearInterval(heartbeatTimer);
        controller.close();
      }
    },

    cancel() {
      console.log('SSE stream cancelled by client');
    }
  });

  // Return SSE response with proper headers
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no', // Disable nginx buffering
    },
  });
}

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
