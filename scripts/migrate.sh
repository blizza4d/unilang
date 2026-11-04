#!/usr/bin/env bash
set -euo pipefail

echo "==> Running DataNova Extract Database Migrations..."
cd "$(dirname "$0")/../backend"

# Execute Alembic upgrade to latest head revision
alembic upgrade head

echo "==> Alembic migrations completed successfully."
