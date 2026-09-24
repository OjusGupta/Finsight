# Project Overview

## What FinSight Is

FinSight is an Agentic Finance and Retail Operations Intelligence Platform. It is designed to turn ERP-style business records into reliable metrics, detected issues, explanations, and eventually recommended actions.

The current repository is strongest in its synthetic dataset, cleaning script, PostgreSQL schema, and loading scripts. The AI, API, and dashboard layers are structured in the repository but are **To be verified** as working implementations.

## Why It Exists

Retail operations produce sales, inventory, customer, payment, return, and expense records. A manager needs answers such as:

- Which stores are selling the most?
- Which products are running low?
- Are returns unusually high?
- Which customers or products need attention?
- Which business actions should happen next?

FinSight creates a shared data foundation for those questions.

## Users

The intended users are:

- Store and operations managers
- Finance teams
- Inventory and supply-chain teams
- Business analysts
- Administrators

The exact authorization model is **To be verified**.

## Major Workflows

1. Source CSV files are preserved as raw data.
2. Sales data is cleaned into a processed copy.
3. Python loaders insert records into PostgreSQL.
4. SQL/Python calculations create daily data products.
5. Validation compares derived totals with direct source-table totals.
6. Planned anomaly detection identifies unusual patterns.
7. Planned agents explain evidence and recommend actions.

## Example Scenario

A store manager sees that a product has low closing stock. SQL calculates the quantity and reorder status. An inventory agent could explain recent sales and purchases, retrieve the relevant reorder policy through RAG, and suggest an action. The exact number comes from PostgreSQL; the language model explains it.

## More Than a Chatbot

A chatbot mainly generates text. FinSight is intended to be an evidence-driven system:

- Database tools retrieve current facts.
- SQL and Python calculate exact values.
- Data products provide stable business metrics.
- RAG supplies policy context.
- Agents coordinate reasoning.
- Action items connect findings to work.

## Decision

**Decision:** Use deterministic calculations before LLM reasoning.

**Why:** Financial and inventory totals must be reproducible.

**Alternative:** Ask an LLM to calculate directly from unstructured data.

**Reason:** That approach can hallucinate values and is difficult to audit.

## Interview Takeaway

- FinSight combines data engineering, analytics, and planned agentic AI.
- The database is the source of truth for business numbers.
- AI is intended to interpret evidence, not replace accounting logic.
- Raw and processed data are deliberately kept separate.
