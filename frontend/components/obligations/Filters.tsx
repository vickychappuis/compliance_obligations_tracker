"use client";

import { useRouter } from "next/navigation";
import type { FormEvent } from "react";

import { Button, Field, Input, Select } from "@/components/ui";
import { OBLIGATION_TYPES, STATUSES } from "@/lib/constants";
import type { Dictionary } from "@/lib/i18n";
import type { ObligationFilters } from "@/lib/types";

export function Filters({
  dict,
  current,
}: {
  dict: Dictionary;
  current: ObligationFilters;
}) {
  const router = useRouter();

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const params = new URLSearchParams();
    const status = String(data.get("status") ?? "");
    const type = String(data.get("type") ?? "");
    const owner = String(data.get("owner") ?? "").trim();
    if (status) params.set("status", status);
    if (type) params.set("type", type);
    if (owner) params.set("owner", owner);
    if (data.get("overdue") === "on") params.set("overdue", "true");
    const query = params.toString();
    router.push(query ? `/?${query}` : "/");
  }

  return (
    <form
      onSubmit={onSubmit}
      className="grid grid-cols-1 items-end gap-3 rounded-lg border border-slate-200 bg-white p-4 sm:grid-cols-5"
    >
      <Field label={dict.filters.status} htmlFor="filter-status">
        <Select id="filter-status" name="status" defaultValue={current.status ?? ""}>
          <option value="">{dict.filters.all}</option>
          {STATUSES.map((status) => (
            <option key={status} value={status}>
              {dict.status[status]}
            </option>
          ))}
        </Select>
      </Field>
      <Field label={dict.filters.type} htmlFor="filter-type">
        <Select id="filter-type" name="type" defaultValue={current.type ?? ""}>
          <option value="">{dict.filters.all}</option>
          {OBLIGATION_TYPES.map((type) => (
            <option key={type} value={type}>
              {dict.type[type]}
            </option>
          ))}
        </Select>
      </Field>
      <Field label={dict.filters.owner} htmlFor="filter-owner">
        <Input id="filter-owner" name="owner" defaultValue={current.owner ?? ""} />
      </Field>
      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          name="overdue"
          defaultChecked={current.overdue === true}
          className="h-4 w-4"
        />
        {dict.filters.overdue}
      </label>
      <div className="flex gap-2">
        <Button type="submit">{dict.filters.apply}</Button>
        <Button type="button" variant="secondary" onClick={() => router.push("/")}>
          {dict.filters.clear}
        </Button>
      </div>
    </form>
  );
}
