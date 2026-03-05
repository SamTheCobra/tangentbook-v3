.PHONY: dev backend frontend setup-backend setup-frontend

dev:
	@echo "Starting TangentBook v3..."
	@make backend & make frontend & wait

backend:
	cd backend && source venv/bin/activate 2>/dev/null || true && uvicorn main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

setup-backend:
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

setup-frontend:
	cd frontend && npm install
