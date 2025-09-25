# Contextra

Real-time insights connecting world events to your portfolio’s future.

## Goal
Provide **financial peace of mind** by tracing how world events impact a portfolio and converting that into **buy/hold/sell** recommendations with **confidence** and an **impact path**.

## Problem We Solve
- **Hidden risks**: second-order effects (suppliers, regulation, geopolitics) are missed.
- **Scale & noise**: fragmented sources; humans can’t connect signals fast enough.
- **Vague outputs**: many LLM tools lack quantified impact or verifiable reasoning.

## Approach (for each component)

0. **Graph Factory** — extract typed entities & relations to build/refresh an **Investment Graph** for each stock/sector 
1. **Monitor** — a) extract events: analyze news (/filings/trends) around n most impactful nodes b) extract insights: analyze UBS research for structural and thematic insight around n most impactful nodes
2. **Reaction Chain** — trace event/insight → intermediaries → portfolio component to capture indirect effects.
3. **Impact Score** — aggregate influence along weighted paths (edge/type weights, distance decay, recency).
4. **Sanity Check** — Reasoning model checks source reliability, sanity-check weights and chains and then after potentially finetuning weights we calculate final impact; produce rationale + evidence bundle.
5. **Decisioning** — **suggest: buy/hold/sell + confidence**, with the **impact path** and a rational (in text). additionaly: align to trading strategy

## Architecture (at a glance)
main
- **graph_factory**: full pipeline + agentic "refinement": extraction, graph creation and then iterative agentic expansion/enrichment
- **monitor**: determine n_most_impactful_nodes (adjuntenmatrix or pageranker) -> monitor those. fetch news, extract and calculate impact -> "alarm"
- **impact_chain_validator**: verification, sanity check, explanation/rational through: state-of-the-art reasoning model

details
- **ingestors**: source adapters, dedupe, rate-limit, source.
- **extractors**: LLM-assisted structured extraction; schema-validated.
- **models**: LLM models (currently nothing local, only API)
- **data**: input, cache and output folder here.

optional
- (**portfolio_decomposition**: 1. Portfolio → Fonds / ETFs / Stocks. 2. Fond/ETF -> (top 10 holdings) -> sector) 
- (**orchestrator**: jobs, caching, retries; pipelines.)


## Milestones
- **MVP**: one sector, top suppliers, end-to-end scoring & explanation.
- (**v1**: multi-sector, conflict/regulatory edges, confidence calibration & backtests.)