"use client";

import { useActionState } from "react";

import { SubmitButton } from "@/components/ui/submit-button";
import { transitionAction } from "@/lib/actions/obligations";
import type { Dictionary } from "@/lib/i18n";
import type { Status } from "@/lib/types";

function TransitionButton({
  id,
  target,
  version,
  label,
  disabled,
  blockedHint,
}: {
  id: string;
  target: Status;
  version: number;
  label: string;
  disabled: boolean;
  blockedHint?: string;
}) {
  const [state, formAction] = useActionState(transitionAction.bind(null, id), {});

  return (
    <div className="space-y-1">
      <form action={formAction}>
        <input type="hidden" name="target_status" value={target} />
        <input type="hidden" name="expected_version" value={version} />
        <SubmitButton
          disabled={disabled}
          variant={target === "done" ? "primary" : "secondary"}
        >
          {label}
        </SubmitButton>
      </form>
      {disabled && blockedHint && (
        <p className="text-xs text-amber-600">{blockedHint}</p>
      )}
      {state.error && <p className="text-xs text-red-600">{state.error}</p>}
    </div>
  );
}

export function TransitionControls({
  id,
  version,
  allowed,
  requiresDocument,
  hasDocument,
  dict,
}: {
  id: string;
  version: number;
  allowed: Status[];
  requiresDocument: boolean;
  hasDocument: boolean;
  dict: Dictionary;
}) {
  if (allowed.length === 0) {
    return <p className="text-sm text-slate-500">{dict.detail.noTransitions}</p>;
  }

  return (
    <div className="flex flex-wrap items-start gap-3">
      {allowed.map((target) => {
        const blocked = target === "submitted" && requiresDocument && !hasDocument;
        return (
          <TransitionButton
            key={target}
            id={id}
            target={target}
            version={version}
            label={dict.status[target]}
            disabled={blocked}
            blockedHint={blocked ? dict.detail.submitBlocked : undefined}
          />
        );
      })}
    </div>
  );
}
