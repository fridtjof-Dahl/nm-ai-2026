# NM i AI 2026 – COMPLETE DOCUMENTATION SUMMARY

**Read:** 2026-03-21 13:51-14:00 CET. Alle 13 task-dokumenter.

---

## 🎯 TRIPLETEX (Task 1: AI Accounting Agent)

### Format
- **Endpoint:** POST /solve
- **Timeout:** 300 sec (5 min)
- **Auth:** Basic Auth (username=0, password=session_token)
- **Input:** JSON with `prompt` (Norwegian), `files` (base64 PDF/images), `tripletex_credentials` (base_url + session_token)
- **Output:** `{"status": "completed"}`

### Scoring
- **Field-by-field checks** (correctness)
- **Tier multiplier:** ×1 (Tier 1), ×2 (Tier 2), ×3 (Tier 3)
- **Efficiency bonus:** Up to 2× multiplier for perfect correctness with minimal API calls
- **Best score per task kept** – bad runs never lower score
- **Max score:** 6.0 (Tier 3 perfect + efficiency bonus)

### Key Rules
- Read `tripletex_credentials.base_url` from request (not hardcoded sandbox)
- Handle 7 languages: Norwegian, English, Spanish, Portuguese, Nynorsk, German, French
- Some tasks include file attachments (decode from base64)
- All API calls through proxy base_url
- Use fields parameter for selective retrieval
- Handle 422 errors — they specify required fields

### Common Patterns
1. **Create entity:** POST /employee, /customer, /product
2. **Create with linking:** GET /customer → POST /order → POST /invoice
3. **Modify:** GET → PUT
4. **Delete/reverse:** DELETE
5. **Multi-step:** Pagination, linked entities, file parsing

### Tier Release
- **Tier 1 & 2:** Open now
- **Tier 3:** Opens Saturday morning

### Rate Limits
- Verified teams: 3 concurrent, 10 per task/day
- Unverified: 1 concurrent, 3 per task/day

---

## 🌍 ASTAR ISLAND (Task 2: Viking Civilization Prediction)

### Format
- **API Base:** https://api.ainm.no/astar-island
- **Auth:** JWT Bearer token or cookie
- **Core task:** Observe 40×40 map through 15×15 viewport, predict terrain probabilities

### Simulation
- **50 years** of simulation
- **6 terrain classes:** Empty (0), Settlement (1), Port (2), Ruin (3), Forest (4), Mountain (5)
- **5 seeds per round** – different random outcomes
- **50 queries total** – shared across all 5 seeds

### Mechanics
- **Growth:** Settlements expand, produce food, build ports
- **Conflict:** Settlements raid (desperate = aggressive), capture territories
- **Trade:** Ports trade for wealth/food
- **Winter:** Severe/mild, settlements starve → collapse → ruins
- **Environment:** Forests reclaim ruins, settlements rebuild sites

### Scoring
- **Entropy-weighted KL divergence** between prediction and ground truth
- **CRITICAL:** Never assign 0.0 probability to any class! If ground truth has p>0 but you predict 0, KL → infinity
- **Fix:** Enforce minimum 0.01 per class, then renormalize to sum to 1.0
- **Score:** max(0, min(100, 100 × exp(-3 × weighted_kl)))
- **Final:** Average of 5 seed scores

### Endpoints
- `GET /rounds` – list all rounds
- `GET /rounds/{id}` – initial states + settlements
- `GET /budget` – remaining queries
- **`POST /simulate`** – observe one viewport (costs 1 query, returns grid + settlements)
- **`POST /submit`** – submit H×W×6 probability tensor for one seed

### Key Insight
- Only 50 queries for entire round – be strategic
- Static cells (ocean→ocean, mountain→mountain) don't count toward scoring
- Weight high-entropy cells (uncertain outcomes)
- Small probability floor (0.01) protects against catastrophic failures

---

## 📦 NORGESGRUPPEN DATA (Task 3: Object Detection)

### Format
- **Upload:** ZIP file with run.py at root
- **Input:** /data/images/ with JPEG files (img_XXXXX.jpg)
- **Output:** /output/predictions.json (JSON array)
- **Timeout:** 300 sec
- **GPU:** NVIDIA L4 (24 GB VRAM), auto-detected

### Submission ZIP
```
submission.zip
├── run.py (required)
├── model.onnx (optional)
└── utils.py (optional)
```

**Limits:**
- Max uncompressed: 420 MB
- Max files: 1000
- Max Python files: 10
- Max weight files: 3
- Allowed types: .py, .json, .yaml, .cfg, .pt, .pth, .onnx, .safetensors, .npy

