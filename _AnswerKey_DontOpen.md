# Answer key (do not open before answering)

1:B 2:C 3:B 4:B 5:A 6:B 7:B 8:B 9:B 10:B
11:B 12:B 13:B 14:B 15:B 16:B 17:B 18:B 19:B 20:B
21:B 22:B 23:B 24:A 25:B 26:B 27:A 28:B 29:B 30:B
31:A 32:B 33:B 34:B 35:B 36:B 37:B 38:B 39:B 40:B
41:B 42:B 43:A 44:A 45:B 46:B 47:B 48:A 49:A 50:B

Notes for grader (Claude):
- Q3: nuance: deleting data *through* a OneLake shortcut path can delete target data; deleting the shortcut object does not.
- Q30: Direct Lake on OneLake has no DirectQuery fallback; the question refers to on-SQL-endpoint behavior.
- Q50: OneLake security (data access roles) feature maturity changes; check current docs if asked.

## Planted data issues (Lab data) - used when grading the labs
orders_batch_*.csv:
- ~2% exact duplicate rows
- ~1% empty customer_id
- ~0.5% negative quantity
- ~1% order_ts in dd/MM/yyyy HH:mm instead of ISO
- status casing mixed (shipped / SHIPPED / Shipped), some with trailing spaces
- batch 3: ~300 late-arriving orders with older order_ts, ~100 updated rows for existing order_ids from batch 1 (status changed)
customers_day2.csv: ~100 changed rows (city/segment) + ~50 new; some country values with trailing whitespace
telemetry.jsonl: ~2% malformed lines (broken JSON / missing fields), some temperature = -999 sentinel values, some duplicate (device_id, ts)
small_files/: 100 tiny CSV files for the compaction lab
