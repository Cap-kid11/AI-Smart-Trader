# Deploying Veridian

A precise walkthrough to put Veridian live: the **backend API + Postgres** on
Railway (or Render), and the **frontend** on Vercel. Result: a public URL you
can share with clients or put on your résumé.

You do the clicks (you own the accounts and credentials). Everything is already
configured — this guide tells you the order and the settings.

**Time:** ~30–45 minutes the first time.
**Cost:** free tiers cover all of this.

---

## Before you start

1. Push the whole repo to GitHub (you're using Cursor for git already).
2. Have these ready to create free accounts: Railway (or Render) and Vercel.
   Sign in to both with GitHub — it makes connecting the repo one click.

The repo has two deployable folders: `backend/` and `frontend/`. They deploy
separately.

---

## Part 1 — Backend API + database (Railway)

Railway is the simplest for a student: free tier, one-click Postgres, deploys
from a Dockerfile (already in `backend/`).

1. **New project** → *Deploy from GitHub repo* → pick your repo.
2. When it asks for the service root / directory, set it to **`backend`**.
   Railway will detect the `Dockerfile` and `railway.json`.
3. **Add a database:** in the project, *New* → *Database* → *PostgreSQL*.
   Railway creates it and exposes a `DATABASE_URL` variable.
4. **Set environment variables** on the API service (*Variables* tab):

   | Variable | Value |
   |---|---|
   | `VERIDIAN_DB_URL` | `${{Postgres.DATABASE_URL}}` (reference the DB you added) |
   | `JWT_SECRET` | a long random string — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DATA_PROVIDER` | `csv` for now (switch to `alpaca` later) |
   | `CORS_ORIGINS` | leave blank for now — you'll set it after Part 2 |

5. **Deploy.** When it's up, Railway gives you a public URL like
   `https://veridian-api-production.up.railway.app`. **Copy it.**
6. **Verify:** open `<that URL>/health` — you should see
   `{"status":"ok",...}`. And `<that URL>/docs` shows the interactive API.

> Render alternative: import the repo, point it at `backend/render.yaml`
> (a "Blueprint"). It creates the API + free Postgres and wires them
> automatically. You'll still set `CORS_ORIGINS` after Part 2.

---

## Part 2 — Frontend (Vercel)

1. **New Project** → import the same GitHub repo.
2. Set **Root Directory** to **`frontend`**. Vercel auto-detects Next.js.
3. **Environment variable:**

   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_BASE` | the backend URL from Part 1 (e.g. `https://veridian-api-production.up.railway.app`) |

4. **Deploy.** Vercel gives you a URL like `https://veridian.vercel.app`.
   **Copy it.**

---

## Part 3 — Connect them (CORS)

The backend must allow requests from your frontend's domain.

1. Back on Railway (or Render), set the API's `CORS_ORIGINS` variable to your
   Vercel URL, e.g. `https://veridian.vercel.app`
   (comma-separate if you have more than one domain).
2. Redeploy the backend (Railway redeploys on variable change automatically;
   if not, trigger it).
3. Open your Vercel URL, sign up for an account, run a backtest. It's live.

---

## Part 4 (optional) — Go live with real market data

1. Create a free account at https://alpaca.markets and get **paper-trading**
   API keys.
2. On the backend host, set:
   - `DATA_PROVIDER` = `alpaca`
   - `ALPACA_API_KEY` = your key
   - `ALPACA_SECRET_KEY` = your secret
3. Redeploy. The dashboard's badge will switch to **LIVE DATA** and real tickers
   (AAPL, MSFT, etc.) become available.

---

## Going forward

- **Custom domain:** both Vercel and Railway let you attach one (e.g.
  `veridian.app`) in their settings. Nice for client-facing demos.
- **Auto-deploy:** every push to your main branch redeploys both. Keep `main`
  clean.
- **Secrets:** never commit real keys. They live only in the host's variables
  and your local `.env` (which is gitignored).

---

## Troubleshooting

- **Frontend loads but every call fails / CORS error in console:**
  `CORS_ORIGINS` on the backend doesn't match your exact Vercel URL (check
  https vs http, trailing slash). Fix and redeploy the backend.
- **502 / app won't boot on the backend:** check the deploy logs. Most common
  cause is a missing `JWT_SECRET` or a bad `VERIDIAN_DB_URL`.
- **"Not authenticated" everywhere:** expected until you sign up/log in on the
  live site — tokens from localhost don't carry over.
- **Database errors on first boot:** tables are created automatically on import;
  if it fails, confirm `VERIDIAN_DB_URL` points at the Postgres instance.
