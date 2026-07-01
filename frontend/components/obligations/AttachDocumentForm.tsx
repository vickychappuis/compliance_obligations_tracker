"use client";

import { useActionState, useEffect, useRef, useState } from "react";

import { SubmitButton } from "@/components/ui/submit-button";
import { attachDocumentAction } from "@/lib/actions/obligations";
import type { Dictionary } from "@/lib/i18n";

export function AttachDocumentForm({ id, dict }: { id: string; dict: Dictionary }) {
  const [state, formAction] = useActionState(
    attachDocumentAction.bind(null, id),
    {},
  );
  const [fileName, setFileName] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (!state.error) {
      formRef.current?.reset();
      setFileName(null);
    }
  }, [state]);

  return (
    <form ref={formRef} action={formAction} className="space-y-3">
      <label
        htmlFor="file"
        className="flex cursor-pointer flex-col items-center gap-1 rounded-lg border-2 border-dashed border-slate-300 px-4 py-6 text-center hover:border-slate-400 hover:bg-slate-50"
      >
        <UploadIcon />
        <span className="text-sm font-medium text-slate-700">
          {fileName ?? dict.detail.uploadPrompt}
        </span>
        <span className="text-xs text-slate-500">{dict.detail.fileHint}</span>
        <input
          id="file"
          name="file"
          type="file"
          accept=".pdf,.doc,.docx,image/*"
          required
          className="sr-only"
          onChange={(event) =>
            setFileName(event.target.files?.[0]?.name ?? null)
          }
        />
      </label>
      <div className="flex items-center gap-3">
        <SubmitButton variant="secondary" disabled={!fileName}>
          {dict.detail.attach}
        </SubmitButton>
        {state.error && <span className="text-xs text-red-600">{state.error}</span>}
      </div>
    </form>
  );
}

function UploadIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-6 w-6 text-slate-400"
      aria-hidden
    >
      <path d="M12 16V4" />
      <path d="m7 9 5-5 5 5" />
      <path d="M5 16v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2" />
    </svg>
  );
}
