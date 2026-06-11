import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(__dirname, "..");

const productShellFiles = [
  "src/layout/ProductShell.tsx",
  "src/layout/OrganizerProductShell.tsx",
  "src/layout/MerchantProductShell.tsx",
  "src/layout/TouristProductShell.tsx"
];

test("product shell files exist as the accepted role shell path", () => {
  for (const file of productShellFiles) {
    expect(existsSync(resolve(root, file))).toBe(true);
  }
});

test("accepted product shell files do not use Ant Design layout primitives", () => {
  for (const file of productShellFiles) {
    const source = readFileSync(resolve(root, file), "utf8");
    expect(source).not.toContain("from \"antd\"");
    expect(source).not.toContain("Layout");
    expect(source).not.toContain("Sider");
    expect(source).not.toContain("Menu");
  }
});

test("App uses product shells instead of legacy role shells", () => {
  const source = readFileSync(resolve(root, "src/App.tsx"), "utf8");
  expect(source).toContain("OrganizerProductShell");
  expect(source).toContain("MerchantProductShell");
  expect(source).toContain("TouristProductShell");
  expect(source).not.toContain("./shells/OrganizerShell");
  expect(source).not.toContain("./shells/MerchantShell");
  expect(source).not.toContain("./shells/UserShell");
});
