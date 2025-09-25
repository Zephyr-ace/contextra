# Contextra

Real-time insights connecting world events to your portfolio’s future.

## Goal
Provide **financial peace of mind** by tracing how world events impact a portfolio and converting that into **buy/hold/sell** recommendations with **confidence** and an **impact path**.

## Problem We Solve
- **Hidden risks**: second-order effects (suppliers, regulation, geopolitics) are missed.
- **Scale & noise**: fragmented sources; humans can’t connect signals fast enough.
- **Vague outputs**: many LLM tools lack quantified impact or verifiable reasoning.

## Approach (end-to-end)
1. **Monitor** — ingest high-signal news/research/filings around portfolio components.
2. **Graph Factory** — extract typed entities & relations to build/refresh an **Investment Graph** for each stock/sector (nodes categories: companies, products, people, events, regulations; edges (no categories): more flexible, reasoning model concludes them).
3. **Reaction Chain** — trace event → intermediaries → portfolio component to capture indirect effects.
4. **Impact Score** — aggregate influence along weighted paths (edge/type weights, distance decay, recency).
5. **Sanity Check** — Reasoning model checks source reliability, sanity-check weights and chains and then after potentially finetuning weights we calculate final impact; produce rationale + evidence bundle.
6. **Decisioning** — align to trading strategy → ** suggest: buy/hold/sell + confidence**, with the **impact path** and a rational (in text).

## Architecture (at a glance)
- **ingestors**: source adapters, dedupe, rate-limit, provenance.
- **extractors**: LLM-assisted structured extraction; schema-validated.
- **models**: LLM models (currently nothing local, only API)
- **data**: input, cache and output folder here.
- **monitor**: determine n most impactful nodes (adjuntenmatrix or pageranker) -> monitor those. fetch news, extract and calculate impact
- **impact_chain_validator**: verification, sanity check, explanation/rational. state-of-the-art reasoning model
- (**Orchestrator**: jobs, caching, retries; pipelines.)


## Milestones
- **MVP**: one sector, top suppliers, end-to-end scoring & explanation.
- (**v1**: multi-sector, conflict/regulatory edges, confidence calibration & backtests.)