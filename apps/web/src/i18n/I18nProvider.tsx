import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { dictionaries } from "./dictionaries";
import { defaultLocale, fallbackLocale, isLocale, localeStorageKey } from "./locales";
import type { I18nContextValue, Locale, TranslationParams } from "./types";

const I18nContext = createContext<I18nContextValue | null>(null);

function readStoredLocale(): Locale {
  if (typeof window === "undefined") {
    return defaultLocale;
  }
  try {
    const stored = window.localStorage.getItem(localeStorageKey);
    return isLocale(stored) ? stored : defaultLocale;
  } catch {
    return defaultLocale;
  }
}

function interpolate(value: string, params?: TranslationParams): string {
  if (!params) {
    return value;
  }
  return value.replace(/\{(\w+)\}/g, (match, key: string) => {
    const next = params[key];
    return next === undefined || next === null ? "" : String(next);
  });
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => readStoredLocale());

  const setLocale = useCallback((nextLocale: Locale) => {
    setLocaleState(nextLocale);
    try {
      window.localStorage.setItem(localeStorageKey, nextLocale);
    } catch {
      // Locale persistence is a UI preference; rendering should continue if storage is unavailable.
    }
  }, []);

  const t = useCallback(
    (key: string, params?: TranslationParams) => {
      const selected = dictionaries[locale]?.[key];
      const fallback = dictionaries[fallbackLocale]?.[key];
      return interpolate(selected || fallback || key, params);
    },
    [locale]
  );

  const value = useMemo<I18nContextValue>(() => ({ locale, setLocale, t }), [locale, setLocale, t]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used inside I18nProvider");
  }
  return context;
}
