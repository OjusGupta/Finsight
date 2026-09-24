# Development Log

This diary records the project phases and separates completed evidence from planned work.

## Phase 1 - Project Definition

**Goal:** Define FinSight as a retail and finance intelligence platform.

**What I did:** Chose a layered design with data, PostgreSQL, analytics, anomalies, agents, RAG, and actions.

**Problems:** The final application layers are not fully implemented.

**Fixes:** Marked API, UI, and AI behavior as planned where code is absent.

**What I learned:** Architecture should describe boundaries honestly.

**Current status:** Foundation defined.

## Phase 2 - Dataset Inspection

**Goal:** Understand the synthetic ERP files.

**What I did:** Organized raw, processed, reference, and quality data folders.

**Problems:** Source data included duplicates and category quality issues.

**Fixes:** Documented issues instead of silently changing source facts.

**What I learned:** Data profiling comes before loading.

**Current status:** Dataset available; full automated profiling is **To be verified**.

## Phase 3 - PostgreSQL Schema

**Goal:** Store normalized business records with relationships and constraints.

**What I did:** Added tables for core entities, events, data quality, metrics, anomalies, insights, actions, automation, and audit records.

**Problems:** Source and target field names/domains did not always match.

**Fixes:** Added loader mappings and documented differences.

**What I learned:** A schema is an executable business contract.

**Current status:** Schema SQL exists; duplicate sections in the schema file should be reviewed before a fresh rebuild.

## Phase 4 - Dataset Restoration

**Goal:** Load the ERP records into `finsight`.

**What I did:** Built `psycopg2` loaders for reference and operational data.

**Problems:** Parent-child load order, constraints, and source status labels required care.

**Fixes:** Used explicit insert columns, conflict handling, and normalization.

**What I learned:** Loading is transformation, not just file copying.

**Current status:** Supplied counts indicate operational data was loaded.

## Phase 5 - Data Cleaning

**Goal:** Prevent duplicate sales from entering analytics.

**What I did:** Kept the first row for duplicate invoice `INV-000151` and wrote processed sales files.

**Problems:** Duplicate sale items and movement references were not perfectly consistent.

**Fixes:** Filtered processed sale items to valid cleaned sale IDs.

**What I learned:** Child records need relationship validation after deduplication.

**Current status:** Cleaning script exists; movement-reference reconciliation is **To be verified**.

## Phase 6 - Database Loading

**Goal:** Insert cleaned and operational data into PostgreSQL.

**What I did:** Loaded reference data, inventory, movements, sales, returns, payments, refunds, expenses, and login events.

**Problems:** `BANK_TRANSFER`, status labels, expense naming, and login schema differed.

**Fixes:** Applied documented loader mappings and constraint preparation.

**What I learned:** Domain normalization prevents avoidable load failures.

**Current status:** Supplied operational counts recorded.

## Phase 7 - Data Product Creation

**Goal:** Create reusable daily analytics tables.

**What I did:** Populated daily store, product, customer, and inventory metrics according to the supplied validation results.

**Problems:** Joins can multiply return quantities; inventory history may lack opening balance.

**Fixes:** Pre-aggregate returns and document inventory balance assumptions.

**What I learned:** A data product needs both a grain and an independent check.

**Current status:** Supplied rows and totals recorded.

## Phase 8 - Validation and Debugging

**Goal:** Reconcile derived data with direct source queries.

**What I did:** Compared sales, return, customer, and inventory totals.

**Problems:** A text validation message was cast to integer, and a failed transaction caused `25P02`.

**Fixes:** Use a Boolean validation gate and run `ROLLBACK;` after transaction failure.

**What I learned:** SQL type discipline and transaction state matter during debugging.

**Current status:** Validation notes recorded; fresh live execution is **To be verified**.

## Phase 9 - Next: Anomaly Detection

**Goal:** Identify unusual sales, returns, stock, or finance patterns.

**What I did:** The schema includes an anomalies table.

**Problems:** A complete detector is not evidenced in inspected code.

**Fixes:** None yet.

**What I learned:** Detection rules should be measurable before an agent explains them.

**Current status:** TODO.

## Phase 10 - Planned AI Layer

**Goal:** Let agents explain evidence and recommend actions.

**What I did:** Created folders for agents, tools, prompts, RAG, and workflows.

**Problems:** Inspected AI files are empty.

**Fixes:** None yet.

**What I learned:** AI should sit after validated data products.

**Current status:** Planned.

## Interview Takeaway

- The project progressed from source data to validated data products before AI.
- Every major issue became a documented engineering lesson.
- Failed SQL does not necessarily mean the data load failed; inspect transaction state and table contents.
- “Implemented” should mean code exists and has been tested.
