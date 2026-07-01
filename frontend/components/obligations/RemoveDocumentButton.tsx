"use client";

import { useActionState } from "react";

import { SubmitButton } from "@/components/ui/submit-button";
import { removeDocumentAction } from "@/lib/actions/obligations";
import type { Dictionary } from "@/lib/i18n";

export function RemoveDocumentButton({
  id,
  documentId,
  dict,
}: {
  id: string;
  documentId: string;
  dict: Dictionary;
}) {
  const [state, formAction] = useActionState(
    removeDocumentAction.bind(null, id, documentId),
    {},
  );

  return (
    <form action={formAction} className="inline-flex items-center gap-2">
      <SubmitButton
        variant="ghost"
        className="px-2 py-0.5 text-xs text-red-600 hover:bg-red-50"
        onClick={(event) => {
          if (!window.confirm(dict.detail.removeConfirm)) event.preventDefault();
        }}
      >
        {dict.detail.remove}
      </SubmitButton>
      {state.error && <span className="text-xs text-red-600">{state.error}</span>}
    </form>
  );
}
