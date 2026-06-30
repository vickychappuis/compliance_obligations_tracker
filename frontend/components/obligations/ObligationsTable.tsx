"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { Badge } from "@/components/ui";
import { StatusBadge } from "@/components/obligations/StatusBadge";
import { cn } from "@/lib/cn";
import { formatDate } from "@/lib/format";
import type { Dictionary } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n/config";
import type { Obligation } from "@/lib/types";

export function ObligationsTable({
  items,
  dict,
  locale,
  filtered = false,
}: {
  items: Obligation[];
  dict: Dictionary;
  locale: Locale;
  filtered?: boolean;
}) {
  const router = useRouter();

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center gap-4 rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-500">
        <p>{filtered ? dict.list.empty : dict.list.emptyAll}</p>
        {!filtered && (
          <Link
            href="/obligations/new"
            className="inline-flex items-center justify-center rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700"
          >
            {dict.list.createFirst}
          </Link>
        )}
      </div>
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
              onClick={() => router.push(`/obligations/${item.id}`)}
              className={cn(
                "cursor-pointer",
                item.overdue ? "bg-red-50" : "hover:bg-slate-50",
              )}
            >
              <td className="px-4 py-3">
                <Link
                  href={`/obligations/${item.id}`}
                  onClick={(event) => event.stopPropagation()}
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
