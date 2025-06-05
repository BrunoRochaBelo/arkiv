"""Seed initial data for development."""
from arkiv_app import create_app
from arkiv_app.extensions import db
from arkiv_app.models import Plan, Organization, User, Membership


def main():
    app = create_app()
    with app.app_context():
        db.create_all()

        plan = Plan.query.first()
        if not plan:
            plan = Plan(name="Demo", storage_quota_gb=10, price_monthly=0)
            db.session.add(plan)
            db.session.commit()

        org = Organization.query.first()
        if not org:
            org = Organization(name="DemoCorp", slug="democorp", plan_id=plan.id)
            db.session.add(org)
            db.session.commit()

        user = User.query.filter_by(email="owner@democorp.com").first()
        if not user:
            user = User(
                name="Owner",
                email="owner@democorp.com",
                password_hash="(OWNER)1234",
            )
            db.session.add(user)
            db.session.commit()
            membership = Membership(user_id=user.id, org_id=org.id, role="OWNER")
            db.session.add(membership)
            db.session.commit()


if __name__ == "__main__":
    main()
