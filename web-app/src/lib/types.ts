export interface Voice {
  id: string;
  name: string;
  language: string;
  gender: string;
  description?: string;
}

export interface VoicesResponse {
  voices: Voice[];
}

export interface TTSRequest {
  text: string;
  voice: string;
  speed: number;
  use_gpu?: boolean;
}

export interface TTSResponse {
  message: string;
  audio_url?: string;
  tokens?: string;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  initialized: boolean;
  cuda_available: boolean;
} 