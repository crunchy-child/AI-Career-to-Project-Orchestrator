export type JDCategory = "required" | "preferred" | "responsibility" | "context";

export interface JDInput {
  id: string;
  category: JDCategory;
  text: string;
}

export interface AnalyzeRequest {
  resume_text: string;
  jd_inputs: JDInput[];
}

export interface AnalyzeResponse {
  gap_summary: {
    match_score: number;
    keyword_matches: unknown[];
    missing_keywords: unknown[];
    validated_missing_keywords: unknown[];
    notes: string;
  };
}
