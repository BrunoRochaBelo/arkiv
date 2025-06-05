import csv
from io import StringIO
from . import reports_bp
from ..celery_app import celery_app
from ..extensions import db
from ..models import Asset, Library
from .. import create_app

@celery_app.task
def generate_assets_report(org_id):
    app = create_app()
    with app.app_context():
        assets = Asset.query.join(Library).filter(Library.org_id == org_id).all()
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['id', 'filename', 'size'])
        for a in assets:
            writer.writerow([a.id, a.filename_orig, a.size])
        return si.getvalue()
