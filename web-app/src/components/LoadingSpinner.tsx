'use client';

import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  message?: string | React.ReactNode;
}

export default function LoadingSpinner({ 
  size = 'md', 
  className,
  message = 'Generating speech...'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className={cn("flex flex-col items-center justify-center space-y-3", className)}>
      <div className="relative">
        <div className={cn(
          "animate-spin rounded-full border-2 border-blue-200",
          sizeClasses[size]
        )}>
          <div className={cn(
            "absolute top-0 left-0 rounded-full border-2 border-transparent border-t-blue-500",
            sizeClasses[size]
          )} />
        </div>
      </div>
      
      {message && (
        <div className="text-sm text-gray-600 text-center space-y-1">
          {message}
        </div>
      )}
    </div>
  );
} 