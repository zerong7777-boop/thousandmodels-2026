import { render, screen } from "@testing-library/react";
import App from "../src/App";
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
  expect(await screen.findByRole("heading", { name: /zhiyin haojiang/i })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: /product access/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /organizer demo/i })).toBeInTheDocument();
  expect(screen.queryByText(/report sold out/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/^Tourist H5$/i)).not.toBeInTheDocument();
});
