'use client';

import { Voice } from '@/lib/types';
import { cn } from '@/lib/utils';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface VoiceSelectorProps {
  voices: Voice[];
  selectedVoice: string;
  onVoiceChange: (voiceId: string) => void;
  disabled?: boolean;
}

export default function VoiceSelector({
  voices,
  selectedVoice,
  onVoiceChange,
  disabled = false
}: VoiceSelectorProps) {
  const selectedVoiceData = voices.find(v => v.id === selectedVoice);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Voice
      </label>
      
      <div className="relative">
        <select
          value={selectedVoice}
          onChange={(e) => onVoiceChange(e.target.value)}
          disabled={disabled}
          className={cn(
            "w-full appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors",
            disabled && "bg-gray-100 cursor-not-allowed"
          )}
        >
          {voices.map((voice) => (
            <option key={voice.id} value={voice.id}>
              {voice.description || `${voice.name} (${voice.language} ${voice.gender})`}
            </option>
          ))}
        </select>
        
        {/* Custom dropdown arrow */}
        <ChevronDownIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
      </div>

      {/* Voice info */}
      {selectedVoiceData && (
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
            {selectedVoiceData.language}
          </span>
          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
            {selectedVoiceData.gender}
          </span>
          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
            {selectedVoiceData.name}
          </span>
        </div>
      )}
    </div>
  );
} 