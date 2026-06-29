import type { Locale } from "./i18n/config";

export function formatDate(iso: string, locale: Locale): string {
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(new Date(iso));
}

export function formatDateTime(iso: string, locale: Locale): string {
  return new Intl.DateTimeFormat(locale, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(iso));
}
