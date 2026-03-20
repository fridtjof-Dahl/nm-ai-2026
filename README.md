# NM i AI 2026 – Tripletex AI Accounting Agent

**Target score: 6.0 (perfect + best efficiency on all tiers)**  
**Model: `claude-opus-4-5`** – Maximum reasoning, best tool_use performance

## Architecture

```
POST /solve
    │
    ▼
main.py          ← FastAPI entry point, request parsing
    │
    ▼
agent.py         ← Claude claude-opus-4-5 agentic loop with tool_use
    │
    ▼
tripletex_client.py  ← Typed Tripletex API v2 wrapper
```

### Why claude-opus-4-5?
- Best-in-class reasoning for multi-step workflows
- Superior tool_use accuracy = fewer wasted API calls = higher efficiency bonus
- Handles all 7 languages natively
- Understands accounting domain context deeply

## Quick Start (local)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
uvicorn main:app --host 0.0.0.0 --port 8000
```

Expose via HTTPS for testing:
```bash
npx cloudflared tunnel --url http://localhost:8000
```

Test it:
```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create an employee named John Doe with email john@example.com",
    "sessionToken": "YOUR_TOKEN",
    "companyId": "123",
    "proxyBaseUrl": "https://proxy.ainm.no/tripletex"
  }'
```

## Deploy to Railway (recommended – 5 min)

1. Push to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Set environment variable: `ANTHROPIC_API_KEY=sk-ant-...`
4. Get your public URL (e.g. `https://nm-ai-2026.up.railway.app`)
5. Submit to [app.ainm.no/submit/tripletex](https://app.ainm.no/submit/tripletex)

## Deploy to Vercel (alternative)

```bash
npm i -g vercel
vercel
vercel env add ANTHROPIC_API_KEY
vercel --prod
```

## Supported Task Categories

| Category | Operations |
|---|---|
| Employees | Create, update, delete, set roles, add employment |
| Customers | Create, update, delete, add contacts |
| Products | Create, update |
| Orders | Create with order lines |
| Invoices | Create, register payment, credit note, delete |
| Travel Expenses | Create, delete |
| Projects | Create, delete |
| Departments | Create, update, enable module |
| Modules | Enable/disable company modules |
| Vouchers | Search, reverse |
| Suppliers | Create, update |
| Generic | Any API endpoint via api_get/post/put/delete |

## Scoring Strategy

The agent is optimized for:
1. **100% correctness** – Claude reads the full task before any API call
2. **Minimum API calls** – Plan first, execute once
3. **Zero 4xx errors** – Validate inputs before sending

Efficiency bonus only applies at perfect correctness.  
**Tier 3 + perfect + best efficiency = 6.0 score (max)**

## Files

- `main.py` – FastAPI server + request handling
- `agent.py` – Claude agentic loop, tool definitions, tool executor
- `tripletex_client.py` – Typed Tripletex API wrapper
- `requirements.txt` – Python dependencies
- `vercel.json` – Vercel deployment config
- `railway.json` – Railway deployment config
- `Procfile` – For Railway/Heroku
