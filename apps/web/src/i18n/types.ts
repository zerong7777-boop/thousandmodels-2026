export const locales = ["zh-Hans", "zh-Hant", "en"] as const;

export type Locale = (typeof locales)[number];
export type TranslationValue = string;
export type TranslationParams = Record<string, string | number | boolean | null | undefined>;
export type TranslationDictionary = Record<string, TranslationValue>;
export type Translator = (key: string, params?: TranslationParams) => string;

export interface I18nContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: Translator;
}
