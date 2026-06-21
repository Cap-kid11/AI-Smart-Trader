import Sparkline from "./Sparkline";
import type { BacktestResult } from "@/lib/backtest-data";

const pct = (n: number) =>
  `${n >= 0 ? "+" : ""}${(n * 100).toFixed(2)}%`;

export default function ResultCard({ result }: { result: BacktestResult }) {
  const positive = result.totalReturn >= 0;

  return (
    <div className="rounded-lg border border-ink-line bg-ink-raised p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-parchment-faint text-xs uppercase tracking-eyebrow">
            Strategy
          </div>
          <div className="font-mono text-parchment text-sm mt-1">
            {result.name}
          </div>
        </div>
        <div
          className={`font-mono text-lg tabular-nums ${
            positive ? "text-gain" : "text-loss"
          }`}
        >
          {pct(result.totalReturn)}
        </div>
      </div>

      <div className="mt-4">
        <Sparkline
          data={result.spark}
          baseline={result.spark[0]}
          positive={positive}
        />
      </div>

      <dl className="mt-4 grid grid-cols-3 gap-x-3 gap-y-3 font-mono text-xs">
        <Metric label="Win rate" value={`${(result.winRate * 100).toFixed(0)}%`} />
        <Metric label="Trades" value={String(result.numTrades)} />
        <Metric
          label="Max DD"
          value={pct(result.maxDrawdown)}
          tone="loss"
        />
        <Metric label="Sharpe" value={result.sharpe.toFixed(2)} />
        <Metric label="Profit factor" value={result.profitFactor.toFixed(2)} />
      </dl>
    </div>
  );
}

function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: "loss";
}) {
  return (
    <div>
      <dt className="text-parchment-faint">{label}</dt>
      <dd
        className={`tabular-nums mt-0.5 ${
          tone === "loss" ? "text-loss" : "text-parchment"
        }`}
      >
        {value}
      </dd>
    </div>
  );
}
