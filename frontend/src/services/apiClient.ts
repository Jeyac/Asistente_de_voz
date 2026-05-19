/**
 * Cliente HTTP base para la API REST del asistente.
 *
 * En desarrollo usa el proxy de Vite (/api/v1). En producción, VITE_API_BASE_URL
 * apunta a la API en Render.
 */
import type { ApiErrorBody } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

/** Error con código HTTP y cuerpo JSON devuelto por FastAPI. */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: ApiErrorBody,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(response: Response): Promise<ApiError> {
  let body: ApiErrorBody | undefined;
  try {
    body = (await response.json()) as ApiErrorBody;
  } catch {
    body = undefined;
  }
  return new ApiError(
    body?.message ?? `Error HTTP ${response.status}`,
    response.status,
    body,
  );
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw await parseError(response);
  return response.json() as Promise<T>;
}

export async function apiPostJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw await parseError(response);
  return response.json() as Promise<T>;
}

export async function apiPostForm<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw await parseError(response);
  return response.json() as Promise<T>;
}

export async function apiPostBinary<T>(
  path: string,
  body: ArrayBuffer,
  headers?: Record<string, string>,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/octet-stream",
      ...headers,
    },
    body,
  });
  if (!response.ok) throw await parseError(response);
  return response.json() as Promise<T>;
}

export async function apiDelete(path: string, headers?: Record<string, string>): Promise<void> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers,
  });
  if (!response.ok) throw await parseError(response);
}

export { API_BASE };
