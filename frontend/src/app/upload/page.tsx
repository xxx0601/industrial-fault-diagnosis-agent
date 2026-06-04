"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { ACCEPTED_LOG_TYPES, listUploads, uploadDeviceLog } from "@/features/upload/api";
import type { UploadItem } from "@/types/upload";

type Status = "idle" | "uploading" | "success" | "error";

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString("zh-CN");
  } catch {
    return iso;
  }
}

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState<string>("");
  const [items, setItems] = useState<UploadItem[]>([]);
  const [loadingList, setLoadingList] = useState(true);

  const refreshList = useCallback(async () => {
    setLoadingList(true);
    try {
      const data = await listUploads();
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
    if (!selectedFile) {
      setMessage("请先选择文件");
      setStatus("error");
      return;
    }

    setStatus("uploading");
    setMessage("正在上传…");

    try {
      const result = await uploadDeviceLog(selectedFile);
      setStatus("success");
      setMessage(`上传成功：${result.filename}（${result.file_id}）`);
      setSelectedFile(null);
      const input = document.getElementById("log-file-input") as HTMLInputElement | null;
      if (input) input.value = "";
      await refreshList();
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "上传失败");
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <p className="text-sm text-slate-500">
        <Link href="/" className="hover:text-slate-700">
          ← 返回首页
        </Link>
      </p>

      <h1 className="mt-4 text-2xl font-semibold text-slate-900">上传设备日志</h1>
      <p className="mt-2 text-sm text-slate-600">
        支持 .txt、.csv、.json。上传后将用于故障诊断 Agent 与知识库检索。
      </p>

      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-6">
        <label htmlFor="log-file-input" className="block text-sm font-medium text-slate-700">
          选择文件
        </label>
        <input
          id="log-file-input"
          type="file"
          accept={ACCEPTED_LOG_TYPES}
          className="mt-2 block w-full text-sm text-slate-600 file:mr-4 file:rounded file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium"
          onChange={(e) => {
            setSelectedFile(e.target.files?.[0] ?? null);
            setStatus("idle");
            setMessage("");
          }}
        />

        <button
          type="button"
          onClick={() => void handleUpload()}
          disabled={status === "uploading" || !selectedFile}
          className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {status === "uploading" ? "上传中…" : "上传"}
        </button>

        {message ? (
          <p
            className={`mt-4 text-sm ${
              status === "error" ? "text-red-600" : status === "success" ? "text-green-700" : "text-slate-600"
            }`}
            role="status"
          >
            {message}
          </p>
        ) : null}
      </section>

      <section className="mt-10">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium text-slate-900">已上传文件</h2>
          <button
            type="button"
            onClick={() => void refreshList()}
            className="text-sm text-slate-600 hover:text-slate-900"
          >
            刷新
          </button>
        </div>

        {loadingList ? (
          <p className="mt-4 text-sm text-slate-500">加载中…</p>
        ) : items.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">暂无上传记录</p>
        ) : (
          <ul className="mt-4 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
            {items.map((item) => (
              <li key={item.file_id} className="px-4 py-3 text-sm">
                <div className="font-medium text-slate-900">{item.filename}</div>
                <div className="mt-1 text-slate-500">
                  <span className="mr-3">ID: {item.file_id}</span>
                  <span className="mr-3">类型: {item.file_type}</span>
                  <span>时间: {formatTime(item.upload_time)}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
