import { render, screen } from "@testing-library/react";
import App from "../src/App";
import { zhHans as zh } from "../src/i18n/dictionaries/zh-Hans";
import { mockAppFetch } from "./authTestUtils";

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal("fetch", mockAppFetch(null));
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("renders backend-backed sign in by default", async () => {
  render(<App />);
  expect(await screen.findByRole("heading", { name: zh["common.brand"] })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: zh["auth.productAccess"] })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /登\s*录/ })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: new RegExp(zh["auth.organizerDemo"]) })).toBeInTheDocument();
  expect(screen.queryByText(zh["merchant.status.reportSoldOut"])).not.toBeInTheDocument();
  expect(screen.queryByText(/^Tourist H5$/i)).not.toBeInTheDocument();
});
