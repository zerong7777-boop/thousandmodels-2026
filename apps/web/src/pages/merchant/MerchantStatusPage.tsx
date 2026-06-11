import { useState } from "react";
import { CheckCircle2, PauseCircle, PackageMinus, PackageX, Users } from "lucide-react";
import { api } from "../../api";
import type { MerchantRuntimeState } from "../../types";
import { Badge } from "../../ui/badge";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { Input } from "../../ui/input";
import { MerchantQuickAction, ProductPageHeader, StatusPill } from "../../components/product";
import { useAsyncData } from "../productUtils";

type Inventory = MerchantRuntimeState["inventory_status"];
type Queue = MerchantRuntimeState["queue_status"];

export function MerchantStatusPage({ merchantId = "m001" }: { merchantId?: string }) {
  const { data: workbench } = useAsyncData(() => api.getMerchantWorkbench(merchantId), { tasks: [] });
  const runtime = workbench.runtime_state;
  const [inventoryStatus, setInventoryStatus] = useState<Inventory>("normal");
  const [queueStatus, setQueueStatus] = useState<Queue>("normal");
  const [availableForVisitors, setAvailableForVisitors] = useState(true);
  const [temporaryNote, setTemporaryNote] = useState("");
  const [lastResult, setLastResult] = useState<string | null>(null);

  const submitStatus = async (override?: Partial<MerchantRuntimeState>) => {
    const payload = {
      inventory_status: override?.inventory_status ?? inventoryStatus,
      queue_status: override?.queue_status ?? queueStatus,
      available_for_visitors: override?.available_for_visitors ?? availableForVisitors,
      temporary_note: override?.temporary_note ?? temporaryNote
    };
    const result = await api.updateRuntimeState(merchantId, payload);
    setLastResult(result.incident || payload.inventory_status === "sold_out" ? "Organizer review requested." : "Status updated.");
  };

  const reportSoldOut = async () => {
    setInventoryStatus("sold_out");
    setAvailableForVisitors(false);
    await submitStatus({ inventory_status: "sold_out", available_for_visitors: false, temporary_note: "Sold out" });
  };

  const quickUpdate = async (override: Partial<MerchantRuntimeState>) => {
    if (override.inventory_status) setInventoryStatus(override.inventory_status);
    if (override.queue_status) setQueueStatus(override.queue_status);
    if (override.available_for_visitors !== undefined) setAvailableForVisitors(override.available_for_visitors);
    if (override.temporary_note !== undefined) setTemporaryNote(override.temporary_note);
    await submitStatus(override);
  };

  return (
    <div className="space-y-4">
      <ProductPageHeader
        eyebrow="Report live status"
        title="Visitor readiness"
        description="Tap the current operating state first. The organizer sees high-risk updates immediately and can recover the route."
        meta={[workbench.merchant?.name ?? "Merchant m001", `${workbench.tasks?.length ?? 0} assigned task`, "Local demo account"]}
        status={runtime?.available_for_visitors === false ? "paused" : "open"}
        tone="merchant"
      />

      <Card>
        <CardHeader>
          <CardTitle>Current status</CardTitle>
          <CardDescription>Last known state from the event runtime.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <StatusItem label="Inventory" value={runtime?.inventory_status ?? "normal"} />
          <StatusItem label="Queue" value={runtime?.queue_status ?? "normal"} />
          <StatusItem label="Visitors" value={runtime?.available_for_visitors === false ? "paused" : "open"} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <CardTitle>Quick actions</CardTitle>
              <CardDescription>Use these during service. Each action sends a real runtime update.</CardDescription>
            </div>
            {lastResult ? <StatusPill tone={lastResult.includes("review") ? "warning" : "success"}>{lastResult}</StatusPill> : null}
          </div>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <MerchantQuickAction
            detail="Stock normal, queue normal, visitors may continue."
            icon={<CheckCircle2 size={18} />}
            label="Accept visitors"
            onClick={() =>
              void quickUpdate({
                inventory_status: "normal",
                queue_status: "normal",
                available_for_visitors: true,
                temporary_note: ""
              })
            }
            tone="accept"
          />
          <MerchantQuickAction
            detail="Temporarily stop new arrivals while keeping the task active."
            icon={<PauseCircle size={18} />}
            label="Pause visitors"
            onClick={() => void quickUpdate({ available_for_visitors: false, temporary_note: "Paused by merchant" })}
            tone="pause"
          />
          <MerchantQuickAction
            detail="Warn the organizer before inventory runs out."
            icon={<PackageMinus size={18} />}
            label="Report low stock"
            onClick={() => void quickUpdate({ inventory_status: "low", temporary_note: "Low stock" })}
            tone="warning"
          />
          <MerchantQuickAction
            detail="Trigger organizer recovery review for this stop."
            icon={<PackageX size={18} />}
            label="Report sold out"
            onClick={() => void reportSoldOut()}
            tone="danger"
          />
          <MerchantQuickAction
            detail="Mark queue pressure high while still serving visitors."
            icon={<Users size={18} />}
            label="Queue busy"
            onClick={() => void quickUpdate({ queue_status: "busy", temporary_note: "Queue busy" })}
            tone="warning"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Advanced report</CardTitle>
          <CardDescription>Fine tune the state if a quick action does not match the situation.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <label className="space-y-1 text-sm">
              <span className="font-medium">Inventory</span>
              <select
                className="h-10 w-full rounded-md border border-slate-200 bg-white px-3"
                value={inventoryStatus}
                onChange={(event) => setInventoryStatus(event.target.value as Inventory)}
              >
                <option value="normal">Normal</option>
                <option value="low">Low</option>
                <option value="sold_out">Sold out</option>
              </select>
            </label>
            <label className="space-y-1 text-sm">
              <span className="font-medium">Queue</span>
              <select
                className="h-10 w-full rounded-md border border-slate-200 bg-white px-3"
                value={queueStatus}
                onChange={(event) => setQueueStatus(event.target.value as Queue)}
              >
                <option value="normal">Normal</option>
                <option value="busy">Busy</option>
                <option value="overloaded">Overloaded</option>
              </select>
            </label>
            <label className="flex items-center gap-2 pt-7 text-sm">
              <input
                type="checkbox"
                checked={availableForVisitors}
                onChange={(event) => setAvailableForVisitors(event.target.checked)}
              />
              Accept visitors
            </label>
          </div>
          <label className="space-y-1 text-sm">
            <span className="font-medium">Temporary note</span>
            <Input value={temporaryNote} onChange={(event) => setTemporaryNote(event.target.value)} />
          </label>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => void submitStatus()}>Submit status</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-slate-500">{label}</div>
      <Badge variant={value === "sold_out" || value === "paused" ? "warning" : "success"}>{value}</Badge>
    </div>
  );
}
