# Decisions Log

Format: `[KATEGORI] Beslutning → Lærdom/resultat`

Kategorier: TECH | BUSINESS | TRADING | CONTENT | WORKFLOW

---

## Mars 2026

### 14. mars
- **[TECH]** Valgte OpenClaw + Claude Sonnet 4.6 som primær stack
  → Rask oppsett, god integrasjon med Telegram
- **[TECH]** Satte opp 6 agenter på én dag
  → Bevis på at systemet er skalerbart
- **[TECH]** Byttet memory-embedding til Gemini (OpenAI-kvote tom)
  → Gemini Flash som fallback funker godt nok
- **[WORKFLOW]** Satt morgenbrief til kl 09:00
  → Matcher Fridtjofs oppvåkningstid

### 15. mars
- **[WORKFLOW]** Kort, generisk prompt → generisk nettside (Kramer Rør)
  → LÆRDOM: Jo mer kontekst, visjon og tillit i prompten, jo bedre resultat
- **[WORKFLOW]** Bedriftskaffen.no-prompten = gullstandard
  → Fortell historien, gi visuell retning, si "full frihet, stoler på deg"
- **[WORKFLOW]** Vinner-workflow bekreftet:
  1. Opus 4.6 + Thinking mode + Agent mode
  2. Lang, visjonær prompt
  3. Resultat: kramer-ror.vercel.app = ny standard
- **[TECH]** Unsplash-bilder som standard i nettside-prompts
  → Format: `https://images.unsplash.com/photo-[id]?w=1200&q=80`
- **[TECH]** System-optimalisering med Claude Opus
  → Alle SOUL, MEMORY, workflow-filer gjennomgått og oppgradert
  → Ny stream-SOUL.md opprettet
  → Mappestruktur: souls/, memory/, workflows/

---

## Beslutningsprinsipper

Når du logger en ny beslutning, inkluder:
1. Hva var alternativene?
2. Hvorfor valgte vi dette?
3. Hva er risikoen?
4. Når bør vi evaluere om det var riktig?

## Beslutninger som venter

| Beslutning | Deadline | Avhenger av |
|-----------|----------|-------------|
| Paper → live trading | 18. mars | Paper-resultater |
| Stream-agent aktivering | TBD | BotFather-token |
| Repurpose.io oppsett | TBD | Stream-agent live |
| Første outreach-batch | Denne uken | Outreach-maler klar |

## 17. mars 2026 – M51 AI OS analyse
**Hva de har vi mangler:**
- PPC Agent (Google Ads-spesialist)
- SEO Agent (dedikert)
- Analytics Agent (GA4/Search Console)
- CRO Agent (konverteringsoptimalisering)
- Competitor Agent (overvåker konkurrenter)
- AI Visibility Agent (GEO/AI søk)
- Reporting Agent (automatiske rapporter)
- Guardian (brannsikring/overvåking)
- Mastermappe (merkevare-kontekst per kunde)

**Prismodell vi bør stjele:**
- Starter: 2 450 kr/mnd
- Pro: 7 450 kr/mnd (17 agenter)
- Enterprise: 14 950 kr/mnd
- Agency (white-label): 24 950 kr/mnd

**Konsepter å ta:**
- "Mastermappe" – tone of voice, strategi, målgrupper per kunde
- Sanntidsanalyse fra GA4+Ads+Search Console i ett dashboard
- "11 timer spart per uke" – kommuniser konkret verdi
- White-label agency-plan

**VisionMedias fortrinn:**
- Vi bygger nettsider også (M51 gjør ikke det)
- Raskere onboarding
- Billigere inngangsterskel

## 17. mars 2026 – Prediction Market Bot strategi (Noisy/@noisyb0y1)
Kilde: https://x.com/noisyb0y1/status/2033602811187884139

**Kjernekonsept: Edge Detection + Kelly Criterion**

FORMLER:
- edge = p_model - p_mkt (trade kun når edge > 0.04)
- Kelly: f = (p*b - q) / b, bruk 0.25-0.35 fractional Kelly
- EV = p*b - (1-p) → trade kun når EV > 0
- Mispricing Z-score: δ = (p_model - p_mkt) / σ → δ > 1.5 = full pipeline

VALIDERINGS-GATES (alle må passere før ordre):
1. edge_gate: edge > 0.04
2. ev_gate: EV > 0
3. kelly_gate: size = kelly(f, bankroll)
4. exposure_gate: exp + bet ≤ max_exp
5. var_gate: VaR(95%) ≤ daily_limit
6. mdd_gate: MDD(30d) < 0.08
7. brier_gate: BS < 0.22 (kalibreringskvalitet)

