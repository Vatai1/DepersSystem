import axios from "axios";
import type {
  DepersonalizeTextRequest,
  DepersonalizeTextResponse,
  DepersonalizeFileResponse,
  ModelInfo,
  HealthResponse,
} from "./types";

const api = axios.create({
  baseURL: "/api",
  timeout: 120_000,
});

export async function healthCheck(): Promise<HealthResponse> {
  const { data } = await api.get("/health");
  return data;
}

export async function getModelInfo(): Promise<ModelInfo> {
  const { data } = await api.get("/model");
  return data;
}

export async function depersonalizeText(
  req: DepersonalizeTextRequest,
): Promise<DepersonalizeTextResponse> {
  const { data } = await api.post("/depersonalize/text", req);
  return data;
}

export async function depersonalizeFile(
  file: File,
  mode: string,
): Promise<DepersonalizeFileResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("mode", mode);
  const { data } = await api.post("/depersonalize/file", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function downloadResult(url: string): Promise<Blob> {
  const { data } = await api.get(url, { responseType: "blob" });
  return data;
}
