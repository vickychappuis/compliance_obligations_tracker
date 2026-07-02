"use client";

import type { ButtonHTMLAttributes } from "react";
import { useFormStatus } from "react-dom";

import { Button } from "@/components/ui";

type Variant = "primary" | "secondary" | "ghost" | "danger";

export function SubmitButton({
  children,
  variant = "primary",
  disabled,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  const { pending } = useFormStatus();
  return (
    <Button
      type="submit"
      variant={variant}
      disabled={disabled || pending}
      aria-busy={pending}
      {...props}
    >
      {children}
      {pending && (
        <span className="ml-2 animate-pulse" aria-hidden>
          …
        </span>
      )}
    </Button>
  );
}
