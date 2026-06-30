import Link from "next/link";

import { Card } from "@/components/ui";
import { cn } from "@/lib/cn";
import type { Dictionary } from "@/lib/i18n";
import { STATUSES } from "@/lib/constants";
import type { Summary } from "@/lib/types";

export function KpiCards({ summary, dict }: { summary: Summary; dict: Dictionary }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <Kpi label={dict.kpi.total} value={summary.total} href="/" />
      <Kpi
        label={dict.kpi.overdue}
        value={summary.overdue}
        tone="danger"
        href="/?overdue=true"
      />
      <Kpi label={dict.kpi.upcoming} value={summary.upcoming} tone="warning" />
      <Card>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {dict.kpi.byStatus}
        </p>
        <ul className="mt-2 space-y-0.5 text-sm">
          {STATUSES.map((status) => (
            <li key={status}>
              <Link
                href={`/?status=${status}`}
                className="flex justify-between rounded px-1 text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              >
                <span>{dict.status[status]}</span>
                <span className="font-medium">{summary.by_status[status] ?? 0}</span>
              </Link>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

function Kpi({
  label,
  value,
  tone,
  href,
}: {
  label: string;
  value: number;
  tone?: "danger" | "warning";
  href?: string;
}) {
  const valueColor =
    tone === "danger"
      ? "text-red-600"
      : tone === "warning"
        ? "text-amber-600"
        : "text-slate-900";
  const body = (
    <>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className={`mt-2 text-3xl font-semibold ${valueColor}`}>{value}</p>
    </>
  );
  return (
    <Card className={cn(href && "transition-colors hover:border-slate-300 hover:shadow")}>
      {href ? (
        <Link href={href} className="block">
          {body}
        </Link>
      ) : (
        body
      )}
    </Card>
  );
}
