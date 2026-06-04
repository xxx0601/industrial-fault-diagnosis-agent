import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "工业设备故障诊断",
  description: "基于 LLM + RAG + Agent 的故障诊断与维修建议系统",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
