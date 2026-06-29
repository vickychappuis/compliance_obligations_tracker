import type { ObligationType, Status } from "./types";

export const STATUSES: Status[] = ["pending", "in_progress", "submitted", "done"];

export const OBLIGATION_TYPES: ObligationType[] = [
  "annual_report",
  "franchise_tax",
  "boi_report",
  "registered_agent_renewal",
];
