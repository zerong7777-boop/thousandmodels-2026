import { Card, Collapse, Progress, Space, Tag, Typography } from "antd";
import type { AgentTrace } from "../types";

interface AgentTracePanelProps {
  traces: AgentTrace[];
}

export function AgentTracePanel({ traces }: AgentTracePanelProps) {
  const steps = traces.flatMap((trace) => trace.steps || []);

  return (
    <Card title="Agent 证据链" className="full-width">
      {steps.length === 0 ? (
        <Typography.Text type="secondary">生成方案后会显示 Agent step、工具结果和结构化输出。</Typography.Text>
      ) : (
        <Collapse
          size="small"
          items={steps.map((step, index) => ({
            key: `${step.agent_name}-${index}`,
            label: (
              <Space wrap>
                <Tag color={step.requires_human_approval ? "gold" : "green"}>{step.agent_name}</Tag>
                <span>{step.decision_reason}</span>
              </Space>
            ),
            children: (
              <Space orientation="vertical" className="full-width">
                <Progress percent={Math.round(step.confidence * 100)} size="small" />
                <Typography.Text type="secondary">输入：{step.input_refs.join(", ")}</Typography.Text>
                <pre className="trace-pre">
                  {JSON.stringify(
                    { tool_calls: step.tool_calls, structured_output: step.structured_output },
                    null,
                    2
                  )}
                </pre>
              </Space>
            )
          }))}
        />
      )}
    </Card>
  );
}
