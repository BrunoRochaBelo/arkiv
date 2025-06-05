from flask import Response
from flask_login import login_required, current_user
import csv
from io import StringIO, BytesIO
import pandas as pd

from ..models import Asset, Library
from ..extensions import db
from . import reports_bp

@reports_bp.route('/reports/assets.csv')
@login_required
def assets_report():
    org_id = current_user.memberships[0].org_id
    assets = (
        Asset.query
        .join(Library)
        .filter(Library.org_id == org_id)
        .all()
    )
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'filename', 'size'])
    for a in assets:
        writer.writerow([a.id, a.filename_orig, a.size])
    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=assets.csv'}
    )


@reports_bp.route('/reports/assets.xlsx')
@login_required
def assets_report_xlsx():
    org_id = current_user.memberships[0].org_id
    assets = (
        Asset.query
        .join(Library)
        .filter(Library.org_id == org_id)
        .all()
    )
    df = pd.DataFrame([{"id": a.id, "filename": a.filename_orig, "size": a.size} for a in assets])
    output = BytesIO()
    df.to_excel(output, index=False)
    return Response(
        output.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=assets.xlsx"}
    )
