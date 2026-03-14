<!--
Sync Impact Report
- Version change: unversioned → v1.0.0
- Added sections: Governance Metadata, Model Explainability (Principle 8),
  Latency Requirements (Principle 9), Model Drift Monitoring (Principle 10),
  Incident Response (Section 6), Fallback Strategy (Section 5.6),
  Testing Standards (Section 9), Security hardening additions (Section 7)
- Modified sections: Principles (expanded from 7 to 10), Security & Privacy (hardened),
  Amendments (formalized with versioning policy)
- Templates requiring updates:
  - .specify/templates/plan-template.md — ✅ compatible (Constitution Check section)
  - .specify/templates/spec-template.md — ✅ compatible
  - .specify/templates/tasks-template.md — ✅ compatible
- Follow-up TODOs: none
-->

# Fraud Detection AI System — Constitution (SDD Governance Document)

**Version**: 1.1.0
**Ratification Date**: 2026-03-11
**Last Amended**: 2026-03-13
**Status**: Active

---

## 1. Purpose

This constitution defines the operational, ethical, and technical rules
for the Fraud Detection AI system targeting ecommerce platforms.
It ensures the system is **reliable, auditable, and compliant** while
maintaining **high accuracy in detecting fraudulent transactions** with
**minimal impact on legitimate customer experience**.

---

## 2. Principles

1. **Accuracy First** — The system MUST detect ≥90% of fraudulent
   transactions (recall ≥0.90). Precision MUST remain ≥0.85.

2. **Minimize False Positives** — Legitimate transactions flagged as
   fraud MUST be ≤5% of total legitimate volume (FPR ≤0.05).

3. **Transparency & Auditability** — Every prediction MUST be logged
   with: input features, predicted label, confidence score, model
   version, and ISO-8601 timestamp.

4. **Data Privacy** — Sensitive information (user IDs, IPs, payment
   info) MUST be handled securely. No external transmission without
   explicit consent. All PII MUST be pseudonymized in logs.

5. **Modularity** — All components (preprocessing, model, API, plugin)
   MUST be independently deployable and testable. Changes to one module
   MUST NOT break other modules.

6. **Reproducibility** — Any model training MUST be repeatable using
   the same dataset, hyperparameters, and random seed. Training
   artifacts (model file, metrics, config) MUST be versioned.

7. **Compliance** — The system MUST be compatible with PCI-DSS (no
   storage of card numbers/CVV), GDPR (right to explanation, data
   deletion), and applicable ecommerce data handling regulations.

8. **Explainability** — Every fraud prediction MUST include top-3
   contributing features with their impact scores. Merchants MUST be
   able to understand why a transaction was flagged. This supports
   GDPR Article 22 (automated decision-making).

9. **Low Latency** — The `/predict` endpoint MUST respond within
   200ms at p95 under normal load. Transactions MUST NOT be blocked
   longer than 500ms under any condition.

10. **Drift Monitoring** — Model performance MUST be evaluated weekly
    against a holdout set. If recall drops below 0.85 or FPR exceeds
    0.07, an automatic alert MUST be triggered and retraining MUST be
    scheduled within 48 hours.

---

## 3. Roles and Responsibilities

| Role                       | Responsibility                                       |
|----------------------------|------------------------------------------------------|
| Developer                  | Implement models, API, plugin, logs, preprocessing   |
| Data Manager               | Collect datasets, clean data, generate synthetic data |
| Tester / QA                | Validate accuracy, monitor FP rate, audit logs       |
| System Operator / Merchant | Deploy plugin, monitor system, report anomalies      |
| Security Lead              | Review access controls, audit API exposure, pen-test |

---

## 4. Data Governance

- **Data Types Allowed**: Transaction amounts, IP addresses (hashed),
  payment method, timestamp, user ID (pseudonymized), device
  fingerprint, shipping/billing address similarity score.
- **Prohibited Data**: Payment card numbers, CVV codes, passwords,
  raw PII in logs.
- **Data Retention**: Prediction logs stored for 90 days; archived
  to cold storage after 90 days; deleted after 1 year unless
  regulatory hold applies.
- **Synthetic Data Usage**: Allowed for training/testing to protect
  user privacy. Synthetic data MUST be labeled as such.

---

## 5. Operational Rules

1. **Prediction Requests**: MUST go through `/predict` endpoint with
   required fields only. Input MUST be validated against schema before
   model inference.

2. **Retraining**: MUST go through `/retrain` endpoint; old model MUST
   be backed up and versioned before replacement. Rollback to previous
   model MUST be possible within 5 minutes.

3. **Logging**: Every prediction MUST be written to the `audit_entries`
   database table with: timestamp, transaction features, predicted label,
   confidence score, model version, and top-3 feature contributions.
   Training events and model rollbacks MUST also be logged to `audit_entries`
   with full context.

