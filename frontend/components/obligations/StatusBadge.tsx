import { Badge } from "@/components/ui";
import type { Status } from "@/lib/types";

const tones = {
  pending: "neutral",
  in_progress: "info",
  submitted: "warning",
  done: "success",
} as const;

export function StatusBadge({ status, label }: { status: Status; label: string }) {
  return <Badge tone={tones[status]}>{label}</Badge>;
}
