import * as React from "react"
import * as ToastPrimitives from "@radix-ui/react-toast"
import { cva, type VariantProps } from "class-variance-authority"
import { X, CheckCircle2, AlertCircle, Info, AlertTriangle } from "lucide-react"

import { cn } from "@/lib/utils"

const ToastProvider = ToastPrimitives.Provider

const ToastViewport = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Viewport>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Viewport>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Viewport
    ref={ref}
    className={cn(
      "fixed top-20 left-1/2 -translate-x-1/2 z-[100] flex max-h-screen w-full max-w-[420px] flex-col gap-2 p-4",
      className
    )}
    {...props}
  />
))
ToastViewport.displayName = ToastPrimitives.Viewport.displayName

const toastVariants = cva(
  "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-xl border border-white/10 p-4 pr-8 shadow-2xl backdrop-blur-xl transition-all data-[swipe=cancel]:translate-y-0 data-[swipe=end]:translate-y-[var(--radix-toast-swipe-end-y)] data-[swipe=move]:translate-y-[var(--radix-toast-swipe-move-y)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-top-full data-[state=open]:slide-in-from-top-full data-[state=open]:duration-300",
  {
    variants: {
      variant: {
        default: "bg-background/80 text-foreground backdrop-blur-xl border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.37)]",
        destructive:
          "destructive group border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-400 backdrop-blur-xl shadow-[0_8px_32px_0_rgba(239,68,68,0.37)]",
        success:
          "border-emerald-500/20 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 backdrop-blur-xl shadow-[0_8px_32px_0_rgba(16,185,129,0.37)]",
        info:
          "border-blue-500/20 bg-blue-500/10 text-blue-600 dark:text-blue-400 backdrop-blur-xl shadow-[0_8px_32px_0_rgba(59,130,246,0.37)]",
        warning:
          "border-yellow-500/20 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 backdrop-blur-xl shadow-[0_8px_32px_0_rgba(234,179,8,0.37)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

const Toast = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Root> &
    VariantProps<typeof toastVariants>
>(({ className, variant, ...props }, ref) => {
  const getIcon = () => {
    switch (variant) {
      case "success":
        return <CheckCircle2 className="h-5 w-5 shrink-0" />
      case "destructive":
        return <AlertCircle className="h-5 w-5 shrink-0" />
      case "info":
        return <Info className="h-5 w-5 shrink-0" />
      case "warning":
        return <AlertTriangle className="h-5 w-5 shrink-0" />
      default:
        return null
    }
  }

  const getTimerColor = () => {
    switch (variant) {
      case "success":
        return "bg-emerald-500"
      case "destructive":
        return "bg-red-500"
      case "info":
        return "bg-blue-500"
      case "warning":
        return "bg-yellow-500"
      default:
        return "bg-primary"
    }
  }

  return (
    <ToastPrimitives.Root
      ref={ref}
      className={cn(toastVariants({ variant }), "relative overflow-hidden", className)}
      {...props}
    >
      {getIcon()}
      <div className="flex-1">{props.children}</div>
      {/* Timer line at the bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/10">
        <div
          className={cn(
            "h-full animate-toast-timer origin-left",
            getTimerColor()
          )}
          style={{
            animation: "toast-timer 5s linear forwards"
          }}
        />
      </div>
    </ToastPrimitives.Root>
  )
})
Toast.displayName = ToastPrimitives.Root.displayName

const ToastAction = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Action>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Action>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Action
    ref={ref}
    className={cn(
      "inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium ring-offset-background transition-colors hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 group-[.destructive]:border-muted/40 group-[.destructive]:hover:border-destructive/30 group-[.destructive]:hover:bg-destructive group-[.destructive]:hover:text-destructive-foreground group-[.destructive]:focus:ring-destructive",
      className
    )}
    {...props}
  />
))
ToastAction.displayName = ToastPrimitives.Action.displayName

const ToastClose = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Close>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Close>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Close
    ref={ref}
    className={cn(
      "absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-all hover:text-foreground hover:bg-white/10 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-primary/50 group-hover:opacity-100 group-[.destructive]:text-red-300 group-[.destructive]:hover:text-red-50 group-[.destructive]:hover:bg-red-500/20 group-[.destructive]:focus:ring-red-400",
      className
    )}
    toast-close=""
    {...props}
  >
    <X className="h-4 w-4" />
  </ToastPrimitives.Close>
))
ToastClose.displayName = ToastPrimitives.Close.displayName

const ToastTitle = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Title>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Title>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Title
    ref={ref}
    className={cn("text-sm font-semibold", className)}
    {...props}
  />
))
ToastTitle.displayName = ToastPrimitives.Title.displayName

const ToastDescription = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Description>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Description>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Description
    ref={ref}
    className={cn("text-sm opacity-90", className)}
    {...props}
  />
))
ToastDescription.displayName = ToastPrimitives.Description.displayName

type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>

type ToastActionElement = React.ReactElement<typeof ToastAction>

export {
  type ToastProps,
  type ToastActionElement,
  ToastProvider,
  ToastViewport,
  Toast,
  ToastTitle,
  ToastDescription,
  ToastClose,
  ToastAction,
}
