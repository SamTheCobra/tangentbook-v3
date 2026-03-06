const API_BASE = "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  // Theses
  getTheses: () => request<Thesis[]>("/theses"),
  getThesis: (id: string) => request<ThesisDetail>(`/theses/${id}`),
  createThesis: (data: ThesisCreateInput) =>
    request<Thesis>("/theses", { method: "POST", body: JSON.stringify(data) }),
  updateThesis: (id: string, data: Partial<ThesisCreateInput>) =>
    request<Thesis>(`/theses/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteThesis: (id: string) =>
    request(`/theses/${id}`, { method: "DELETE" }),
  toggleArchive: (id: string) =>
    request(`/theses/${id}/archive`, { method: "PATCH" }),
  toggleCollapse: (id: string) =>
    request(`/theses/${id}/collapse`, { method: "PATCH" }),
  reorderThesis: (id: string, displayOrder: number) =>
    request(`/theses/${id}/reorder`, {
      method: "PATCH",
      body: JSON.stringify({ display_order: displayOrder }),
    }),
  updateConviction: (id: string, score: number, note?: string) =>
    request<Thesis>(`/theses/${id}/conviction`, {
      method: "PUT",
      body: JSON.stringify({ score, note }),
    }),

  // Effects
  getEffects: (thesisId: string) => request<Effect[]>(`/theses/${thesisId}/effects`),
  createEffect: (thesisId: string, data: EffectCreateInput) =>
    request<Effect>(`/theses/${thesisId}/effects`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getEffect: (id: string) => request<Effect>(`/effects/${id}`),
  updateEffect: (id: string, data: Partial<EffectCreateInput>) =>
    request<Effect>(`/effects/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteEffect: (id: string) =>
    request(`/effects/${id}`, { method: "DELETE" }),
  updateEffectConviction: (id: string, score: number, note?: string) =>
    request(`/effects/${id}/conviction`, {
      method: "PUT",
      body: JSON.stringify({ score, note }),
    }),

  // Equity Bets
  createBet: (thesisId: string, data: BetCreateInput) =>
    request(`/theses/${thesisId}/bets`, { method: "POST", body: JSON.stringify(data) }),
  createEffectBet: (effectId: string, data: BetCreateInput) =>
    request(`/effects/${effectId}/bets`, { method: "POST", body: JSON.stringify(data) }),
  updateBet: (id: string, data: Partial<BetCreateInput>) =>
    request(`/bets/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteBet: (id: string) =>
    request(`/bets/${id}`, { method: "DELETE" }),

  // Startup Opportunities
  createOpportunity: (thesisId: string, data: OpportunityCreateInput) =>
    request(`/theses/${thesisId}/opportunities`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateOpportunity: (id: string, data: Partial<OpportunityCreateInput>) =>
    request(`/opportunities/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteOpportunity: (id: string) =>
    request(`/opportunities/${id}`, { method: "DELETE" }),

  // Feeds
  getFeeds: (thesisId: string) => request<Feed[]>(`/theses/${thesisId}/feeds`),
  refreshFeeds: (thesisId: string) =>
    request(`/theses/${thesisId}/feeds/refresh`, { method: "POST" }),
  getFeedHistory: (feedId: string) => request(`/feeds/${feedId}/history`),

  // Macro
  getMacroHeader: () => request<MacroHeader>("/macro/header"),
};

// ── Types ────────────────────────────────────────────────────────────────────

export interface THI {
  score: number;
  direction: string;
  trend: string;
  evidence: { score: number; weight: number };
  momentum: { score: number; weight: number };
  conviction: { score: number; weight: number };
}

export interface UserConviction {
  score: number;
  note?: string;
  updatedAt?: string;
  divergenceWarning?: string;
  history?: { score: number; updatedAt: string; note?: string }[];
}

export interface EquityBet {
  id: string;
  ticker: string;
  companyName: string;
  companyDescription: string;
  role: string;
  rationale: string;
  timeHorizon: string;
  isFeedbackIndicator: boolean;
  feedbackWeight: number;
  currentPrice?: number;
  priceChange12mPct?: number;
  priceHistory?: { date: string; close: number }[];
}

export interface StartupOpportunity {
  id: string;
  name: string;
  oneLiner: string;
  timing: string;
  timeHorizon: string;
}

export interface Effect {
  id: string;
  thesisId: string;
  parentEffectId?: string;
  order: number;
  title: string;
  description: string;
  inheritanceWeight: number;
  isCollapsed: boolean;
  thi: { score: number; direction: string; trend: string };
  userConviction: UserConviction;
  equityBets: EquityBet[];
  startupOpportunities: StartupOpportunity[];
  childEffects: Effect[];
}

export interface Thesis {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  timeHorizon: string;
  tags: string[];
  isArchived: boolean;
  isCollapsed: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
  thi: THI;
  userConviction: UserConviction;
  effects: Effect[];
  equityBets: EquityBet[];
  startupOpportunities: StartupOpportunity[];
}

export interface ThesisDetail extends Thesis {
  thiHistory: {
    date: string;
    score: number;
    evidenceScore: number;
    momentumScore: number;
    convictionScore: number;
  }[];
}

export interface Feed {
  id: string;
  name: string;
  description: string;
  source: string;
  sourceType: string;
  seriesId?: string;
  keyword?: string;
  ticker?: string;
  updateFrequency: string;
  status: string;
  lastFetched?: string;
  rawValue?: number;
  normalizedScore?: number;
  confirmingDirection: string;
  weight: number;
}

export interface MacroHeader {
  regime: string;
  ffr: number | null;
  tenYearTwoYearSpread: number | null;
  vix: number | null;
  lastUpdated: string | null;
}

export interface ThesisCreateInput {
  title: string;
  subtitle: string;
  description: string;
  time_horizon: string;
  tags: string[];
  user_conviction_score: number;
}

export interface EffectCreateInput {
  title: string;
  description: string;
  order: number;
  parent_effect_id?: string;
}

export interface BetCreateInput {
  ticker: string;
  company_name: string;
  role: string;
  rationale: string;
  time_horizon: string;
  is_feedback_indicator: boolean;
  feedback_weight: number;
}

export interface OpportunityCreateInput {
  name: string;
  one_liner: string;
  timing: string;
  time_horizon: string;
}
