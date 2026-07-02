"use client";

import { useActionState } from "react";

import { SubmitButton } from "@/components/ui/submit-button";
import { transitionAction } from "@/lib/actions/obligations";
import type { Dictionary } from "@/lib/i18n";
import type { Status } from "@/lib/types";

const STATUS_ORDER: Record<Status, number> = {
  pending: 0,
  in_progress: 1,
  submitted: 2,
  done: 3,
};

function transitionLabel(
  from: Status,
  to: Status,
  dict: Dictionary,
): string {
  const t = dict.transition;
  if (to === "submitted") return t.to_submitted;
  if (to === "done") return t.to_done;
  if (to === "pending") return t.back_to_pending;
  if (from === "pending") return t.to_in_progress;
  if (from === "done") return t.reopen;
  return t.back_to_in_progress;
}

function TransitionButton({
  id,
  target,
  version,
  label,
  disabled,
  primary,
  blockedHint,
  confirmMessage,
}: {
  id: string;
  target: Status;
  version: number;
  label: string;
  disabled: boolean;
  primary: boolean;
  blockedHint?: string;
  confirmMessage?: string;
}) {
  const [state, formAction] = useActionState(transitionAction.bind(null, id), {});

  return (
    <div className="space-y-1">
      <form action={formAction}>
        <input type="hidden" name="target_status" value={target} />
        <input type="hidden" name="expected_version" value={version} />
        <SubmitButton
          disabled={disabled}
          variant={primary ? "primary" : "secondary"}
          onClick={
            confirmMessage
              ? (event) => {
                  if (!window.confirm(confirmMessage)) event.preventDefault();
                }
              : undefined
          }
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
  status,
  version,
  allowed,
  canSubmit,
  dict,
}: {
  id: string;
  status: Status;
  version: number;
  allowed: Status[];
  canSubmit: boolean;
  dict: Dictionary;
}) {
  if (allowed.length === 0) {
    return <p className="text-sm text-slate-500">{dict.detail.noTransitions}</p>;
  }

  return (
    <div className="flex flex-wrap items-start gap-3">
      {allowed.map((target) => {
        const blocked = target === "submitted" && !canSubmit;
        const isForward = STATUS_ORDER[target] > STATUS_ORDER[status];
        return (
          <TransitionButton
            key={target}
            id={id}
            target={target}
            version={version}
            label={transitionLabel(status, target, dict)}
            disabled={blocked}
            primary={isForward}
            blockedHint={blocked ? dict.detail.submitBlocked : undefined}
            confirmMessage={!isForward ? dict.transition.confirm : undefined}
          />
        );
      })}
    </div>
  );
}
