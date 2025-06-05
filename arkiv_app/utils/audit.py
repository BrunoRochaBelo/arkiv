from flask import request
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
