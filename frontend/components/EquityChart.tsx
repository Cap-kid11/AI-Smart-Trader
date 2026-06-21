"use client";

import { useState } from "react";
import type { EquityPoint } from "@/lib/api";

type Props = {
  data: EquityPoint[];
  baseline: number;
  height?: number;
};

// A full equity-curve chart with a baseline (starting equity), axis labels,
// and a hover readout. Colors honestly: green if ended up, red if ended down.
export default function EquityChart({ data, baseline, height = 280 }: Props) {
  const [hover, setHover] = useState<number | null>(null);

  if (data.length === 0) {
    return (
      <div className="text-parchment-faint font-mono text-sm">
        No equity data.
      </div>
    );
  }

  const width = 720;
  const padL = 56;
  const padR = 16;
  const padT = 16;
  const padB = 28;

  const values = data.map((d) => d.equity);
  const min = Math.min(...values, baseline);
  const max = Math.max(...values, baseline);
  const range = max - min || 1;

  const x = (i: number) =>
    padL + (i / (data.length - 1)) * (width - padL - padR);
  const y = (v: number) =>
    height - padB - ((v - min) / range) * (height - padT - padB);

  const ended = values[values.length - 1];
  const positive = ended >= baseline;
  const color = positive ? "#5FA88A" : "#C16A5E";

  const path = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${x(i).toFixed(1)} ${y(d.equity).toFixed(1)}`)
    .join(" ");

  const areaPath =
    `${path} L ${x(data.length - 1).toFixed(1)} ${(height - padB).toFixed(1)}` +
    ` L ${x(0).toFixed(1)} ${(height - padB).toFixed(1)} Z`;

  // y-axis ticks
  const ticks = [min, min + range / 2, max];

  const onMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * width;
    const i = Math.round(
      ((px - padL) / (width - padL - padR)) * (data.length - 1)
    );
    setHover(Math.max(0, Math.min(data.length - 1, i)));
  };

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="w-full"
      onMouseMove={onMove}
      onMouseLeave={() => setHover(null)}
      role="img"
      aria-label="Equity curve over the backtest period"
    >
      <defs>
        <linearGradient id="eqfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.18" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* y grid + labels */}
      {ticks.map((t, i) => (
        <g key={i}>
          <line
            x1={padL}
            x2={width - padR}
            y1={y(t)}
            y2={y(t)}
            stroke="#23302F"
            strokeWidth={1}
          />
          <text
            x={padL - 8}
            y={y(t) + 3}
            textAnchor="end"
            className="fill-parchment-faint"
            style={{ fontSize: 10, fontFamily: "var(--font-mono)" }}
          >
            ${Math.round(t).toLocaleString()}
          </text>
        </g>
      ))}

      {/* baseline (starting equity) */}
      <line
        x1={padL}
        x2={width - padR}
        y1={y(baseline)}
        y2={y(baseline)}
        stroke="#5C6764"
        strokeWidth={1}
        strokeDasharray="3 3"
      />

      <path d={areaPath} fill="url(#eqfill)" />
      <path d={path} fill="none" stroke={color} strokeWidth={1.75} />

      {/* hover */}
      {hover !== null && (
        <g>
          <line
            x1={x(hover)}
            x2={x(hover)}
            y1={padT}
            y2={height - padB}
            stroke="#5C6764"
            strokeWidth={1}
          />
          <circle cx={x(hover)} cy={y(data[hover].equity)} r={3} fill={color} />
          <text
            x={Math.min(x(hover) + 8, width - 120)}
            y={padT + 12}
            className="fill-parchment"
            style={{ fontSize: 11, fontFamily: "var(--font-mono)" }}
          >
            {data[hover].date} · ${Math.round(data[hover].equity).toLocaleString()}
          </text>
        </g>
      )}

      {/* x endpoints */}
      <text
        x={padL}
        y={height - 8}
        className="fill-parchment-faint"
        style={{ fontSize: 10, fontFamily: "var(--font-mono)" }}
      >
        {data[0].date}
      </text>
      <text
        x={width - padR}
        y={height - 8}
        textAnchor="end"
        className="fill-parchment-faint"
        style={{ fontSize: 10, fontFamily: "var(--font-mono)" }}
      >
        {data[data.length - 1].date}
      </text>
    </svg>
  );
}
