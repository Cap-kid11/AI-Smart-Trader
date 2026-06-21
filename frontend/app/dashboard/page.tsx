"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  api,
  ApiError,
  type BacktestResponse,
  type StrategyInfo,
} from "@/lib/api";
import EquityChart from "@/components/EquityChart";
import MetricsGrid from "@/components/MetricsGrid";

export default function Dashboard() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [strategies, setStrategies] = useState<StrategyInfo[]>([]);
  const [loadErr, setLoadErr] = useState<string | null>(null);

  // form state
  const [symbol, setSymbol] = useState("SAMPL");
  const [strategyKey, setStrategyKey] = useState("rsi_mean_reversion");
  const [startingEquity, setStartingEquity] = useState(10000);
  const [fractionPerTrade, setFractionPerTrade] = useState(0.5);
  const [stopLoss, setStopLoss] = useState(5); // percent
  const [maxCapital, setMaxCapital] = useState(100); // percent
  const [bailOut, setBailOut] = useState(0); // percent, 0 = off

  // result state
  const [result, setResult] = useState<BacktestResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [runErr, setRunErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [s, st] = await Promise.all([api.symbols(), api.strategies()]);
        setSymbols(s.symbols);
        setStrategies(st.strategies);
      } catch (e) {
        setLoadErr(
          e instanceof ApiError
            ? `Couldn't reach the API (${e.status}). Is the backend running on :8000?`
            : "Couldn't reach the API. Start the backend with: uvicorn api.main:app --reload"
        );
      }
    })();
  }, []);

  const run = async () => {
    setRunning(true);
    setRunErr(null);
    try {
      const res = await api.backtest({
        symbol,
        strategy_key: strategyKey,
        starting_equity: startingEquity,
        risk: {
          fraction_per_trade: fractionPerTrade,
          stop_loss_pct: stopLoss > 0 ? stopLoss / 100 : null,
          max_capital_fraction: maxCapital / 100,
          bail_out_drawdown_pct: bailOut > 0 ? bailOut / 100 : null,
        },
      });
      setResult(res);
    } catch (e) {
      setRunErr(
        e instanceof ApiError ? e.message : "Something went wrong running the backtest."
      );
    } finally {
      setRunning(false);
    }
  };

  const selectedStrategy = strategies.find((s) => s.key === strategyKey);

  return (
    <main className="min-h-screen">
      <header className="border-b border-ink-line">
        <div className="mx-auto flex max-w-readable items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <Mark />
            <span className="font-mono text-sm text-parchment">VERIDIAN</span>
          </Link>
          <span className="font-mono text-xs text-parchment-faint">
            Backtest console
          </span>
        </div>
      </header>

      <div className="mx-auto grid max-w-readable gap-8 px-6 py-10 lg:grid-cols-[300px_1fr]">
        {/* Control panel */}
        <aside className="space-y-6">
          <div>
            <h1 className="font-sans text-lg font-semibold text-parchment">
              Run a backtest
            </h1>
            <p className="mt-1 text-sm text-parchment-dim">
              Pick a strategy, set your limits, and see what actually happened.
            </p>
          </div>

          {loadErr && (
            <div className="rounded-md border border-loss/40 bg-loss/5 p-3 font-mono text-xs text-loss">
              {loadErr}
            </div>
          )}

          <Field label="Symbol">
            <Select value={symbol} onChange={setSymbol} options={symbols.length ? symbols : ["SAMPL"]} />
          </Field>

          <Field label="Strategy">
            <Select
              value={strategyKey}
              onChange={setStrategyKey}
              options={strategies.map((s) => s.key)}
              labels={Object.fromEntries(strategies.map((s) => [s.key, s.name]))}
            />
            {selectedStrategy && (
              <p className="mt-2 text-xs leading-relaxed text-parchment-dim">
                {selectedStrategy.description}
              </p>
            )}
          </Field>

          <Field label={`Starting equity · $${startingEquity.toLocaleString()}`}>
            <input
              type="number"
              min={1000}
              step={1000}
              value={startingEquity}
              onChange={(e) => setStartingEquity(Number(e.target.value))}
              className="w-full rounded-md border border-ink-line bg-ink-raised px-3 py-2 font-mono text-sm text-parchment focus:border-signal"
            />
          </Field>

          <div className="border-t border-ink-line pt-5">
            <div className="font-mono text-[11px] uppercase tracking-eyebrow text-signal">
              Your risk limits
            </div>
            <p className="mt-1 text-xs text-parchment-dim">
              You control how much trades, and when it bails.
            </p>
          </div>

          <Slider label="Capital per trade" value={fractionPerTrade * 100} min={5} max={100} step={5}
            suffix="%" onChange={(v) => setFractionPerTrade(v / 100)} />
          <Slider label="Stop loss" value={stopLoss} min={0} max={20} step={1}
            suffix={stopLoss === 0 ? " · off" : "%"} onChange={setStopLoss} />
          <Slider label="Max capital deployed" value={maxCapital} min={10} max={100} step={5}
            suffix="%" onChange={setMaxCapital} />
          <Slider label="Bail out at loss" value={bailOut} min={0} max={50} step={5}
            suffix={bailOut === 0 ? " · off" : "%"} onChange={setBailOut} />

          <button
            type="button"
            onClick={run}
            disabled={running || !!loadErr}
            className="w-full rounded-md bg-signal px-4 py-2.5 font-mono text-sm text-ink hover:bg-signal-deep disabled:opacity-50"
          >
            {running ? "Running…" : "Run backtest"}
          </button>
        </aside>

        {/* Results */}
        <section className="min-w-0">
          {runErr && (
            <div className="mb-4 rounded-md border border-loss/40 bg-loss/5 p-3 font-mono text-xs text-loss">
              {runErr}
            </div>
          )}

          {!result && !runErr && (
            <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-ink-line">
              <p className="font-mono text-sm text-parchment-faint">
                Run a backtest to see results.
              </p>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              <div className="flex items-baseline justify-between">
                <h2 className="font-sans text-xl font-semibold text-parchment">
                  {result.strategy}{" "}
                  <span className="font-mono text-sm text-parchment-faint">
                    · {result.symbol}
                  </span>
                </h2>
              </div>

              <div className="rounded-lg border border-ink-line bg-ink-raised p-4">
                <EquityChart
                  data={result.equity_curve}
                  baseline={result.starting_equity}
                />
              </div>

              <MetricsGrid
                metrics={result.metrics}
                endingEquity={result.ending_equity}
                startingEquity={result.starting_equity}
              />

              <p className="font-mono text-[11px] leading-relaxed text-parchment-faint">
                {result.disclaimer}
              </p>

              <TradesTable trades={result.trades} />
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function TradesTable({ trades }: { trades: BacktestResponse["trades"] }) {
  if (trades.length === 0)
    return (
      <p className="font-mono text-xs text-parchment-faint">
        This strategy opened no trades on this data.
      </p>
    );
  return (
    <div className="overflow-x-auto rounded-lg border border-ink-line">
      <table className="w-full border-collapse font-mono text-xs">
        <thead>
          <tr className="border-b border-ink-line text-parchment-faint">
            <Th>Entry</Th><Th>Exit</Th><Th>In</Th><Th>Out</Th>
            <Th>Shares</Th><Th>Reason</Th><Th>Return</Th>
          </tr>
        </thead>
        <tbody>
          {trades.map((t, i) => (
            <tr key={i} className="border-b border-ink-line/50">
              <Td>{t.entry_date}</Td>
              <Td>{t.exit_date}</Td>
              <Td>${t.entry_price}</Td>
              <Td>${t.exit_price}</Td>
              <Td>{t.shares}</Td>
              <Td>
                <span className={t.reason === "stop" ? "text-loss" : "text-parchment-dim"}>
                  {t.reason}
                </span>
              </Td>
              <Td>
                <span className={t.return_pct >= 0 ? "text-gain" : "text-loss"}>
                  {t.return_pct >= 0 ? "+" : ""}
                  {(t.return_pct * 100).toFixed(2)}%
                </span>
              </Td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// --- small UI primitives ---

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="font-mono text-[11px] uppercase tracking-eyebrow text-parchment-faint">
        {label}
      </label>
      <div className="mt-2">{children}</div>
    </div>
  );
}

function Select({
  value,
  onChange,
  options,
  labels,
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
  labels?: Record<string, string>;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-md border border-ink-line bg-ink-raised px-3 py-2 font-mono text-sm text-parchment focus:border-signal"
    >
      {options.map((o) => (
        <option key={o} value={o}>
          {labels?.[o] ?? o}
        </option>
      ))}
    </select>
  );
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  suffix,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  suffix: string;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-eyebrow text-parchment-faint">
          {label}
        </span>
        <span className="font-mono text-xs text-parchment tabular-nums">
          {value}
          {suffix}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="mt-2 w-full accent-signal"
      />
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return <th className="px-3 py-2 text-left font-medium">{children}</th>;
}
function Td({ children }: { children: React.ReactNode }) {
  return <td className="px-3 py-2 text-parchment">{children}</td>;
}

function Mark() {
  return (
    <svg width="14" height="18" viewBox="0 0 14 18" aria-hidden="true">
      <line x1="7" y1="0" x2="7" y2="18" stroke="#E0A84E" strokeWidth="1.5" />
      <rect x="3" y="5" width="8" height="8" fill="#0E1518" stroke="#E0A84E" strokeWidth="1.5" />
    </svg>
  );
}
