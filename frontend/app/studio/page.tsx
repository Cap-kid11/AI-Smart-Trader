"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  api,
  ApiError,
  type AnnotationOut,
  type Bar,
} from "@/lib/api";
import CandleChart from "@/components/CandleChart";

// For now the user id is fixed; real auth arrives with accounts later.
const USER_ID = "demo-user";

export default function Studio() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [symbol, setSymbol] = useState("SAMPL");
  const [bars, setBars] = useState<Bar[]>([]);
  const [annotations, setAnnotations] = useState<AnnotationOut[]>([]);
  const [vocabulary, setVocabulary] = useState<Record<string, number>>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [label, setLabel] = useState("");
  const [note, setNote] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // show a recent slice so candles are wide enough to click comfortably
  const visibleBars = bars.slice(-120);
  const annotatedDates = new Set(annotations.map((a) => a.date));

  useEffect(() => {
    (async () => {
      try {
        const s = await api.symbols();
        setSymbols(s.symbols);
      } catch {
        setErr("Couldn't reach the API. Start the backend on :8000.");
      }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      setErr(null);
      try {
        const [b, a] = await Promise.all([
          api.bars(symbol),
          api.listAnnotations(USER_ID, symbol),
        ]);
        setBars(b.bars);
        setAnnotations(a.annotations);
        setVocabulary(a.vocabulary);
      } catch (e) {
        setErr(
          e instanceof ApiError
            ? `API error (${e.status}). Is the backend running?`
            : "Couldn't load data."
        );
      }
    })();
  }, [symbol]);

  const refreshAnnotations = async () => {
    const a = await api.listAnnotations(USER_ID, symbol);
    setAnnotations(a.annotations);
    setVocabulary(a.vocabulary);
  };

  const save = async () => {
    if (!selected || !label.trim()) return;
    setSaving(true);
    setErr(null);
    try {
      await api.createAnnotation({
        user_id: USER_ID,
        symbol,
        date: selected,
        label: label.trim(),
        note: note.trim(),
      });
      setLabel("");
      setNote("");
      setSelected(null);
      await refreshAnnotations();
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Couldn't save the annotation.");
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: number) => {
    await api.deleteAnnotation(USER_ID, id);
    await refreshAnnotations();
  };

  return (
    <main className="min-h-screen">
      <header className="border-b border-ink-line">
        <div className="mx-auto flex max-w-readable items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <Mark />
            <span className="font-mono text-sm text-parchment">VERIDIAN</span>
          </Link>
          <nav className="flex gap-6 font-mono text-xs text-parchment-dim">
            <Link href="/dashboard" className="hover:text-parchment">Backtest</Link>
            <span className="text-parchment">Teach</span>
          </nav>
        </div>
      </header>

      <div className="mx-auto max-w-readable px-6 py-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-sans text-xl font-semibold text-parchment">
              Teach the assistant
            </h1>
            <p className="mt-1 max-w-xl text-sm text-parchment-dim">
              Click any candle and label what you see. Each tag is saved with the
              surrounding price action and indicators — building a library of how{" "}
              <span className="text-parchment">you</span> read the chart.
            </p>
          </div>
          <div>
            <label className="font-mono text-[11px] uppercase tracking-eyebrow text-parchment-faint">
              Symbol
            </label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="mt-1 block rounded-md border border-ink-line bg-ink-raised px-3 py-1.5 font-mono text-sm text-parchment focus:border-signal"
            >
              {(symbols.length ? symbols : ["SAMPL"]).map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>

        {err && (
          <div className="mt-4 rounded-md border border-loss/40 bg-loss/5 p-3 font-mono text-xs text-loss">
            {err}
          </div>
        )}

        <div className="mt-6 rounded-lg border border-ink-line bg-ink-raised p-4">
          <CandleChart
            bars={visibleBars}
            annotatedDates={annotatedDates}
            onSelect={setSelected}
            selectedDate={selected}
          />
          <p className="mt-2 font-mono text-[11px] text-parchment-faint">
            Showing the most recent {visibleBars.length} candles. Amber dots mark
            candles you&rsquo;ve already labeled.
          </p>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_1fr]">
          {/* Annotation form */}
          <div className="rounded-lg border border-ink-line p-5">
            <h2 className="font-mono text-[11px] uppercase tracking-eyebrow text-signal">
              Label this candle
            </h2>
            {selected ? (
              <div className="mt-3 space-y-3">
                <div className="font-mono text-sm text-parchment">
                  Selected: <span className="text-signal">{selected}</span>
                </div>
                <input
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  placeholder="Your label, e.g. “my setup”, “fakeout”"
                  className="w-full rounded-md border border-ink-line bg-ink-raised px-3 py-2 font-mono text-sm text-parchment placeholder:text-parchment-faint focus:border-signal"
                />
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Optional note — why does this candle matter?"
                  rows={2}
                  className="w-full rounded-md border border-ink-line bg-ink-raised px-3 py-2 font-sans text-sm text-parchment placeholder:text-parchment-faint focus:border-signal"
                />
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={save}
                    disabled={saving || !label.trim()}
                    className="rounded-md bg-signal px-4 py-2 font-mono text-sm text-ink hover:bg-signal-deep disabled:opacity-50"
                  >
                    {saving ? "Saving…" : "Save label"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelected(null)}
                    className="rounded-md border border-ink-line px-4 py-2 font-mono text-sm text-parchment-dim hover:text-parchment"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <p className="mt-3 text-sm text-parchment-dim">
                Click a candle on the chart to label it.
              </p>
            )}
          </div>

          {/* Vocabulary */}
          <div className="rounded-lg border border-ink-line p-5">
            <h2 className="font-mono text-[11px] uppercase tracking-eyebrow text-signal">
              Your vocabulary
            </h2>
            {Object.keys(vocabulary).length === 0 ? (
              <p className="mt-3 text-sm text-parchment-dim">
                No labels yet. The terms you use most will collect here — the
                start of how the assistant learns your style.
              </p>
            ) : (
              <div className="mt-3 flex flex-wrap gap-2">
                {Object.entries(vocabulary).map(([term, count]) => (
                  <span
                    key={term}
                    className="rounded-full border border-ink-line bg-ink-raised px-3 py-1 font-mono text-xs text-parchment"
                  >
                    {term} <span className="text-parchment-faint">×{count}</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Library */}
        <div className="mt-6">
          <h2 className="font-mono text-[11px] uppercase tracking-eyebrow text-parchment-faint">
            Your labeled candles · {annotations.length}
          </h2>
          {annotations.length === 0 ? (
            <p className="mt-3 text-sm text-parchment-dim">
              Nothing labeled yet on {symbol}.
            </p>
          ) : (
            <div className="mt-3 overflow-x-auto rounded-lg border border-ink-line">
              <table className="w-full border-collapse font-mono text-xs">
                <thead>
                  <tr className="border-b border-ink-line text-parchment-faint">
                    <Th>Date</Th><Th>Label</Th><Th>RSI(14)</Th><Th>Note</Th><Th></Th>
                  </tr>
                </thead>
                <tbody>
                  {annotations.map((a) => (
                    <tr key={a.id} className="border-b border-ink-line/50">
                      <Td>{a.date}</Td>
                      <Td><span className="text-signal">{a.label}</span></Td>
                      <Td>{a.indicators?.rsi14 ?? "—"}</Td>
                      <Td><span className="text-parchment-dim">{a.note || "—"}</span></Td>
                      <Td>
                        <button
                          type="button"
                          onClick={() => remove(a.id)}
                          className="text-parchment-faint hover:text-loss"
                          aria-label="Delete annotation"
                        >
                          ✕
                        </button>
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

function Th({ children }: { children?: React.ReactNode }) {
  return <th className="px-3 py-2 text-left font-medium">{children}</th>;
}
function Td({ children }: { children?: React.ReactNode }) {
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
