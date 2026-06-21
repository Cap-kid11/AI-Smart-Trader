import ResultCard from "@/components/ResultCard";
import { RESULTS } from "@/lib/backtest-data";

export default function Home() {
  return (
    <main className="min-h-screen">
      <Nav />
      <Hero />
      <Honesty />
      <HowItWorks />
      <Autonomy />
      <Cta />
      <Footer />
    </main>
  );
}

function Nav() {
  return (
    <header className="border-b border-ink-line">
      <div className="mx-auto flex max-w-readable items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <Mark />
          <span className="font-mono text-parchment text-sm tracking-wide">
            VERIDIAN
          </span>
        </div>
        <nav className="hidden gap-8 font-mono text-xs text-parchment-dim sm:flex">
          <a href="#honesty" className="hover:text-parchment">The premise</a>
          <a href="#how" className="hover:text-parchment">How it works</a>
          <a href="#autonomy" className="hover:text-parchment">The arc</a>
        </nav>
        <a
          href="#cta"
          className="font-mono text-xs text-signal hover:text-signal-deep"
        >
          Early access →
        </a>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="bg-grid border-b border-ink-line">
      <div className="mx-auto grid max-w-readable gap-12 px-6 py-20 md:grid-cols-[1.1fr_0.9fr] md:py-28">
        <div className="flex flex-col justify-center">
          <p className="font-mono text-xs uppercase tracking-eyebrow text-signal">
            Strategy backtesting &amp; market education
          </p>
          <h1 className="mt-5 font-sans text-4xl font-semibold leading-[1.1] text-parchment md:text-5xl">
            Most trading tools sell you a number they can&rsquo;t back up.
            <span className="text-parchment-dim">
              {" "}
              This one shows you the truth instead.
            </span>
          </h1>
          <p className="mt-6 max-w-xl text-parchment-dim leading-relaxed">
            Veridian helps you build trading strategies, test them against real
            history, and learn to read the market yourself. No guaranteed win
            rates. No black box. Just honest metrics, candlestick fluency, and
            paper trading under limits you set.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <a
              href="#cta"
              className="rounded-md bg-signal px-5 py-2.5 font-mono text-sm text-ink hover:bg-signal-deep"
            >
              Get early access
            </a>
            <a
              href="#honesty"
              className="font-mono text-sm text-parchment-dim hover:text-parchment"
            >
              Why honesty matters →
            </a>
          </div>
        </div>

        {/* Signature element: real, un-cherry-picked backtest results.
            One won, one lost. Showing the loss is the whole point. */}
        <div className="flex flex-col justify-center gap-4">
          <div className="font-mono text-xs text-parchment-faint">
            <span className="text-parchment-dim">Live from our own engine</span>{" "}
            — two strategies, sample data, nothing hidden:
          </div>
          <ResultCard result={RESULTS.rsi} />
          <ResultCard result={RESULTS.ma} />
          <p className="font-mono text-[11px] leading-relaxed text-parchment-faint">
            The second strategy lost ~19%. We show it because a tool that only
            shows winners is lying to you.
          </p>
        </div>
      </div>
    </section>
  );
}

