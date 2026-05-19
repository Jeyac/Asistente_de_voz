export type AssistantStatus =
  | "idle"
  | "wake_listening"
  | "listening"
  | "processing"
  | "success"
  | "error";

export interface VoiceProcessResult {
  transcript: string;
  language: string;
  intent: string;
  confidence: number;
  above_threshold: boolean;
  cleaned_text: string;
  response: string;
  probabilities: Record<string, number>;
  action_performed?: boolean;
  action_url?: string | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export interface ApiErrorBody {
  error?: string;
  message?: string;
  details?: unknown;
}
