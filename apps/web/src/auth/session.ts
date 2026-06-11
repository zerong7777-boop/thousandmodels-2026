export type DemoRole = "organizer" | "merchant" | "tourist";

export interface DemoSession {
  role: DemoRole;
  actor_id: string;
  display_name: string;
  merchant_id?: string;
}

export const DEMO_SESSION_KEY = "zhiyin.demo.session";

export const DEMO_ACCOUNTS: Record<DemoRole, DemoSession> = {
  organizer: {
    role: "organizer",
    actor_id: "org-demo",
    display_name: "Organizer demo"
  },
  merchant: {
    role: "merchant",
    actor_id: "merchant-m001",
    display_name: "Merchant m001",
    merchant_id: "m001"
  },
  tourist: {
    role: "tourist",
    actor_id: "tourist-demo",
    display_name: "Tourist demo"
  }
};

function isDemoRole(role: unknown): role is DemoRole {
  return role === "organizer" || role === "merchant" || role === "tourist";
}

export function getDemoSession(): DemoSession | null {
  const raw = localStorage.getItem(DEMO_SESSION_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as Partial<DemoSession>;
    if (isDemoRole(parsed.role) && parsed.actor_id && parsed.display_name) {
      return {
        role: parsed.role,
        actor_id: String(parsed.actor_id),
        display_name: String(parsed.display_name),
        merchant_id: parsed.merchant_id ? String(parsed.merchant_id) : undefined
      };
    }
  } catch {
    localStorage.removeItem(DEMO_SESSION_KEY);
  }

  return null;
}

export function setDemoSession(session: DemoSession): void {
  localStorage.setItem(DEMO_SESSION_KEY, JSON.stringify(session));
}

export function clearDemoSession(): void {
  localStorage.removeItem(DEMO_SESSION_KEY);
}
