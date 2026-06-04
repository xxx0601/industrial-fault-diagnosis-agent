import { apiGet, apiPost } from "@/lib/api-client";
import type {
  DiagnosisDetail,
  DiagnosisRequest,
  DiagnosisResponse,
} from "@/types/diagnosis";

const DIAGNOSIS_PATH = "/api/v1/diagnosis";

export async function runDiagnosis(body: DiagnosisRequest): Promise<DiagnosisResponse> {
  return apiPost<DiagnosisResponse>(DIAGNOSIS_PATH, body);
}

export async function getDiagnosisDetail(diagnosisId: string): Promise<DiagnosisDetail> {
  return apiGet<DiagnosisDetail>(`${DIAGNOSIS_PATH}/${diagnosisId}`);
}

/** Human-readable node label for timeline UI */
export function traceNodeLabel(step: { node: string; metadata?: Record<string, unknown> }): string {
  const label = step.metadata?.node_label;
  if (typeof label === "string") return label;
  return step.node
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
