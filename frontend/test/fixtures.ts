import { en } from "@/lib/i18n/en";
import type { Obligation } from "@/lib/types";

export const dict = en;

export function makeObligation(overrides: Partial<Obligation> = {}): Obligation {
  return {
    id: "ob-1",
    type: "annual_report",
    title: "Delaware Annual Report",
    description: "File it.",
    status: "pending",
    due_date: "2026-03-01",
    owner: "Jane Founder",
    requires_document: false,
    has_document: false,
    company_tax_id: "••••6789",
    version: 1,
    overdue: false,
    can_submit: true,
    allowed_transitions: ["in_progress"],
    created_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}
