"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { api, setAuthToken } from "@/lib/api";

type AuthUser = { user_id: string; email: string };

type AuthCtx = {
  user: AuthUser | null;
  token: string | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const Ctx = createContext<AuthCtx | null>(null);

// Token is held in memory and mirrored to sessionStorage so a refresh doesn't
// log the user out. (Artifacts can't use storage, but a real Next app can; in
// the Claude preview this degrades gracefully to in-memory only.)
const STORAGE_KEY = "veridian_token";

function readStored(): string | null {
  try {
    return window.sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStored(token: string | null) {
  try {
    if (token) window.sessionStorage.setItem(STORAGE_KEY, token);
    else window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* storage unavailable — in-memory only */
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  // On mount, try to restore a session.
  useEffect(() => {
    const stored = readStored();
    if (stored) {
      setAuthToken(stored);
      api
        .me()
        .then((u) => {
          setUser(u);
          setToken(stored);
        })
        .catch(() => {
          setAuthToken(null);
          writeStored(null);
        })
        .finally(() => setReady(true));
    } else {
      setReady(true);
    }
  }, []);

  const apply = (token: string, u: AuthUser) => {
    setAuthToken(token);
    writeStored(token);
    setToken(token);
    setUser(u);
  };

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.login({ email, password });
    apply(res.token, { user_id: res.user_id, email: res.email });
  }, []);

  const signup = useCallback(async (email: string, password: string) => {
    const res = await api.signup({ email, password });
    apply(res.token, { user_id: res.user_id, email: res.email });
  }, []);

  const logout = useCallback(() => {
    setAuthToken(null);
    writeStored(null);
    setToken(null);
    setUser(null);
  }, []);

  return (
    <Ctx.Provider value={{ user, token, ready, login, signup, logout }}>
      {children}
    </Ctx.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
