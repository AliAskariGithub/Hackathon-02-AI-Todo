'use client';

import { Button } from '@/components/ui/button';
import {
  CheckCircle2,
  Trash2,
  X,
  AlertCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface BulkActionsToolbarProps {
  selectedCount: number;
  onClearSelection: () => void;
  onBulkComplete: () => void;
  onBulkDelete: () => void;
  onBulkSetPriority: (priority: 'High' | 'Medium' | 'Low') => void;
  isProcessing?: boolean;
}

export function BulkActionsToolbar({
  selectedCount,
  onClearSelection,
  onBulkComplete,
  onBulkDelete,
  onBulkSetPriority,
  isProcessing = false
}: BulkActionsToolbarProps) {
  return (
    <AnimatePresence>
      {selectedCount > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
        >
          <div className="bg-background/95 backdrop-blur-lg border border-border rounded-2xl shadow-2xl p-4 min-w-[400px]">
            <div className="flex items-center justify-between gap-4">
              {/* Selection Info */}
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
                  <span className="text-sm font-bold text-primary">{selectedCount}</span>
                </div>
                <div>
                  <p className="text-sm font-semibold">
                    {selectedCount} {selectedCount === 1 ? 'task' : 'tasks'} selected
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Choose an action below
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                {/* Complete Button */}
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkComplete}
                  disabled={isProcessing}
                  className="gap-2 text-emerald-600 hover:text-emerald-700 hover:bg-emerald-500/10"
                >
                  {isProcessing ? (
                    <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4" />
                  )}
                  Complete
                </Button>

                {/* Priority Dropdown */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={isProcessing}
                      className="gap-2"
                    >
                      <AlertCircle className="w-4 h-4" />
                      Priority
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => onBulkSetPriority('High')}>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-500" />
                        <span>High Priority</span>
                      </div>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onBulkSetPriority('Medium')}>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-yellow-500" />
                        <span>Medium Priority</span>
                      </div>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => onBulkSetPriority('Low')}>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        <span>Low Priority</span>
                      </div>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/* Delete Button */}
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onBulkDelete}
                  disabled={isProcessing}
                  className="gap-2 text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  {isProcessing ? (
                    <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                  Delete
                </Button>

                {/* Clear Selection */}
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={onClearSelection}
                  disabled={isProcessing}
                  className="gap-2"
                >
                  <X className="w-4 h-4" />
                  Clear
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
