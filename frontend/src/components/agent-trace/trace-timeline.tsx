import { traceNodeLabel } from "@/features/diagnosis/api";
import type { TraceStep } from "@/types/diagnosis";

type RagHit = {
  doc_id: string;
  doc_name?: string | null;
  chunk_text: string;
  similarity_score: number;
};

function ToolCallDetail({
  toolName,
  toolInput,
  toolOutput,
  status,
  durationMs,
  error,
}: {
  toolName: string;
  toolInput: Record<string, unknown>;
  toolOutput: Record<string, unknown>;
  status: string;
  durationMs?: number;
  error?: string | null;
}) {
  return (
    <div className="mt-3 rounded border border-slate-200 bg-slate-50 p-3 text-xs">
      <p className="font-medium text-slate-800">Tool: {toolName}</p>
      <p className="mt-2 text-slate-500">
        Status:{" "}
        <span className={status === "success" ? "text-green-700" : "text-red-600"}>
          {status}
        </span>
        {durationMs != null ? (
          <span className="ml-2 text-slate-400">{durationMs} ms</span>
        ) : null}
      </p>
      <p className="mt-2 font-medium text-slate-600">Input</p>
      <pre className="mt-1 overflow-x-auto rounded bg-white p-2 text-slate-700">
        {JSON.stringify(toolInput, null, 2)}
      </pre>
      <p className="mt-2 font-medium text-slate-600">Output</p>
      <pre className="mt-1 overflow-x-auto rounded bg-white p-2 text-slate-700">
        {JSON.stringify(toolOutput, null, 2)}
      </pre>
      {error ? <p className="mt-2 text-red-600">{error}</p> : null}
    </div>
  );
}

function RagHitsDetail({ hits, query }: { hits: RagHit[]; query?: string }) {
  if (!Array.isArray(hits) || hits.length === 0) {
    return <p className="mt-2 text-xs text-slate-500">无匹配文档</p>;
  }
  return (
    <div className="mt-3 rounded border border-slate-100 bg-slate-50 p-3 text-xs">
      {query ? <p className="text-slate-500">查询: {query}</p> : null}
      <ul className="mt-2 space-y-2">
        {hits.map((h, i) => (
          <li key={`${h.doc_id}-${i}`} className="text-slate-600">
            <span className="font-medium text-slate-800">
              {h.doc_name || h.doc_id}
            </span>
            <span className="ml-2 text-slate-400">
              相似度 {(h.similarity_score * 100).toFixed(1)}%
            </span>
            <p className="mt-1 line-clamp-2 text-slate-500">{h.chunk_text}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

const STATUS_DOT: Record<string, string> = {
  success: "bg-green-500",
  error: "bg-red-500",
  running: "bg-amber-400",
};

type Props = {
  trace: TraceStep[];
};

export function TraceTimeline({ trace }: Props) {
  return (
    <ol className="relative space-y-0">
      {trace.map((step, index) => (
        <li key={`${step.step}-${step.node}`} className="relative flex gap-4 pb-8">
          {index < trace.length - 1 ? (
            <span
              className="absolute left-[11px] top-6 h-full w-px bg-slate-200"
              aria-hidden
            />
          ) : null}
          <span
            className={`relative z-10 mt-1 h-6 w-6 shrink-0 rounded-full ring-4 ring-white ${
              STATUS_DOT[step.status] ?? "bg-slate-400"
            }`}
            title={step.status}
          />
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Step {step.step}
            </p>
            <p className="font-medium text-slate-900">{traceNodeLabel(step)}</p>
            <p className="mt-1 text-sm text-slate-600">{step.message}</p>
            {step.node === "tool_call" && step.metadata?.tool_name ? (
              <ToolCallDetail
                toolName={String(step.metadata.tool_name)}
                toolInput={(step.metadata.tool_input as Record<string, unknown>) || {}}
                toolOutput={(step.metadata.tool_output as Record<string, unknown>) || {}}
                status={step.status}
                durationMs={step.metadata.duration_ms as number | undefined}
                error={step.metadata.error as string | null | undefined}
              />
            ) : null}
            {step.node === "rag_retrieve" && step.metadata?.hits ? (
              <RagHitsDetail hits={step.metadata.hits as RagHit[]} query={step.metadata.query as string | undefined} />
            ) : null}
          </div>
        </li>
      ))}
    </ol>
  );
}
