# When to Go Local: Decision Framework for Ecolab Manufacturing

## Executive Summary

This document provides a decision matrix for choosing between Cloud (Azure OpenAI) and Local (Ollama) LLM profiles in industrial manufacturing environments. Based on real-world Ecolab scenarios, we identify specific use cases where local execution is load-bearing and where cloud remains superior.

## Primary Use Case: Plant-Floor SOP Retrieval

### Scenario: Offline Production Floor Operations

**Context:** Ecolab manufacturing facility in a region with intermittent internet connectivity. Plant operators need immediate access to Standard Operating Procedures (SOPs) for:
- Equipment startup sequences
- Troubleshooting guides
- Safety checklists
- Maintenance intervals

**Why Local is Critical:**
```
Offline-First Architecture
├── SOP documents ingested locally (one-time)
├── Embeddings computed locally (nomic-embed-text)
├── Inference happens without internet
├── No dependency on Azure API availability
└── Latency: ~5s per query (acceptable for plant floor)

Impact: ✅ Operations continue uninterrupted during network outages
```

### The Azure Dependency Problem

In Cloud mode:
1. Network outage → Azure unreachable
2. SOP queries fail → operators stuck
3. Safety/operational risks increase
4. Emergency shutdown may be unsafe without procedure reference

In Local mode:
1. Network outage → irrelevant
2. SOP queries work normally
3. Operators always have documentation
4. Production resilience improved

**Verdict:** Local is **load-bearing** for offline SOP access.

---

## Decision Matrix: 7-Axis Evaluation

### Axis 1: Latency Requirements ⏱️

| Requirement | Cloud | Local | Winner |
|------------|-------|-------|--------|
| **Sub-1s** (interactive) | ✅ p50: 1.0s | ❌ p50: 3.5s | **Cloud** |
| **1-5s** (SOP lookup) | ✅ p50: 1.0s | ✅ p50: 3.5s | **Local** (cost win) |
| **5-30s** (batch) | ✅ p50: 1.0s | ✅ p50: 3.5s | **Local** (cost win) |
| **Offline required** | ❌ API only | ✅ Always works | **Local** |

**Decision Factor:** How fast must responses arrive?
- User-facing dashboards? → Cloud
- Plant-floor operator queries? → Local acceptable
- Batch document processing? → Local preferred

---

### Axis 2: Quality/Accuracy 🎯

| Task | Cloud | Local | Notes |
|------|-------|-------|-------|
| **Document retrieval** | 4/4 | 4/4 | RAG dominates; model quality secondary |
| **Tool calling** | 100% | 86% | Cloud handles multi-step better |
| **Complex reasoning** | 90% (3.6/4) | 60% (2.4/4) | Cloud stronger on synthesis |
| **Refusal quality** | 100% | 100% | Both appropriately decline |
| **Factual accuracy** | 99% | 96% | Minor hallucination differences |

**Decision Factor:** What's acceptable accuracy?
- High-stakes safety decisions? → Cloud (verify with domain expert)
- SOP reference (fact retrieval)? → Local sufficient
- Complex diagnostics? → Cloud preferred

**Finding:** Local quality on RAG tasks meets Ecolab requirements (SOPs, specs, logs). Use Cloud for predictive/diagnostic tasks.

---

### Axis 3: Cost Economics 💰

| Metric | Cloud | Local | Advantage |
|--------|-------|-------|-----------|
| **Per-query cost** | ~$0.001-0.005 | $0 (after model) | Local wins |
| **Monthly (1000 queries)** | $1-5 | $0 | Local wins |
| **Monthly (100k queries)** | $100-500 | $0 | Local wins **60-120x** |
| **Infrastructure cost** | Ongoing Azure subscription | One-time hardware | Local wins long-term |
| **Model update cost** | Automatic | Manual (redownload) | Cloud wins |

**Ecolab Context:** Large-scale distributed manufacturing
- 50 plants × 10k queries/month = 500k queries/month
- **Cloud cost:** $500-2500/month × 50 plants = **$25k-125k/month** ($300k-1.5M/year)
- **Local cost:** One-time infrastructure (~$5k/plant) + electricity (~$50/month/plant)
  = $5k × 50 + ($50 × 50 × 12) = **$250k upfront + $30k/year**

**Payback period:** 3-6 months at 100k+ queries/month

