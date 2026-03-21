# 🚀 HANDOFF: NM i AI 2026 – Tripletex Agent Rebuild

**Date:** 2026-03-21 17:58  
**Current Score:** 7.3 / 28/30 tasks / Rank #275  
**Target:** 54.5 (beat brother at #59)  
**Session:** dAIhl → Cursor (SuperPowers)

---

## 📊 SITUATION

**What We Found:**
- Brother scored 54.5 points (27-28/30 tasks, rank #59)
- We scored 7.3 points (9-10/30 tasks partial, rank #275)
- Gap: 47 points = ~18 unsolved task types

**Root Cause Analysis (via Sonnet):**
- Using **broken endpoints** (GET /ledger/paymentType → 404)
- Wrong endpoint method (`POST /invoice/payment` → 405, should be `PUT`)
- **Wasting iterations** discovering required fields late (iteration 5-6 of 8)
- Agent doesn't validate payloads before submission (vouchers not balanced, dates missing)
- System prompt too verbose → Claude overthinks instead of executes

**What Works:**
- ✅ create_customer, create_employee, create_product (simple)
- ✅ Payment registration (PUT /invoice/{id}/:payment) – proven 7/7
- ✅ Orders, invoices (with correct date ranges)
- ✅ Minimal prompts force execution over planning

---

## 🔧 REBUILD STATUS

### Completed
- ✅ Endpoint analysis (38 tasks, 204 errors parsed)
- ✅ Dead endpoint identification (GET /ledger/paymentType, POST /invoice/payment, etc.)
- ✅ Payload templates designed (minimal, correct structures)
- ✅ System prompt rewritten (ultra-minimal, execution-focused)
- ✅ Auto-context loading designed (pre-fetch admin, VAT types)

### Next Steps (IN CURSOR)

1. **Verify rebuild in workspace**
   ```bash
   cd /home/fridtjofdahl/.openclaw/workspace-coding/nm-ai-2026-round2
   git diff HEAD~1 agent.py  # See changes
   git status
   ```

2. **Test locally (5 min)**
   - Start server: `python3 -m uvicorn main:app --host 0.0.0.0 --port 8001`
   - Hit test endpoint: `curl http://localhost:8001/`

3. **Submit (1 submission)**
   - Should see improvement immediately (43% → 80%+ success rate target)

4. **Analyze logs**
   - `tail -100 /tmp/agent_live.log`
   - Parse errors, feed back to agent

5. **Iterate (SuperPowers loop)**
   - Brainstorm: "What's failing now?"
   - Plan: "Fix these 3 endpoints"
   - Execute: Update agent, restart, submit
   - Review: Read logs, learn pattern

---

## 📋 WORKING ENDPOINTS (ONLY THESE)

### Simple Creates (1 call each)
- ✅ POST /customer → create_customer(name, email)
- ✅ POST /employee → create_employee(firstName, lastName, email)
- ✅ POST /product → create_product(name, number)
- ✅ POST /department → create_department(name)

### Payment (Proven working)
- ✅ PUT /invoice/{id}/:payment → register_payment(invoice_id, date, amount, payment_type_id)

### Multi-step (Needs testing)
- ✅ POST /order → create_order(customer, lines, orderDate, deliveryDate)
- ✅ POST /invoice → create_invoice(customer, lines, invoiceDate, invoiceDueDate)
- ✅ PUT /invoice/{id}/:createCreditNote → create_credit_note(date, comment)

### Broken (REMOVE)
- ❌ GET /ledger/paymentType → 404
- ❌ POST /invoice/payment → 405 (use PUT instead)
- ❌ POST /project/activity → 405 (doesn't exist)
- ❌ POST /ledger/voucher → 422 (needs complex posting structure)
- ❌ /salary/* → 500 errors (API broken)

---

## 🎯 SUPERPOWERS WORKFLOW

### Phase: Brainstorm
**Command:** `/superpowers:brainstorm "Why are we at 7.3? What's the biggest gap?"`

**Goal:** Identify next highest-value task type to solve

### Phase: Plan
**Command:** `/superpowers:write-plan "Fix [endpoint]. Required: [fields]. Test: [payload]. Submit: [condition]"`

**Goal:** Write out the exact fix before coding

### Phase: Execute
**Command:** `/superpowers:execute-plan "[implementation steps]"`

**Goal:** Build + test + submit systematically

### Phase: Review
**Command:** `/superpowers:review "Logs show [error]. Root cause: [analysis]. Fix: [next step]"`

**Goal:** Learn from each failure

---

## 📈 SUCCESS METRICS

**Immediate (after rebuild):**
- Target: 10-12/30 tasks = 8.0+ score
- Success: Error rate drops from 43% → 20%

**Medium (5-10 submissions):**
- Target: 15-18/30 tasks = 9.0+ score
- Get above rank #100

**Long term (before deadline 2026-03-22 15:00):**
- Target: 27/30 tasks = 10.0+ score
- Beat brother (54.5 = rank #59)

---

## 🚀 IMMEDIATE ACTION (IN CURSOR)

1. **Verify code:**
   ```bash
   git log --oneline -5
   grep -n "def create_customer" agent.py
   ```

2. **Start server:**
   ```bash
   pkill -f uvicorn; sleep 1
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 &
   sleep 2 && curl http://localhost:8001/
   ```

3. **Test payload:**
   ```bash
   curl -X POST http://localhost:8001/ \
     -H "Content-Type: application/json" \
     -d '{"prompt":"Create a customer named Test", "tripletex_credentials":{"base_url":"https://kkpqfuj-amager.tripletex.dev/v2", "session_token":"..."}}' 
   ```

4. **Read latest logs:**
   ```bash
   tail -50 /tmp/agent_live.log
   ```

5. **When ready: SUBMIT** and watch scores climb! 🎯

---

## 📚 KEY FILES

- `agent.py` – Main agent loop (rebuilt with minimal prompt)
- `tripletex_client.py` – API client (dead endpoints removed)
- `main.py` – FastAPI server
- `/tmp/agent_live.log` – Live logs (read after every submit!)
- `LEARNING.md` – Lessons learned (update continuously)

---

## 💡 REMEMBER

- **Score = sum of all successes** (can only go up)
- **Rank matters more than score** (beat brother = win)
- **Read logs after EVERY submit** (learn the pattern)
- **Minimal payload = higher success** (brother figured this out)
- **Test locally first** (don't waste submissions)
- **SuperPowers = your thinking amplifier** (use it!)

---

**YOU GOT THIS.** 🔥

Trust the rebuild. Trust the process. **CLIMB.** 💪
