import { StatusBadge } from "@/components/obligations/StatusBadge";
import { formatDateTime } from "@/lib/format";
import type { Dictionary } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n/config";
import type { AuditEntry } from "@/lib/types";

export function AuditHistory({
  entries,
  dict,
  locale,
}: {
  entries: AuditEntry[];
  dict: Dictionary;
  locale: Locale;
}) {
  return (
    <ol className="space-y-2">
      {entries.map((entry, index) => (
        <li
          key={index}
          className="flex flex-wrap items-center gap-2 text-sm text-slate-600"
        >
          <span className="tabular-nums text-slate-400">
            {formatDateTime(entry.timestamp, locale)}
          </span>
          {entry.from_status ? (
            <>
              <StatusBadge
                status={entry.from_status}
                label={dict.status[entry.from_status]}
              />
              <span aria-hidden>→</span>
              <StatusBadge
                status={entry.to_status}
                label={dict.status[entry.to_status]}
              />
            </>
          ) : (
            <>
              <span className="text-slate-500">{dict.detail.created}</span>
              <StatusBadge
                status={entry.to_status}
                label={dict.status[entry.to_status]}
              />
            </>
          )}
        </li>
      ))}
    </ol>
  );
}
