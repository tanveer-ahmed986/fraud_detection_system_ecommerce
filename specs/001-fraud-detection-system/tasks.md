# Tasks: Fraud Detection System for E-commerce

**Input**: Design documents from `/specs/001-fraud-detection-system/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks included (tests already exist in `backend/tests/`).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Docker, and dependency configuration

- [X] T001 Create project root files: `docker-compose.yml`, `.env.example`, `Makefile`
- [X] T002 [P] Initialize backend Python project with `backend/pyproject.toml` and `backend/Dockerfile`
- [X] T003 [P] Initialize frontend React project with `frontend/package.json`, `frontend/vite.config.ts`, `frontend/Dockerfile`, `frontend/nginx.conf`
- [X] T004 [P] Initialize WooCommerce plugin skeleton with `plugin/woo-fraud-detect/woo-fraud-detect.php` and `plugin/woo-fraud-detect/readme.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement application config with Pydantic Settings in `backend/app/config.py`
- [X] T006 Set up async database engine and session factory in `backend/app/dependencies.py`
- [X] T007 Define all 5 SQLAlchemy ORM models (Transaction, Prediction, Model, AuditEntry, MerchantConfig) in `backend/app/models/db.py`
- [X] T008 [P] Set up Alembic migrations in `backend/alembic.ini` and `backend/alembic/env.py`
- [X] T009 [P] Create Pydantic request/response schemas in `backend/app/schemas/transaction.py`
- [X] T010 [P] Create training schemas in `backend/app/schemas/training.py`
- [X] T011 [P] Create audit schemas in `backend/app/schemas/audit.py`
- [X] T012 [P] Create dashboard schemas in `backend/app/schemas/dashboard.py`
- [X] T013 Implement feature engineering pipeline (13→17 features, log-amount, sin/cos time, one-hot) in `backend/app/ml/preprocess.py`
- [X] T014 Implement model save/load with SHA-256 integrity verification in `backend/app/ml/model_store.py`
- [X] T015 Implement token-bucket rate limiter middleware in `backend/app/middleware/rate_limiter.py`
- [X] T016 Implement fallback middleware (allow <$50, queue rest) in `backend/app/middleware/fallback.py`
- [X] T017 Create FastAPI app with lifespan, CORS, middleware, router includes in `backend/app/main.py`
- [X] T018 Implement seed script for 5k synthetic transactions and initial model in `backend/app/seed.py`
- [X] T019 Create backend entrypoint script for auto-seeding on first run in `backend/entrypoint.sh`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Real-time Fraud Prediction (Priority: P1) 🎯 MVP

**Goal**: Submit a transaction → receive fraud/legitimate verdict with confidence score and top-3 feature explanations within 200ms p95

**Independent Test**: `curl -X POST localhost:8000/api/v1/predict` with sample transaction data → returns verdict, confidence, top-3 features

### Tests for User Story 1

- [X] T020 [P] [US1] Unit test: preprocessing produces correct shape and feature values in `backend/tests/test_predict.py`
- [X] T021 [P] [US1] Unit test: prediction returns label, confidence, top_features, latency_ms in `backend/tests/test_predict.py`

### Implementation for User Story 1

- [X] T022 [US1] Implement FraudPredictor class with cached SHAP TreeExplainer in `backend/app/ml/predict.py`
- [X] T023 [US1] Implement POST /api/v1/predict router with async DB writes (transaction + prediction + audit) in `backend/app/routers/predict.py`
- [X] T024 [US1] Implement GET /api/v1/health endpoint in `backend/app/routers/health.py`

**Checkpoint**: User Story 1 fully functional — submit transaction, get verdict with explanation

---

## Phase 4: User Story 2 — Model Training and Retraining (Priority: P2)

**Goal**: Train model on dataset, evaluate with metric gates (recall ≥0.90, FPR ≤0.05), version and promote, support rollback

**Independent Test**: `curl -X POST localhost:8000/api/v1/retrain -H "X-API-Key: demo-api-key"` → returns metrics, version, promotion status

### Tests for User Story 2

- [X] T025 [P] [US2] Unit test: training returns recall/precision/f1/fpr metrics in `backend/tests/test_retrain.py`
- [X] T026 [P] [US2] Unit test: metric gate blocks promotion when below threshold in `backend/tests/test_retrain.py`

### Implementation for User Story 2

- [X] T027 [US2] Implement training pipeline with RandomForest (n=200, balanced, seed=42) in `backend/app/ml/train.py`
- [X] T028 [US2] Implement drift monitoring (weekly eval, alert if recall <0.85 or FPR >0.07) in `backend/app/ml/monitor.py`
- [X] T029 [US2] Implement POST /api/v1/retrain with API key auth, metric gates, auto-promote in `backend/app/routers/retrain.py`
- [X] T030 [US2] Implement GET /api/v1/models and POST /api/v1/models/{version}/activate (rollback) in `backend/app/routers/models.py`

**Checkpoint**: User Story 2 functional — train, version, rollback models with quality gates

---

## Phase 5: User Story 3 — Analytics Dashboard (Priority: P3)

**Goal**: Visual web dashboard showing fraud rate, model metrics, prediction history, and transaction drill-down

**Independent Test**: Open `localhost:3000` → see metrics cards, fraud rate chart, prediction table; click transaction → see SHAP feature contributions

### Implementation for User Story 3

