import { en } from "./en";
import { zhHans } from "./zh-Hans";
import { zhHant } from "./zh-Hant";
import type { Locale, TranslationDictionary } from "../types";

export const dictionaries: Record<Locale, TranslationDictionary> = {
  "zh-Hans": zhHans,
  "zh-Hant": zhHant,
  en
};
