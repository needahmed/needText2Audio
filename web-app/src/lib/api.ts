import axios from 'axios';
import { TTSRequest, TTSResponse, VoicesResponse, HealthResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for TTS generation
});

export class TTSApi {
  static async getVoices(): Promise<VoicesResponse> {
    const response = await api.get<VoicesResponse>('/api/voices');
    return response.data;
  }

  static async generateSpeech(request: TTSRequest): Promise<TTSResponse> {
    const response = await api.post<TTSResponse>('/api/tts', request);
    return response.data;
  }

  static async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/api/health');
    return response.data;
  }

  static async deleteAudio(filename: string): Promise<void> {
    await api.delete(`/api/audio/${filename}`);
  }

  static getAudioUrl(audioPath: string): string {
    if (audioPath.startsWith('/audio/')) {
      return `${API_BASE_URL}${audioPath}`;
    }
    return audioPath;
  }
}

export default TTSApi; 