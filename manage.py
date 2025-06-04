#!/usr/bin/env python
import os
from arkiv_app import create_app
from flask_migrate import Migrate, upgrade
from arkiv_app.extensions import db

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    from arkiv_app.models import (
        User, Organization, Membership, Library, Folder, Asset, Tag, Plan
    )
    return dict(
        db=db,
        User=User,
        Organization=Organization,
        Membership=Membership,
        Library=Library,
        Folder=Folder,
        Asset=Asset,
        Tag=Tag,
        Plan=Plan
    )

if __name__ == "__main__":
    upgrade()