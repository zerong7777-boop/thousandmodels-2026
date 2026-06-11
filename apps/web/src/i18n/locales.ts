import { locales, type Locale } from "./types";

export { locales };

export const defaultLocale: Locale = "zh-Hans";
export const fallbackLocale: Locale = "en";
export const localeStorageKey = "zhiyin.locale";

export const localeLabels: Record<Locale, string> = {
  "zh-Hans": "简体中文",
  "zh-Hant": "繁體中文",
  en: "English"
};

export const localeShortLabels: Record<Locale, string> = {
  "zh-Hans": "简",
  "zh-Hant": "繁",
  en: "EN"
};

export function isLocale(value: string | null | undefined): value is Locale {
  return typeof value === "string" && (locales as readonly string[]).includes(value);
}
