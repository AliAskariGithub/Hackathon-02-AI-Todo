import { cn } from "@/lib/utils"

interface SkeletonProps extends React.ComponentProps<"div"> {
  /**
   * Defines the width of the skeleton
   */
  width?: string | number;
  /**
   * Defines the height of the skeleton
   */
  height?: string | number;
  /**
   * Whether to animate the skeleton
   * @default true
   */
  animated?: boolean;
}

function Skeleton({
  className,
  width,
  height,
  animated = true,
  ...props
}: SkeletonProps) {
  const style = {
    width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
    height: height ? (typeof height === 'number' ? `${height}px` : height) : undefined,
  };

  return (
    <div
      data-slot="skeleton"
      className={cn(
        "rounded-md bg-primary/10 dark:bg-gray-700",
        animated && "animate-pulse",
        className
      )}
      style={style}
      {...props}
    />
  )
}

export { Skeleton }
