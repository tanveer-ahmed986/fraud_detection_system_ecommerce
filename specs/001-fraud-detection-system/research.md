# Research: Technology Decisions

## Stack Selection

### Backend: Python 3.11 + FastAPI
**Chosen over**: Django REST, Flask, Node.js Express
- **Rationale**: Async-first, auto OpenAPI docs, Pydantic validation, best ML ecosystem interop
- **Risk**: Single-threaded GIL — mitigated by async I/O and CPU-bound work offloaded to model preload

### ML: scikit-learn RandomForest + SHAP
**Chosen over**: XGBoost, LightGBM, PyTorch
- **Rationale**: Fast training/inference (<5ms), interpretable, SHAP TreeExplainer cached for <5ms explanations, no GPU required
- **Risk**: Less accurate than gradient boosting — acceptable for portfolio demo; easily swappable

### Frontend: React + Vite + Recharts
**Chosen over**: Next.js, Vue, Streamlit
- **Rationale**: Industry standard, fast HMR, Recharts is lightweight and declarative
- **Risk**: None significant

### Database: PostgreSQL 16
**Chosen over**: SQLite, MySQL, MongoDB
- **Rationale**: JSONB for flexible audit/feature data, UUID native, production-grade, async driver (asyncpg)
- **Risk**: Requires Docker — acceptable for target deployment

### Plugin: PHP 8.x WooCommerce
- **Rationale**: WooCommerce is the #1 ecommerce platform (40%+ market share), PHP is required
- Standard WordPress plugin architecture with Settings API

## Key Library Versions
| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | ≥0.110 | Web framework |
| SQLAlchemy | ≥2.0.25 | Async ORM |
| scikit-learn | ≥1.4 | ML model |
| SHAP | ≥0.44 | Explainability |
| React | 18.x | UI framework |
| Recharts | 2.x | Charts |
| PostgreSQL | 16 | Database |

## Alternatives Considered but Rejected
- **Celery for async training**: Over-engineered for single-machine demo; `asyncio.create_task` suffices
- **Redis for rate limiting**: In-memory dict with token bucket is simpler and sufficient
- **Kafka for audit events**: Direct DB writes with async tasks meet latency goals
- **Docker Swarm/K8s**: Single docker-compose is the right complexity for portfolio
