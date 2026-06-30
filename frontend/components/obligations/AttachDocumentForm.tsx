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
    <form action={formAction} className="space-y-2">
      <div className="flex items-end gap-2">
        <Field label={dict.detail.file} htmlFor="file">
          <Input
            id="file"
            name="file"
            type="file"
            accept=".pdf,.doc,.docx,image/*"
            aria-describedby="file-hint"
            required
          />
        </Field>
        <SubmitButton variant="secondary">{dict.detail.attach}</SubmitButton>
      </div>
      <p id="file-hint" className="text-xs text-slate-500">
        {dict.detail.fileHint}
      </p>
      {state.error && <p className="text-xs text-red-600">{state.error}</p>}
    </form>
  );
}
