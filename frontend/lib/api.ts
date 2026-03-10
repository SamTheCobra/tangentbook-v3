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
  generateThesis: (rawThesis: string, conviction: number) =>
    request<{ id: string }>("/theses/generate", {
      method: "POST",
      body: JSON.stringify({ raw_thesis: rawThesis, conviction }),
    }),
  generateEffects: (thesisId: string, order: number, count: number) =>
    request<{ created: number; ids: string[] }>(`/theses/${thesisId}/generate-effects`, {
      method: "POST",
      body: JSON.stringify({ order, count }),
    }),
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

  // Scoring
  getScoringBreakdown: (thesisId: string) => request<ScoringBreakdown>(`/theses/${thesisId}/scoring-breakdown`),
  getEffectScoringBreakdown: (effectId: string) => request<ScoringBreakdown>(`/effects/${effectId}/scoring-breakdown`),

  // Effect feeds
  refreshEffectFeeds: (effectId: string) =>
    request(`/effects/${effectId}/feeds/refresh`, { method: "POST" }),

  // Feeds
  getFeeds: (thesisId: string) => request<Feed[]>(`/theses/${thesisId}/feeds`),
  refreshFeeds: (thesisId: string) =>
    request(`/theses/${thesisId}/feeds/refresh`, { method: "POST" }),
  refreshSingleFeed: (feedId: string) =>
    request(`/feeds/${feedId}/refresh`, { method: "POST" }),
  getFeedHistory: (feedId: string) => request(`/feeds/${feedId}/history`),

  // Portfolio
  getPortfolio: (thesisId: string) => request<Portfolio>(`/theses/${thesisId}/portfolio`),
  addPosition: (thesisId: string, data: PositionCreateInput) =>
    request<PortfolioPosition>(`/theses/${thesisId}/portfolio/positions`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updatePosition: (positionId: string, data: Partial<PositionUpdateInput>) =>
    request<PortfolioPosition>(`/portfolio/positions/${positionId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deletePosition: (positionId: string) =>
    request(`/portfolio/positions/${positionId}`, { method: "DELETE" }),

  // EFS / STS
  getThesisEquityScores: (thesisId: string) => request<EquityScoreResult[]>(`/theses/${thesisId}/equity-scores`),
  refreshThesisEquityScores: (thesisId: string) => request(`/theses/${thesisId}/equity-scores/refresh`, { method: "POST" }),
  getBetEFS: (betId: string) => request<{ betId: string; ticker: string; efs: EFSScore | null }>(`/equity-bet/${betId}/efs`),
  getStartupSTS: (oppId: string) => request<{ oppId: string; name: string; sts: STSScore | null }>(`/startup/${oppId}/sts`),
  getEffectEquityScores: (effectId: string) => request<EquityScoreResult[]>(`/effects/${effectId}/equity-scores`),

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
  summary: string;
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

export interface ScoringBreakdownFeed {
  name: string;
  value: number | null;
  formattedValue: string | null;
  normalizedScore: number | null;
  status: string;
  lastUpdated: string | null;
  seriesId: string | null;
  keyword: string | null;
  source: string | null;
  confirmingDirection: string | null;
  pctVs1yr: number | null;
  pctVs5yrAvg: number | null;
  context: string | null;
}

export interface EvidenceDimension {
  weight: number;
  description: string;
  score: number | null;
  feeds: ScoringBreakdownFeed[];
  lastUpdated: string | null;
}

export interface MomentumEntry {
  delta: number | null;
  score: number;
  prevEvidence: number | null;
  prevDate: string | null;
}

export interface ScoringBreakdown {
  thiScore: number;
  thiFormula: {
    evidenceScore: number;
    momentumScore: number;
    qualityScore: number;
    evidenceContrib: number;
    momentumContrib: number;
    qualityContrib: number;
  };
  evidence: {
    score: number;
    contribution: number;
    formula: string;
    flow: EvidenceDimension;
    structural: EvidenceDimension;
    adoption: EvidenceDimension;
    policy: EvidenceDimension;
    dimContributions: Record<string, number>;
  };
  momentum: {
    score: number;
    contribution: number;
    hasEnoughHistory: boolean;
    firstSnapshotDate: string | null;
    currentEvidence: number;
    thirtyDay: MomentumEntry;
    ninetyDay: MomentumEntry;
    oneYear: MomentumEntry;
  };
  dataQuality: {
    score: number;
    contribution: number;
    totalFeeds: number;
    scoredFeeds: number;
    agreement: { pctConfirming: number | null; score: number; scoredCount: number; totalCount: number };
    freshness: { avgAgeDays: number | null; live: number; stale: number; degraded: number; offline: number; score: number };
    sourceQuality: { weightedAvg: number; score: number; activeSources: string[] };
  };
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

export interface PortfolioPosition {
  id: string;
  thesisId: string;
  ticker: string;
  shares: number;
  entryPrice: number;
  entryDate: string | null;
  isShort: boolean;
  currentPrice: number | null;
  currentValue: number | null;
  pnl: number | null;
  pnlPct: number | null;
  lastUpdated: string | null;
  isClosed: boolean;
  closedAt: string | null;
  closePrice: number | null;
}

export interface Portfolio {
  positions: PortfolioPosition[];
  totalValue: number;
  totalCost: number;
  totalPnl: number;
  totalPnlPct: number;
  thiScore: number;
  interpretation: string;
  history: {
    date: string;
    totalValue: number;
    totalPnl: number;
    totalPnlPct: number;
    thiScore: number | null;
  }[];
}

export interface PositionCreateInput {
  ticker: string;
  shares: number;
  entry_price: number;
  is_short?: boolean;
}

export interface PositionUpdateInput {
  shares?: number;
  current_price?: number;
  is_closed?: boolean;
  close_price?: number;
}

export interface EFSScore {
  id: string;
  equityBetId: string;
  thesisId: string;
  effectId: string | null;
  revenueAlignmentScore: number;
  thesisBetaScore: number;
  momentumAlignmentScore: number;
  valuationBufferScore: number;
  signalPurityScore: number;
  efsScore: number;
  revenueAlignmentPct: number | null;
  forwardPE: number | null;
  sectorMedianPE: number | null;
  segmentCount: number | null;
  thesisBetaRaw: number | null;
  momentumDirection: string | null;
  stockReturn90d: number | null;
  thiDelta90d: number | null;
  lastUpdated: string | null;
  dataSourcesUsed: string[];
}

export interface STSScore {
  id: string;
  startupOppId: string;
  thiAlignmentScore: number;
  thiVelocityScore: number;
  competitionDensityScore: number;
  stsScore: number;
  competitorCount: number | null;
  fundedStartupsInCategory: number | null;
  totalFundingInCategory: number | null;
  timingLabel: string;
  lastUpdated: string | null;
}

export interface EquityScoreResult {
  ticker: string;
  companyName: string;
  role: string;
  betId: string;
  efs: EFSScore | null;
}
