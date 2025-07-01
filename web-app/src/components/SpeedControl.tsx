'use client';

import { cn } from '@/lib/utils';

interface SpeedControlProps {
  speed: number;
  onSpeedChange: (speed: number) => void;
  disabled?: boolean;
  min?: number;
  max?: number;
  step?: number;
}

export default function SpeedControl({
  speed,
  onSpeedChange,
  disabled = false,
  min = 0.5,
  max = 2.0,
  step = 0.1
}: SpeedControlProps) {
  const getSpeedLabel = (speed: number) => {
    if (speed < 0.8) return 'Very Slow';
    if (speed < 1.0) return 'Slow';
    if (speed === 1.0) return 'Normal';
    if (speed < 1.5) return 'Fast';
    return 'Very Fast';
  };

  const getSpeedColor = (speed: number) => {
    if (speed < 0.8) return 'text-blue-600';
    if (speed < 1.0) return 'text-blue-500';
    if (speed === 1.0) return 'text-green-600';
    if (speed < 1.5) return 'text-orange-500';
    return 'text-red-500';
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="block text-sm font-medium text-gray-700">
          Speed
        </label>
        <div className="flex items-center space-x-2">
          <span className={cn("text-sm font-medium", getSpeedColor(speed))}>
            {getSpeedLabel(speed)}
          </span>
          <span className="text-sm text-gray-500">
            {speed.toFixed(1)}x
          </span>
        </div>
      </div>
      
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={speed}
          onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
          disabled={disabled}
          className={cn(
            "w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer",
            "focus:outline-none focus:ring-2 focus:ring-blue-500",
            "[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4",
            "[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-blue-500",
            "[&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-md",
            "[&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:rounded-full",
            "[&::-moz-range-thumb]:bg-blue-500 [&::-moz-range-thumb]:cursor-pointer",
            "[&::-moz-range-thumb]:border-none [&::-moz-range-thumb]:shadow-md",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        />
        
        {/* Speed markers */}
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>0.5x</span>
          <span>1.0x</span>
          <span>1.5x</span>
          <span>2.0x</span>
        </div>
      </div>

      {/* Reset button */}
      <button
        onClick={() => onSpeedChange(1.0)}
        disabled={disabled || speed === 1.0}
        className={cn(
          "text-xs text-blue-600 hover:text-blue-700 underline",
          (disabled || speed === 1.0) && "opacity-50 cursor-not-allowed hover:text-blue-600"
        )}
      >
        Reset to Normal
      </button>
    </div>
  );
} 