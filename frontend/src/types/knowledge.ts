export type KnowledgeUploadResponse = {
  doc_id: string;
  doc_name: string;
  status: string;
  upload_time: string;
  chunk_count: number;
};

export type KnowledgeDocument = {
  doc_id: string;
  doc_name: string;
  description: string | null;
  filename: string;
  status: string;
  chunk_count: number;
  upload_time: string;
};

export type KnowledgeDocumentListResponse = {
  items: KnowledgeDocument[];
  total: number;
};

export type KnowledgeSearchHit = {
  doc_id: string;
  doc_name: string | null;
  chunk_text: string;
  similarity_score: number;
  chunk_index: number | null;
};
