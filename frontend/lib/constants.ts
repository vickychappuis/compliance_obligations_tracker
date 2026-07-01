import type { ObligationType, Status } from "./types";

export const STATUSES: Status[] = ["pending", "in_progress", "submitted", "done"];

export const OBLIGATION_TYPES: ObligationType[] = [
  "annual_report",
  "franchise_tax",
  "boi_report",
  "registered_agent_renewal",
];

export const MAX_UPLOAD_MB = 10;
export const MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024;
