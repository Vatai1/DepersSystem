export interface PiiEntity {
  text: string;
  label: string;
  start: number;
  end: number;
  score: number;
  per_parts?: { text: string; role: string }[];
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
  model_name: string;
  display_name?: string;
  description?: string;
  size?: string;
  scheme: string;
  is_loaded: boolean;
}

export interface ModelListItem {
  model_name: string;
  display_name: string;
  description: string;
  size: string;
  scheme: string;
  is_active: boolean;
}

export interface ModelsListResponse {
  models: ModelListItem[];
  active: string;
}

export interface SwitchModelResponse {
  status: string;
  model: ModelInfo;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
}
