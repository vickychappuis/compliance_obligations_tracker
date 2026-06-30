"use client";

import { Button } from "@/components/ui";
import { en } from "@/lib/i18n/en";
import { es } from "@/lib/i18n/es";

function clientDict() {
  if (typeof document !== "undefined") {
    const match = document.cookie.match(/(?:^|;\s*)locale=([^;]+)/);
    if (match && match[1] === "es") return es;
  }
  return en;
}

export default function Error({ reset }: { error: Error; reset: () => void }) {
  const dict = clientDict();
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{dict.common.errorTitle}</h1>
      <p className="text-slate-600">{dict.common.errorBody}</p>
      <Button onClick={() => reset()}>{dict.common.retry}</Button>
    </div>
  );
}
