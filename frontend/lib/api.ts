import "server-only";

import type {
  Obligation,
  ObligationDetail,
  ObligationFilters,
  ObligationType,
  Status,
  Summary,
} from "./types";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const message =
      (data as { error?: { message?: string } } | null)?.error?.message ??
      res.statusText;
    throw new ApiError(res.status, message);
  }

  return data as T;
}

function toQuery(filters: ObligationFilters): string {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.type) params.set("type", filters.type);
  if (filters.owner) params.set("owner", filters.owner);
  if (filters.overdue !== undefined) params.set("overdue", String(filters.overdue));
  const query = params.toString();
  return query ? `?${query}` : "";
}

export function listObligations(filters: ObligationFilters = {}): Promise<Obligation[]> {
  return request<Obligation[]>(`/obligations${toQuery(filters)}`);
}

export function getObligation(id: string): Promise<ObligationDetail> {
  return request<ObligationDetail>(`/obligations/${id}`);
}

export function getSummary(): Promise<Summary> {
  return request<Summary>("/obligations/summary");
}

export interface ObligationInput {
  type: ObligationType;
  title: string;
  description: string;
  due_date: string;
  owner: string;
  requires_document: boolean;
  company_tax_id: string;
}

export function createObligation(input: ObligationInput): Promise<ObligationDetail> {
  return request<ObligationDetail>("/obligations", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function patchObligation(
  id: string,
  input: Partial<ObligationInput>,
): Promise<ObligationDetail> {
  return request<ObligationDetail>(`/obligations/${id}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function transitionObligation(
  id: string,
  targetStatus: Status,
  expectedVersion: number,
): Promise<ObligationDetail> {
  return request<ObligationDetail>(`/obligations/${id}/transition`, {
    method: "POST",
    body: JSON.stringify({
      target_status: targetStatus,
      expected_version: expectedVersion,
    }),
  });
}

export function attachDocument(
  id: string,
  filename: string,
  contentType: string,
): Promise<ObligationDetail> {
  return request<ObligationDetail>(`/obligations/${id}/document`, {
    method: "POST",
    body: JSON.stringify({ filename, content_type: contentType }),
  });
}