- [X] T031 [P] [US3] Implement dashboard API: GET /api/v1/dashboard/summary in `backend/app/routers/dashboard.py`
- [X] T032 [P] [US3] Implement dashboard API: GET /api/v1/dashboard/timeseries in `backend/app/routers/dashboard.py`
- [X] T033 [P] [US3] Implement dashboard API: GET /api/v1/dashboard/predictions in `backend/app/routers/dashboard.py`
- [X] T034 [P] [US3] Create Axios API client with typed interfaces in `frontend/src/api/client.ts`
- [X] T035 [P] [US3] Create MetricsCard component in `frontend/src/components/MetricsCard.tsx`
- [X] T036 [P] [US3] Create FraudRateChart (Recharts LineChart) in `frontend/src/components/FraudRateChart.tsx`
- [X] T037 [P] [US3] Create PredictionTable component in `frontend/src/components/PredictionTable.tsx`
- [X] T038 [P] [US3] Create FeatureContribBar (SHAP bar chart) in `frontend/src/components/FeatureContribBar.tsx`
- [X] T039 [US3] Create Dashboard page composing all components in `frontend/src/pages/Dashboard.tsx`
- [X] T040 [US3] Create TransactionDetail drill-down page in `frontend/src/pages/TransactionDetail.tsx`
- [X] T041 [US3] Create ModelComparison page with version metrics table in `frontend/src/pages/ModelComparison.tsx`
- [X] T042 [US3] Create App shell with routing and navigation in `frontend/src/App.tsx` and `frontend/src/main.tsx`

**Checkpoint**: Dashboard fully functional — view metrics, charts, drill into transactions

---

## Phase 6: User Story 4 — Audit Logging and Compliance (Priority: P4)

**Goal**: Every prediction/training/rollback event logged with full context, queryable by type and date range

**Independent Test**: Submit transactions, then `curl localhost:8000/api/v1/audit?event_type=prediction` → returns paginated audit entries with full context

### Tests for User Story 4

- [X] T043 [P] [US4] Unit test: audit entry creation and valid event types in `backend/tests/test_audit.py`

### Implementation for User Story 4

- [X] T044 [US4] Implement GET /api/v1/audit with pagination and filtering (event_type, date range) in `backend/app/routers/audit.py`

**Checkpoint**: Audit log functional — all events traceable, filterable by type and date

---

## Phase 7: User Story 5 — WooCommerce Plugin (Priority: P5)

**Goal**: PHP plugin sends checkout transactions to fraud API, flags fraud orders, notifies merchant

**Independent Test**: Simulate WooCommerce checkout → plugin calls predict endpoint, flags fraudulent orders, sends merchant email

### Implementation for User Story 5

- [X] T045 [P] [US5] Implement API client (wp_remote_post/get) in `plugin/woo-fraud-detect/includes/class-api-client.php`
- [X] T046 [P] [US5] Implement admin settings page with health check in `plugin/woo-fraud-detect/includes/class-settings.php`
- [X] T047 [US5] Implement order handler: hook checkout, hash PII, call API, auto-hold fraud, email notification in `plugin/woo-fraud-detect/includes/class-order-handler.php`
- [X] T048 [US5] Wire plugin main file with WooCommerce dependency check in `plugin/woo-fraud-detect/woo-fraud-detect.php`

**Checkpoint**: WooCommerce plugin functional — checkout triggers fraud check, orders flagged automatically

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation, tests, and documentation

- [X] T049 [P] Unit test: model save/load with SHA-256 integrity, DataFrame preprocessing in `backend/tests/test_ml_pipeline.py`
- [X] T050 [P] Create test fixtures (sample transactions, trained model) in `backend/tests/conftest.py`
- [X] T051 Run `docker compose up --build` and validate all 3 services start without errors
- [X] T052 Run quickstart.md validation: clone → prediction in <5 minutes
- [X] T053 Run `pytest` and verify all backend tests pass
- [X] T054 Verify p95 prediction latency ≤200ms with sample requests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Prediction): No story dependencies — MVP
  - US2 (Training): Independent of US1 but shares ML pipeline
  - US3 (Dashboard): Consumes data from US1 predictions; can stub data for independent dev
  - US4 (Audit): Audit writes happen inside US1/US2 routers; query endpoint is independent
  - US5 (Plugin): Calls US1 predict endpoint; can develop against API contract independently
- **Polish (Phase 8)**: Depends on all user stories being complete

### Within Each User Story

- Tests FIRST → then implementation
- Models/schemas → services/ML → routers/endpoints → integration
- Core implementation before UI/integration

### Parallel Opportunities

- T002, T003, T004: All setup tasks in parallel (different directories)
- T008-T012: Schema + migration tasks in parallel (independent files)
- T020-T021, T025-T026, T043: All test tasks within a story in parallel
- T031-T038: Dashboard API + frontend components in parallel
- T045-T046: Plugin API client + settings in parallel
- User Stories 1-5 can proceed in parallel after Phase 2 (with caveats above)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (Real-time Prediction)
4. **STOP and VALIDATE**: `curl POST /api/v1/predict` returns verdict + confidence + features
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (Prediction) → Core working → Demo MVP
3. US2 (Training) → Retrain and version models
4. US3 (Dashboard) → Visual showcase for portfolio
5. US4 (Audit) → Compliance proof point
6. US5 (Plugin) → Real-world integration demo

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 54 |
| Phase 1 (Setup) | 4 |
| Phase 2 (Foundational) | 15 |
| Phase 3 (US1 - Prediction) | 5 |
| Phase 4 (US2 - Training) | 6 |
| Phase 5 (US3 - Dashboard) | 12 |
| Phase 6 (US4 - Audit) | 2 |
| Phase 7 (US5 - Plugin) | 4 |
| Phase 8 (Polish) | 6 |
| Parallel opportunities | 6 groups identified |
| MVP scope | Phase 1 + 2 + 3 (24 tasks) |

## Notes

- All source files already exist from initial implementation
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
