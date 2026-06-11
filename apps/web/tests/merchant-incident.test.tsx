import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "../src/App";
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
  expect(await screen.findByRole("button", { name: /sold out/i })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /sold out/i }));
  await waitFor(() => expect(fetch).toHaveBeenCalled());
});
