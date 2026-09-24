# AI Agent Design

## Status

This is the planned AI layer. The repository contains folders for agents, tools, prompts, RAG, and workflows, but inspected agent files are empty. The following describes intended responsibilities, not completed runtime behavior.

## Current Foundation

The database and data products provide evidence for future agents. AI should query those products through controlled tools rather than inventing totals.

## Planned Agents

### Supervisor Agent

Routes a user request to the most appropriate specialist and combines results when a question crosses domains.

### Sales Agent

Explains sales trends, revenue, orders, and product performance using sales tools.

### Finance Agent

Explains revenue, expenses, returns, and financial ratios using finance tools.

### Inventory Agent

Explains stock, movement history, reorder levels, and low-stock products using inventory tools.

### Anomaly Agent

Explains unusual records or patterns from the `anomalies` data product. Detection implementation is **To be verified**.

## Tools

Planned database tools in `ai/tools/` should return structured facts such as totals, rows, dates, and identifiers. A tool should make its filters explicit and avoid returning ambiguous prose when a number is required.

## RAG

RAG means retrieval-augmented generation. It retrieves relevant business-policy or finance documents and adds them as context to an agent request. RAG answers questions such as “what is the reorder policy?”; PostgreSQL answers questions such as “what is the current quantity?”

## Planned Flow

```text
User question
    -> supervisor
    -> specialist agent
    -> database tool for facts
    -> RAG retrieval for policy
    -> explanation and recommendation
    -> optional action item
```

## Why Agents Need Tools

Agents should not hallucinate database numbers. A tool call creates a traceable link between the answer and the source records. The LLM can interpret a verified result, but SQL/Python should calculate the result.

## Action Generation

A recommendation should state:

- What was observed
- Which records support it
- Which policy applies
- What action is suggested
- What confidence or uncertainty remains

Writing to `action_items` or triggering automation requires authorization and audit logging. Implementation is **To be verified**.

## Interview Takeaway

- An agent is a decision-making workflow around tools, not just a prompt.
- RAG supplies relevant documents; it does not replace structured queries.
- Tool outputs should be evidence and structured values.
- Deterministic calculations must stay outside the LLM.
