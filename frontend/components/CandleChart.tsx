"use client";

import { useState } from "react";
import type { Bar } from "@/lib/api";

type Props = {
  bars: Bar[];
  annotatedDates?: Set<string>;
  onSelect: (date: string) => void;
  selectedDate?: string | null;
  height?: number;
};

// A real candlestick chart. Click any candle to select it for annotation.
// Annotated candles get a small amber marker so the user sees their library
// building up on the chart itself.
export default function CandleChart({
  bars,
  annotatedDates = new Set(),
  onSelect,
  selectedDate,
  height = 320,
}: Props) {
  const [hover, setHover] = useState<number | null>(null);

  if (bars.length === 0) {
    return (
      <div className="font-mono text-sm text-parchment-faint">No bars.</div>
    );
  }

  const width = 760;
  const padL = 52;
  const padR = 12;
  const padT = 12;
  const padB = 24;

  const highs = bars.map((b) => b.high);
  const lows = bars.map((b) => b.low);
  const min = Math.min(...lows);
  const max = Math.max(...highs);
  const range = max - min || 1;

  const plotW = width - padL - padR;
  const step = plotW / bars.length;
  const cw = Math.max(1.5, Math.min(8, step * 0.6)); // candle body width

  const x = (i: number) => padL + i * step + step / 2;
  const y = (v: number) =>
    height - padB - ((v - min) / range) * (height - padT - padB);

  const ticks = [min, min + range / 2, max];

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="w-full"
      onMouseLeave={() => setHover(null)}
      role="img"
      aria-label="Candlestick chart — click a candle to annotate it"
    >
      {ticks.map((t, i) => (
        <g key={i}>
          <line x1={padL} x2={width - padR} y1={y(t)} y2={y(t)} stroke="#23302F" strokeWidth={1} />
          <text x={padL - 8} y={y(t) + 3} textAnchor="end" className="fill-parchment-faint"
            style={{ fontSize: 10, fontFamily: "var(--font-mono)" }}>
            ${Math.round(t)}
          </text>
        </g>
      ))}

      {bars.map((b, i) => {
        const up = b.close >= b.open;
        const color = up ? "#5FA88A" : "#C16A5E";
        const bodyTop = y(Math.max(b.open, b.close));
        const bodyBot = y(Math.min(b.open, b.close));
        const isSel = selectedDate === b.date;
        const isAnnotated = annotatedDates.has(b.date);
        return (
          <g
            key={b.date}
            onClick={() => onSelect(b.date)}
            onMouseEnter={() => setHover(i)}
            style={{ cursor: "pointer" }}
          >
            {/* invisible wide hit area for easy clicking */}
            <rect x={padL + i * step} y={padT} width={step} height={height - padT - padB} fill="transparent" />
            {isSel && (
              <rect x={padL + i * step} y={padT} width={step} height={height - padT - padB}
                fill="#E0A84E" opacity={0.12} />
            )}
            <line x1={x(i)} x2={x(i)} y1={y(b.high)} y2={y(b.low)} stroke={color} strokeWidth={1} />
            <rect
              x={x(i) - cw / 2}
              y={bodyTop}
              width={cw}
              height={Math.max(1, bodyBot - bodyTop)}
              fill={color}
            />
            {isAnnotated && (
              <circle cx={x(i)} cy={padT + 4} r={2.5} fill="#E0A84E" />
            )}
          </g>
        );
      })}

      {hover !== null && (
        <text x={padL} y={height - 8} className="fill-parchment"
          style={{ fontSize: 10, fontFamily: "var(--font-mono)" }}>
          {bars[hover].date} · O {bars[hover].open} H {bars[hover].high} L {bars[hover].low} C {bars[hover].close}
        </text>
      )}
    </svg>
  );
}
