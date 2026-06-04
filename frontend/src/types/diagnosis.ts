export type TraceStep = {
  step: number;
  node: string;
  message: string;
  status: string;
  started_at?: string | null;
  ended_at?: string | null;
  metadata?: Record<string, unknown>;
};

export type FaultRef = {
  code: string;
  description: string;
};

export type TrendMetric = {
  metric: string;
  direction: string;
  from_value?: number | null;
  to_value?: number | null;
  delta?: number | null;
};

export type DiagnosisResult = {
  risk_level: string;
  possible_causes: string[];
  recommendations: string[];
  fault_codes?: string[];
  primary_fault?: FaultRef | null;
  related_faults?: FaultRef[];
  fault_evolution?: string[];
  temperature_trend?: TrendMetric | null;
  vibration_trend?: TrendMetric | null;
};

export type DiagnosisRequest = {
  file_id: string;
  fault_code?: string | null;
};

export type DiagnosisResponse = {
  diagnosis_id: string;
  risk_level: string;
  possible_causes: string[];
  recommendations: string[];
  trace: TraceStep[];
  fault_codes?: string[];
  primary_fault?: FaultRef | null;
  related_faults?: FaultRef[];
  fault_evolution?: string[];
  temperature_trend?: TrendMetric | null;
  vibration_trend?: TrendMetric | null;
};

export type RagSource = {
  doc_id: string;
  doc_name: string | null;
  chunk_text: string;
  similarity_score: number;
};

export type LogEntry = {
  index?: number;
  timestamp?: string | null;
  status?: string | null;
  fault_code?: string | null;
  temperature?: number | null;
  vibration?: number | null;
};

export type DiagnosisDetail = {
  diagnosis_id: string;
  file_id: string;
  fault_code: string | null;
  created_at: string;
  diagnosis_result: DiagnosisResult;
  trace: TraceStep[];
  log_preview: string | null;
  rag_sources: RagSource[];
  tool_results: ToolResultRecord[];
  risk_score: number | null;
  work_order_id: string | null;
  log_entries?: LogEntry[];
};

export type ToolResultRecord = {
  tool_name: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  status: string;
  duration_ms?: number;
  error?: string | null;
};
