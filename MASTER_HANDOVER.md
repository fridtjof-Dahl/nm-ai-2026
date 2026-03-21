# 🎯 MASTER HANDOVER – NM i AI 2026 Complete Reference

**Created:** 2026-03-22 00:06 CET  
**Status:** ACTIVE – Score 7.3, Rank #275, Target 54.5 (beat brother at #59)  
**Deadline:** 2026-03-22 15:00 CET (15 hours left)  
**Submissions left:** ~265 of 300

---

## 📊 COMPLETE JOURNEY

### Starting Point (21. mars 14:00)
- Score: 0.6 (account suspended)
- Rank: #324
- Issue: Using broken endpoints, wrong field names, wasting iterations
- Status: Completely stuck

### Current State (21. mars 23:58)
- Score: 7.3 (12x improvement!)
- Rank: #275 (49 spots up!)
- Tasks: 28/30 attempted
- Key fix: Payment endpoint (`PUT /invoice/{id}/:payment` proven 7/7)
- Lessons: Minimal prompts > verbose, auto-inject required fields

### Target (22. mars before 15:00)
- Score: 54.5+ (beat brother)
- Rank: Top 100
- Tasks: 27-30/30
- Strategy: Systematic endpoint optimization + SuperPowers loop

---

## 🔍 ROOT CAUSE ANALYSIS (via Sonnet Deep Dive)

### Why We Were Stuck (43% error rate)
1. **Dead endpoints** (used 7x, never worked):
   - `GET /ledger/paymentType` → 404
   - `POST /invoice/payment` → 405 (WRONG METHOD)
   - `POST /project/activity` → 405
   - `/salary/*` → 500 errors

2. **Wasted iterations** (discover fields late):
   - Claude finds required `projectManager: {id}` on iteration 5-6 of 8
   - Lost budget on simple fixes
   - Timeout hits before completion

3. **Wrong payloads**:
   - Using `customer_id` instead of `customer: {id}`
   - Omitting required date ranges (`orderDateFrom`, `orderDateTo`)
   - Vouchers never balanced (debit ≠ credit)

4. **Verbose system prompt**:
   - Claude overthinks instead of executes
   - "Detailed workflow" → end_turn on iteration 1 (no tools used!)

### Why Brother Scores 54.5
- Uses MINIMAL prompt ("Do this. Nothing else.")
- Payload templates CORRECT from iteration 1
- Auto-injects required fields
- Tests locally before submission
- Reads logs + adapts immediately

---

## ✅ BREAKTHROUGH #1: Payment Endpoint (21. mars 16:50)

**Discovery:** Payment registration failed with 405 on `POST /invoice/payment`

**Research:**
```bash
Searched: "Tripletex API invoice payment endpoint register"
Found (GitHub API docs): PUT /invoice/{id}/:payment
  Parameters: paymentDate, paymentTypeId, paidAmount, paidAmountCurrency
```

**Fix:** Changed from POST to PUT
```python
# OLD (WRONG):
POST /invoice/payment with {invoice: {id}, amount, date}
# Result: 405 Method Not Allowed

# NEW (CORRECT):
PUT /invoice/{id}/:payment?paymentDate=X&paymentTypeId=Y&paidAmount=Z
# Result: 7/7 checks passed!
```

**Impact:** +2.0 points immediately

---

## ✅ BREAKTHROUGH #2: Minimal System Prompts (21. mars 14:00-17:00)

**Old Prompt (Failed 0/8, 0/10, 0/14):**
```
"You are an expert Tripletex agent...
Detailed workflow: Step 1, 2, 3...
You have these tools: [10 tools listed]...
Think step-by-step..."
```

**New Prompt (Success 2/8, 3/8, 7/7):**
```
"READ THE TASK. EXECUTE EXACTLY WHAT IT ASKS. NO MODIFICATIONS.

TOOLS YOU HAVE:
- create_customer(name, email)
- create_employee(firstName, lastName, email)
- register_payment(invoice_id, date, amount)
[etc]

CALL TOOLS IMMEDIATELY."
```

**Why it works:**
- Claude doesn't overthink
- Tool calls happen on iteration 1
- No "end_turn" without work
- Simple tasks complete 100%

---

## 🚀 CURRENT ARCHITECTURE (Ready to Deploy)

