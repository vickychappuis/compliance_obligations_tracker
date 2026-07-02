import { setLocale } from "@/lib/actions/locale";
import { locales, type Locale } from "@/lib/i18n/config";
import { cn } from "@/lib/cn";

export function LocaleSwitcher({ current }: { current: Locale }) {
  return (
    <div className="flex items-center gap-1" aria-label="Language">
      {locales.map((locale) => (
        <form key={locale} action={setLocale.bind(null, locale)}>
          <button
            type="submit"
            aria-current={locale === current}
            className={cn(
              "rounded px-2 py-1 text-xs font-medium uppercase",
              locale === current
                ? "bg-slate-900 text-white"
                : "text-slate-500 hover:bg-slate-200",
            )}
          >
            {locale}
          </button>
        </form>
      ))}
    </div>
  );
}
