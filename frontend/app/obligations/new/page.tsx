import { ObligationForm } from "@/components/obligations/ObligationForm";
import { createObligationAction } from "@/lib/actions/obligations";
import { getDictionary } from "@/lib/i18n";

export default async function NewObligationPage() {
  const dict = await getDictionary();
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">{dict.form.createTitle}</h1>
      <ObligationForm
        dict={dict}
        action={createObligationAction}
        submitLabel={dict.form.create}
        includeTaxId
        cancelHref="/"
      />
    </div>
  );
}
