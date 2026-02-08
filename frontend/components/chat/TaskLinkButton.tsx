'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ExternalLink, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from '@/hooks/use-toast'
import { generateTaskLink, validateTaskAccess } from '@/lib/utils/taskLinkGenerator'
import { cn } from '@/lib/utils'

interface TaskLinkButtonProps {
  taskId: string
  children?: React.ReactNode
  className?: string
}

/**
 * Clickable button that navigates to a task detail page
 * Validates task existence before navigation
 */
export function TaskLinkButton({
  taskId,
  children,
  className,
}: TaskLinkButtonProps) {
  const router = useRouter()
  const [isValidating, setIsValidating] = useState(false)

  const handleClick = async () => {
    setIsValidating(true)

    try {
      const isValid = await validateTaskAccess(taskId)

      if (!isValid) {
        toast({
          variant: 'destructive',
          title: 'Task not found',
          description: `Task #${taskId} does not exist or you don't have access to it.`,
        })
        return
      }

      // Navigate to task detail page
      const taskLink = generateTaskLink(taskId)
      router.push(taskLink)
    } catch {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to open task. Please try again.',
      })
    } finally {
      setIsValidating(false)
    }
  }

  return (
    <Button
      variant="link"
      size="sm"
      onClick={handleClick}
      disabled={isValidating}
      className={cn(
        'inline-flex items-center gap-1 h-auto p-0 text-[#0FFF50] hover:text-[#0FFF50]/80',
        'font-medium underline-offset-4 hover:underline',
        className
      )}
    >
      {isValidating ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : (
        <ExternalLink className="h-3 w-3" />
      )}
      {children || `Task #${taskId}`}
    </Button>
  )
}
