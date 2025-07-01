'use client';

import { useState } from 'react';
import { cn, sampleTexts, getRandomSampleText } from '@/lib/utils';

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  maxLength?: number;
  placeholder?: string;
  disabled?: boolean;
}

export default function TextInput({
  value,
  onChange,
  maxLength = 25000,
  placeholder = "Enter the text you want to convert to speech...",
  disabled = false
}: TextInputProps) {
  const characterCount = value.length;
  const isNearLimit = characterCount > maxLength * 0.8;
  const isOverLimit = characterCount > maxLength;

  const handleSampleText = (type: 'random' | 'gatsby' | 'frankenstein') => {
    let text = '';
    switch (type) {
      case 'random':
        text = getRandomSampleText();
        break;
      case 'gatsby':
        text = sampleTexts.gatsby;
        break;
      case 'frankenstein':
        text = sampleTexts.frankenstein;
        break;
    }
    onChange(text);
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(
            "w-full min-h-[120px] p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors",
            disabled && "bg-gray-100 cursor-not-allowed",
            isOverLimit && "border-red-500 focus:ring-red-500",
            !isOverLimit && !disabled && "border-gray-300"
          )}
          rows={6}
        />
        
        {/* Character counter */}
        <div className={cn(
          "absolute bottom-3 right-3 text-sm",
          isOverLimit && "text-red-500",
          isNearLimit && !isOverLimit && "text-yellow-500",
          !isNearLimit && "text-gray-500"
        )}>
          {characterCount}/{maxLength}
        </div>
      </div>

      {/* Sample text buttons */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleSampleText('random')}
          disabled={disabled}
          className="px-3 py-1.5 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          🎲 Random Quote
        </button>
        <button
          onClick={() => handleSampleText('gatsby')}
          disabled={disabled}
          className="px-3 py-1.5 text-sm bg-green-100 hover:bg-green-200 text-green-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          🥂 Gatsby
        </button>
        <button
          onClick={() => handleSampleText('frankenstein')}
          disabled={disabled}
          className="px-3 py-1.5 text-sm bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          💀 Frankenstein
        </button>
      </div>

      {isOverLimit && (
        <p className="text-red-500 text-sm">
          Text exceeds maximum length of {maxLength} characters. Please shorten your text.
        </p>
      )}
    </div>
  );
} 