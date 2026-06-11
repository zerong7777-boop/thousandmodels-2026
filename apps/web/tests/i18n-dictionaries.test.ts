import { describe, expect, test } from "vitest";
import { dictionaries, fallbackLocale, isLocale, locales } from "../src/i18n";

describe("i18n dictionaries", () => {
  test("supports exactly zh-Hans zh-Hant and en with zh-Hans default and en fallback", () => {
    expect(locales).toEqual(["zh-Hans", "zh-Hant", "en"]);
    expect(fallbackLocale).toBe("en");
    expect(isLocale("zh-Hans")).toBe(true);
    expect(isLocale("zh-Hant")).toBe(true);
    expect(isLocale("en")).toBe(true);
    expect(isLocale("fr")).toBe(false);
  });

  test("all supported dictionaries expose the same required keys", () => {
    const englishKeys = Object.keys(dictionaries.en).sort();
    for (const locale of locales) {
      expect(Object.keys(dictionaries[locale]).sort()).toEqual(englishKeys);
    }

    expect(englishKeys).toContain("auth.signIn");
    expect(englishKeys).toContain("shell.nav.dashboard");
    expect(englishKeys).toContain("public.event.liveUpdate");
    expect(englishKeys).toContain("merchant.status.reportSoldOut");
  });
});