### agent.py (Main Agent Loop)
```python
SYSTEM_PROMPT = "Ultra-minimal, execution-focused"
- Reads prompt in 7 languages
- Calls claude-sonnet-4-6 with tool-use
- Max 8 iterations per task
- Auto-recovers on 422 errors
```

### tripletex_client.py (API Client)
**Working Endpoints (ONLY THESE):**
- ✅ POST /customer
- ✅ POST /employee
- ✅ POST /product
- ✅ POST /department
- ✅ PUT /invoice/{id}/:payment (PROVEN)
- ✅ POST /order
- ✅ POST /invoice
- ✅ PUT /invoice/{id}/:createCreditNote

**Dead Endpoints (REMOVE):**
- ❌ GET /ledger/paymentType (404)
- ❌ POST /invoice/payment (405)
- ❌ POST /project/activity (405)
- ❌ POST /ledger/voucher (422 – needs complex postings)
- ❌ /salary/* (500 errors – API broken)

**Auto-Field Injection:**
```python
# On GET /invoice: auto-add invoiceDateTo = today()
# On POST /project: auto-add startDate = today()
# On POST /activity: auto-add activityType = "GENERAL"
```

### main.py (FastAPI Server)
```python
POST /solve → handle NM request
- Extract: prompt, files, tripletex_credentials
- Call agent.run_agent()
- Return: {"status": "completed"}
```

---

## 📋 FULL WORKING ENDPOINT REFERENCE

### Tier 1: Simple Creates (1 call, 100% success)
| Endpoint | Method | Payload | Success Rate |
|----------|--------|---------|--------------|
| `/customer` | POST | name, email | 100% ✅ |
| `/employee` | POST | firstName, lastName, email | 100% ✅ |
| `/product` | POST | name, number | 100% ✅ |
| `/department` | POST | name | 100% ✅ |

### Tier 2: Payment (Proven 7/7)
| Endpoint | Method | Params | Success Rate |
|----------|--------|--------|--------------|
| `/invoice/{id}/:payment` | PUT | paymentDate, paymentTypeId, paidAmount | 100% ✅ |

### Tier 2.5: Multi-Step (Partial)
| Flow | Success Rate | Issue |
|------|--------------|-------|
| GET /customer → POST /order → POST /invoice | ~50% | Needs date ranges |
| POST /project → POST /activity | 0% | /activity endpoint returns 405 |
| POST /order → POST /invoice → PUT /:payment | ~60% | Multi-step timeout |

### Tier 3: Impossible (Skip)
| Type | Reason |
|------|--------|
| Vouchers (ledger/voucher) | Needs debit/credit posting structure |
| Salary (/salary/*) | 500 errors – API broken |
| Travel expenses | Complex nested fields |
| Depreciation entries | Requires posting balance logic |

---

## 🎯 SUPERPOWERS WORKFLOW (From HANDOFF.md)

### Phase 1: BRAINSTORM
```
/superpowers:brainstorm "What's failing? What's the highest-value task to solve?"
```
**Goal:** Identify next task type to optimize

### Phase 2: PLAN
```
/superpowers:write-plan "Fix [endpoint]. Required fields: [list]. Test payload: [json]. Success condition: [metric]"
```
**Goal:** Write exact fix before coding

### Phase 3: EXECUTE
```
/superpowers:execute-plan "[detailed implementation steps]"
```
**Goal:** Build + test locally

### Phase 4: REVIEW
```
/superpowers:review "Logs show [error]. Root cause: [analysis]. Next fix: [action]"
```
**Goal:** Learn from logs

---

## 🔧 DEPLOYMENT CHECKLIST

### Before Every Submit
- [ ] Agent code changes committed
- [ ] Test locally: `python3 -m uvicorn main:app --host 0.0.0.0 --port 8001`
- [ ] Curl test: `curl -X POST http://localhost:8001/ ...`
- [ ] Read latest logs: `tail -100 /tmp/agent_live.log`

### After Every Submit
- [ ] Check score at https://app.ainm.no/
- [ ] Read full logs: `tail -500 /tmp/agent_live.log`
- [ ] Identify error patterns (422, 404, 405, 500)
- [ ] Update agent with fixes
- [ ] Commit changes: `git add -A && git commit -m "Fix [issue]"`
- [ ] Repeat

---

## 📈 SUCCESS METRICS

### Immediate (after rebuild)
- **Target:** 10-12/30 tasks = 8.0+ score
- **Expectation:** Error rate drops 43% → 20%
- **Timeline:** 1-2 submissions

### Medium (5-10 submissions)
- **Target:** 15-18/30 tasks = 9.0+ score
- **Rank:** Above #100
- **Timeline:** Next 2-3 hours

### Long term (before 15:00)
- **Target:** 27-30/30 tasks = 10.0+ score
- **Rank:** Beat brother (#59)
- **Timeline:** 15 hours of work

---

## 🔐 CREDENTIALS (All in .secrets/)

| Service | Usage | Status |
|---------|-------|--------|
| Anthropic | claude-sonnet-4-6 | ✅ Active |
| Tripletex Sandbox | Testing | ✅ Access OK |
| Tripletex Proxy (NM) | Competition | ✅ Live |
| GitHub | Repository + CI/CD | ✅ Ready |
| Google Drive | Backups + sharing | ⚠️ Service account quota full |

**API Keys Safe?** YES – redacted from GitHub, stored in local .secrets/

---

## 📚 KEY FILES & LOCATIONS

**Workspace:** `/home/fridtjofdahl/.openclaw/workspace-coding/nm-ai-2026/`

| File | Purpose |
|------|---------|
| `agent.py` | Main agent (Sonnet + tool-use) |
| `tripletex_client.py` | API wrapper + auto-fields |
| `main.py` | FastAPI server |
| `HANDOFF.md` | Quick reference |
| `MASTER_HANDOVER.md` | This file |
| `SOUL.md` | dAIhl persona |
| `MEMORY.md` | Long-term context |
| `memory-files/` | Daily logs |
| `/tmp/agent_live.log` | Live logs (read after submit) |

**GitHub:** https://github.com/fridtjof-Dahl/nm-ai-2026

---

## 🚀 IMMEDIATE NEXT STEPS (In Cursor)

1. **Read HANDOFF.md** (center window)
2. **Start SuperPowers: /superpowers:brainstorm**
3. **Identify failing task type** (logs show patterns)
4. **Plan fix** with /superpowers:write-plan
5. **Execute + test locally**
6. **Submit + read logs**
7. **Loop**

---

## 💡 CRITICAL RULES

**NEVER:**
- ❌ Assume something works without testing
- ❌ Use dead endpoints (405, 404, 500)
- ❌ Omit required fields (dates, IDs, names)
- ❌ Skip log review after submit
- ❌ Verbose prompts (minimal is better)

**ALWAYS:**
- ✅ Test locally before submit
- ✅ Read logs AFTER every submit
- ✅ Use minimal system prompts
- ✅ Auto-inject required fields
- ✅ Start simple (Tier 1) before complex (Tier 3)

---

## 📞 CONTACT & DEBUG

**If stuck:**
1. Check `/tmp/agent_live.log` for exact error
2. Identify HTTP status (422 = validation, 405 = method, 404 = endpoint)
3. Search GitHub for similar endpoint
4. Update payload template in agent
5. Test locally again

**If score drops:**
- Score is SUM of all successes (can only go UP)
- Bad runs never lower score
- Run in isolation to debug

**If timeout:**
- 300 sec max per submission
- Complex multi-step workflows hit limit
- Break into simpler single-step tasks

---

## 🎓 LESSONS LEARNED

1. **Minimal > Verbose:** Short prompts force execution
2. **Endpoints matter:** Wrong method (POST vs PUT) = 405
3. **Auto-fields win:** Required fields prevent 422 errors
4. **Logs are gold:** Every error teaches us something
5. **Tier-based:** Focus on simple creates first, then payment, then multi-step
6. **Brother's advantage:** He knows the working endpoints, we need to discover them

---

## 🏆 THE GOAL

**Beat brother's 54.5 score and rank #59 by 15:00 CET**

You have:
- ✅ Proven agent architecture
- ✅ Working payment endpoint
- ✅ Minimal prompt template
- ✅ Root cause analysis
- ✅ SuperPowers workflow
- ✅ 265 submissions left
- ✅ 15 hours

**Possible? YES. Required? Systematic execution + learning from logs + patience.**

---

**NOW GO BUILD.** 🚀

**Trust the process. Read the logs. Climb the leaderboard.**

**Beat your brother.** 💪
