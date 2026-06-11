import { Globe2 } from "lucide-react";
import { Button } from "../ui/button";
import { localeLabels, localeShortLabels, locales } from "./locales";
import { useI18n } from "./I18nProvider";

export function LanguageSwitcher({ compact = false }: { compact?: boolean }) {
  const { locale, setLocale, t } = useI18n();

  return (
    <div aria-label={t("common.language")} className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white p-1">
      {!compact ? <Globe2 aria-hidden="true" className="ml-1 text-slate-500" size={14} /> : null}
      {locales.map((item) => {
        const selected = item === locale;
        return (
          <Button
            aria-pressed={selected}
            aria-label={localeLabels[item]}
            className={selected ? "bg-slate-900 text-white hover:bg-slate-800" : "h-8 px-2"}
            key={item}
            onClick={() => setLocale(item)}
            size="sm"
            type="button"
            variant={selected ? "primary" : "ghost"}
          >
            {compact ? localeShortLabels[item] : localeLabels[item]}
          </Button>
        );
      })}
    </div>
  );
}
