import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false
  })
});

Object.defineProperty(window, "ResizeObserver", {
  writable: true,
  value: ResizeObserverMock
});

afterEach(() => {
  document.head
    .querySelectorAll("style[data-css-hash], style[data-token-hash], style[data-rc-order], style[data-ant-cssinjs-cache-path]")
    .forEach((node) => node.remove());
});
