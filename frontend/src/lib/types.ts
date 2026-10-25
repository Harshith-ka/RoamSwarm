export interface LandmarkPOI {
  id: string;
  osm_type: string;
  osm_id: number;
  name: string;
  latitude: float;
  longitude: float;
  category: string;
  distance_meters?: number;
  tags?: {
    historic?: string;
    tourism?: string;
    amenity?: string;
    religion?: string;
    opening_hours?: string;
    wheelchair?: string;
    website?: string;
    phone?: string;
    fee?: string;
    wikipedia?: string;
    wikidata?: string;
    description?: string;
    start_date?: string;
  };
}

export type float = number;

export interface ToolExecutionTrace {
  agent_name: string;
  tool_name: string;
  sanitized_input: Record<string, any>;
  sanitized_output: Record<string, any>;
  duration_ms: number;
  timestamp: string;
  success: boolean;
  error?: string;
}

export interface CitationItem {
  claim_id: string;
  claim_text: string;
  source_url: string;
  publisher: string;
  confidence: number;
  verification_status: "verified" | "unverified" | "disputed" | "stale";
}

export interface VenueFact {
  attribute: string;
  value: string;
  status: "verified" | "unverified" | "missing" | "stale";
  confidence: number;
  source: string;
  note?: string;
}

export interface ExplorationSession {
  session_id: string;
  landmark_id: string;
  landmark_name: string;
  latitude?: number;
  longitude?: number;
  status: "pending" | "researching" | "validating" | "writing" | "generating_audio" | "completed" | "partial" | "failed";
  language: string;
  story_style: "documentary" | "conversational" | "educational";
  duration_seconds: number;
  story_script?: string;
  audio_url?: string;
  audio_duration_seconds?: number;
  citations: CitationItem[];
  historical_facts: any[];
  venue_facts: VenueFact[];
  tool_calls: ToolExecutionTrace[];
  execution_timeline: Array<{
    event: string;
    agent: string;
    timestamp: number;
    detail: string;
  }>;
  created_at?: string;
  completed_at?: string;
}

export interface BenchmarkMetrics {
  sample_size: number;
  multi_agent: {
    avg_composite_score: number;
    completion_rate_pct: number;
    avg_citation_accuracy_pct: number;
    avg_factuality_score_pct: number;
    avg_word_adherence_pct: number;
    avg_citations_count: number;
    avg_tool_executions: number;
    p50_latency_ms: number;
    p95_latency_ms: number;
  };
  single_agent_baseline: {
    avg_composite_score: number;
    completion_rate_pct: number;
    avg_citation_accuracy_pct: number;
    avg_factuality_score_pct: number;
    avg_word_adherence_pct: number;
    avg_citations_count: number;
    avg_tool_executions: number;
    p50_latency_ms: number;
    p95_latency_ms: number;
  };
  citation_grounding_improvement_pct: number;
  factuality_improvement_pct: number;
}
