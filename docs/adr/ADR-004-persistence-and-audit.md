# ADR-004: Persistence and Immutable Audit Ledger

## Status
Accepted

## Context
Financial document processing requires strict compliance with Sarbanes-Oxley (SOX) and international accounting standards. Systems must maintain complete audit logs of every human modification made to machine-extracted data.

## Decision
We implemented a lightweight persistence layer using SQLAlchemy 2.0 with asynchronous SQLite (`aiosqlite`):
- SHA256 document hashing ensures automatic deduplication and fast cache lookups.
- Edit logs record `field_path`, `old_value`, `new_value`, `user_id`, and timestamps.
- Approval logs capture reviewer credentials and approval notes.
- Automatic history trimming enforces a configurable maximum document retention window.

## Consequences
- Full trace of all manual corrections.
- Zero external database installation required for developer setup or local testing.
- Easy migration to PostgreSQL in enterprise production deployments via standard SQLAlchemy dialect configuration.
