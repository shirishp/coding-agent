---
name: db-migrations
description: Create or modify database migrations. Use when adding a column, changing a schema, or when a migration fails to apply.
---

# Migrations

## Rules
- Every migration must define both `upgrade()` and `downgrade()`.
- Never edit a migration that has been merged to main. Add a new one.
- Adding a NOT NULL column requires three migrations: add nullable, backfill,
  then set NOT NULL. A single-step add locks the table and has caused two outages.
