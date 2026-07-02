"use client";

import { useActionState, useEffect, useRef, useState, type ChangeEvent } from "react";

import { cn } from "@/lib/cn";
import { attachDocumentAction } from "@/lib/actions/obligations";
import { MAX_UPLOAD_BYTES } from "@/lib/constants";
import type { Dictionary } from "@/lib/i18n";

export function AttachDocumentForm({ id, dict }: { id: string; dict: Dictionary }) {
  const [state, formAction, isPending] = useActionState(
    attachDocumentAction.bind(null, id),
    {},
  );
  const [fileName, setFileName] = useState<string | null>(null);
  const [sizeError, setSizeError] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (!state.error) {
      formRef.current?.reset();
      setFileName(null);
    }
  }, [state]);

  function onChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      setFileName(null);
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setSizeError(true);
      setFileName(null);
      event.target.value = "";
      return;
    }
    setSizeError(false);
    setFileName(file.name);
    formRef.current?.requestSubmit();
  }

  const error = sizeError ? dict.detail.fileTooLarge : state.error;

  return (
    <form ref={formRef} action={formAction} className="space-y-2">
      <label
        htmlFor="file"
        aria-busy={isPending}
        className={cn(
          "flex cursor-pointer flex-col items-center gap-1 rounded-lg border-2 border-dashed border-slate-300 px-4 py-6 text-center hover:border-slate-400 hover:bg-slate-50",
          isPending && "pointer-events-none opacity-60",
        )}
      >
        <UploadIcon />
        <span className="text-sm font-medium text-slate-700">
          {isPending
            ? `${dict.detail.uploading} ${fileName ?? ""}`.trim()
            : (fileName ?? dict.detail.uploadPrompt)}
        </span>
        <span className="text-xs text-slate-500">{dict.detail.fileHint}</span>
        <input
          id="file"
          name="file"
          type="file"
          accept=".pdf,.doc,.docx,image/*"
          required
          disabled={isPending}
          className="sr-only"
          onChange={onChange}
        />
      </label>
      {error && <p className="text-xs text-red-600">{error}</p>}
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
