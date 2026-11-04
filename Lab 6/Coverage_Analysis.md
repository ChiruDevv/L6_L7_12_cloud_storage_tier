# Coverage Analysis

**Student:** Chiranthan Shankar  
**SRN:** PES2UG24CS137  
**Application:** `cloud_storage_tier.py`

## Code (line) coverage

The focused code-coverage suite executes all 57 executable statements (100%). It exercises each storage tier, the large-bucket discount, backup fee, egress overage, inactive accounts, empty usage, invalid inputs and tiers, invalid bucket sizes, corruption behavior, audit flagging, and both replication-monitor outcomes. The captured run reports 9 passing tests.

## Branch coverage

The branch suite executes all 40 decision outcomes (100%) with zero partially covered branches, with 8 passing tests. It covers both outcomes of the input validation decision, active/inactive tenants, every tier and the unknown-tier fallback, empty/non-empty bucket iterations, invalid/valid sizes, corrupted/uncorrupted buckets, archive/non-archive corruption, the >500 GB discount threshold, the >100 GB egress threshold, backup-vault selection, audit and billing status decisions, no-data handling, latency threshold comparisons, streak resets, and consecutive-latency alerts.

## Interpretation

The results show complete statement and branch execution for the provided module under the test data. Coverage is a measure of exercised code paths; it is not a proof that every possible input or business rule is correct. The tests assert the expected results for the selected normal, threshold, and error cases.

## Reproduce

Run each suite from `Lab 6` using the commands in `README.md`. The terminal transcripts and PNG captures in `evidence/` are generated from those runs.



