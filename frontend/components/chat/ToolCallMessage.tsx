import React from 'react';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, Loader2, Hammer } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ToolCallProps {
  toolName: string;
  arguments: Record<string, unknown>;
  status: 'initiated' | 'executing' | 'completed' | 'failed';
  result?: Record<string, unknown>;
  className?: string;
}

const ToolCallMessage: React.FC<ToolCallProps> = ({
  toolName,
  arguments: args,
  status,
  result,
  className
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'initiated':
      case 'executing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Hammer className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'initiated':
      case 'executing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <div className={cn("mt-3 p-3 rounded-lg border bg-background", className)}>
      <div className="flex items-center gap-2 mb-2">
        <Hammer className="h-4 w-4 text-primary" />
        <span className="font-medium text-sm">Tool Execution</span>
        <Badge variant="secondary" className={`text-xs ${getStatusColor()}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </Badge>
        {getStatusIcon()}
      </div>

      <div className="text-sm">
        <div className="font-medium text-primary">{toolName}</div>

        <div className="mt-1 text-muted-foreground text-xs">
          <div className="font-medium">Arguments:</div>
          <pre className="bg-muted p-2 rounded mt-1 overflow-x-auto">
            {JSON.stringify(args, null, 2)}
          </pre>
        </div>

        {result && (
          <div className="mt-2 text-xs">
            <div className="font-medium">Result:</div>
            <pre className="bg-muted p-2 rounded mt-1 overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ToolCallMessage;