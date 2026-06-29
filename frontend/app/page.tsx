import { Filters } from "@/components/obligations/Filters";
import { KpiCards } from "@/components/obligations/KpiCards";
import { ObligationsTable } from "@/components/obligations/ObligationsTable";
import { getSummary, listObligations } from "@/lib/api";
import { getDictionary, getLocale } from "@/lib/i18n";
import type { ObligationFilters, ObligationType, Status } from "@/lib/types";

type SearchParams = Record<string, string | string[] | undefined>;

function one(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function parseFilters(params: SearchParams): ObligationFilters {
  const status = one(params.status);
  const type = one(params.type);
  const owner = one(params.owner);
  return {
    status: status ? (status as Status) : undefined,
    type: type ? (type as ObligationType) : undefined,
    owner: owner || undefined,
    overdue: one(params.overdue) === "true" ? true : undefined,
  };
}

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const [dict, locale, params] = await Promise.all([
    getDictionary(),
    getLocale(),
    searchParams,
  ]);
  const filters = parseFilters(params);

  let content;
  try {
    const [summary, items] = await Promise.all([
      getSummary(),
      listObligations(filters),
    ]);
    content = (
      <>
        <KpiCards summary={summary} dict={dict} />
        <Filters dict={dict} current={filters} />
        <ObligationsTable items={items} dict={dict} locale={locale} />
      </>
    );
  } catch {
    content = (
      <p className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
        {dict.common.error}
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">{dict.nav.dashboard}</h1>
      {content}
    </div>
  );
}
