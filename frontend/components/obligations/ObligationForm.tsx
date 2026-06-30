"use client";

import Link from "next/link";
import { useActionState } from "react";

import { Field, Input, Select, Textarea } from "@/components/ui";
import { SubmitButton } from "@/components/ui/submit-button";
import type { ActionState } from "@/lib/actions/obligations";
import { OBLIGATION_TYPES } from "@/lib/constants";
import type { Dictionary } from "@/lib/i18n";
import type { ObligationType } from "@/lib/types";

interface DefaultValues {
  title?: string;
  description?: string;
  type?: ObligationType;
  due_date?: string;
  owner?: string;
  requires_document?: boolean;
}

export function ObligationForm({
  dict,
  action,
  submitLabel,
  includeTaxId,
  cancelHref,
  defaultValues = {},
}: {
  dict: Dictionary;
  action: (prev: ActionState, formData: FormData) => Promise<ActionState>;
  submitLabel: string;
  includeTaxId: boolean;
  cancelHref: string;
  defaultValues?: DefaultValues;
}) {
  const [state, formAction] = useActionState(action, {});

  return (
    <form action={formAction} className="max-w-xl space-y-4">
      {state.error && (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {state.error}
        </p>
      )}

      <Field label={dict.form.title} htmlFor="title">
        <Input id="title" name="title" defaultValue={defaultValues.title} required />
      </Field>

      <Field label={dict.form.description} htmlFor="description">
        <Textarea
          id="description"
          name="description"
          rows={3}
          defaultValue={defaultValues.description}
        />
      </Field>

      <Field label={dict.form.type} htmlFor="type">
        <Select
          id="type"
          name="type"
          defaultValue={defaultValues.type ?? OBLIGATION_TYPES[0]}
        >
          {OBLIGATION_TYPES.map((type) => (
            <option key={type} value={type}>
              {dict.type[type]}
            </option>
          ))}
        </Select>
      </Field>

      <Field label={dict.form.dueDate} htmlFor="due_date">
        <Input
          id="due_date"
          name="due_date"
          type="date"
          defaultValue={defaultValues.due_date}
          required
        />
      </Field>

      <Field label={dict.form.owner} htmlFor="owner">
        <Input id="owner" name="owner" defaultValue={defaultValues.owner} required />
      </Field>

      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          name="requires_document"
          defaultChecked={defaultValues.requires_document}
          className="h-4 w-4"
        />
        {dict.form.requiresDocument}
      </label>

      {includeTaxId && (
        <div className="space-y-1">
          <Field label={dict.form.companyTaxId} htmlFor="company_tax_id">
            <Input
              id="company_tax_id"
              name="company_tax_id"
              inputMode="numeric"
              placeholder="123456789"
              aria-describedby="company_tax_id_hint"
              required
            />
          </Field>
          <p id="company_tax_id_hint" className="text-xs text-slate-500">
            {dict.form.companyTaxIdHint}
          </p>
        </div>
      )}

      <div className="flex gap-2">
        <SubmitButton>{submitLabel}</SubmitButton>
        <Link
          href={cancelHref}
          className="inline-flex items-center justify-center rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-900 hover:bg-slate-100"
        >
          {dict.form.cancel}
        </Link>
      </div>
    </form>
  );
}
