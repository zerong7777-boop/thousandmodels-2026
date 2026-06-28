import { useState, type FormEvent } from "react";
import { api } from "../../api";
import { useI18n } from "../../i18n";
import type { EventCreateRequest, EventSummary } from "../../types";
import { Button } from "../../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../ui/card";
import { Input } from "../../ui/input";
import { cn } from "../../ui/utils";

type EventCreateFormState = {
  event_id: string;
  title: string;
  area: string;
  date: string;
  time_window: string;
  budget_mop: string;
  target_audience: string;
  event_goal: string;
  theme_preferences: string;
  constraints: string;
  priority_rules: string;
};

const emptyForm: EventCreateFormState = {
  event_id: "",
  title: "",
  area: "",
  date: "",
  time_window: "",
  budget_mop: "",
  target_audience: "",
  event_goal: "",
  theme_preferences: "",
  constraints: "",
  priority_rules: ""
};

export function parseListField(value: string): string[] {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function messageFromError(error: unknown): string | null {
  const raw = error instanceof Error ? error.message : typeof error === "string" ? error : "";
  if (!raw.trim()) return null;

  try {
    const parsed = JSON.parse(raw) as { detail?: unknown; message?: unknown };
    if (typeof parsed.detail === "string") return parsed.detail;
    if (typeof parsed.message === "string") return parsed.message;
  } catch {
    // Non-JSON backend errors are already displayable text.
  }

  return raw;
}

function TextAreaField({
  id,
  label,
  value,
  onChange,
  placeholder
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <label className="space-y-1 text-sm font-medium text-slate-700" htmlFor={id}>
      <span>{label}</span>
      <textarea
        id={id}
        value={value}
        placeholder={placeholder}
        rows={3}
        onChange={(event) => onChange(event.target.value)}
        className={cn(
          "w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none transition",
          "focus:border-harbor focus:ring-2 focus:ring-teal-100 disabled:cursor-not-allowed disabled:opacity-60"
        )}
      />
    </label>
  );
}

export function EventCreatePanel({ onCreated }: { onCreated: (event: EventSummary) => void }) {
  const { t } = useI18n();
  const [form, setForm] = useState<EventCreateFormState>(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateField = (field: keyof EventCreateFormState, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const buildPayload = (): EventCreateRequest | null => {
    const budget = Number(form.budget_mop);
    const targetAudience = parseListField(form.target_audience);
    const themePreferences = parseListField(form.theme_preferences);
    const constraints = parseListField(form.constraints);
    const priorityRules = parseListField(form.priority_rules);

    if (
      !form.title.trim() ||
      !form.area.trim() ||
      !form.date.trim() ||
      !form.time_window.trim() ||
      !form.event_goal.trim() ||
      !Number.isFinite(budget) ||
      budget <= 0 ||
      !targetAudience.length ||
      !themePreferences.length ||
      !constraints.length ||
      !priorityRules.length
    ) {
      return null;
    }

    return {
      ...(form.event_id.trim() ? { event_id: form.event_id.trim() } : {}),
      title: form.title.trim(),
      area: form.area.trim(),
      date: form.date.trim(),
      time_window: form.time_window.trim(),
      budget_mop: budget,
      target_audience: targetAudience,
      event_goal: form.event_goal.trim(),
      theme_preferences: themePreferences,
      constraints,
      priority_rules: priorityRules
    };
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    const payload = buildPayload();
    if (!payload) {
      setError(t("organizer.events.form.validationError"));
      return;
    }

    setSubmitting(true);
    try {
      const created = await api.createEvent(payload);
      setForm(emptyForm);
      onCreated(created);
    } catch (createError) {
      setError(messageFromError(createError) ?? t("organizer.events.form.createError"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("organizer.events.createTitle")}</CardTitle>
        <CardDescription>{t("organizer.events.createDescription")}</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={(event) => void submit(event)}>
          {error ? (
            <div role="alert" className="rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-900">
              {error}
            </div>
          ) : null}
          <div className="grid gap-3 md:grid-cols-2">
            <label className="space-y-1 text-sm font-medium text-slate-700" htmlFor="event-create-id">
              <span>{t("organizer.events.form.eventId")}</span>
              <Input
                id="event-create-id"
                value={form.event_id}
                onChange={(event) => updateField("event_id", event.target.value)}
              />
            </label>
            <label className="space-y-1 text-sm font-medium text-slate-700" htmlFor="event-create-title">
              <span>{t("organizer.events.form.title")}</span>
              <Input
                id="event-create-title"
                value={form.title}
                onChange={(event) => updateField("title", event.target.value)}
              />
            </label>
            <label className="space-y-1 text-sm font-medium text-slate-700" htmlFor="event-create-area">
              <span>{t("organizer.events.form.area")}</span>
              <Input
                id="event-create-area"
                value={form.area}
                onChange={(event) => updateField("area", event.target.value)}
              />
            </label>
            <label className="space-y-1 text-sm font-medium text-slate-700" htmlFor="event-create-date">
              <span>{t("organizer.events.form.date")}</span>
              <Input
                id="event-create-date"
                type="date"
                value={form.date}
                onChange={(event) => updateField("date", event.target.value)}
              />
            </label>
            <label className="space-y-1 text-sm font-medium text-slate-700" htmlFor="event-create-time-window">
              <span>{t("organizer.events.form.timeWindow")}</span>
              <Input
                id="event-create-time-window"
                value={form.time_window}
                placeholder="15:00-20:00"
                onChange={(event) => updateField("time_window", event.target.value)}
              />
            </label>
            <label className="space-y-1 text-sm font-medium text-slate-700" htmlFor="event-create-budget">
              <span>{t("organizer.events.form.budget")}</span>
              <Input
                id="event-create-budget"
                type="number"
                min="1"
                value={form.budget_mop}
                onChange={(event) => updateField("budget_mop", event.target.value)}
              />
            </label>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextAreaField
              id="event-create-target-audience"
              label={t("organizer.events.form.targetAudience")}
              value={form.target_audience}
              onChange={(value) => updateField("target_audience", value)}
            />
            <TextAreaField
              id="event-create-theme-preferences"
              label={t("organizer.events.form.themePreferences")}
              value={form.theme_preferences}
              onChange={(value) => updateField("theme_preferences", value)}
            />
            <TextAreaField
              id="event-create-constraints"
              label={t("organizer.events.form.constraints")}
              value={form.constraints}
              onChange={(value) => updateField("constraints", value)}
            />
            <TextAreaField
              id="event-create-priority-rules"
              label={t("organizer.events.form.priorityRules")}
              value={form.priority_rules}
              onChange={(value) => updateField("priority_rules", value)}
            />
          </div>
          <TextAreaField
            id="event-create-goal"
            label={t("organizer.events.form.eventGoal")}
            value={form.event_goal}
            onChange={(value) => updateField("event_goal", value)}
          />
          <Button type="submit" disabled={submitting}>
            {t("organizer.events.form.submit")}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
