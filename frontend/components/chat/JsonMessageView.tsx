'use client'

import { Suspense, lazy } from 'react'
import { Loader2 } from 'lucide-react'

// Dynamically import react-json-view for bundle optimization
const ReactJson = lazy(() => import('react-json-view'))

interface JsonMessageViewProps {
  content: string
  toolCalls?: Array<{
    id: string
    name: string
    arguments: Record<string, unknown>
    status: string
    result?: Record<string, unknown>
  }>
}

/**
 * Component to render chat messages as formatted JSON
 * Uses react-json-view with dynamic import for bundle optimization
 */
export function JsonMessageView({ content, toolCalls }: JsonMessageViewProps) {
  // Parse content if it's a JSON string, otherwise wrap in object
  let jsonData: Record<string, unknown>
  try {
    jsonData = JSON.parse(content) as Record<string, unknown>
  } catch {
    jsonData = { content }
  }

  // Add tool calls to JSON if present
  if (toolCalls && toolCalls.length > 0) {
    jsonData = {
      ...jsonData,
      tool_calls: toolCalls,
    }
  }

  return (
    <Suspense
      fallback={
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Loading JSON viewer...</span>
        </div>
      }
    >
      <div className="rounded-md overflow-hidden">
        <ReactJson
          src={jsonData}
          theme="monokai"
          collapsed={1}
          displayDataTypes={false}
          displayObjectSize={true}
          enableClipboard={true}
          name={false}
          style={{
            padding: '1rem',
            borderRadius: '0.375rem',
            fontSize: '0.875rem',
          }}
        />
      </div>
    </Suspense>
  )
}
