"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import {
  ACCEPTED_KNOWLEDGE_TYPES,
  deleteKnowledgeDocument,
  listKnowledgeDocuments,
  uploadKnowledgeDocument,
} from "@/features/knowledge/api";
import type { KnowledgeDocument } from "@/types/knowledge";

type Status = "idle" | "uploading" | "success" | "error";

export default function KnowledgeUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [docName, setDocName] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [items, setItems] = useState<KnowledgeDocument[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const refreshList = useCallback(async () => {
    setLoadingList(true);
    try {
      const data = await listKnowledgeDocuments();
      setItems(data.items);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "加载列表失败");
      setStatus("error");
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    void refreshList();
  }, [refreshList]);

  async function handleUpload() {
    if (!file) {
      setMessage("请选择 PDF 或 TXT 文件");
      setStatus("error");
      return;
    }
    const name = docName.trim() || file.name.replace(/\.pdf$/i, "");
    setStatus("uploading");
    setMessage("正在上传并建立索引…");
    try {
      const result = await uploadKnowledgeDocument(file, name, description.trim() || undefined);
      setStatus("success");
      setMessage(
        `入库成功：${result.doc_name}（${result.chunk_count} 个片段，状态 ${result.status}）`
      );
      setFile(null);
      setDocName("");
      setDescription("");
      const input = document.getElementById("kb-file") as HTMLInputElement | null;
      if (input) input.value = "";
      await refreshList();
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "上传失败");
    }
  }

  async function handleDelete(docId: string, docName: string) {
    if (!window.confirm(`确定删除「${docName}」？\n将同时移除向量索引与本地文件，且不可恢复。`)) {
      return;
    }
    setDeletingId(docId);
    try {
      const result = await deleteKnowledgeDocument(docId);
      setStatus("success");
      setMessage(result.message);
      await refreshList();
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "删除失败");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <p className="text-sm text-slate-500">
        <Link href="/" className="hover:text-slate-700">
          ← 返回首页
        </Link>
      </p>

      <h1 className="mt-4 text-2xl font-semibold text-slate-900">知识库文档上传</h1>
      <p className="mt-2 text-sm text-slate-600">
        上传维修手册（PDF / TXT），系统将解析、切块并写入向量库，供诊断 Agent RAG 检索。
      </p>

      <section className="mt-8 space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <div>
          <label className="block text-sm font-medium text-slate-700">文档文件（PDF / TXT）</label>
          <input
            id="kb-file"
            type="file"
            accept={ACCEPTED_KNOWLEDGE_TYPES}
            className="mt-2 block w-full text-sm"
            onChange={(e) => {
              const f = e.target.files?.[0] ?? null;
              setFile(f);
              if (f && !docName) setDocName(f.name.replace(/\.(pdf|txt)$/i, ""));
            }}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">文档名称</label>
          <input
            type="text"
            value={docName}
            onChange={(e) => setDocName(e.target.value)}
            placeholder="例如：主轴维修手册"
            className="mt-2 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">描述（可选）</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="mt-2 w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <button
          type="button"
          disabled={status === "uploading" || !file}
          onClick={() => void handleUpload()}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {status === "uploading" ? "处理中…" : "上传并入库"}
        </button>
        {message ? (
          <p
            className={`text-sm ${
              status === "error" ? "text-red-600" : status === "success" ? "text-green-700" : "text-slate-600"
            }`}
          >
            {message}
          </p>
        ) : null}
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-medium text-slate-900">已入库文档</h2>
        {loadingList ? (
          <p className="mt-4 text-sm text-slate-500">加载中…</p>
        ) : items.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">暂无文档</p>
        ) : (
          <ul className="mt-4 divide-y rounded-lg border border-slate-200 bg-white">
            {items.map((doc) => (
              <li
                key={doc.doc_id}
                className="flex items-start justify-between gap-4 px-4 py-3 text-sm"
              >
                <div className="min-w-0 flex-1">
                  <div className="font-medium text-slate-900">{doc.doc_name}</div>
                  <div className="mt-1 text-slate-500">
                    {doc.filename} · {doc.chunk_count} chunks · {doc.status}
                  </div>
                </div>
                <button
                  type="button"
                  disabled={deletingId === doc.doc_id}
                  onClick={() => void handleDelete(doc.doc_id, doc.doc_name)}
                  className="shrink-0 rounded border border-red-200 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
                >
                  {deletingId === doc.doc_id ? "删除中…" : "删除"}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
