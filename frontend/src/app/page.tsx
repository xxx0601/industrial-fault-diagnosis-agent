import Link from "next/link";

const navItems = [
  { href: "/upload", label: "上传日志", desc: "上传设备运行日志（txt / csv / json）" },
  { href: "/diagnose", label: "故障诊断", desc: "LangGraph + Tool Calling + RAG 生成诊断建议" },
  { href: "/knowledge/upload", label: "知识库", desc: "上传 PDF / TXT 维修手册并入库" },
] as const;

export default function HomePage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <header className="mb-12">
        <p className="text-sm font-medium text-slate-500">Industrial Fault Diagnosis</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
          工业设备故障诊断
        </h1>
        <p className="mt-3 text-slate-600 leading-relaxed">
          上传设备日志或输入故障码，由 Agent 分析原因、检索维修知识库并生成维修建议。
        </p>
      </header>

      <nav className="grid gap-4 sm:grid-cols-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="block rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow"
          >
            <span className="font-medium text-slate-900">{item.label}</span>
            <span className="mt-1 block text-sm text-slate-500">{item.desc}</span>
          </Link>
        ))}
      </nav>
    </main>
  );
}
