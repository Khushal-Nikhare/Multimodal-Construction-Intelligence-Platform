# Multimodal Construction Intelligence Platform

## Deploying to Vercel

This repository is configured as a single Vercel project:

- Vite builds the frontend from `frontend/` into `frontend/dist`.
- `api/index.py` exposes the FastAPI app as a Vercel Python function.
- `/api/*` requests are routed to FastAPI; all other routes fall back to the React app.

### Vercel project settings

Import the repository into Vercel with the repository root as the project root. Keep the
framework preset as **Other** (the checked-in `vercel.json` provides the build settings).
The build command and output directory should be detected as:

```text
npm --prefix frontend ci && npm --prefix frontend run build
frontend/dist
```

### Required environment variables

Add these in Vercel for the Production (and Preview, if needed) environments:

```text
GROQ_API_KEY=<your Groq API key>
GROQ_LLM_MODEL=<supported Groq text model>
GROQ_VISION_MODEL=<supported Groq vision model>
ENVIRONMENT=production
CORS_ORIGINS=https://<your-vercel-domain>
```

The weather URL variables are optional because the application has Open-Meteo defaults:

```text
WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
WEATHER_GEOCODING_URL=https://geocoding-api.open-meteo.com/v1/search
```

Do not commit `.env` or put API keys in frontend environment variables. The Groq key is
used only by the server-side FastAPI function.

### Important Vercel limitations

The AI endpoints are synchronous serverless requests. Their runtime duration is subject
to the Vercel plan's function timeout, and image uploads are subject to Vercel's request
body limit. Large images may be rejected before FastAPI's 10 MB validation runs. For
production workloads with long AI requests or larger uploads, deploy `backend/` to a
long-running Python host and set the frontend API base URL to that backend instead.

After deployment, verify:

```text
https://<your-vercel-domain>/health
https://<your-vercel-domain>/api/info
```
