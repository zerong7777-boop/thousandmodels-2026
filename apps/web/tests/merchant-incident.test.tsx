import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
import { zhHans as zh } from "../src/i18n/dictionaries/zh-Hans";
import { mockAppFetch } from "./authTestUtils";

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("merchant status page exposes runtime update controls", async () => {
  localStorage.clear();
  vi.stubGlobal(
    "fetch",
    mockAppFetch("merchant", () => ({
      merchant: { merchant_id: "m001", name: "Merchant m001", type: "food" },
      tasks: [],
      runtime_state: {
        merchant_id: "m001",
        inventory_status: "normal",
        queue_status: "normal",
        available_for_visitors: true,
        temporary_note: "",
        updated_at: "2026-06-10T00:00:00Z"
      }
    }))
  );
  window.history.pushState({}, "", "/merchant/events/demo-night-tour/status");
  render(<App />);
  expect(await screen.findByTestId("merchant-shell")).toBeInTheDocument();
  expect(await screen.findByRole("button", { name: new RegExp(`^${zh["merchant.status.reportSoldOut"]}`) })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: new RegExp(`^${zh["merchant.status.reportSoldOut"]}`) }));
  await waitFor(() =>
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/merchants/m001/runtime-state"),
      expect.objectContaining({
        body: expect.stringContaining("\"inventory_status\":\"sold_out\"")
      })
    )
  );
});
