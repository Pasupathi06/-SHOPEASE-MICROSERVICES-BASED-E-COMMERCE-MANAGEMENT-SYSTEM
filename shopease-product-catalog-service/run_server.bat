@echo off
echo Starting ShopEase Product Catalog Service on port 8004...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
pause
