type SparklineProps = {
  data: number[];
  baseline: number;
  width?: number;
  height?: number;
  positive: boolean;
};

// A minimal equity-curve sparkline. Colors honestly: green path if the
// strategy ended up, red if it ended down. Baseline (starting equity) shown
// as a faint dashed line so the reader sees gain vs loss at a glance.
export default function Sparkline({
  data,
  baseline,
  width = 280,
  height = 72,
  positive,
}: SparklineProps) {
  if (data.length === 0) return null;

  const min = Math.min(...data, baseline);
  const max = Math.max(...data, baseline);
  const range = max - min || 1;
  const pad = 4;

  const x = (i: number) =>
    pad + (i / (data.length - 1)) * (width - pad * 2);
  const y = (v: number) =>
    height - pad - ((v - min) / range) * (height - pad * 2);

  const path = data
    .map((v, i) => `${i === 0 ? "M" : "L"} ${x(i).toFixed(1)} ${y(v).toFixed(1)}`)
    .join(" ");

  const baselineY = y(baseline);
  const color = positive ? "var(--c-gain)" : "var(--c-loss)";

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={`Equity curve, ${positive ? "ended higher" : "ended lower"} than the starting balance`}
      style={
        {
          ["--c-gain" as string]: "#5FA88A",
          ["--c-loss" as string]: "#C16A5E",
        } as React.CSSProperties
      }
    >
      <line
        x1={pad}
        x2={width - pad}
        y1={baselineY}
        y2={baselineY}
        stroke="#5C6764"
        strokeWidth={1}
        strokeDasharray="3 3"
      />
      <path d={path} fill="none" stroke={color} strokeWidth={1.75} />
      <circle
        cx={x(data.length - 1)}
        cy={y(data[data.length - 1])}
        r={2.5}
        fill={color}
      />
    </svg>
  );
}