4. **Thresholds**:
   - Detection recall target: ≥90%
   - False positive limit: ≤5%
   - Latency p95: ≤200ms

5. **Model Updates**: Retraining allowed only with validated data.
   Manual approval required for production deployment. A/B testing
   SHOULD be used when feasible.

6. **Fallback Strategy**: If the prediction service is unavailable:
   - Transactions under a configurable amount threshold (default: $50)
     MUST be allowed through.
   - Transactions above the threshold MUST be queued for manual review.
   - The system MUST NOT block all transactions due to service outage.
   - Fallback mode MUST be logged and alerted within 1 minute.

---

## 6. Incident Response

1. **Model Degradation**: If weekly evaluation shows recall <0.85 or
   FPR >0.07, the on-call developer MUST be notified. Retraining MUST
   begin within 48 hours.

2. **False Negative (Missed Fraud)**: Every confirmed missed fraud
   case MUST be added to the training dataset. Root cause analysis
   MUST be completed within 72 hours.

3. **Service Outage**: Fallback strategy (Section 5.6) activates
   automatically. Post-incident review MUST be completed within 5
   business days.

4. **Data Breach**: Follow PCI-DSS incident response procedures.
   Affected merchants MUST be notified within 24 hours.

---

## 7. Security & Privacy Rules

- IP addresses MUST be hashed before storage; user IDs MUST be
  pseudonymized in all logs.
- No PII MUST be transmitted outside the local environment without
  explicit consent and encryption.
- HTTPS is MANDATORY for any non-localhost API exposure.
- `/retrain` endpoint MUST require API key authentication. Keys MUST
  be rotated every 90 days.
- `/predict` endpoint MUST enforce rate limiting (default: 100 req/s
  per client) to prevent abuse and adversarial probing.
- Input validation MUST reject malformed or out-of-range feature
  values to mitigate adversarial input attacks.
- Model files MUST be integrity-checked (SHA-256 hash) before loading
  to prevent model poisoning.
- Secrets and API keys MUST use environment variables or a secrets
  manager. NEVER hardcode in source.

---

## 8. Compliance and Audit

- Prediction logs MUST be auditable for every flagged transaction.
- Model evaluation metrics (recall, precision, F1-score, FPR) MUST
  be recorded and reviewed weekly.
- Thresholds MUST only be tuned after evaluating audit logs and
  performance metrics with documented justification.
- GDPR: Users MUST be able to request explanation of any automated
  fraud decision affecting their transaction.

---

## 9. Testing Standards

- All modules MUST have unit tests covering core logic.
- Integration tests MUST verify the predict and retrain endpoints.
- Model accuracy tests MUST run against a fixed holdout set before
  any production deployment.
- Minimum test pass rate for deployment: 100% (no failing tests).
- Load tests MUST verify p95 ≤200ms under expected peak traffic
  before production release.

---

## 10. Modularity Rules

Each module MUST have clear interfaces:
- `preprocess.py` — Prepares and validates transaction data
- `train.py` — Trains models with versioned artifacts
- `predict.py` / FastAPI `main.py` — Serves predictions with
  explainability
- `monitor.py` — Tracks drift and triggers alerts
- Plugin folder — Connects API to WooCommerce / Stripe

Changes to one module MUST NOT break other modules. All inter-module
contracts MUST be documented.

---

## 11. Governance of Code Generation

- All code generated by AI assistants MUST adhere to field names,
  preprocessing rules, model specs, and API contracts defined in
  `spec.md`.
- Generated code MUST be reviewed for compliance with this
  constitution before deployment.
- Generated code MUST include appropriate error handling and input
  validation.

---

## 12. Amendments

### Amendment Policy

This constitution may be updated when:
1. New regulations require additional compliance measures.
2. Detection accuracy or false positive thresholds need adjustment.
3. System architecture evolves (new models, new plugins, new
   integrations).
4. Incident post-mortems reveal gaps in operational rules.

### Amendment Process

1. Propose change with rationale in a pull request.
2. Review by at least one other team member.
3. Update version number following semantic versioning:
   - **MAJOR**: Principle removals or incompatible redefinitions.
   - **MINOR**: New principles, sections, or material expansions.
   - **PATCH**: Clarifications, wording fixes, non-semantic changes.
4. Update `Last Amended` date.
5. Log amendment in commit history with rationale.

### Amendment History

| Version | Date       | Summary                                    |
|---------|------------|--------------------------------------------|
| 1.1.0   | 2026-03-13 | Updated Section 5.3 logging to use database (audit_entries table) instead of CSV for production-grade auditability |
| 1.0.0   | 2026-03-11 | Initial ratified constitution              |

---

**End of Constitution — Fraud Detection AI System**