function Honesty() {
  const lies = [
    "“92% accuracy” with no out-of-sample proof",
    "Guaranteed signals that quietly disappear when wrong",
    "A black box you can never learn from or leave",
    "Backtests tuned until the past looks perfect",
  ];
  const truths = [
    "Real metrics: win rate, drawdown, Sharpe, profit factor",
    "Out-of-sample testing, with no peeking at the future",
    "Patterns explained so you actually learn to read charts",
    "Risk limits and a bail-out switch that you control",
  ];

  return (
    <section id="honesty" className="border-b border-ink-line">
      <div className="mx-auto max-w-readable px-6 py-20">
        <p className="font-mono text-xs uppercase tracking-eyebrow text-signal">
          The premise
        </p>
        <h2 className="mt-4 max-w-2xl font-sans text-3xl font-semibold leading-tight text-parchment">
          A reliable way to beat the market would not be sold to you for a
          monthly fee.
        </h2>
        <p className="mt-5 max-w-2xl text-parchment-dim leading-relaxed">
          The biggest quant funds in the world, with enormous resources, do not
          sustain the win rates that trading-bot ads promise. When a product
          guarantees a number, that number is the product&rsquo;s first lie.
          Veridian is built on the opposite bet: give you rigorous, honest tools
          and teach you to use them.
        </p>

        <div className="mt-12 grid gap-6 md:grid-cols-2">
          <div className="rounded-lg border border-ink-line p-6">
            <div className="font-mono text-xs uppercase tracking-eyebrow text-loss">
              What the category sells
            </div>
            <ul className="mt-4 space-y-3">
              {lies.map((l) => (
                <li key={l} className="flex gap-3 text-sm text-parchment-dim">
                  <span className="text-loss">✕</span>
                  <span>{l}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-lg border border-ink-line bg-ink-raised p-6">
            <div className="font-mono text-xs uppercase tracking-eyebrow text-gain">
              What Veridian gives you
            </div>
            <ul className="mt-4 space-y-3">
              {truths.map((t) => (
                <li key={t} className="flex gap-3 text-sm text-parchment">
                  <span className="text-gain">✓</span>
                  <span>{t}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    {
      n: "01",
      t: "Define a strategy",
      d: "Pick a preset or write your own rules over indicators like RSI and moving averages. Plain logic, no hidden parameters.",
    },
    {
      n: "02",
      t: "Backtest it honestly",
      d: "Run it over real history with no lookahead. Get win rate, drawdown, Sharpe, and profit factor — the numbers that expose a weak idea before it costs you.",
    },
    {
      n: "03",
      t: "Learn to read the chart",
      d: "Veridian detects candlestick patterns precisely and teaches you what they mean, with honest stats on what actually followed them.",
    },
    {
      n: "04",
      t: "Paper trade on your terms",
      d: "Let the assistant trade your chosen strategy in simulation, capped by the position limits and bail-out threshold you set.",
    },
  ];

  return (
    <section id="how" className="border-b border-ink-line">
      <div className="mx-auto max-w-readable px-6 py-20">
        <p className="font-mono text-xs uppercase tracking-eyebrow text-signal">
          How it works
        </p>
        <h2 className="mt-4 font-sans text-3xl font-semibold text-parchment">
          From idea to tested strategy, in the open.
        </h2>
        <div className="mt-12 grid gap-px overflow-hidden rounded-lg border border-ink-line bg-ink-line sm:grid-cols-2">
          {steps.map((s) => (
            <div key={s.n} className="bg-ink p-6">
              <div className="font-mono text-2xl text-signal">{s.n}</div>
              <h3 className="mt-3 font-sans text-lg font-medium text-parchment">
                {s.t}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-parchment-dim">
                {s.d}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Autonomy() {
  const stages = [
    {
      t: "The assistant trades",
      d: "It runs your chosen strategy faithfully, marks the indicators, and executes the rules — within your risk limits.",
    },
    {
      t: "You trade together",
      d: "It advises and explains; you decide. Every call comes with the reasoning, so you&rsquo;re learning the whole way.",
    },
    {
      t: "You trade alone",
      d: "The goal most tools never admit: you understand the market well enough that you don&rsquo;t need the assistant at all.",
    },
  ];

  return (
    <section id="autonomy" className="border-b border-ink-line bg-grid">
      <div className="mx-auto max-w-readable px-6 py-20">
        <p className="font-mono text-xs uppercase tracking-eyebrow text-signal">
          The arc
        </p>
        <h2 className="mt-4 max-w-2xl font-sans text-3xl font-semibold leading-tight text-parchment">
          Built to make itself unnecessary.
        </h2>
        <p className="mt-5 max-w-2xl text-parchment-dim leading-relaxed">
          Most trading products want you dependent forever. Veridian is designed
          to graduate you off of it.
        </p>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {stages.map((s, i) => (
            <div key={s.t} className="relative rounded-lg border border-ink-line bg-ink-raised p-6">
              <div className="font-mono text-xs text-signal">
                STAGE {i + 1}
              </div>
              <h3 className="mt-3 font-sans text-lg font-medium text-parchment">
                {s.t}
              </h3>
              <p
                className="mt-2 text-sm leading-relaxed text-parchment-dim"
                dangerouslySetInnerHTML={{ __html: s.d }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Cta() {
  return (
    <section id="cta" className="border-b border-ink-line">
      <div className="mx-auto max-w-readable px-6 py-24 text-center">
        <h2 className="mx-auto max-w-2xl font-sans text-3xl font-semibold leading-tight text-parchment md:text-4xl">
          Learn the market with a tool that won&rsquo;t lie to you about it.
        </h2>
        <p className="mx-auto mt-5 max-w-xl text-parchment-dim leading-relaxed">
          Veridian is in early development. Join the early-access list to follow
          the build and be first in when it opens.
        </p>
        <div className="mx-auto mt-8 flex max-w-md flex-col items-center gap-3 sm:flex-row">
          <input
            type="email"
            placeholder="you@email.com"
            aria-label="Email address"
            className="w-full rounded-md border border-ink-line bg-ink-raised px-4 py-2.5 font-mono text-sm text-parchment placeholder:text-parchment-faint focus:border-signal"
          />
          <button
            type="button"
            className="w-full rounded-md bg-signal px-5 py-2.5 font-mono text-sm text-ink hover:bg-signal-deep sm:w-auto"
          >
            Notify me
          </button>
        </div>
        <p className="mt-4 font-mono text-[11px] text-parchment-faint">
          No trading advice. Paper trading only. Your data stays yours.
        </p>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer>
      <div className="mx-auto flex max-w-readable flex-col gap-4 px-6 py-10 text-parchment-faint sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <Mark />
          <span className="font-mono text-xs">VERIDIAN</span>
        </div>
        <p className="max-w-md font-mono text-[11px] leading-relaxed">
          Veridian is an educational and strategy-development tool. It does not
          provide investment advice or execute real-money trades. Markets carry
          risk; past results never guarantee future ones.
        </p>
      </div>
    </footer>
  );
}

function Mark() {
  // A small candlestick glyph — a single honest bar with wick.
  return (
    <svg width="14" height="18" viewBox="0 0 14 18" aria-hidden="true">
      <line x1="7" y1="0" x2="7" y2="18" stroke="#E0A84E" strokeWidth="1.5" />
      <rect x="3" y="5" width="8" height="8" fill="#0E1518" stroke="#E0A84E" strokeWidth="1.5" />
    </svg>
  );
}
