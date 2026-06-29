import { getDictionary } from "@/lib/i18n";

export default async function HomePage() {
  const dict = await getDictionary();
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold">{dict.nav.dashboard}</h1>
      <p className="text-slate-600">{dict.common.loading}</p>
    </div>
  );
}
