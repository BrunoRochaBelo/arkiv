from datetime import datetime

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    ph = PasswordHasher()
except Exception:  # pragma: no cover - optional argon2 fallback
    # Allows running without argon2 installed (e.g., in minimal dev envs)
    from werkzeug.security import generate_password_hash, check_password_hash

    class PasswordHasher:
        def hash(self, password: str) -> str:
            return generate_password_hash(password)

        def verify(self, hashed: str, password: str) -> bool:
            return check_password_hash(hashed, password)

    class VerifyMismatchError(Exception):
        pass

    ph = PasswordHasher()

from .extensions import db
from flask_login import UserMixin

class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    plan = db.relationship('Plan', backref='organizations')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    members = db.relationship('Membership', back_populates='organization')
    libraries = db.relationship('Library', back_populates='organization')


class Plan(db.Model):
    __tablename__ = 'plan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    storage_quota_gb = db.Column(db.Integer, nullable=False)
    price_monthly = db.Column(db.Numeric(10, 2), nullable=False)
    features = db.Column(db.JSON)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    mfa_enabled = db.Column(db.Boolean, default=False)

    memberships = db.relationship('Membership', back_populates='user')
    uploads = db.relationship('Asset', back_populates='uploader')

    def set_password(self, password: str) -> None:
        self.password_hash = ph.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False

class Membership(db.Model):
    __tablename__ = 'membership'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), primary_key=True)
    role = db.Column(db.String(15), nullable=False)

    user = db.relationship('User', back_populates='memberships')
    organization = db.relationship('Organization', back_populates='members')


class Library(db.Model):
    __tablename__ = 'library'
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship('Organization', back_populates='libraries')
    folders = db.relationship('Folder', back_populates='library')


class Folder(db.Model):
    __tablename__ = 'folder'
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    library = db.relationship('Library', back_populates='folders')
    parent = db.relationship('Folder', remote_side=[id], backref='children')
    assets = db.relationship('Asset', back_populates='folder')

    __table_args__ = (
        db.UniqueConstraint('library_id', 'parent_id', 'name', name='uq_folder_name'),
    )


class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    filename_orig = db.Column(db.String(255), nullable=False)
    filename_storage = db.Column(db.String(255), nullable=False, unique=True)
    mime = db.Column(db.String(50), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    checksum_sha256 = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    folder = db.relationship('Folder', back_populates='assets')
    uploader = db.relationship('User', back_populates='uploads')
    tags = db.relationship('Tag', secondary='asset_tag', back_populates='assets')


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    color_hex = db.Column(db.String(7), default='#CCCCCC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organization = db.relationship('Organization')
    assets = db.relationship('Asset', secondary='asset_tag', back_populates='tags')

    __table_args__ = (
        db.UniqueConstraint('org_id', 'name', name='uq_tag_per_org'),
    )


class AssetTag(db.Model):
    __tablename__ = 'asset_tag'
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    # Use Integer for broader SQLite compatibility
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    entity = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    payload = db.Column(db.JSON)

    __table_args__ = (
        db.Index('idx_audit_org_time', 'org_id', 'timestamp'),
        {
            # ensure AUTOINCREMENT behavior on SQLite so ids are generated
            'sqlite_autoincrement': True,
        },
    )
