# FinSight Data Capability Audit

This document outlines what analytical questions can and cannot be answered by the current PostgreSQL schema. It serves as a single source of truth for AI Copilot grounding.

| Metric / Question Type | Available? | Source Table(s) | Calculation | Limitations |
|---|---|---|---|---|
| **Total Revenue** | Yes | sales | SUM(total_amount) | Only calculates based on finalized invoice sums; no line-item level granularity exists. |
| **Store Sales Performance** | Yes | sales | Group by store_id | Cannot separate by cash vs credit; no labor cost deduction. |
| **Store Inventory Value** | Yes | inventory JOIN products | SUM(quantity * unit_price) | Cannot calculate exact carrying cost, only retail value approximation. |
| **Product Margin / Profit** | Yes | products | unit_price - cost_price | Only calculated at the unit level; we don't have per-sale margin because sales_lines is missing. |
| **Sales by Product** | No | N/A | N/A | Missing sales_lines table. We cannot join sales directly to products. |
| **Sales by Category** | No | N/A | N/A | Missing sales_lines. |
| **Low Stock / Reorder** | Yes | inventory | quantity <= reorder_level | Does not account for pending POs (no purchase_orders table). |
| **Customer LTV (Total Spent)** | Yes | sales JOIN customers | SUM(total_amount) where customer_id | We only have aggregate total spent, no cart analysis or product preferences per customer. |
| **Reconciliation Rate** | Yes | inance_reconciliation_run | matched_records / total_records | Granular reasons for mismatch require inance_reconciliation_line inspection. |
| **Anomalies / Fraud** | Yes | nomalies | Query by status / anomaly_type | System-generated anomalies only. |
