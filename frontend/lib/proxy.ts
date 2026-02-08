/**
 * Proxy configuration for Next.js 16.1.2 with streaming support
 * Handles the network boundary and streaming headers for chat endpoints
 */

import { NextRequest, NextResponse } from 'next/server';

export const config = {
  runtime: 'edge',
};

/**
 * Handles streaming responses for chat endpoints
 * @param req The incoming Next.js request
 * @returns Streaming response with appropriate headers
 */
export async function handleChatStream(req: NextRequest) {
  // Get the original request URL and path
  const url = new URL(req.url);
  const path = url.pathname;

  // Backend API URL (adjust this to match your backend server)
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  const targetUrl = `${backendUrl}${path}`;

  // Clone the request headers
  const headers = new Headers(req.headers);

  // Ensure proper streaming headers
  headers.set('Accept', 'text/event-stream');
  headers.set('Cache-Control', 'no-cache');
  headers.set('Connection', 'keep-alive');

  // Forward the request to the backend
  const backendResponse = await fetch(targetUrl, {
    method: req.method,
    headers,
    body: req.body ? await req.blob() : undefined,
  });

  // Create a response with streaming headers
  const responseHeaders = new Headers(backendResponse.headers);
  responseHeaders.set('Content-Type', 'text/plain; charset=utf-8');
  responseHeaders.set('Transfer-Encoding', 'chunked');
  responseHeaders.set('Cache-Control', 'no-cache, no-transform');
  responseHeaders.set('Connection', 'keep-alive');
  responseHeaders.delete('Content-Length'); // Remove content-length for streaming

  // Create the response
  const response = new NextResponse(backendResponse.body, {
    status: backendResponse.status,
    statusText: backendResponse.statusText,
    headers: responseHeaders,
  });

  return response;
}

/**
 * Handles MCP tool execution with streaming
 * @param req The incoming Next.js request
 * @returns Response from the MCP tool execution
 */
export async function handleMcpStream(req: NextRequest) {
  // Get the original request URL and path
  const url = new URL(req.url);
  const path = url.pathname;

  // Backend API URL (adjust this to match your backend server)
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  const targetUrl = `${backendUrl}${path}`;

  // Clone the request headers
  const headers = new Headers(req.headers);

  // Ensure proper streaming headers for MCP tools
  headers.set('Accept', 'application/json, text/plain, */*');
  headers.set('Cache-Control', 'no-cache');
  headers.set('Connection', 'keep-alive');

  // Forward the request to the backend
  const backendResponse = await fetch(targetUrl, {
    method: req.method,
    headers,
    body: req.body ? await req.blob() : undefined,
  });

  // Create a response with appropriate headers
  const responseHeaders = new Headers(backendResponse.headers);
  responseHeaders.set('Content-Type', 'application/json; charset=utf-8');
  responseHeaders.set('Cache-Control', 'no-cache');
  responseHeaders.set('Access-Control-Allow-Origin', '*');
  responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  responseHeaders.set('Access-Control-Allow-Headers', '*');

  // Create the response
  const response = new NextResponse(backendResponse.body, {
    status: backendResponse.status,
    statusText: backendResponse.statusText,
    headers: responseHeaders,
  });

  return response;
}

/**
 * Main proxy handler for streaming requests
 * @param req The incoming Next.js request
 * @returns Appropriate response based on the endpoint
 */
export default async function proxy(req: NextRequest) {
  const url = new URL(req.url);
  const path = url.pathname;

  // Determine which handler to use based on the path
  if (path.includes('/chat') || path.includes('/stream')) {
    return handleChatStream(req);
  } else if (path.includes('/mcp') || path.includes('/execute-tool')) {
    return handleMcpStream(req);
  } else {
    // For non-streaming endpoints, just forward normally
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const targetUrl = `${backendUrl}${path}`;

    const backendResponse = await fetch(targetUrl, {
      method: req.method,
      headers: req.headers,
      body: req.body ? await req.blob() : undefined,
    });

    return backendResponse;
  }
}