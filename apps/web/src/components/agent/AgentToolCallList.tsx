import type { AgentToolCall } from "../../types";
import { Badge } from "../../ui/badge";
import { useI18n } from "../../i18n";
import { compactPayload } from "./agentEvidenceUtils";

export function AgentToolCallList({ toolCalls }: { toolCalls: AgentToolCall[] }) {
  const { t } = useI18n();
  if (!toolCalls.length) {
    return <p className="text-sm text-slate-500">{t("organizer.agentEvidence.partialEvidence")}</p>;
  }
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-ink">{t("organizer.agentEvidence.toolEvidence")}</h3>
      {toolCalls.map((call) => (
        <div key={call.tool_call_id} className="rounded-lg border border-slate-200 bg-white p-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-medium text-ink">{call.tool_name}</span>
            <Badge variant={call.status === "success" ? "success" : "warning"}>{call.status}</Badge>
          </div>
          <div className="mt-2 grid gap-2 text-xs text-slate-600 md:grid-cols-2">
            <code className="rounded bg-slate-100 p-2">{compactPayload(call.input_payload)}</code>
            <code className="rounded bg-slate-100 p-2">{compactPayload(call.output_payload)}</code>
          </div>
        </div>
      ))}
    </div>
  );
}
