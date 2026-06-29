import Link from "next/link";

import { Badge } from "@/components/ui";
import { StatusBadge } from "@/components/obligations/StatusBadge";
import { formatDate } from "@/lib/format";
import type { Dictionary } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n/config";
import type { Obligation } from "@/lib/types";

export function ObligationsTable({
  items,
  dict,
  locale,
}: {
  items: Obligation[];
  dict: Dictionary;
  locale: Locale;
}) {
  if (items.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-500">
        {dict.list.empty}
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">{dict.list.title}</th>
            <th className="px-4 py-3">{dict.list.type}</th>
            <th className="px-4 py-3">{dict.list.status}</th>
            <th className="px-4 py-3">{dict.list.dueDate}</th>
            <th className="px-4 py-3">{dict.list.owner}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((item) => (
            <tr
              key={item.id}
              className={item.overdue ? "bg-red-50" : "hover:bg-slate-50"}
            >
              <td className="px-4 py-3">
                <Link
                  href={`/obligations/${item.id}`}
                  className="font-medium text-slate-900 hover:underline"
                >
                  {item.title}
                </Link>
              </td>
              <td className="px-4 py-3 text-slate-600">{dict.type[item.type]}</td>
              <td className="px-4 py-3">
                <StatusBadge status={item.status} label={dict.status[item.status]} />
              </td>
              <td className="px-4 py-3 text-slate-600">
                <span className="flex items-center gap-2">
                  {formatDate(item.due_date, locale)}
                  {item.overdue && (
                    <Badge tone="danger">{dict.list.overdueBadge}</Badge>
                  )}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">{item.owner}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
