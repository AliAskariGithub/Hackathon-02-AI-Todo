/**
 * Utility functions for parsing and generating task links from chat messages
 */

interface TaskReference {
  taskId: string
  originalText: string
  startIndex: number
  endIndex: number
}

/**
 * Parse task references from chat message content
 * Supports formats: "task #123", "task 123", "#123" (when preceded by "task")
 */
export function parseTaskReferences(content: string): TaskReference[] {
  const references: TaskReference[] = []

  // Pattern 1: "task #123" or "task 123"
  const taskPattern = /\btask\s+#?(\d+)\b/gi
  let match: RegExpExecArray | null

  while ((match = taskPattern.exec(content)) !== null) {
    references.push({
      taskId: match[1],
      originalText: match[0],
      startIndex: match.index,
      endIndex: match.index + match[0].length,
    })
  }

  return references
}

/**
 * Generate a task detail page link with optional source parameter
 */
export function generateTaskLink(taskId: string, source: string = 'chat'): string {
  return `/dashboard/tasks/${taskId}?source=${source}`
}

/**
 * Validate if a task exists and is accessible to the user
 * Returns true if task exists, false otherwise
 */
export async function validateTaskAccess(taskId: string): Promise<boolean> {
  try {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001'
    const authToken = localStorage.getItem('auth-token')
    const userId = localStorage.getItem('userId')

    if (!authToken || !userId) {
      return false
    }

    const response = await fetch(
      `${apiBaseUrl}/api/${userId}/tasks/${taskId}`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      }
    )

    return response.ok
  } catch (error) {
    console.error('Error validating task access:', error)
    return false
  }
}
