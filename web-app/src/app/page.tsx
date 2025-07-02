'use client';

import { useState, useEffect } from 'react';
import { Voice, TTSRequest } from '@/lib/types';
import TTSApi from '@/lib/api';
import { splitTextIntoChunks, fetchAndCombineAudio } from '@/lib/utils';
import TextInput from '@/components/TextInput';
import VoiceSelector from '@/components/VoiceSelector';
import SpeedControl from '@/components/SpeedControl';
import AudioPlayer from '@/components/AudioPlayer';
import LoadingSpinner from '@/components/LoadingSpinner';
import { SpeakerWaveIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const TEXT_CHUNK_SIZE = 2500; // Process text in chunks of 2500 characters
const MAX_TEXT_LENGTH = 25000; // The total character limit for the input field

export default function Home() {
  const [text, setText] = useState('');
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState('af_heart');
  const [speed, setSpeed] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState<React.ReactNode>('Initializing...');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [tokens, setTokens] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [useGpu, setUseGpu] = useState(true);

  // Load voices on component mount
  useEffect(() => {
    const loadVoices = async () => {
      try {
        const voicesResponse = await TTSApi.getVoices();
        setVoices(voicesResponse.voices);
      } catch (err) {
        setError('Failed to load voices. Please make sure the API server is running.');
        console.error('Failed to load voices:', err);
      }
    };

    loadVoices();
  }, []);
  
  // Clean up blob URL when component unmounts or audioUrl changes
  useEffect(() => {
    return () => {
      if (audioUrl && audioUrl.startsWith('blob:')) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError('Please enter some text to convert to speech.');
      return;
    }

    if (text.length > MAX_TEXT_LENGTH) {
      setError(`Text is too long. Please keep it under ${MAX_TEXT_LENGTH} characters.`);
      return;
    }

    setIsLoading(true);
    setError(null);
    setAudioUrl(null);
    setTokens(null);

    const chunks = splitTextIntoChunks(text.trim(), TEXT_CHUNK_SIZE);
    const audioUrls: string[] = [];
    const allTokens: string[] = [];

    try {
      for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        setLoadingMessage(
          <div>
            <p>Generating speech...</p>
            <p className="font-semibold">Processing chunk {i + 1} of {chunks.length}</p>
          </div>
        );
        
        const request: TTSRequest = { text: chunk, voice: selectedVoice, speed, use_gpu: useGpu };
        const response = await TTSApi.generateSpeech(request);

        if (response.audio_url) {
          audioUrls.push(TTSApi.getAudioUrl(response.audio_url));
          if(response.tokens) allTokens.push(response.tokens);
        } else {
          throw new Error(`Failed to generate audio for chunk ${i + 1}.`);
        }
      }

      setTokens(allTokens.join(' '));

      if (audioUrls.length > 0) {
        setLoadingMessage(
          <div>
            <p>Generation complete!</p>
            <p className="font-semibold">Preparing audio...</p>
          </div>
        );
        const combinedAudioBlob = await fetchAndCombineAudio(audioUrls, (progress) => {
            setLoadingMessage(
              <div>
                <p>Downloading & merging audio...</p>
                <p className="font-semibold">Progress: {Math.round(progress * 100)}%</p>
              </div>
            );
        });
        const blobUrl = URL.createObjectURL(combinedAudioBlob);
        setAudioUrl(blobUrl);
      } else {
        throw new Error("No audio was generated from any text chunk.");
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An unknown error occurred during generation.');
      console.error('Generation failed:', err);
    } finally {
      setIsLoading(false);
      // Clean up the individual chunk files from the server
      for(const url of audioUrls) {
        if(url.includes('/audio/')) {
          const filename = url.split('/').pop();
          if(filename) TTSApi.deleteAudio(filename).catch(e => console.error("Failed to delete chunk:", e));
        }
      }
    }
  };

  const clearError = () => setError(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-3">
            <SpeakerWaveIcon className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Kokoro TTS</h1>
              <p className="text-gray-600">High-quality text-to-speech synthesis</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left column - Input controls */}
          <div className="lg:col-span-2 space-y-6">
            {/* Text input */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Text Input</h2>
              <TextInput
                value={text}
                onChange={setText}
                disabled={isLoading}
                placeholder="Enter text up to 25,000 characters. Long text will be synthesized in chunks."
                maxLength={MAX_TEXT_LENGTH}
              />
            </div>

            {/* Voice and speed controls */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Voice Settings</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <VoiceSelector
                  voices={voices}
                  selectedVoice={selectedVoice}
                  onVoiceChange={setSelectedVoice}
                  disabled={isLoading}
                />
                <SpeedControl
                  speed={speed}
                  onSpeedChange={setSpeed}
                  disabled={isLoading}
                />
              </div>
              
              {/* GPU toggle */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={useGpu}
                    onChange={(e) => setUseGpu(e.target.checked)}
                    disabled={isLoading}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Use GPU acceleration (faster)</span>
                </label>
              </div>
            </div>

            {/* Generate button */}
            <button
              onClick={handleGenerate}
              disabled={isLoading || !text.trim() || text.length > MAX_TEXT_LENGTH}
              className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {isLoading ? 'Generating...' : 'Generate Speech'}
            </button>
          </div>

          {/* Right column - Output */}
          <div className="space-y-6">
            {/* Loading state */}
            {isLoading && (
              <div className="bg-white rounded-lg border border-gray-200 p-6 flex justify-center items-center">
                <LoadingSpinner 
                  size="lg" 
                  message={loadingMessage}
                />
              </div>
            )}

            {/* Error display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-red-700 text-sm">{error}</p>
                    <button
                      onClick={clearError}
                      className="text-red-600 hover:text-red-700 text-sm underline mt-1"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Audio player */}
            {audioUrl && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Audio</h3>
                <AudioPlayer audioUrl={audioUrl} />
              </div>
            )}

            {/* Tokens display */}
            {tokens && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Tokens</h3>
                <div className="bg-gray-50 rounded p-3">
                  <p className="text-sm text-gray-700 font-mono break-all">
                    {tokens}
                  </p>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  These are the phonetic tokens used to generate the speech.
                </p>
              </div>
            )}

            {/* Tips */}
            {!isLoading && !audioUrl && (
              <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                <h3 className="text-sm font-semibold text-blue-900 mb-2">💡 Tips</h3>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• Use punctuation for better intonation.</li>
                  <li>• Long text is automatically split and combined.</li>
                  <li>• Adjust speed for different effects.</li>
                  <li>• Try a sample text to get started quickly.</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>Powered by <a href="https://huggingface.co/hexgrad/Kokoro-82M" className="text-blue-600 hover:text-blue-700 underline" target="_blank" rel="noopener noreferrer">Kokoro TTS</a></p>
          </div>
        </div>
      </footer>
    </div>
  );
}