RISIKOREGLER:
- Target Sharpe Ratio > 2.0
- Max Drawdown blokkerer trading ved MDD > 8%, 72h cooldown
- Profit Factor > 1.5 (ellers compound-skill review)
- Monte Carlo VaR med 10,000+ paths

IMPLEMENTERE:
- Polymarket-scanner + Kelly-sizing
- 7 validerings-gates i Python
- Bayes-oppdatering av p_model ved ny info
- Win rate target: 78.3%

## 17. mars 2026 – Arcads + OpenClaw video pipeline
Kilde: @everestchris6 på X

KONSEPT:
- OpenClaw researcher trending topics + skriver scripts
- Arcads genererer video med AI-avatar (realistisk person)
- Poster automatisk til TikTok/Instagram/X
- Flere kontoer, flere personas, alt 24/7

FOR VISIONMEDIA:
- Discodahl-avatar: AI + trading + consciousness content
- VisionMedia-avatar: markedsføringstips til bedrifter
- Kan brukes for kunder også (selge som tjeneste!)

NESTE STEG:
1. Sjekk Arcads.ai – pris og API
2. Koble til Stream-agenten vår
3. Stream-agent: research → script → Arcads video → auto-post

Dette er en ENORM mulighet for VisionMedia som produkt til kunder.

## 17. mars 2026 – Research Agent mangler
BEHOV: Dedikert Research Agent
- Send URL/tema → dyptgående analyse
- Finner konkurrenter, priser, muligheter
- Leverer briefing til andre agenter
- Gjør hele systemet smartere over tid

BRUKSTILFELLER:
- "Research okara.ai" → pris, features, API
- "Research konkurrenter til VisionMedia" 
- "Research trading-strategi X"
- "Research Arcads vs HeyGen vs Synthesia"

NESTE STEG: Sett opp Research-agent med Perplexity API som primær kilde

## 17. mars 2026 – Trading dataregel (UFRAVIKELIG)
**REGEL: Aldri gjetning. Alltid live Bybit API-data.**

Før enhver trading-analyse eller anbefaling:
1. Hent live pris fra Bybit API
2. Hent 4H + 1H klines
3. Beregn EMA, S/R-nivåer fra faktiske data
4. Finn funding rates
5. KUN DERETTER gi analyse eller anbefaling

Brudd på denne regelen = ugyldig analyse.
Script: /tmp/full_analysis.py

## 17. mars 2026 – Lead Scraping Stack (endelig løsning)

**Nåværende stack (gratis/lavkost):**
- Serper.dev → LinkedIn-profiler via Google-søk (2500 gratis)
- Serper.dev → E-post via Google-søk (~40-50% treffsannsynlighet)
- Perplexity API → Enrichment (bedrift, telefon, kontekst)
- Google Drive → CSV-backup
- Notion → CRM med Lead Pipeline database

**Scripts:**
- Scraping: workspace-coding/lead-scraper/scraper.py
- E-post-søk: /tmp/find_email.py (regex fra Google snippets)
- Notion upload: /tmp/create_notion_db.py + enrich_notion.py

**Treffsannsynlighet e-post:** ~40-50%
**Kostnad:** ~$0 (innenfor gratis tiers)

**Neste oppgradering når vi har råd:**
- Hunter.io ($34/mnd) → 70-80% treffsannsynlighet
- Apollo.io ($49/mnd) → 85%+ treffsannsynlighet

**LinkedIn DM er bedre enn e-post for norske leads uansett.**

## 17. mars 2026 – Notion Lead Pipeline regel
REGEL: Én scraping = ett eget Notion-ark

Navnekonvensjon: "[Målgruppe] – Potensielle kunder"
Eksempler:
- "AI Stack – Potensielle kunder" ✅
- "Recruitment Managers – Potensielle kunder" ✅
- "Google Maps Leads – Rørleggere Oslo" ✅

Hvert ark får samme struktur:
- Navn, Tittel, Bedrift, E-post, Telefon, LinkedIn
- Nettside, Ansatte, Poststed, Orgnr
- Status (Ny/Kontaktet/Dialog/Demo/Kunde/Ikke interessert)
- Produkt (AI Stack/AutoPost/Google Ads/SEO/Nettside)
- Score, Dato funnet, Notater

Brreg API er standard for norske leads – gratis e-post + telefon.
