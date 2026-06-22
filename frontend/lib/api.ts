// Typed client for the Veridian API (the FastAPI backend).
// Base URL is configurable so the same build works in dev and production.

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

// --- Response types (mirror api/schemas.py) ---

export type StrategyInfo = {
  key: string;
  name: string;
  description: string;
};

export type RiskParams = {
  fraction_per_trade: number;
  stop_loss_pct: number | null;
  max_capital_fraction: number;
  bail_out_drawdown_pct: number | null;
};

export type BacktestMetrics = {
  total_return: number;
  num_trades: number;
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  profit_factor: number;
  max_drawdown: number;
  sharpe: number;
};

export type EquityPoint = { date: string; equity: number };

export type TradeOut = {
  entry_date: string;
  exit_date: string;
  entry_price: number;
  exit_price: number;
  shares: number;
  reason: string;
  pnl: number;
  return_pct: number;
};

export type BacktestResponse = {
  symbol: string;
  strategy: string;
  starting_equity: number;
  ending_equity: number;
  metrics: BacktestMetrics;
  equity_curve: EquityPoint[];
  trades: TradeOut[];
  disclaimer: string;
};

export type FollowThrough = {
  pattern: string;
  bias: string;
  occurrences: number;
  horizon: number;
  pct_up: number;
  avg_return: number;
  median_return: number;
  reliable_sample: boolean;
};

export type PatternsResponse = {
  symbol: string;
  hits: { date: string; pattern_key: string; pattern_name: string; bias: string }[];
  follow_through: FollowThrough[];
  disclaimer: string;
};

export type AnnotationOut = {
  id: number;
  user_id: string;
  symbol: string;
  date: string;
  label: string;
  note: string;
  indicators: Record<string, number | null>;
  window_size: number;
  created_at: string;
};

export type AnnotationList = {
  annotations: AnnotationOut[];
  vocabulary: Record<string, number>;
};

// --- Fetch helpers ---

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new ApiError(res.status, detail?.detail ?? res.statusText);
  }
  return res.json();
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new ApiError(res.status, detail?.detail ?? res.statusText);
  }
  return res.json();
}

async function deleteJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { method: "DELETE" });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new ApiError(res.status, detail?.detail ?? res.statusText);
  }
  return res.json();
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

// --- Endpoints ---

export const api = {
  health: () => getJSON<{ status: string }>("/health"),
  symbols: () => getJSON<{ symbols: string[] }>("/symbols"),
  strategies: () =>
    getJSON<{ strategies: StrategyInfo[] }>("/strategies"),
  bars: (symbol: string) =>
    getJSON<{ symbol: string; bars: Bar[] }>(`/bars/${symbol}`),
  backtest: (body: {
    symbol: string;
    strategy_key: string;
    starting_equity: number;
    risk: RiskParams;
    params?: Record<string, number>;
  }) => postJSON<BacktestResponse>("/backtest", body),
  patterns: (symbol: string, horizon = 5) =>
    getJSON<PatternsResponse>(`/patterns/${symbol}?horizon=${horizon}`),

  // Annotations ("teach the AI")
  createAnnotation: (body: {
    user_id: string;
    symbol: string;
    date: string;
    label: string;
    note?: string;
  }) => postJSON<AnnotationOut>("/annotations", body),
  listAnnotations: (userId: string, symbol?: string) =>
    getJSON<AnnotationList>(
      `/annotations/${userId}${symbol ? `?symbol=${symbol}` : ""}`
    ),
  deleteAnnotation: (userId: string, id: number) =>
    deleteJSON<{ deleted: boolean }>(`/annotations/${userId}/${id}`),
};

export type Bar = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};
