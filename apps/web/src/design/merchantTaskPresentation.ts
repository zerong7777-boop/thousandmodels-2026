import type { MerchantTask } from "../types";

export function merchantContingencyInstruction(task: MerchantTask): string {
  return task["fallback_instruction"];
}
