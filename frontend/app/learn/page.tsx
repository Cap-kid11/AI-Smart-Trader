"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, ApiError, type Lesson } from "@/lib/api";

const USER_ID = "demo-user";

type Msg = { role: "user" | "tutor"; text: string; live?: boolean };

export default function Tutor() {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [symbol, setSymbol] = useState("SAMPL");
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [liveAvailable, setLiveAvailable] = useState<boolean | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    (async () => {
      try {
        const [s, l] = await Promise.all([api.symbols(), api.lessons()]);
        setSymbols(s.symbols);
        setLessons(l.lessons);
        setLiveAvailable(l.live_coaching_available);
      } catch {
        setErr("Couldn't reach the API. Start the backend on :8000.");
      }
    })();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  const send = async (text: string) => {
    const q = text.trim();
    if (!q || busy) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setBusy(true);
    setErr(null);
    try {
      const res = await api.askTutor({ question: q, symbol, user_id: USER_ID });
      setMessages((m) => [...m, { role: "tutor", text: res.answer, live: res.live }]);
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : "Couldn't reach the tutor.");
    } finally {
      setBusy(false);
    }
  };

  const starters = [
    "What is a hammer, and does it actually work?",
    "How do candlesticks work?",
    "What does follow-through mean?",
    "Explain bullish engulfing.",
  ];

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
            <Link href="/studio" className="hover:text-parchment">Teach</Link>
            <span className="text-parchment">Learn</span>
          </nav>
        </div>
      </header>

      <div className="mx-auto grid max-w-readable gap-8 px-6 py-8 lg:grid-cols-[1fr_320px]">
        {/* Chat */}
        <section className="flex min-h-0 flex-col">
          <div className="flex items-end justify-between gap-4">
            <div>
              <h1 className="font-sans text-xl font-semibold text-parchment">
                Learn to read the chart
              </h1>
              <p className="mt-1 max-w-lg text-sm text-parchment-dim">
                Ask anything about candles and patterns. The tutor explains — it
                never tells you what to trade.
              </p>
            </div>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="rounded-md border border-ink-line bg-ink-raised px-3 py-1.5 font-mono text-xs text-parchment focus:border-signal"
            >
              {(symbols.length ? symbols : ["SAMPL"]).map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>

          {liveAvailable === false && (
            <div className="mt-4 rounded-md border border-ink-line bg-ink-raised p-3 font-mono text-[11px] text-parchment-dim">
              Live coaching isn&rsquo;t configured (no API key set), so answers
              come from the built-in lessons. Set ANTHROPIC_API_KEY on the
              backend for personalized, context-aware coaching.
            </div>
          )}

          {err && (
            <div className="mt-4 rounded-md border border-loss/40 bg-loss/5 p-3 font-mono text-xs text-loss">
              {err}
            </div>
          )}

          <div
            ref={scrollRef}
            className="mt-4 min-h-[320px] flex-1 space-y-4 overflow-y-auto rounded-lg border border-ink-line bg-ink-raised p-4"
          >
            {messages.length === 0 ? (
              <div className="space-y-3">
                <p className="font-mono text-xs text-parchment-faint">
                  Try a starter question:
                </p>
                <div className="flex flex-wrap gap-2">
                  {starters.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => send(s)}
                      className="rounded-full border border-ink-line px-3 py-1.5 text-left font-mono text-xs text-parchment-dim hover:border-signal hover:text-parchment"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m, i) => <Bubble key={i} msg={m} />)
            )}
            {busy && (
              <div className="font-mono text-xs text-parchment-faint">
                Tutor is thinking…
              </div>
            )}
          </div>

          <div className="mt-3 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send(input)}
              placeholder="Ask about a candle or pattern…"
              className="flex-1 rounded-md border border-ink-line bg-ink-raised px-3 py-2.5 font-sans text-sm text-parchment placeholder:text-parchment-faint focus:border-signal"
            />
            <button
              type="button"
              onClick={() => send(input)}
              disabled={busy || !input.trim()}
              className="rounded-md bg-signal px-5 py-2.5 font-mono text-sm text-ink hover:bg-signal-deep disabled:opacity-50"
            >
              Ask
            </button>
          </div>
        </section>

        {/* Lessons library */}
        <aside>
          <h2 className="font-mono text-[11px] uppercase tracking-eyebrow text-signal">
            Pattern lessons
          </h2>
          <div className="mt-3 space-y-2">
            {lessons.map((l) => (
              <details
                key={l.key}
                className="rounded-lg border border-ink-line bg-ink-raised p-3"
              >
                <summary className="cursor-pointer font-sans text-sm font-medium text-parchment">
                  {l.title}
                </summary>
                <div className="mt-2 space-y-2 text-xs leading-relaxed text-parchment-dim">
                  <p><span className="text-parchment-faint">What:</span> {l.what}</p>
                  <p><span className="text-parchment-faint">Why:</span> {l.why}</p>
                  <p><span className="text-parchment-faint">Watch for:</span> {l.watch_for}</p>
                </div>
              </details>
            ))}
          </div>
        </aside>
      </div>
    </main>
  );
}

function Bubble({ msg }: { msg: Msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={isUser ? "flex justify-end" : "flex justify-start"}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-signal/15 text-parchment"
            : "border border-ink-line text-parchment-dim"
        }`}
      >
        {!isUser && (
          <div className="mb-1 font-mono text-[10px] uppercase tracking-eyebrow text-parchment-faint">
            Tutor {msg.live ? "· live" : "· lesson"}
          </div>
        )}
        <div className="whitespace-pre-wrap font-sans">{msg.text}</div>
      </div>
    </div>
  );
}

function Mark() {
  return (
    <svg width="14" height="18" viewBox="0 0 14 18" aria-hidden="true">
      <line x1="7" y1="0" x2="7" y2="18" stroke="#E0A84E" strokeWidth="1.5" />
      <rect x="3" y="5" width="8" height="8" fill="#0E1518" stroke="#E0A84E" strokeWidth="1.5" />
    </svg>
  );
}
