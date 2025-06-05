import os
import uuid
import hashlib
from PIL import Image

from ..celery_app import celery_app
from ..extensions import db
from ..models import Asset
from .. import create_app


@celery_app.task
def generate_thumbnail(asset_id, upload_dir, thumb_dir):
    app = create_app()
    with app.app_context():
        asset = Asset.query.get(asset_id)
        if not asset:
            return
        img_path = os.path.join(upload_dir, asset.filename_storage)
        thumb_path = os.path.join(thumb_dir, asset.filename_storage)
        try:
            img = Image.open(img_path)
            img.thumbnail((256, 256))
            img.save(thumb_path)
            asset.width, asset.height = img.size
            db.session.commit()
        except Exception:
            pass


@celery_app.task
def perform_ocr(asset_id):
    app = create_app()
    with app.app_context():
        asset = Asset.query.get(asset_id)
        if not asset:
            return
        # Placeholder for OCR using pytesseract
        return 'ok'
