"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { TraceTimeline } from "@/components/agent-trace/trace-timeline";
import { runDiagnosis } from "@/features/diagnosis/api";
import { listUploads } from "@/features/upload/api";
import type { DiagnosisResponse } from "@/types/diagnosis";
import type { UploadItem } from "@/types/upload";

const RISK_STYLES: Record<string, string> = {
  HIGH: "text-red-700 bg-red-50",
  MEDIUM: "text-amber-800 bg-amber-50",
  LOW: "text-green-800 bg-green-50",
};

export default function DiagnosePage() {
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const [fileId, setFileId] = useState("");
  const [faultCode, setFaultCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<DiagnosisResponse | null>(null);

  useEffect(() => {
    void listUploads()
      .then((data) => {
        setUploads(data.items);
        if (data.items.length > 0) {
          setFileId((prev) => prev || data.items[0].file_id);
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "加载上传列表失败"));
  }, []);

  async function handleDiagnose() {
    if (!fileId) {
      setError("请先上传日志并选择 file_id");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await runDiagnosis({
        file_id: fileId,
        fault_code: faultCode.trim() || null,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "诊断失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <p className="text-sm text-slate-500">
        <Link href="/" className="hover:text-slate-700">
          ← 返回首页
        </Link>
      </p>

      <h1 className="mt-4 text-2xl font-semibold text-slate-900">故障诊断</h1>
      <p className="mt-2 text-sm text-slate-600">
        基于已上传日志运行 LangGraph 诊断工作流（Industrial Fault Diagnosis Agent）。
      </p>

      <section className="mt-8 space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <div>
          <label htmlFor="file-id" className="block text-sm font-medium text-slate-700">
            日志文件
          </label>
          {uploads.length === 0 ? (
            <p className="mt-2 text-sm text-slate-500">
              暂无上传记录，请先到{" "}
              <Link href="/upload" className="text-slate-900 underline">
                上传页面
              </Link>{" "}
              上传日志。
            </p>
          ) : (
            <select
              id="file-id"
              value={fileId}
              onChange={(e) => setFileId(e.target.value)}
              className="mt-2 w-full rounded border border-slate-300 px-3 py-2 text-sm"
            >
              {uploads.map((u) => (
                <option key={u.file_id} value={u.file_id}>
                  {u.filename} ({u.file_id.slice(0, 8)}…)
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label htmlFor="fault-code" className="block text-sm font-medium text-slate-700">
            故障码（可选）
          </label>
          <input
            id="fault-code"
            type="text"
            placeholder="例如 E204"
            value={faultCode}
            onChange={(e) => setFaultCode(e.target.value)}
            className="mt-2 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>

        <button
          type="button"
          onClick={() => void handleDiagnose()}
          disabled={loading || !fileId}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "诊断中…" : "开始诊断"}
        </button>

        {error ? <p className="text-sm text-red-600">{error}</p> : null}
      </section>

      {result ? (
        <section className="mt-10 space-y-6">
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="text-lg font-medium text-slate-900">诊断结果</h2>
            <p className="mt-2 text-xs text-slate-500">
              ID: {result.diagnosis_id} ·{" "}
              <Link
                href={`/diagnosis/${result.diagnosis_id}`}
                className="font-medium text-slate-900 underline"
              >
                查看完整 Trace 与日志
              </Link>
            </p>
            <p className="mt-4">
              <span
                className={`inline-block rounded px-2 py-1 text-sm font-medium ${
                  RISK_STYLES[result.risk_level] ?? "bg-slate-100 text-slate-800"
                }`}
              >
                风险等级：{result.risk_level}
              </span>
            </p>
            {result.primary_fault ? (
              <p className="mt-4 text-sm text-slate-700">
                主要故障：{" "}
                <span className="font-mono font-medium text-red-800">
                  {result.primary_fault.code} {result.primary_fault.description}
                </span>
              </p>
            ) : null}
            {result.fault_codes && result.fault_codes.length > 0 ? (
              <p className="mt-2 text-xs text-slate-500">
                故障码：{result.fault_codes.join(" → ")}
              </p>
            ) : null}
            <div className="mt-4">
              <h3 className="text-sm font-medium text-slate-700">可能原因</h3>
              <ul className="mt-2 list-inside list-disc text-sm text-slate-600">
                {result.possible_causes.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
            <div className="mt-4">
              <h3 className="text-sm font-medium text-slate-700">维修建议</h3>
              <ul className="mt-2 list-inside list-disc text-sm text-slate-600">
                {result.recommendations.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h2 className="text-lg font-medium text-slate-900">Agent Trace（摘要）</h2>
            <div className="mt-4">
              <TraceTimeline trace={result.trace} />
            </div>
          </div>
        </section>
      ) : null}
    </main>
  );
}
