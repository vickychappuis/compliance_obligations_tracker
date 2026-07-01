import { notFound } from "next/navigation";

import { ObligationForm } from "@/components/obligations/ObligationForm";
import { ApiError, getObligation } from "@/lib/api";
import { updateObligationAction } from "@/lib/actions/obligations";
import { getDictionary } from "@/lib/i18n";

export default async function EditObligationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const dict = await getDictionary();

  let obligation;
  try {
    obligation = await getObligation(id);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">{dict.form.editTitle}</h1>
      <ObligationForm
        dict={dict}
        action={updateObligationAction.bind(null, id)}
        submitLabel={dict.form.save}
        includeTaxId
        taxIdOptional
        taxIdPlaceholder={obligation.company_tax_id}
        cancelHref={`/obligations/${id}`}
        defaultValues={{
          title: obligation.title,
          description: obligation.description,
          type: obligation.type,
          due_date: obligation.due_date,
          owner: obligation.owner,
          requires_document: obligation.requires_document,
        }}
      />
    </div>
  );
}
