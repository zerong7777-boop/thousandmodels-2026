import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { I18nProvider, LanguageSwitcher, useI18n } from "../src/i18n";

function Probe() {
  const { locale, t } = useI18n();
  return (
    <div>
      <p data-testid="locale">{locale}</p>
      <p data-testid="sign-in">{t("auth.signIn")}</p>
      <p data-testid="fallback">{t("test.missingInChinese")}</p>
      <p data-testid="interpolation">{t("test.interpolation", { count: 2 })}</p>
      <LanguageSwitcher />
    </div>
  );
}

beforeEach(() => {
  localStorage.clear();
});

describe("I18nProvider", () => {
  test("defaults to Simplified Chinese and persists language choice", () => {
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>
    );

    expect(screen.getByTestId("locale")).toHaveTextContent("zh-Hans");
    expect(screen.getByTestId("sign-in")).toHaveTextContent("登录");

    fireEvent.click(screen.getByRole("button", { name: /繁體中文/i }));
    expect(screen.getByTestId("locale")).toHaveTextContent("zh-Hant");
    expect(localStorage.getItem("zhiyin.locale")).toBe("zh-Hant");
  });

  test("falls back to English for missing selected-locale keys and interpolates params", () => {
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>
    );

    expect(screen.getByTestId("fallback")).toHaveTextContent("English fallback copy");
    expect(screen.getByTestId("interpolation")).toHaveTextContent("2 个站点");
  });

  test("ignores invalid stored locale", () => {
    localStorage.setItem("zhiyin.locale", "fr");
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>
    );

    expect(screen.getByTestId("locale")).toHaveTextContent("zh-Hans");
  });

  test("throws a clear error when useI18n is rendered outside provider", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => undefined);
    expect(() => render(<Probe />)).toThrow(/useI18n must be used inside I18nProvider/);
    spy.mockRestore();
  });
});
