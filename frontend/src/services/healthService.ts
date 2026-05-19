import type { HealthResponse } from "../types/api";
import { apiGet } from "./apiClient";

export async function checkHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>("/health");
}