### run.py Contract
```bash
python run.py --input /data/images --output /output/predictions.json
```

Output JSON format:
```json
[
  {
    "image_id": 42,
    "category_id": 0,
    "bbox": [120.5, 45.0, 80.0, 110.0],
    "score": 0.923
  }
]
```
- **image_id:** From filename (img_00042.jpg → 42)
- **category_id:** 0-355 from training annotations
- **bbox:** [x, y, width, height] in COCO format
- **score:** Confidence 0-1

### Scoring
- **70% detection mAP** (IoU ≥ 0.5, category ignored)
- **30% classification mAP** (IoU ≥ 0.5 + correct category_id)
- Detection-only (all category_id=0) scores up to 0.70 max
- Final: 0.7 × detection_mAP + 0.3 × classification_mAP

### Training Data
- **COCO dataset:** 248 images, ~22,700 annotations, 356 product categories
- **Product reference:** 327 products with multi-angle photos
- **Categories:** IDs 0-355 (product names), 356 = unknown_product

### Sandbox Environment
- Python 3.11
- PyTorch 2.6.0+cu124
- ultralytics 8.1.0 (YOLOv8, RT-DETR)
- torchvision 0.21.0
- ONNX runtime 1.20.0
- 4 vCPU, 8 GB RAM, NVIDIA L4 GPU
- **NO NETWORK ACCESS** (offline)
- 300 sec timeout

### Security Restrictions (CRITICAL)
**BLOCKED imports:**
- os, sys, subprocess, socket, ctypes, builtins, importlib
- pickle, marshal, shelve, shutil
- yaml (use json)
- requests, urllib, http.client
- multiprocessing, threading, signal

**BLOCKED calls:**
- eval(), exec(), compile(), __import__(), getattr() (dangerous names)
- Binaries, symlinks, path traversal

**USE INSTEAD:**
- pathlib for files
- json for config

### Models
**Pre-installed + pinned versions required:**
- YOLOv8 (ultralytics==8.1.0)
- Faster R-CNN, RetinaNet (torchvision==0.21.0)
- timm models (timm==0.9.12)

**NOT installed:**
- YOLOv9, YOLOv10, YOLO11, Detectron2, MMDetection
- **Solution:** Export to ONNX or include model code

### Submission Limits
- 2 in-flight per team
- 3 per day
- Infrastructure failures: 2 free per day

---

## 📊 OVERALL SCORING

| Task | Weight | Max Score |
|------|--------|-----------|
| Tripletex | 33% | 6.0 |
| Astar Island | 33% | 100 |
| NorgesGruppen | 33% | 1.0 |

**Leaderboard score** = average normalized across all 3 tasks

---

## 🚫 CRITICAL MISTAKES (From NorgesGruppen Ban)

1. ❌ Included `import os` in run.py → security scan triggered
2. ❌ Didn't read security restrictions before coding
3. ❌ Never tested locally in sandbox environment
4. ❌ Submitted blind (no baseline testing first)

**NEVER DO THIS AGAIN:**
- Always check security policy FIRSTbefore writing code
- Always test locally/in sandbox before submission
- Always read ALL docs before building
- Random baseline first, then iterate

---

## 📋 REQUIRED SETUP (For Round 2+)

### Before Coding
1. ✅ Read ALL task docs (13 URLs)
2. ✅ Understand scoring formula
3. ✅ Test code locally
4. ✅ Check security policy
5. ✅ Verify imports are allowed

### Before Submission
1. ✅ Random baseline works
2. ✅ Output format is correct
3. ✅ ZIP structure is correct
4. ✅ No disallowed imports
5. ✅ Timeout is safe (<300s)

### After Submission
1. ✅ Read logs immediately
2. ✅ Understand failure reason
3. ✅ Fix root cause
4. ✅ Don't spam (3 per day limit)

---

## 🎯 NEXT ROUND STRATEGY

**Tripletex:**
- Build agent with proper error handling
- Test each task type in sandbox
- Optimize for efficiency (minimize API calls)
- Tier 3 opens Saturday – prepare in advance

**Astar Island:**
- Start with simple uniform baseline
- Use 10-15 queries to understand map patterns
- Build probabilistic model
- Enforce 0.01 floor on ALL probabilities

**NorgesGruppen (APPEAL PENDING):**
- Wait for appeal decision
- If approved: Remove `import os`, resubmit
- If rejected: Rebuild with YOLOv8 baseline + fine-tuning
- Safety check: No forbidden imports

---

**Finish time:** 14:00 CET
**Next deadline:** 15:00 CET (60 min remaining)