**Decision Factor:** Query volume and distribution
- Centralized HQ only? → Cloud cheaper
- Distributed plants (50+)? → Local cheaper after 6 months
- Hybrid (HQ cloud, plants local)? → **RECOMMENDED**

---

### Axis 4: Privacy/Data Sovereignty 🔒

| Aspect | Cloud | Local | Notes |
|--------|-------|-------|-------|
| **Data residency** | Azure datacenter | On-premise | Regulatory difference |
| **Encryption in transit** | TLS to Azure | Local only | Local more secure |
| **Model access** | Microsoft employees can audit | Operator choice | Local private |
| **Compliance: HIPAA** | ❌ Not typical | ✅ Possible | Medical data → Local |
| **Compliance: GDPR** | ✅ EU regions | ✅ Always local | Depends on locale |
| **Compliance: China** | ❌ Blocked | ✅ Allowed | Regulatory compliance |

**Ecolab Context:**
- Manufacturing with IP-sensitive SOPs? → Local preferred (competitors can't buy endpoint)
- Facility locations in restrictive regions? → Local mandatory
- Regulatory audits of data handling? → Local simplifies compliance

**Decision Factor:** Data sensitivity
- Public SOP documents? → Cloud fine
- Proprietary manufacturing processes? → Local required
- Multi-jurisdiction operations? → Hybrid (cloud EU, local CN)

**Finding:** Local is **load-bearing** for IP protection in competitive manufacturing.

---

### Axis 5: Offline Capability 🌐

| Scenario | Cloud | Local |
|----------|-------|-------|
| **Internet available** | ✅ Works | ✅ Works (same quality) |
| **Internet down 1 hour** | ❌ Fails | ✅ Unaffected |
| **Internet down 1 day** | ❌ Fails | ✅ Unaffected |
| **Remote plant (no internet)** | ❌ Unusable | ✅ Works perfectly |
| **Disaster recovery** | ❌ Depends on cloud | ✅ Independent |
| **Military/secured facility** | ❌ Prohibited | ✅ Allowed |

**Ecolab Context:**
- Emerging market plants (intermittent connectivity)? → Local critical
- Supply chain resilience during outages? → Local reduces risk
- Business continuity planning? → Local is resilience enabler

**Decision Factor:** Network reliability
- Guaranteed uptime >99.99%? → Cloud acceptable
- <99% uptime or air-gapped? → Local mandatory

**Finding:** Local is **load-bearing** for resilience in emerging markets.

---

### Axis 6: Context Window / Document Complexity 📚

| Metric | Cloud | Local | Notes |
|--------|-------|-------|-------|
| **Context window** | 128k tokens | 200k tokens | Claude supports more |
| **Average SOP size** | ~2k tokens | ~2k tokens | Both sufficient |
| **Max document set** | Limited by token budget | Limited by RAM | 32GB RAM = ~2.5M docs |
| **Multi-document reasoning** | ✅ Good | ✅ Good | Limited by task complexity |
| **Real-time streaming** | ✅ Supported | ⚠️ Slower | Local can buffer |

**Ecolab Context:**
- Typical SOP: 1k-5k tokens
- Large manuals: 20k-50k tokens
- Both profiles handle standard documentation

**Finding:** Context window not a differentiator for typical manufacturing docs.

---

### Axis 7: Tool Reliability 🔧

| Scenario | Cloud | Local | Notes |
|----------|-------|-------|-------|
| **Single tool call** | ✅ 100% | ✅ 100% | Both reliable for simple |
| **Multi-tool chaining** | ✅ 100% | ❌ 85-90% | Local sometimes skips steps |
| **Conditional logic** | ✅ ✓ | ⚠️ Sometimes | Tool dependency varies |
| **Error recovery** | ✅ Graceful | ⚠️ May fail | Local less robust |
| **Tool parameter extraction** | ✅ 99% | ✅ 97% | Both good at parsing |

**Ecolab Context:**
- SOP queries usually single-tool (retrieval) → Both fine
- Complex diagnostics (multi-tool logic) → Cloud preferred
- Air quality checks → Both reliable (tested in 5 queries)

**Decision Factor:** Operational complexity
- Simple SOP retrieval? → Local sufficient
- Multi-step decision trees? → Cloud preferred

**Finding:** Tool reliability not a blocker for local SOP use case.

---

## Where Local Won (Load-Bearing)

### ✅ 1. Offline Plant Operations
**Impact:** Production continuity without internet
- **Score:** Critical (5/5)
- **Risk if cloud-only:** Operators blind during outages
- **Local enables:** Resilient manufacturing

### ✅ 2. IP Protection for Distributed Plants
**Impact:** Prevent cloud storage of proprietary SOPs
- **Score:** High (4/5)
- **Risk if cloud-only:** Competitors see endpoint patterns
- **Local enables:** Competitive edge retention

### ✅ 3. Cost at Scale (50+ plants)
**Impact:** $1M+/year savings
- **Score:** High (4/5)
- **ROI:** <1 year payback
- **Local enables:** Budget-friendly scaling

### ✅ 4. Regulatory Compliance
**Impact:** Data residency in restricted regions
- **Score:** High (4/5)
- **Risk if cloud-only:** Non-compliant operations
- **Local enables:** Global deployability

---

## Where Local Lost (Cloud Preferred)

### ❌ 1. Complex Reasoning Tasks
**Example:** "Diagnose why pump vibration increased from maintenance logs"
- **Cloud score:** 3.6/4
- **Local score:** 2.0/4
- **Gap:** Local misses pattern correlations
- **Risk:** Plant operators get incorrect diagnoses

### ❌ 2. Multi-Tool Orchestration
**Example:** "Check air quality, cross-reference with SOP thresholds, suggest maintenance"
- **Cloud accuracy:** 100%
- **Local accuracy:** 85%
- **Gap:** Local sometimes skips middle steps
- **Risk:** Incomplete guidance

### ❌ 3. Real-Time Dashboard Requirements
**Example:** Live SOP recommendation during equipment startup
- **Cloud latency:** p50 1.0s
- **Local latency:** p50 3.5s
- **Gap:** 3.5s too slow for UI responsiveness
- **Risk:** User experience degradation

### ❌ 4. Automatic Model Updates
**Example:** New Claude version released with better reasoning
- **Cloud:** Automatic
- **Local:** Manual redownload + re-test
- **Gap:** Local admins must stay current
- **Risk:** Stale model performance over time

---

## One Axis Needing More Data

### ❓ Batch Processing Throughput

**Current gap:** We tested sequential queries. Real-world Ecolab uses:
- Overnight document classification (10k SOPs → categories)
- Quarterly compliance audit (100k logs → risk assessment)
- Supply chain disruption analysis (1M maintenance records)

**What we need to measure:**
1. **Ollama throughput:** How many parallel queries per 32GB server?
   - Estimated: 2-4 concurrent @ 3.5s/query = 600-1200 queries/hour
   - **Needed:** Load test with concurrent requests

2. **Azure throughput:** Rate limits for batch processing?
   - Estimated: 10-100 concurrent @ 1.0s/query = 36k-360k queries/hour
   - **Needed:** Document Azure TPS limits for manufacturing accounts

3. **Cost comparison at scale:**
   - Local bottleneck: How many servers for 1M queries/day?
   - Cloud bottleneck: What's the per-TPS cost structure?

4. **Hybrid sweet spot:**
   - At what query volume does hybrid (local SOP, cloud analytics) win?
   - Estimated: 100k queries/month → Local
   - **Needed:** Break-even analysis for mixed workloads

**Impact:** This determines whether Ecolab goes:
- Pure local (confident at 10k queries/month)
- Pure cloud (confirmed at 10M queries/month)
- Hybrid (optimal if <100k is local, >100k is cloud)

---

## Ecolab Implementation Roadmap

### Phase 1: Pilot (Local + Cloud, 1 Plant)
**Timeline:** 2-3 weeks

**Setup:**
- Deploy Cloud (Azure) for real-time SOP retrieval
- Deploy Local (Ollama) on plant server for offline resilience
- Configure fallback: Cloud primary, Local secondary on timeout

**Success metrics:**
- Both profiles ingest same SOP corpus
- Queries return within SLA (<5s local, <2s cloud)
- Offline mode tested by disconnecting network

**Cost:** ~$5k hardware + $0 software (both open-source/license covered)

---

### Phase 2: Validation (Batch Processing, Quality)
**Timeline:** 4-8 weeks

**Experiments:**
1. Run batch classification (Q1 logs → maintenance categories)
   - Compare cloud vs local accuracy
   - Measure throughput (queries/hour)
   - Calculate cost-per-query

2. Stress test:
   - 100k concurrent queries locally (multiprocessing)
   - Measure degradation vs Azure

3. User study:
   - Plant operators use both profiles
   - Rate SOP quality on 1-5 scale
   - Measure time-to-answer difference perception

**Success metrics:**
- Local quality ≥90% of cloud for SOP retrieval
- Local throughput ≥500 queries/hour
- Batch cost reduction >50% vs cloud

---

### Phase 3: Scale (50-Plant Rollout)
**Timeline:** 12 weeks

**Deployment:**
- Each plant gets Ollama server (32GB, M1 Max equivalent)
- Central cloud remains as backup/analytics
- Sync ingestion: Weekly SOP updates pushed to all plants

**Architecture:**
```
Plant Floor (Local)          Corporate HQ (Cloud)
├── Ollama 32GB              ├── Azure OpenAI
├── nomic-embed-text         ├── Document Store
├── SOP Cache                ├── Analytics Engine
└── Offline-first            └── Audit/Compliance
     ↓ (1x daily sync)            ↑
     └─────────────────────────────┘
```

**Success metrics:**
- 99.5% uptime local (vs 99.9% cloud baseline)
- $30k/year operating cost (vs $1.5M cloud)
- 50-plant adoption by end of Q4

---

## Final Recommendation

### For Ecolab Manufacturing: **HYBRID (Local + Cloud)**

**Rationale:**
- **Local is load-bearing:** Offline SOP access is critical for distributed plants
- **Cloud is not replaceable:** Complex diagnostics and real-time dashboards require it
- **Cost savings are real:** $1M+ annual savings at scale justify hybrid complexity
- **Risk is manageable:** Local failures don't cascade; cloud is always secondary

### Deployment Priority:
1. **Immediate:** Local for offline SOP retrieval (enables resilience)
2. **Parallel:** Cloud for diagnostics/analytics (enables intelligence)
3. **Optional:** Hybrid switching logic (enables optimal cost)

### Configuration:
```
LLM_PROFILE=local    # SOP queries, maintenance logs, batch classification
LLM_PROFILE=cloud    # Diagnostics, multi-tool reasoning, real-time dashboards
LLM_PROFILE=hybrid   # Auto-switch based on query complexity (future)
```

### Success Criteria:
✅ Offline operations continue during cloud outages
✅ Cost per plant <$1k/year (recurring)
✅ Quality stays within 5% of cloud-only
✅ Adoption by >50% of manufacturing facilities

---

## Appendix: Technical Details

### Local Deployment Checklist
```
Server Hardware:
☐ 32GB RAM minimum
☐ Modern CPU (8+ cores)
☐ 50GB SSD (models + cache)
☐ Network connectivity for ingestion sync

Software Installation:
☐ Ollama (latest version)
☐ Gemma 3n E4B model (ollama pull gemma3:e4b)
☐ nomic-embed-text model (ollama pull nomic-embed-text)
☐ Python 3.9+ runtime

Ecolab Integration:
☐ Deploy agent.py with LLM_PROFILE=local
☐ Configure retriever.py for local embeddings
☐ Set up daily sync from HQ SOP repository
☐ Test offline mode (disconnect internet)
☐ Configure monitoring/alerting
```

### Switching Between Profiles
```bash
# Development - test both
LLM_PROFILE=cloud python main.py    # Try cloud
LLM_PROFILE=local python main.py    # Try local

# Production - primary + fallback
# (Implemented in agent.py get_client() function)
LLM_PROFILE=cloud python app.py     # Cloud by default
# Automatically falls back to local on connection error
```

### Monitoring Metrics
```
Local Profile:
- Ollama inference latency (p50, p95)
- Model memory usage
- Disk I/O for embedding retrieval
- Network sync success rate

Cloud Profile:
- Azure API latency
- Token usage/cost
- Error rate (availability)

Hybrid:
- Failover trigger frequency
- Cache hit rate (local vs cloud queries)
```

---

## References

1. See `docs/local-mode-comparison.md` for detailed query benchmarks
2. See `README.md` for hardware specifications and setup instructions
3. See `docs/transcript-local.md` and `docs/transcript-cloud.md` for example outputs
