import Link from "next/link";

import { getDictionary } from "@/lib/i18n";

export default async function NotFound() {
  const dict = await getDictionary();
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{dict.notFound.title}</h1>
      <p className="text-slate-600">{dict.notFound.description}</p>
      <Link
        href="/"
        className="inline-flex items-center justify-center rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700"
      >
        {dict.notFound.back}
      </Link>
    </div>
  );
}
