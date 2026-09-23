# SQL Query Performance Analysis on Normalized Databases

Benchmarks how database normalization and query complexity affect SQL performance as data scales, comparing an unnormalized flat-table design against a properly normalized 3NF schema across 1MB, 10MB, and 100MB datasets.

## Problem

Does normalizing a database actually pay off in query performance — and does that payoff hold consistently as data volume grows, or does query complexity change the picture?

## Approach

This repo contains two versions of the same benchmark, run side by side for direct comparison:

1. **`baseline_unnormalized.py`** — loads each CSV into a single flat SQLite table and runs 6 queries against it (`queries_unnormalized.txt`).
2. **`normalized_pipeline.py`** — restructures the same data into a normalized relational schema (6 related tables: `persons`, `schools`, `campus`, `department`, `dept_campus`, `employment_records`, satisfying 1NF–3NF with foreign keys enforcing referential integrity), then runs the equivalent 6 queries rewritten as joins (`queries_normalized.txt`).

Both scripts benchmark execution time with `time.perf_counter()`/`time.time()` across all three dataset sizes and plot the results with matplotlib.

## Results

| Query type | Normalized: 1MB → 100MB growth |
|---|---|
| Simple filter (Q1) | ~57x |
| Simple filter (Q4) | ~80x |
| Aggregation + GROUP BY (Q6) | **~703x** |

A 100x increase in data volume caused simple filter queries to slow ~57–80x (roughly proportional), while the aggregation query slowed ~703x — nearly 10x worse than the simple queries. Full results, including query outputs, are in `results/`.

## Key Finding

**Query complexity compounds non-linearly with data volume.** Normalization reduces redundant scanning and improves performance overall, but the benefit isn't uniform — queries involving joins and aggregation become disproportionately more expensive as data scales, which has direct implications for query optimization priorities in growing systems.

## Tech Stack

`Python` `SQLite` `pandas` `matplotlib`

## Repository Structure

```
├── normalized_pipeline.py              # Builds the normalized schema, runs benchmarks
├── baseline_unnormalized.py            # Flat-table baseline for comparison
├── queries_normalized.txt              # Queries rewritten as joins over the normalized schema
├── queries_unnormalized.txt            # Original queries against the flat table
├── requirements.txt
├── data/
│   └── salary_tracker_1MB.csv          # Sample dataset (1MB) — included so the scripts run out of the box
└── results/
    ├── query_execution_times_normalized.png
    ├── query_execution_times_unnormalized.png
    └── query_results_normalized.txt              # Full query output + timing, normalized schema
```

> **Note:** the original `baseline_unnormalized.py` had a bug where it reopened its log file in write mode a second time, erasing the detailed per-query results. The bug is fixed in this version (it now appends instead of overwriting), so re-running `baseline_unnormalized.py` will produce a full `results/output_unnormalized.txt` alongside the summary.

Only the 1MB sample dataset is included in the repo. The 10MB and 100MB datasets used for the full benchmark are larger, scaled-up copies of the same schema and aren't tracked here — generate your own (or scale up the 1MB sample) to reproduce the full 1MB–100MB comparison.

## Running It

```bash
pip install -r requirements.txt
python baseline_unnormalized.py
python normalized_pipeline.py
```
The included `data/salary_tracker_1MB.csv` lets both scripts run immediately. To reproduce the full 1MB/10MB/100MB benchmark, add scaled-up versions of the same CSV schema as `data/salary_tracker_10MB.csv` and `data/salary_tracker_100MB.csv`.

## Future Work

- Extend benchmarking to PostgreSQL/MySQL for comparison against SQLite
- Add query plan (`EXPLAIN`) analysis to explain *why* aggregation queries scale worse
- Test with indexing strategies to see how much of the gap indexing closes
