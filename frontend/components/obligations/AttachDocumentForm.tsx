"use client";

import { useActionState } from "react";

import { Field, Input } from "@/components/ui";
import { SubmitButton } from "@/components/ui/submit-button";
import { attachDocumentAction } from "@/lib/actions/obligations";
import type { Dictionary } from "@/lib/i18n";

export function AttachDocumentForm({ id, dict }: { id: string; dict: Dictionary }) {
  const [state, formAction] = useActionState(
    attachDocumentAction.bind(null, id),
    {},
  );

  return (
    <form action={formAction} className="flex items-end gap-2">
      <Field label={dict.detail.filename} htmlFor="filename">
        <Input id="filename" name="filename" placeholder="filing.pdf" required />
      </Field>
      <SubmitButton variant="secondary">{dict.detail.attach}</SubmitButton>
      {state.error && <p className="text-xs text-red-600">{state.error}</p>}
    </form>
  );
}
