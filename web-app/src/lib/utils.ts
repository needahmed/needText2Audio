import { type ClassValue, clsx } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export const sampleTexts = {
  random: [
    "Hello world! This is a test of the Kokoro text-to-speech system.",
    "The quick brown fox jumps over the lazy dog.",
    "Technology is best when it brings people together.",
    "In the midst of winter, I found there was, within me, an invincible summer.",
    "The only way to do great work is to love what you do."
  ],
  gatsby: "In my younger and more vulnerable years my father gave me some advice that I've carried with me ever since. 'Whenever you feel like criticizing anyone,' he told me, 'just remember that all the people in this world haven't had the advantages that you've had.'",
  frankenstein: "It was on a dreary night of November that I beheld the accomplishment of my toils. With an anxiety that almost amounted to agony, I collected the instruments of life around me, that I might infuse a spark of being into the lifeless thing that lay at my feet."
};

export function getRandomSampleText(): string {
  const randomTexts = sampleTexts.random;
  return randomTexts[Math.floor(Math.random() * randomTexts.length)];
}

export function splitTextIntoChunks(text: string, chunkSize: number): string[] {
  if (text.length <= chunkSize) {
    return [text];
  }

  // Split by sentence-ending punctuation. This is a simple but effective regex.
  const sentences = text.match(/[^.!?]+[.!?]*/g) || [];
  const chunks: string[] = [];
  let currentChunk = "";

  for (const sentence of sentences) {
    if (currentChunk.length + sentence.length > chunkSize) {
      // Current chunk is full, push it to the array.
      if (currentChunk.trim()) {
        chunks.push(currentChunk.trim());
      }
      // Start a new chunk. If the sentence itself is larger than the chunk size,
      // it will be its own chunk (and might be truncated by the API later, which is a fallback).
      currentChunk = sentence;
    } else {
      currentChunk += sentence;
    }
  }

  // Add the last remaining chunk.
  if (currentChunk.trim()) {
    chunks.push(currentChunk.trim());
  }

  return chunks;
}

/**
 * Encodes an AudioBuffer into a WAV file (blob).
 * @param buffer The AudioBuffer to encode.
 * @returns A Blob representing the WAV file.
 */
function audioBufferToWavBlob(buffer: AudioBuffer): Blob {
  const numOfChan = buffer.numberOfChannels;
  const aOffset = 44; // Offset for the data chunk after the 44-byte header
  const length = buffer.length * numOfChan * 2 + aOffset;
  const newBuffer = new ArrayBuffer(length);
  const view = new DataView(newBuffer);
  let offset = 0;

  // Write WAV header
  const writeString = (s: string) => {
    for (let i = 0; i < s.length; i++) {
      view.setUint8(offset + i, s.charCodeAt(i));
    }
    offset += s.length;
  };

  const writeUint32 = (d: number) => {
    view.setUint32(offset, d, true);
    offset += 4;
  };

  const writeUint16 = (d: number) => {
    view.setUint16(offset, d, true);
    offset += 2;
  };

  writeString("RIFF");
  writeUint32(length - 8);
  writeString("WAVE");
  writeString("fmt ");
  writeUint32(16);
  writeUint16(1); // PCM
  writeUint16(numOfChan);
  writeUint32(buffer.sampleRate);
  writeUint32(buffer.sampleRate * 2 * numOfChan); // ByteRate
  writeUint16(numOfChan * 2); // BlockAlign
  writeUint16(16); // BitsPerSample
  writeString("data");
  writeUint32(length - aOffset);

  // Write interleaved audio data
  for (let i = 0; i < buffer.length; i++) {
    for (let channel = 0; channel < numOfChan; channel++) {
      let sample = buffer.getChannelData(channel)[i];
      // Clamp and convert to 16-bit PCM
      sample = Math.max(-1, Math.min(1, sample));
      const pcmSample = sample < 0 ? sample * 32768 : sample * 32767;
      view.setInt16(offset, pcmSample, true);
      offset += 2;
    }
  }

  return new Blob([view], { type: "audio/wav" });
}

/**
 * Fetches multiple audio files and concatenates them into a single audio blob.
 * @param audioUrls An array of URLs pointing to the audio files.
 * @returns A Promise that resolves with a single Blob of the concatenated audio.
 */
export async function fetchAndCombineAudio(audioUrls: string[], onProgress: (progress: number) => void): Promise<Blob> {
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  
  const audioBuffers = await Promise.all(
    audioUrls.map(async (url, index) => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch audio from ${url}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      const decodedBuffer = await audioContext.decodeAudioData(arrayBuffer);
      onProgress((index + 1) / audioUrls.length);
      return decodedBuffer;
    })
  );

  if (audioBuffers.length === 0) {
    throw new Error("No audio buffers to combine.");
  }
  if (audioBuffers.length === 1) {
    return audioBufferToWavBlob(audioBuffers[0]);
  }

  const totalLength = audioBuffers.reduce((acc, buffer) => acc + buffer.length, 0);
  const numberOfChannels = audioBuffers[0].numberOfChannels;
  const sampleRate = audioBuffers[0].sampleRate;
  const combinedBuffer = audioContext.createBuffer(numberOfChannels, totalLength, sampleRate);

  let currentOffset = 0;
  for (const buffer of audioBuffers) {
    if (buffer.numberOfChannels !== numberOfChannels) {
      console.warn("Mismatch in channel count, skipping a buffer.");
      continue;
    }
    for (let i = 0; i < numberOfChannels; i++) {
      combinedBuffer.copyToChannel(buffer.getChannelData(i), i, currentOffset);
    }
    currentOffset += buffer.length;
  }

  return audioBufferToWavBlob(combinedBuffer);
} 