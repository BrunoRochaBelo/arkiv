from flask import request
from sqlalchemy import text
from ..extensions import db
from ..models import AuditLog


def record_audit(action, entity, entity_id, user_id=None, org_id=None, payload=None):
    log = AuditLog(
        org_id=org_id,
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=request.remote_addr,
        payload=payload or {},
    )
    db.session.add(log)
    db.session.commit()


def ensure_audit_log_schema():
    """Ensure audit_log uses AUTOINCREMENT on SQLite."""
    engine = db.engine
    if not engine.url.drivername.startswith("sqlite"):
        return
    result = engine.execute(
        text(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='audit_log'"
        )
    ).fetchone()
    if result and "AUTOINCREMENT" not in result[0].upper():
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE audit_log RENAME TO audit_log_old"))
            AuditLog.__table__.create(conn)
            conn.execute(
                text(
                    "INSERT INTO audit_log (id, org_id, user_id, action, entity, entity_id, timestamp, ip_address, payload) "
                    "SELECT id, org_id, user_id, action, entity, entity_id, timestamp, ip_address, payload FROM audit_log_old"
                )
            )
            conn.execute(text("DROP TABLE audit_log_old"))
