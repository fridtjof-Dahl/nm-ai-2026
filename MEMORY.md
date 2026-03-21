# dAIhl Master Memory

Sist oppdatert: 21. mars 2026

---

## 🔴 L0 – SANNTID

### System Status
| System | Status | Merknad |
|--------|--------|---------|
| Bybit API | ✅ LIVE | Key: ElynMsBxpGdYhK8jEA |
| Trading alerts | ❌ AV | Skru på når klar til å trade |
| Polymarket bot | ⏸️ PAUSET | XGBoost ikke trent |
| Morning Brief | ✅ 07:45 | Med Calendar + Gmail + Crypto |
| Daily Report | ✅ 09:00 | TG + email (English) alle 5 repos |
| Ukesrapport | ✅ Fredag 15:00 | TG + email (English) |
| Månedssummary | ✅ Siste dag 15:00 | TG + email (English) |
| Kveldssjekk | ✅ 23:00 | Hverdager, Haiku |
| Crisis Alert | ✅ 12t | Haiku |

### Rapport-system
**English. Sendes til: rikard@purgemedia.no + fridtjof@visionmedia.no**
- Per prosjekt: commits + status + next week
- ⚡ F & R Effect (tid spart i uker)
- 💰 Estimated Market Value (NOK: copywriter 500/art, dev 1500/t, SEO 1200/t)

### Repos (alle klonet til /workspace-coding/)
- NorPept, enkelfinansiering, Alarm-Service, Bedriftskaffen, mynewcasino
- GitHub token: ~/.secrets/github-token.txt ([REDACTED_GITHUB_TOKEN]

### Neste milestones
1. NorPept bilder → nettsiden (norpept.com)
2. Discodahl raw footage → ~/content/discodahl/raw/
3. Send $100 USDC til Polygon ([REDACTED_KEY])
4. Fiks Polymarket XGBoost model

---

## 🤖 AGENT-SYSTEM

### 9 Telegram Bots (alle tokens i TOOLS.md)
dAIhl/news, Polymarket, Stream, Trading, Research, Sales, Life, Content, Coding

### Delegering
Produktbilder/visuelt → content | Nettside/API → coding | Trading → trading | Admin/faktura → admin

### Agent Briefs: /workspace-news/briefs/

---

## 🎨 AI PRODUKTBILDER
1. Be om referansebilde FØR start
2. Generer med Imagen 4 (imagen-4.0-generate-001) via Gemini API
3. Backup: fal.ai FLUX Pro (ingen daglig kvote)
4. Upload via GOG CLI

**NorPept FINAL:** https://drive.google.com/drive/folders/17ZPj_a0i-GFYqHcm9jPfbUiD34HjPhWI

---

## 🌐 KUNDER

| Kunde | Drive | Notion |
|-------|-------|--------|
| NorPept | [mappe](https://drive.google.com/drive/folders/1SiNTiRGQ7ovkOXzJhrzSSUqKpmcjWm8g) | [portal](https://notion.so/327999b3958281ddb5cbc370d7b8991f) |
| Brinaxi | [mappe](https://drive.google.com/drive/folders/1eb-njZaGqCXYoKCsIoL75qiDtk8MtGbe) | [portal](https://notion.so/327999b3958281b5b716f1f56f420ebe) |
| Enkel Fin | nettside: enkelfinansiering.no | – |

One-shot setup: `python3 setup_new_customer.py --customer "Navn"`

---

## 🔧 CREDENTIALS (.secrets/)
| Service | Nøkkel |
|---------|--------|
| Bybit | ElynMsBxpGdYhK8jEA / SrUt0IxOAUf5nGJi6AFoICFRF7H7MVayEgvg |
| Gemini | [REDACTED_GOOGLE_KEY]
| fal.ai | [REDACTED_UUID]:ed014578fafab2d2d290d42443f51c60 |
| Polymarket | Polygon: [REDACTED_KEY] |
| Notion | [REDACTED_NOTION_TOKEN]
| GOG | fridtjof123@gmail.com / openclaw |
| Anthropic | [REDACTED_ANTHROPIC_KEY]

---

## 👤 FRIDTJOF DAHL
Oslo, grunnlegger VisionMedia.no (2017–), Discodahl, Bybit-trader, fridtjof123@gmail.com

---

## 📚 VIKTIGE REGLER
- ALDRI anta tall – alltid hent real data
- ALDRI si noe fungerer uten å ha testet det
- Les logger etter hver feil FØR neste forsøk
- Haiku for enkle tasks, Sonnet for komplekst
- Ny session = lavere context-kostnad
