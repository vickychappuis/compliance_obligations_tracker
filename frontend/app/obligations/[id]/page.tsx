import Link from "next/link";
import { notFound } from "next/navigation";

import { AttachDocumentForm } from "@/components/obligations/AttachDocumentForm";
import { AuditHistory } from "@/components/obligations/AuditHistory";
import { RemoveDocumentButton } from "@/components/obligations/RemoveDocumentButton";
import { StatusBadge } from "@/components/obligations/StatusBadge";
import { TransitionControls } from "@/components/obligations/TransitionControls";
import { Badge, Card } from "@/components/ui";
import { ApiError, getDocumentUrl, getObligation } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { getDictionary, getLocale } from "@/lib/i18n";

export default async function ObligationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [dict, locale] = await Promise.all([getDictionary(), getLocale()]);

  let ob;
  try {
    ob = await getObligation(id);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  const documentUrls = new Map<string, string>(
    (
      await Promise.all(
        ob.documents.map(async (doc) => {
          try {
            const { url } = await getDocumentUrl(id, doc.id);
            return [doc.id, url] as const;
          } catch {
            return null;
          }
        }),
      )
    ).filter((entry): entry is readonly [string, string] => entry !== null),
  );

  return (
    <div className="space-y-6">
      <Link href="/" className="text-sm text-slate-500 hover:text-slate-900">
        ← {dict.detail.back}
      </Link>

      <div className="space-y-2">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold">{ob.title}</h1>
          <StatusBadge status={ob.status} label={dict.status[ob.status]} />
          {ob.overdue && <Badge tone="danger">{dict.list.overdueBadge}</Badge>}
        </div>
        {ob.description && <p className="text-slate-600">{ob.description}</p>}
      </div>

      <Card>
        <div className="mb-3 flex items-center justify-between gap-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            {dict.detail.fields}
          </h2>
          <Link
            href={`/obligations/${id}/edit`}
            className="inline-flex items-center justify-center rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-900 hover:bg-slate-100"
          >
            {dict.detail.edit}
          </Link>
        </div>
        <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <Row label={dict.detail.type} value={dict.type[ob.type]} />
          <Row label={dict.detail.owner} value={ob.owner} />
          <Row label={dict.detail.dueDate} value={formatDate(ob.due_date, locale)} />
          <Row label={dict.detail.taxId} value={ob.company_tax_id} mono />
          <Row
            label={dict.detail.requiresDocument}
            value={ob.requires_document ? dict.common.yes : dict.common.no}
          />
        </dl>
      </Card>

      <Card>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          {dict.detail.document}
        </h2>
        {ob.documents.length > 0 ? (
          <ul className="mb-4 space-y-1 text-sm text-slate-700">
            {ob.documents.map((doc) => {
              const url = documentUrls.get(doc.id);
              return (
                <li key={doc.id} className="flex items-center gap-2">
                  <span>📎 {doc.filename}</span>
                  {url && (
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-medium text-slate-500 hover:text-slate-900 hover:underline"
                    >
                      {dict.detail.download}
                    </a>
                  )}
                  <RemoveDocumentButton id={id} documentId={doc.id} dict={dict} />
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="mb-4 text-sm text-slate-500">{dict.detail.noDocument}</p>
        )}
        <AttachDocumentForm id={id} dict={dict} />
      </Card>

      <Card>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          {dict.detail.transitions}
        </h2>
        <TransitionControls
          id={id}
          status={ob.status}
          version={ob.version}
          allowed={ob.allowed_transitions}
          requiresDocument={ob.requires_document}
          hasDocument={ob.has_document}
          dict={dict}
        />
      </Card>

      <Card>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          {dict.detail.auditHistory}
        </h2>
        <AuditHistory entries={ob.audit} dict={dict} locale={locale} />
      </Card>
    </div>
  );
}

function Row({
  label,
  value,
  mono,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-slate-400">{label}</dt>
      <dd className={mono ? "font-mono" : ""}>{value}</dd>
    </div>
  );
}
