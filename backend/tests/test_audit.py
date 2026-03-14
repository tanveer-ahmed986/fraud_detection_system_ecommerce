import pytest
from app.models.db import AuditEntry


class TestAuditEntry:
    def test_create_audit_entry(self):
        entry = AuditEntry(
            event_type="prediction",
            event_data={"transaction_id": "123", "label": "fraud"},
            model_version="1.0",
        )
        assert entry.event_type == "prediction"
        assert entry.event_data["label"] == "fraud"

    def test_valid_event_types(self):
        valid_types = ["prediction", "training", "rollback", "config_change", "fallback"]
        for etype in valid_types:
            entry = AuditEntry(event_type=etype, event_data={})
            assert entry.event_type == etype
