# Bookkeeping Web

## Setup

```bash
cd /Users/kerriewalubengo/Desktop/bookkeeping/web
npm install
```

## Run

```bash
npm run dev
```

## API Base

Set `NEXT_PUBLIC_API_BASE` to point at the FastAPI server.

```bash
export NEXT_PUBLIC_API_BASE="http://localhost:8000"
```

## Prisma (optional)

```bash
cp .env.example .env
npm install
npx prisma generate
```

Prisma is used by the Next.js app for direct reads if needed. The API remains backed by SQLAlchemy.

## PWA Install

This app is installable on iOS and Windows as a PWA.

Steps:
1. Host the app over HTTPS (required for iOS install).
2. Open the app in Safari on iOS, tap Share, then "Add to Home Screen".
3. On Windows, open in Chrome/Edge and choose Install.

Service worker and manifest are already wired in `web/public`.

## Deploy Guide (HTTPS Required)

PWA install on iOS requires HTTPS. Choose one:

### Vercel
1. Create a Vercel project for `/Users/kerriewalubengo/Desktop/bookkeeping/web`.
2. Set env vars:
   - `NEXT_PUBLIC_API_BASE` = your FastAPI URL (e.g., `https://api.example.com`)
3. Deploy. Vercel auto-provisions HTTPS.

### Netlify
1. Build command: `npm run build`
2. Publish directory: `.next`
3. Set env var `NEXT_PUBLIC_API_BASE` to your FastAPI URL.
4. Deploy; Netlify provides HTTPS.

### API Hosting Notes
If the API is on a different domain, ensure CORS is enabled in FastAPI.
