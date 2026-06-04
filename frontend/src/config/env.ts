/** Centralized public env — validated in later steps if needed. */
export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001",
} as const;
