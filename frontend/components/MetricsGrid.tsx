import type { BacktestMetrics } from "@/lib/api";

const pct = (n: number, sign = true) =>
  `${sign && n >= 0 ? "+" : ""}${(n * 100).toFixed(2)}%`;

// Honest metrics, presented plainly. Drawdown is always shown in the loss
// color because it is always a loss; total return is colored by its actual sign.
export default function MetricsGrid({
  metrics,
  endingEquity,
  startingEquity,
}: {
  metrics: BacktestMetrics;
  endingEquity: number;
  startingEquity: number;
}) {
  const positive = metrics.total_return >= 0;

  const items: { label: string; value: string; tone?: "gain" | "loss" }[] = [
    {
      label: "Total return",
      value: pct(metrics.total_return),
      tone: positive ? "gain" : "loss",
    },
    {
      label: "Ending equity",
      value: `$${endingEquity.toLocaleString()}`,
      tone: endingEquity >= startingEquity ? "gain" : "loss",
    },
    { label: "Win rate", value: `${(metrics.win_rate * 100).toFixed(0)}%` },
    { label: "Trades", value: String(metrics.num_trades) },
    { label: "Avg win", value: pct(metrics.avg_win), tone: "gain" },
    { label: "Avg loss", value: pct(metrics.avg_loss), tone: "loss" },
    { label: "Profit factor", value: metrics.profit_factor.toFixed(2) },
    { label: "Max drawdown", value: pct(metrics.max_drawdown), tone: "loss" },
    { label: "Sharpe", value: metrics.sharpe.toFixed(2) },
  ];

  return (
    <dl className="grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-ink-line bg-ink-line">
      {items.map((it) => (
        <div key={it.label} className="bg-ink p-4">
          <dt className="font-mono text-[11px] uppercase tracking-eyebrow text-parchment-faint">
            {it.label}
          </dt>
          <dd
            className={`mt-1.5 font-mono text-base tabular-nums ${
              it.tone === "gain"
                ? "text-gain"
                : it.tone === "loss"
                  ? "text-loss"
                  : "text-parchment"
            }`}
          >
            {it.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}
