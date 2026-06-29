export type Status = "pending" | "in_progress" | "submitted" | "done";

export type ObligationType =
  | "annual_report"
  | "franchise_tax"
  | "boi_report"
  | "registered_agent_renewal";

export interface AuditEntry {
  from_status: Status | null;
  to_status: Status;
  timestamp: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  content_type: string;
  uploaded_at: string;
}

export interface Obligation {
  id: string;
  type: ObligationType;
  title: string;
  description: string;
  status: Status;
  due_date: string;
  owner: string;
  requires_document: boolean;
  has_document: boolean;
  company_tax_id: string;
  version: number;
  overdue: boolean;
  allowed_transitions: Status[];
  created_at: string;
}

export interface ObligationDetail extends Obligation {
  audit: AuditEntry[];
  documents: DocumentInfo[];
}

export interface Summary {
  total: number;
  by_status: Record<string, number>;
  overdue: number;
  upcoming: number;
}

export interface ObligationFilters {
  status?: Status;
  type?: ObligationType;
  owner?: string;
  overdue?: boolean;
}
