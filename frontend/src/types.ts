/**
 * UPDATED: TypeScript interfaces for Synapse Council v2.0
 */

export interface DecisionWeights {
  risk: number;
  eq: number;
  values: number;
  red_team: number;
}

export interface DecisionRequest {
  dilemma: string;
  context?: string;
  weights?: DecisionWeights;
  gita_weight?: number;
  image_summaries?: string[];
  user_api_key?: string;
  session_id?: string;
}

export interface AgentResponse {
  recommendation: "PROCEED" | "CAUTION" | "BLOCK";
  confidence_score: number;
  reasoning: string;
  risk_level?: string;
  burnout_risk?: string;
  stakeholder_impact?: string;
  unstated_assumptions?: string;
  additional_data?: Record<string, unknown>;
  relationship_impact?: string;
  identity_alignment?: string;
  growth_potential?: string;
  wellbeing_trajectory?: string;
  ethical_concerns?: string;
  integrity_risk?: string;
  second_order_effects?: string;
  long_term_regret_likelihood?: string;
  strongest_counter_case?: string;
  wild_card_scenarios?: string;
  overconfidence_flags?: string;
  radical_alternative?: string;
  worst_case_scenario?: string;
  failure_probability?: string;
  financial_impact?: string;
  relevant_shlokas?: string;
  dharma_analysis?: string;
  karma_implications?: string;
  core_teaching?: string;
}

export interface ConflictMatrix {
  risk_eq: number;
  risk_values: number;
  risk_red_team: number;
  eq_values: number;
  eq_red_team: number;
  values_red_team: number;
}

export interface HeadCouncilVerdictData {
  final_verdict: string;
  confidence_score: number;
  summary: string;
  rationale: string;
  key_conflicts: string;
  suggested_next_actions: string;
  council_reasoning: string;
}

export interface AuditEntry {
  round: number;
  responses: Record<string, AgentResponse>;
  conflict_matrix?: ConflictMatrix;
}

export interface RecommendationResponse {
  recommendation: string;
  confidence_score: number;
  conflict_heatmap: ConflictMatrix;
  agent_responses: Record<string, AgentResponse>;
  debate_rounds: number;
  audit_trail: AuditEntry[];
  execution_time_ms: number;
  head_council_verdict?: HeadCouncilVerdictData;
  numeric_score?: number;
  numeric_confidence?: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export const AGENT_NAMES = {
  risk: "Risk & Logic",
  eq: "EQ Advocate",
  values: "Values Guard",
  red_team: "Red Team",
  gita: "Gita Guide",
} as const;

export const AGENT_COLORS = {
  risk: "#ef4444",
  eq: "#3b82f6",
  values: "#10b981",
  red_team: "#f59e0b",
  gita: "#8b5cf6",
} as const;