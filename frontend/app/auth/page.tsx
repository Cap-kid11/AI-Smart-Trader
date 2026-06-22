"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";

export default function AuthPage() {
  const { login, signup } = useAuth();
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true);
    setErr(null);
    try {
      if (mode === "signup") await signup(email, password);
      else await login(email, password);
      router.push("/dashboard");
    } catch (e) {
      setErr(
        e instanceof ApiError
          ? e.message
          : "Couldn't reach the API. Is the backend running on :8000?"
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen">
      <header className="border-b border-ink-line">
        <div className="mx-auto flex max-w-readable items-center px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <Mark />
            <span className="font-mono text-sm text-parchment">VERIDIAN</span>
          </Link>
        </div>
      </header>

      <div className="mx-auto flex max-w-sm flex-col px-6 py-16">
        <h1 className="font-sans text-2xl font-semibold text-parchment">
          {mode === "login" ? "Welcome back" : "Create your account"}
        </h1>
        <p className="mt-2 text-sm text-parchment-dim">
          {mode === "login"
            ? "Log in to your strategies, labels, and paper portfolio."
            : "Free to start. Your portfolio and labels are saved to your account."}
        </p>

        {err && (
          <div className="mt-4 rounded-md border border-loss/40 bg-loss/5 p-3 font-mono text-xs text-loss">
            {err}
          </div>
        )}

        <div className="mt-6 space-y-3">
          <label className="block">
            <span className="font-mono text-[11px] uppercase tracking-eyebrow text-parchment-faint">
              Email
            </span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-md border border-ink-line bg-ink-raised px-3 py-2.5 font-mono text-sm text-parchment focus:border-signal"
            />
          </label>
          <label className="block">
            <span className="font-mono text-[11px] uppercase tracking-eyebrow text-parchment-faint">
              Password
            </span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit()}
              placeholder={mode === "signup" ? "at least 8 characters" : ""}
              className="mt-1 w-full rounded-md border border-ink-line bg-ink-raised px-3 py-2.5 font-mono text-sm text-parchment placeholder:text-parchment-faint focus:border-signal"
            />
          </label>
          <button
            type="button"
            onClick={submit}
            disabled={busy || !email || !password}
            className="w-full rounded-md bg-signal px-4 py-2.5 font-mono text-sm text-ink hover:bg-signal-deep disabled:opacity-50"
          >
            {busy ? "…" : mode === "login" ? "Log in" : "Sign up"}
          </button>
        </div>

        <button
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "signup" : "login");
            setErr(null);
          }}
          className="mt-4 font-mono text-xs text-parchment-dim hover:text-parchment"
        >
          {mode === "login"
            ? "Need an account? Sign up"
            : "Already have an account? Log in"}
        </button>

        <p className="mt-8 font-mono text-[11px] leading-relaxed text-parchment-faint">
          Veridian is an education tool. No real-money trading, no investment
          advice. We only store your email and a hashed password.
        </p>
      </div>
    </main>
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
