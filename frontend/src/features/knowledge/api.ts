import { apiDelete, apiGet, apiPostForm } from "@/lib/api-client";
import type {
  KnowledgeDocumentListResponse,
  KnowledgeSearchHit,
  KnowledgeUploadResponse,
} from "@/types/knowledge";

const BASE = "/api/v1/knowledge";

export const ACCEPTED_KNOWLEDGE_TYPES = ".pdf,.txt,application/pdf,text/plain";

export async function uploadKnowledgeDocument(
  file: File,
  docName: string,
  description?: string
): Promise<KnowledgeUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("doc_name", docName);
  if (description) form.append("description", description);
  return apiPostForm<KnowledgeUploadResponse>(`${BASE}/upload`, form);
}

/** @deprecated Use uploadKnowledgeDocument */
export const uploadKnowledgePdf = uploadKnowledgeDocument;

export async function listKnowledgeDocuments(): Promise<KnowledgeDocumentListResponse> {
  return apiGet<KnowledgeDocumentListResponse>(`${BASE}/documents`);
}

export type KnowledgeDeleteResponse = {
  doc_id: string;
  deleted: boolean;
  message: string;
};

export async function deleteKnowledgeDocument(
  docId: string
): Promise<KnowledgeDeleteResponse> {
  return apiDelete<KnowledgeDeleteResponse>(`${BASE}/documents/${docId}`);
}

export async function searchKnowledge(
  query: string,
  topK = 5
): Promise<{ query: string; hits: KnowledgeSearchHit[]; total: number }> {
  const params = new URLSearchParams({ query, top_k: String(topK) });
  return apiGet(`${BASE}/search?${params.toString()}`);
}
