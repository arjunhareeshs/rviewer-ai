export type InterviewPhase = 'introduction' | 'technical' | 'critical' | 'closing';

export interface EvaluationScore {
  answer_quality: number;
  technical_correctness: number;
  communication: number;
  problem_solving: number;
  attitude_confidence: number;
  overall_recommendation: number;
  feedback_details: Record<string, string>;
  summary: string;
  strengths: string[];
  areas_for_improvement: string[];
}

export interface SessionStatus {
  room_name: string;
  phase: InterviewPhase;
  exchange_count: number;
  report_ready: boolean;
}

export interface InterviewReport {
  score: EvaluationScore;
  pdfUrl: string;
}
