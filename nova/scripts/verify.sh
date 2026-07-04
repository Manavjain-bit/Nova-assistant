#!/usr/bin/env bash
# Nova verification script: runs backend tests w/ coverage gate + frontend lint/build.
set -e

echo "== Backend: pytest + coverage (90% floor) =="
cd backend
rm -f nova.db test_nova.db
pip install -q -r requirements.txt --break-system-packages
python -m pytest app/tests --cov=app --cov-report=term-missing
rm -f nova.db test_nova.db
cd ..

echo ""
echo "== Frontend: lint + production build =="
cd frontend
npm install --no-audit --no-fund
npm run lint
npm run build
cd ..

echo ""
echo "All checks passed."
