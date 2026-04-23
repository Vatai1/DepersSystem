export interface PiiEntity {
  text: string;
  label: string;
  start: number;
  end: number;
  score: number;
}

export interface DepersonalizeTextRequest {
  text: string;
  mode: "fake" | "replace" | "mask" | "redact";
  language?: string;
}

export interface DepersonalizeTextResponse {
  original_text: string;
  processed_text: string;
  entities: PiiEntity[];
  stats: {
    total_entities: number;
    by_type: Record<string, number>;
  };
}

export interface DepersonalizeFileResponse {
  filename: string;
  entities: PiiEntity[];
  stats: {
    total_entities: number;
    by_type: Record<string, number>;
  };
  download_url: string;
}

export interface ModelInfo {
  name: string;
  loaded: boolean;
  device: string;
  languages: string[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
}
