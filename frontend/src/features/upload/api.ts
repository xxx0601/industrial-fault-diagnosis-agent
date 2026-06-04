import { apiGet, apiPostForm } from "@/lib/api-client";
import type { UploadItem, UploadListResponse } from "@/types/upload";

const UPLOADS_PATH = "/api/v1/uploads";

export async function listUploads(): Promise<UploadListResponse> {
  return apiGet<UploadListResponse>(UPLOADS_PATH);
}

export async function uploadDeviceLog(file: File): Promise<UploadItem> {
  const form = new FormData();
  form.append("file", file);
  return apiPostForm<UploadItem>(UPLOADS_PATH, form);
}

export const ACCEPTED_LOG_TYPES = ".txt,.csv,.json";
