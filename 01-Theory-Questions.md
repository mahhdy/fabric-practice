# سوالات نظری و تشریحی (۳۱ سوال)

**روش کار:** جواب‌ها رو در فایل جدا (مثلاً `answers-theory.md`) بنویس، فارسی یا انگلیسی. برای هر سوال این ۳ چیز رو بیار:
۱. تعریف دقیق ۲. چرا/چطور کار می‌کنه ۳. یک مثال یا سناریو و trade-off.
در مصاحبه همین ساختار رو دارن. جواب‌ها رو برام بفرست تا نمره بدم و نقاط ضعف رو بگم.

## A. معماری و Capacity
1. Explain OneLake. How does it differ from provisioning separate ADLS Gen2 accounts per team? What are the implications for duplication, security and governance?
2. Compare Lakehouse, Warehouse and Eventhouse. Give decision criteria and a scenario where each is the right choice.
3. Explain capacity SKU, CU, smoothing, bursting and throttling. How do you diagnose a throttled capacity and what are your options?
4. Shortcuts vs Mirroring vs Copy activity: when do you use each? What are the security/limitation considerations (e.g. identity used to read the target)?
5. How would you design workspaces for a company with 3 business domains and Dev/Test/Prod? Discuss roles, domains, capacities and ALM impact.

## B. Lakehouse، Delta و Spark
6. What physically exists in a Delta table? How do ACID and time travel work? What do OPTIMIZE, VACUUM, V-Order and Z-ORDER do and what are the trade-offs?
7. What causes the small-files problem and how do you fix and prevent it in Fabric?
8. Design a medallion architecture for an e-commerce company. What goes in each layer? How do you handle schema drift, bad records and idempotency?
9. Walk through implementing SCD Type 2 with MERGE. What are the pitfalls (duplicate source keys, late data, nondeterminism)?
10. Spark in Fabric: starter pool vs custom pool, Environments, high concurrency mode. How do you tune a slow job (skew, shuffle, broadcast joins, partitions)?
11. A 2 TB fact table receives daily loads and is filtered mostly by date and store. Propose partitioning/clustering/maintenance. Why not partition by customer_id?
12. Design an idempotent incremental load. How do you handle late-arriving data, updates and deletes (CDC), and re-runs after failure?

## C. Warehouse و T-SQL
13. Warehouse vs the Lakehouse SQL analytics endpoint: capabilities, limitations, metadata sync delay.
14. How does Fabric Warehouse differ from Synapse dedicated SQL pool (distribution, indexes, statistics, concurrency/transactions)?
15. Describe every security layer from tenant to row for an HR dataset where managers must see only their own team and salary must be masked for most users.

## D. Ingestion و Orchestration
16. Dataflow Gen2 vs Pipeline vs Notebook: when to use which? Consider skills, scale, cost, lineage and maintainability.
17. Describe pipeline control flow (Lookup, ForEach, If, parameters, expressions), retries, error handling and alerting. Build a metadata-driven ingestion pattern.

## E. Semantic Model و DAX
18. Star schema vs flat table. Explain cardinality, cross-filter direction, role-playing dimensions, many-to-many and bridge tables.
19. Explain Direct Lake: how it loads data, what framing/transcoding/temperature mean, when it falls back to DirectQuery, guardrails, and when you would not use it.
20. Import vs DirectQuery vs Direct Lake vs Composite: choose for (a) 50 GB sales mart with hourly refresh, (b) near-real-time ops dashboard, (c) lakehouse with 5 billion rows.
21. Filter context vs row context, context transition, and how CALCULATE works. Give an example where a naive measure gives wrong totals.
22. A report is slow. Walk through your diagnosis (tools, order of steps) and typical fixes at model, DAX and visual level.
23. Incremental refresh, hybrid tables, XMLA endpoint, large model format: purpose and setup.
24. RLS static vs dynamic. Where should RLS live (semantic model vs warehouse vs OneLake security)? Interaction with Direct Lake fallback, and what is OLS?

## F. ALM، Monitoring و Governance
25. Git integration + deployment pipelines: what is versioned, branching strategy, deployment rules, known limitations.
26. How do you monitor and alert on Fabric (Monitoring hub, Capacity Metrics, Spark history, pipeline run details, Log Analytics)? What would your runbook look like for a failing nightly load?
27. Explain governance: Purview integration, sensitivity labels, endorsement, lineage, impact analysis, tenant settings and who controls what.

## G. Real-Time Intelligence
28. Describe an architecture from Eventstream to Activator. When would you choose KQL/Eventhouse over Spark Structured Streaming?
29. KQL: explain ingestion mapping, update policy, retention vs caching policy, materialized views.

## H. سناریو و Troubleshooting (شبیه مصاحبه)
30. **Case:** A retailer has 10 source systems (SQL Server, Oracle, SaaS APIs, CSV drops), ~2 TB, a 4-person team and a need for self-service BI plus a near-real-time inventory view. Design end-to-end: ingestion, layers, modeling, security, ALM, monitoring, capacity sizing and cost control. State assumptions and risks.
31. **Troubleshooting:** How would you approach each? (a) Direct Lake report suddenly slow. (b) Pipeline Copy succeeded but row count is lower than source. (c) Notebook fails with OOM. (d) Users see data they shouldn't after RLS deployment. (e) Capacity throttling every morning at 9:00.
