"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { TraceTimeline } from "@/components/agent-trace/trace-timeline";
import { getDiagnosisDetail } from "@/features/diagnosis/api";
import type { DiagnosisDetail } from "@/types/diagnosis";

const RISK_STYLES: Record<string, string> = {
  HIGH: "text-red-700 bg-red-50 border-red-200",
  MEDIUM: "text-amber-800 bg-amber-50 border-amber-200",
  LOW: "text-green-800 bg-green-50 border-green-200",
};

export default function DiagnosisDetailPage() {
  const params = useParams();
  const diagnosisId = typeof params.id === "string" ? params.id : "";

  const [detail, setDetail] = useState<DiagnosisDetail | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!diagnosisId) {
      setError("无效的 diagnosis_id");
      setLoading(false);
      return;
    }
    void getDiagnosisDetail(diagnosisId)
      .then(setDetail)
      .catch((err) => setError(err instanceof Error ? err.message : "加载失败"))
      .finally(() => setLoading(false));
  }, [diagnosisId]);

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12">
        <p className="text-sm text-slate-500">加载诊断详情…</p>
      </main>
    );
  }

  if (error || !detail) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12">
        <p className="text-sm text-red-600">{error || "未找到诊断记录"}</p>
        <Link href="/diagnose" className="mt-4 inline-block text-sm text-slate-600 underline">
          返回诊断页
        </Link>
      </main>
    );
  }

  const { diagnosis_result: result } = detail;
  const riskClass = RISK_STYLES[result.risk_level] ?? "bg-slate-50 text-slate-800 border-slate-200";

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <p className="text-sm text-slate-500">
        <Link href="/diagnose" className="hover:text-slate-700">
          ← 返回诊断
        </Link>
      </p>

      <header className="mt-4">
        <h1 className="text-2xl font-semibold text-slate-900">诊断详情</h1>
        <p className="mt-1 text-xs text-slate-500">
          ID: {detail.diagnosis_id} · 文件: {detail.file_id}
          {detail.fault_code ? ` · 故障码: ${detail.fault_code}` : null}
        </p>
      </header>

      {/* 区域 1 — Diagnosis Summary */}
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-medium text-slate-900">诊断摘要</h2>
        <p className={`mt-4 inline-block rounded border px-3 py-1 text-sm font-medium ${riskClass}`}>
          风险等级：{result.risk_level}
          {detail.risk_score != null ? ` · 风险分数 ${detail.risk_score}` : null}
        </p>
        {detail.work_order_id ? (
          <p className="mt-2 text-sm text-slate-600">
            维修工单已创建：<span className="font-mono">{detail.work_order_id}</span>
          </p>
        ) : null}

        {result.fault_codes && result.fault_codes.length > 0 ? (
          <p className="mt-4 text-sm text-slate-600">
            故障码序列：{" "}
            <span className="font-mono">{result.fault_codes.join(" → ")}</span>
          </p>
        ) : null}

        {(result.temperature_trend || result.vibration_trend) && (
          <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-600">
            {result.temperature_trend ? (
              <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1">
                温度趋势：{result.temperature_trend.direction}
                {result.temperature_trend.from_value != null &&
                result.temperature_trend.to_value != null
                  ? ` (${result.temperature_trend.from_value} → ${result.temperature_trend.to_value})`
                  : null}
              </span>
            ) : null}
            {result.vibration_trend ? (
              <span className="rounded border border-slate-200 bg-slate-50 px-2 py-1">
                振动趋势：{result.vibration_trend.direction}
                {result.vibration_trend.from_value != null &&
                result.vibration_trend.to_value != null
                  ? ` (${result.vibration_trend.from_value} → ${result.vibration_trend.to_value})`
                  : null}
              </span>
            ) : null}
          </div>
        )}

        {result.primary_fault ? (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-slate-700">主要故障 (Primary Fault)</h3>
            <p className="mt-2 font-mono text-sm text-red-800">
              {result.primary_fault.code} {result.primary_fault.description}
            </p>
          </div>
        ) : null}

        {result.related_faults && result.related_faults.length > 0 ? (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-slate-700">关联故障 (Related Faults)</h3>
            <ul className="mt-2 list-inside list-disc text-sm text-slate-600">
              {result.related_faults.map((f) => (
                <li key={f.code}>
                  <span className="font-mono">{f.code}</span> {f.description}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {result.fault_evolution && result.fault_evolution.length > 0 ? (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-slate-700">故障演化 (Fault Evolution)</h3>
            <ol className="mt-3 space-y-1 text-sm text-slate-700">
              {result.fault_evolution.map((step, i) => (
                <li key={`${step}-${i}`} className="flex items-start gap-2">
                  <span className="text-slate-400">{i > 0 ? "↓" : "•"}</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        ) : null}

        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          <div>
            <h3 className="text-sm font-medium text-slate-700">可能原因</h3>
            <ul className="mt-2 list-inside list-disc text-sm text-slate-600">
              {result.possible_causes.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-medium text-slate-700">维修建议</h3>
            <ul className="mt-2 list-inside list-disc text-sm text-slate-600">
              {result.recommendations.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* 区域 2 — Agent Trace */}
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-medium text-slate-900">Agent Trace</h2>
        <p className="mt-1 text-sm text-slate-500">决策链与节点执行顺序（兼容 LangGraph 节点映射）</p>
        <div className="mt-6">
          <TraceTimeline trace={detail.trace} />
        </div>
      </section>

      {detail.rag_sources && detail.rag_sources.length > 0 ? (
        <section className="mt-8 rounded-lg border border-blue-100 bg-blue-50/50 p-6">
          <h2 className="text-lg font-medium text-slate-900">RAG 知识库引用</h2>
          <ul className="mt-4 space-y-3 text-sm">
            {detail.rag_sources.map((src, i) => (
              <li key={`${src.doc_id}-${i}`} className="rounded border border-blue-100 bg-white p-3">
                <span className="font-medium text-slate-900">{src.doc_name || src.doc_id}</span>
                <span className="ml-2 text-xs text-slate-400">
                  相似度 {(src.similarity_score * 100).toFixed(1)}%
                </span>
                <p className="mt-2 line-clamp-3 text-slate-600">{src.chunk_text}</p>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {detail.log_entries && detail.log_entries.length > 0 ? (
        <section className="mt-8 rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="text-lg font-medium text-slate-900">日志时间线</h2>
          <ul className="mt-4 space-y-2 text-sm">
            {detail.log_entries.map((entry, i) => (
              <li
                key={i}
                className="flex flex-wrap gap-2 rounded border border-slate-100 bg-slate-50 px-3 py-2"
              >
                {entry.timestamp ? (
                  <span className="font-mono text-slate-500">{entry.timestamp}</span>
                ) : null}
                <span className="font-medium text-slate-800">
                  {entry.fault_code || entry.status || "—"}
                </span>
                {entry.temperature != null ? (
                  <span className="text-slate-500">T={entry.temperature}</span>
                ) : null}
                {entry.vibration != null ? (
                  <span className="text-slate-500">V={entry.vibration}</span>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {/* 区域 3 — Raw Log Preview */}
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-medium text-slate-900">原始日志预览</h2>
        {detail.log_preview ? (
          <pre className="mt-4 max-h-96 overflow-auto rounded bg-slate-50 p-4 text-xs leading-relaxed text-slate-700">
            {detail.log_preview}
          </pre>
        ) : (
          <p className="mt-4 text-sm text-slate-500">无法加载日志（文件可能已删除）</p>
        )}
      </section>
    </main>
  );
}
