# Placewise Local Development & Execution Guide

## 1. Running the Backend API Server
```bash
# From repository root:
python3 -m backend.main
# Server starts at http://localhost:8000
```

## 2. Running the React Frontend Application
```bash
# Navigate to frontend:
cd frontend

# Install dependencies:
npm install

# Start development server:
npm run dev
# Vite server starts at http://localhost:3000
```

## 3. Building for Production
```bash
cd frontend
npm run build
# Outputs optimized static bundle to frontend/dist/
```

## 4. Running Verification Suites
```bash
# Run pytest unit tests:
pytest tests/ -v

# Run semantic quality verification:
python3 scripts/verify_semantic_quality.py

# Run comprehensive Genie evaluation:
python3 scripts/evaluate_genie.py

# Run 12 end-to-end application scenarios:
python3 scripts/test_app_scenarios.py
```
